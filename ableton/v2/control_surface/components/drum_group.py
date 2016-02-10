#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/drum_group.py
from __future__ import absolute_import, print_function
from itertools import imap
from ...base import depends, find_if, first, clamp, listens_group, listens, liveobj_valid
from ..control import ButtonControl
from .slide import SlideComponent, Slideable
from .playable import PlayableComponent
BASE_DRUM_RACK_NOTE = 36

class DrumGroupComponent(PlayableComponent, SlideComponent, Slideable):
    mute_button = ButtonControl()
    solo_button = ButtonControl()
    delete_button = ButtonControl()
    quantize_button = ButtonControl()

    @depends(set_pad_translations=None)
    def __init__(self, translation_channel = None, set_pad_translations = None, *a, **k):
        self._drum_group_device = None
        self._selected_drum_pad = None
        self._all_drum_pads = []
        self._assigned_drum_pads = []
        self._translation_channel = translation_channel
        super(DrumGroupComponent, self).__init__(*a, **k)
        self._set_pad_translations = set_pad_translations

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
        if liveobj_valid(drum):
            return any(imap(lambda pad: pad.chains, drum.drum_pads[index * 4:index * 4 + 4]))
        return False

    @property
    def position(self):
        if liveobj_valid(self._drum_group_device):
            return self._drum_group_device.view.drum_pads_scroll_position
        return 0

    @position.setter
    def position(self, index):
        if not 0 <= index <= 28:
            raise AssertionError
            self._drum_group_device.view.drum_pads_scroll_position = liveobj_valid(self._drum_group_device) and index

    @property
    def assigned_drum_pads(self):
        return self._assigned_drum_pads

    def _update_assigned_drum_pads(self):
        assigned_drum_pads = []
        visible_drum_pads = self._drum_group_device.visible_drum_pads if liveobj_valid(self._drum_group_device) else None
        if visible_drum_pads and self._all_drum_pads:
            first_pad = first(visible_drum_pads)
            if first_pad:
                size = self.width * self.height
                first_note = first_pad.note
                if first_note > 128 - size:
                    size = 128 - first_note
                offset = clamp(first_note, 0, 128 - len(visible_drum_pads))
                assigned_drum_pads = self._all_drum_pads[offset:offset + size]
        self._assigned_drum_pads = assigned_drum_pads

    def set_matrix(self, matrix):
        super(DrumGroupComponent, self).set_matrix(matrix)
        self._update_assigned_drum_pads()
        self._create_and_set_pad_translations()

    def set_drum_group_device(self, drum_group_device):
        if drum_group_device and not drum_group_device.can_have_drum_pads:
            drum_group_device = None
        if drum_group_device != self._drum_group_device:
            self.__on_visible_drum_pads_changed.subject = drum_group_device
            drum_group_view = drum_group_device.view if drum_group_device else None
            self.__on_selected_drum_pad_changed.subject = drum_group_view
            self.__on_drum_pads_scroll_position_changed.subject = drum_group_view
            self._drum_group_device = drum_group_device
            self._update_drum_pad_listeners()
            self._update_selected_drum_pad()
            self._update_note_translations()
            super(DrumGroupComponent, self).update()

    def _update_drum_pad_listeners(self):
        """
        add and remove listeners for visible drum pads, including
        mute and solo state
        """
        if liveobj_valid(self._drum_group_device):
            self._all_drum_pads = self._drum_group_device.drum_pads
            visible_drum_pads = self._drum_group_device.visible_drum_pads
            self.__on_solo_changed.replace_subjects(visible_drum_pads)
            self.__on_mute_changed.replace_subjects(visible_drum_pads)
            self._update_assigned_drum_pads()
            self._update_note_translations()

    @listens_group('solo')
    def __on_solo_changed(self, pad):
        self._update_led_feedback()

    @listens_group('mute')
    def __on_mute_changed(self, pad):
        self._update_led_feedback()

    def _update_led_feedback(self):
        if liveobj_valid(self._drum_group_device):
            super(DrumGroupComponent, self)._update_led_feedback()

    def _update_button_color(self, button):
        pad = self._pad_for_button(button)
        if pad:
            button.color = self._color_for_pad(pad)

    def _color_for_pad(self, pad):
        has_soloed_pads = bool(find_if(lambda pad: pad.solo, self._all_drum_pads))
        button_color = 'DrumGroup.PadEmpty'
        if pad == self._selected_drum_pad:
            button_color = 'DrumGroup.PadSelected'
            if has_soloed_pads and not pad.solo and not pad.mute:
                button_color = 'DrumGroup.PadSelectedNotSoloed'
            elif pad.mute and not pad.solo:
                button_color = 'DrumGroup.PadMutedSelected'
            elif has_soloed_pads and pad.solo:
                button_color = 'DrumGroup.PadSoloedSelected'
        elif pad.chains:
            button_color = 'DrumGroup.PadFilled'
            if has_soloed_pads and not pad.solo:
                button_color = 'DrumGroup.PadFilled' if not pad.mute else 'DrumGroup.PadMuted'
            elif not has_soloed_pads and pad.mute:
                button_color = 'DrumGroup.PadMuted'
            elif has_soloed_pads and pad.solo:
                button_color = 'DrumGroup.PadSoloed'
        return button_color

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

    def _on_matrix_pressed(self, button):
        selected_drum_pad = self._pad_for_button(button)
        if self.mute_button.is_pressed:
            selected_drum_pad.mute = not selected_drum_pad.mute
        if self.solo_button.is_pressed:
            selected_drum_pad.solo = not selected_drum_pad.solo
        if self.quantize_button.is_pressed:
            button.color = 'DrumGroup.PadAction'
            self.quantize_pitch(selected_drum_pad.note)
        if self.delete_button.is_pressed:
            button.color = 'DrumGroup.PadAction'
            self.delete_pitch(selected_drum_pad)
        if self.select_button.is_pressed:
            self._drum_group_device.view.selected_drum_pad = selected_drum_pad
            self.select_drum_pad(selected_drum_pad)
            super(DrumGroupComponent, self)._on_matrix_pressed(button)
        if self.mute_button.is_pressed or self.solo_button.is_pressed:
            self._update_led_feedback()

    @listens('visible_drum_pads')
    def __on_visible_drum_pads_changed(self):
        self._update_drum_pad_listeners()
        self._update_led_feedback()

    @listens('drum_pads_scroll_position')
    def __on_drum_pads_scroll_position_changed(self):
        self._update_note_translations()
        self._update_led_feedback()
        self.notify_position()

    @listens('selected_drum_pad')
    def __on_selected_drum_pad_changed(self):
        self._update_selected_drum_pad()
        self._on_selected_drum_pad_changed()

    def _update_selected_drum_pad(self):
        self._selected_drum_pad = self._drum_group_device.view.selected_drum_pad if liveobj_valid(self._drum_group_device) else None
        self._update_led_feedback()

    def _on_selected_drum_pad_changed(self):
        pass

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

    @property
    def has_assigned_pads(self):
        return self._assigned_drum_pads and liveobj_valid(first(self._assigned_drum_pads))

    def _pad_for_button(self, button):
        if self.has_assigned_pads:
            index = self._button_coordinates_to_pad_index(first(self._assigned_drum_pads).note, button.coordinate)
            if index < 128:
                return self._all_drum_pads[index]
            return None

    def _note_translation_for_button(self, button):
        identifier = None
        channel = None
        if self.has_assigned_pads:
            identifier = self._button_coordinates_to_pad_index(first(self._assigned_drum_pads).note, button.coordinate)
            channel = self._translation_channel
        return (identifier, channel)

    def _update_note_translations(self):
        if self._assigned_drum_pads:
            if not self._can_set_pad_translations():
                super(DrumGroupComponent, self)._update_note_translations()

    def _can_set_pad_translations(self):
        return self.width <= 4 and self.height <= 4

    def _create_and_set_pad_translations(self):

        def create_translation_entry(button):
            row, col = button.coordinate
            return (col,
             row,
             button.identifier,
             button.channel)

        if self._can_set_pad_translations():
            translations = []
            for button in self.matrix:
                button.channel = self._translation_channel
                button.identifier = self._button_coordinates_to_pad_index(BASE_DRUM_RACK_NOTE, button.coordinate)
                button.enabled = True
                translations.append(create_translation_entry(button))

            self._set_pad_translations(tuple(translations))
        else:
            self._update_note_translations()
            self._set_pad_translations(None)

    def select_drum_pad(self, drum_pad):
        """ Override when you give it a select button """
        raise NotImplementedError

    def quantize_pitch(self, note):
        """ Override when you give it a quantize button """
        raise NotImplementedError

    def delete_pitch(self, drum_pad):
        """ Override when you give it a delete button """
        raise NotImplementedError