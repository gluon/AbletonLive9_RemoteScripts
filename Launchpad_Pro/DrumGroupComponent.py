#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/DrumGroupComponent.py
from itertools import imap
from _Framework.Util import find_if, first, clamp
from _Framework.Dependency import depends
from _Framework.SubjectSlot import subject_slot_group, subject_slot
from _Framework.Control import PlayableControl, ButtonControl, control_matrix
from .consts import ACTION_BUTTON_COLORS
from .SlideComponent import SlideComponent, Slideable, ScrollComponent
BASE_DRUM_RACK_NOTE = 36
DEFAULT_POSITION = 9

class ResettableSlideComponent(SlideComponent):

    def __init__(self, slideable = None, *a, **k):
        super(SlideComponent, self).__init__(*a, **k)
        slideable = slideable or self
        self._slideable = slideable
        self._position_scroll, self._page_scroll = self.register_components(ResettingScrollComponent(), ResettingScrollComponent())
        self._position_scroll.scrollable = self
        self._page_scroll.scrollable = self
        self._page_scroll.can_scroll_up = self.can_scroll_page_up
        self._page_scroll.can_scroll_down = self.can_scroll_page_down
        self._page_scroll.scroll_down = self.scroll_page_down
        self._page_scroll.scroll_up = self.scroll_page_up
        self._on_position_changed.subject = slideable

    def reset(self):
        self._slideable.position = DEFAULT_POSITION


class ResettingScrollComponent(ScrollComponent):

    def __init__(self, scrollable = None, *a, **k):
        self._did_reset = False
        super(ResettingScrollComponent, self).__init__(*a, **k)

    def _on_scroll_pressed(self, button, scroll_step, scroll_task):
        self._did_reset = self._should_reset()
        if self._did_reset:
            self._scroll_task_up.kill()
            self._scroll_task_down.kill()
            self.scrollable.reset()
        else:
            super(ResettingScrollComponent, self)._on_scroll_pressed(button, scroll_step, scroll_task)

    def _on_scroll_released(self, scroll_task):
        scroll_task.kill()
        if not self._did_reset:
            self._ensure_scroll_one_direction()

    def _should_reset(self):
        return self.scroll_up_button.is_pressed and self.scroll_down_button.is_pressed

    def _update_scroll_buttons(self):
        if self.can_scroll_up():
            self.scroll_up_button.color = 'Scrolling.Enabled'
            self.scroll_up_button.pressed_color = 'Scrolling.Pressed'
        else:
            self.scroll_up_button.color = 'Scrolling.Disabled'
            self.scroll_up_button.pressed_color = 'Scrolling.Disabled'
        if self.can_scroll_down():
            self.scroll_down_button.color = 'Scrolling.Enabled'
            self.scroll_down_button.pressed_color = 'Scrolling.Pressed'
        else:
            self.scroll_down_button.color = 'Scrolling.Disabled'
            self.scroll_down_button.pressed_color = 'Scrolling.Disabled'


class DrumGroupComponent(ResettableSlideComponent, Slideable):
    __subject_events__ = ('pressed_pads',)
    mute_button = ButtonControl()
    solo_button = ButtonControl()
    delete_button = ButtonControl(**ACTION_BUTTON_COLORS)
    quantize_button = ButtonControl()
    select_button = ButtonControl(color='Misc.Shift', pressed_color='Misc.ShiftOn')
    drum_matrix = control_matrix(PlayableControl)

    @depends(set_pad_translations=None)
    def __init__(self, pitch_deleter, translation_channel = None, set_pad_translations = None, *a, **k):
        self._pitch_deleter = pitch_deleter
        self._takeover_drums = False
        self._drum_group_device = None
        self._selected_drum_pad = None
        self._all_drum_pads = []
        self._selected_pads = []
        self._visible_drum_pads = []
        self._translation_channel = translation_channel
        self._coordinate_to_pad_map = {}
        super(DrumGroupComponent, self).__init__(*a, **k)
        self._set_pad_translations = set_pad_translations
        self._on_selected_clip_changed.subject = self._pitch_deleter
        self._layout_set = False

    position_count = 32
    page_length = 4
    page_offset = 1

    def contents_range(self, pmin, pmax):
        pos_count = self.position_count
        first_pos = max(int(pmin - 0.05), 0)
        last_pos = min(int(pmax + 0.2), pos_count)
        return xrange(first_pos, last_pos)

    def contents(self, index):
        drum = self._drum_group_device
        if drum:
            return any(imap(lambda pad: pad.chains, drum.drum_pads[index * 4:index * 4 + 4]))
        return False

    def _get_position(self):
        if self._drum_group_device:
            return self._drum_group_device.view.drum_pads_scroll_position
        return 0

    def _set_position(self, index):
        if not 0 <= index <= 28:
            raise AssertionError
            self._drum_group_device.view.drum_pads_scroll_position = self._drum_group_device and index

    position = property(_get_position, _set_position)

    @property
    def width(self):
        if self.drum_matrix.width:
            return self.drum_matrix.width
        return 4

    @property
    def height(self):
        if self.drum_matrix.height:
            return self.drum_matrix.height
        return 4

    @property
    def pressed_pads(self):
        return self._selected_pads

    @property
    def visible_drum_pads(self):
        if self._visible_drum_pads and self._all_drum_pads:
            first_pad = first(self._visible_drum_pads)
            if first_pad:
                size = self.width * self.height
                first_note = first_pad.note
                if first_note > 128 - size:
                    size = 128 - first_note
                offset = clamp(first_note, 0, 128 - len(self._visible_drum_pads))
                return self._all_drum_pads[offset:offset + size]
        return []

    def update(self):
        super(DrumGroupComponent, self).update()
        self._set_control_pads_from_script(False)
        self._update_led_feedback()

    def set_drum_matrix(self, matrix):
        if not matrix or not self._layout_set:
            self.drum_matrix.set_control_element(matrix)
            for button in self.drum_matrix:
                button.channel = self._translation_channel

            if self._selected_pads:
                self._selected_pads = []
                self.notify_pressed_pads()
            self._create_and_set_pad_translations()
            self._update_control_from_script()
            self._update_identifier_translations()
            self._layout_set = bool(matrix)
            self._update_led_feedback()

    @subject_slot('selected_clip')
    def _on_selected_clip_changed(self):
        if self.is_enabled():
            self.delete_button.enabled = self._pitch_deleter.can_perform_midi_clip_action()

    def set_drum_group_device(self, drum_group_device):
        if drum_group_device and not drum_group_device.can_have_drum_pads:
            drum_group_device = None
        if drum_group_device != self._drum_group_device:
            self._on_visible_drum_pads_changed.subject = drum_group_device
            drum_group_view = drum_group_device.view if drum_group_device else None
            self._on_selected_drum_pad_changed.subject = drum_group_view
            self._on_drum_pads_scroll_position_changed.subject = drum_group_view
            self._drum_group_device = drum_group_device
            self._update_drum_pad_listeners()
            self._on_selected_drum_pad_changed()
            self._update_identifier_translations()
            super(DrumGroupComponent, self).update()

    def _update_drum_pad_listeners(self):
        """
        add and remove listeners for visible drum pads, including
        mute and solo state
        """
        if self._drum_group_device:
            self._all_drum_pads = self._drum_group_device.drum_pads
            self._visible_drum_pads = self._drum_group_device.visible_drum_pads
            self._on_solo_changed.replace_subjects(self._visible_drum_pads)
            self._on_mute_changed.replace_subjects(self._visible_drum_pads)
            self._update_identifier_translations()

    @subject_slot_group('solo')
    def _on_solo_changed(self, pad):
        self._update_led_feedback()

    @subject_slot_group('mute')
    def _on_mute_changed(self, pad):
        self._update_led_feedback()

    def _update_led_feedback(self):
        if self._drum_group_device:
            soloed_pads = find_if(lambda pad: pad.solo, self._all_drum_pads)
            for button in self.drum_matrix:
                pad = self._coordinate_to_pad_map.get(button.coordinate, None)
                if pad:
                    self._update_pad_led(pad, button, soloed_pads)

    def _update_pad_led(self, pad, button, soloed_pads):
        button_color = 'DrumGroup.PadEmpty'
        if pad == self._selected_drum_pad:
            if soloed_pads and not pad.solo and not pad.mute:
                button_color = 'DrumGroup.PadSelectedNotSoloed'
            elif pad.mute and not pad.solo:
                button_color = 'DrumGroup.PadMutedSelected'
            elif soloed_pads and pad.solo:
                button_color = 'DrumGroup.PadSoloedSelected'
            else:
                button_color = 'DrumGroup.PadSelected'
        elif pad.chains:
            if soloed_pads and not pad.solo:
                if not pad.mute:
                    button_color = 'DrumGroup.PadFilled'
                else:
                    button_color = 'DrumGroup.PadMuted'
            elif not soloed_pads and pad.mute:
                button_color = 'DrumGroup.PadMuted'
            elif soloed_pads and pad.solo:
                button_color = 'DrumGroup.PadSoloed'
            else:
                button_color = 'DrumGroup.PadFilled'
        else:
            button_color = 'DrumGroup.PadEmpty'
        button.color = button_color

    def _button_coordinates_to_pad_index(self, first_note, coordinates):
        y, x = coordinates
        y = self.height - y - 1
        if x < 4 and y >= 4:
            first_note += 16
        elif x >= 4 and y < 4:
            first_note += 4 * self.width
        elif x >= 4 and y >= 4:
            first_note += 4 * self.width + 16
        index = x % 4 + y % 4 * 4 + first_note
        return index

    @drum_matrix.pressed
    def drum_matrix(self, pad):
        self._on_matrix_pressed(pad)

    @drum_matrix.released
    def drum_matrix(self, pad):
        self._on_matrix_released(pad)

    def _on_matrix_released(self, pad):
        selected_drum_pad = self._coordinate_to_pad_map[pad.coordinate]
        if selected_drum_pad in self._selected_pads:
            self._selected_pads.remove(selected_drum_pad)
            if not self._selected_pads:
                self._update_control_from_script()
            self.notify_pressed_pads()
        self._update_led_feedback()

    def _on_matrix_pressed(self, pad):
        selected_drum_pad = self._coordinate_to_pad_map[pad.coordinate]
        if self.mute_button.is_pressed:
            selected_drum_pad.mute = not selected_drum_pad.mute
        if self.solo_button.is_pressed:
            selected_drum_pad.solo = not selected_drum_pad.solo
        if self.quantize_button.is_pressed:
            pad.color = 'DrumGroup.PadAction'
            self.quantize_pitch(selected_drum_pad.note)
        if self.delete_button.is_pressed:
            pad.color = 'DrumGroup.PadAction'
            self.delete_pitch(selected_drum_pad)
        if self.select_button.is_pressed:
            self._drum_group_device.view.selected_drum_pad = selected_drum_pad
            self.select_drum_pad(selected_drum_pad)
            self._selected_pads.append(selected_drum_pad)
            if len(self._selected_pads) == 1:
                self._update_control_from_script()
            self.notify_pressed_pads()
        if self.mute_button.is_pressed or self.solo_button.is_pressed:
            self._update_led_feedback()

    @subject_slot('visible_drum_pads')
    def _on_visible_drum_pads_changed(self):
        self._update_drum_pad_listeners()
        self._update_led_feedback()

    @subject_slot('drum_pads_scroll_position')
    def _on_drum_pads_scroll_position_changed(self):
        self._update_identifier_translations()
        self._update_led_feedback()
        self.notify_position()

    @subject_slot('selected_drum_pad')
    def _on_selected_drum_pad_changed(self):
        self._selected_drum_pad = self._drum_group_device.view.selected_drum_pad if self._drum_group_device else None
        self._update_led_feedback()

    @mute_button.value
    def mute_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    @solo_button.value
    def solo_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    @delete_button.value
    def delete_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    @quantize_button.value
    def quantize_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    @select_button.value
    def select_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    def _set_control_pads_from_script(self, takeover_drums):
        """
        If takeover_drums, the matrix buttons will be controlled from
        the script. Otherwise they send midi notes to the track
        associated to this drum group.
        """
        if takeover_drums != self._takeover_drums:
            self._takeover_drums = takeover_drums
            self._update_control_from_script()

    def _update_control_from_script(self):
        takeover_drums = self._takeover_drums or bool(self._selected_pads)
        for button in self.drum_matrix:
            button.set_playable(not takeover_drums)

    def _update_identifier_translations(self):
        if not self._can_set_pad_translations():
            self._set_non_pad_translated_identifiers()
        else:
            self._set_pad_translated_identifiers()

    def _set_non_pad_translated_identifiers(self):
        visible_drum_pads = self.visible_drum_pads
        if visible_drum_pads:
            for button in self.drum_matrix:
                identifier = self._button_coordinates_to_pad_index(first(visible_drum_pads).note, button.coordinate)
                if identifier < 128:
                    button.identifier = identifier
                    button.enabled = True
                    self._coordinate_to_pad_map[button.coordinate] = self._all_drum_pads[button.identifier]
                else:
                    button.enabled = False

    def _set_pad_translated_identifiers(self):
        visible_drum_pads = self.visible_drum_pads
        if visible_drum_pads:
            for index, button in enumerate(self.drum_matrix):
                row, col = button.coordinate
                self._coordinate_to_pad_map[self.width - 1 - row, col] = visible_drum_pads[index]

    def _can_set_pad_translations(self):
        return self.width <= 4 and self.height <= 4

    def _create_and_set_pad_translations(self):

        def create_translation_entry(button):
            row, col = button.coordinate
            button.identifier = self._button_coordinates_to_pad_index(BASE_DRUM_RACK_NOTE, button.coordinate)
            return (col,
             row,
             button.identifier,
             button.channel)

        if self._can_set_pad_translations():
            translations = tuple(map(create_translation_entry, self.drum_matrix))
            self._set_pad_translated_identifiers()
        else:
            translations = None
            self._set_non_pad_translated_identifiers()
        self._set_pad_translations(translations)

    def select_drum_pad(self, drum_pad):
        """ Override when you give it a select button """
        pass

    def quantize_pitch(self, note):
        """ Override when you give it a quantize button """
        raise NotImplementedError

    def delete_pitch(self, drum_pad):
        self._pitch_deleter.delete_pitch(drum_pad.note)