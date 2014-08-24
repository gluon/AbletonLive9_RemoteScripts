#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Push/DrumGroupComponent.py
from itertools import imap, ifilter
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if, first
from consts import MessageBoxText
from MatrixMaps import PAD_FEEDBACK_CHANNEL
from MessageBoxComponent import Messenger
from SlideComponent import SlideComponent, Slideable

class DrumGroupComponent(SlideComponent, Slideable, Messenger):
    """
    Class representing a drum group pads in a matrix.
    """
    __subject_events__ = ('pressed_pads',)

    def __init__(self, *a, **k):
        self._select_button = None
        self._quantize_button = None
        self._delete_button = None
        self._mute_button = None
        self._solo_button = None
        self._drum_matrix = None
        self._drum_group_device = None
        self._visible_drum_pads = []
        self._all_drum_pads = []
        self._selected_drum_pad = None
        self._selected_pads = []
        self._takeover_drums = False
        super(DrumGroupComponent, self).__init__(dragging_enabled=True, *a, **k)
        self._visible_drum_pad_slots = self.register_slot_manager()

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
    def pressed_pads(self):
        return self._selected_pads

    def update(self):
        super(DrumGroupComponent, self).update()
        self._set_control_pads_from_script(False)
        self._update_drum_pad_leds()

    def set_drum_group_device(self, drum_group_device):
        if drum_group_device and not drum_group_device.can_have_drum_pads:
            drum_group_device = None
        if drum_group_device != self._drum_group_device:
            drum_group_view = drum_group_device.view if drum_group_device else None
            self._on_chains_changed.subject = drum_group_device
            self._on_visible_drum_pads_changed.subject = drum_group_device
            self._on_selected_drum_pad_changed.subject = drum_group_view
            self._on_drum_pads_scroll_position_changed.subject = drum_group_view
            self._drum_group_device = drum_group_device
            self._update_drum_pad_listeners()
            self._on_selected_drum_pad_changed()
            self.notify_contents()
            super(DrumGroupComponent, self).update()

    def set_drum_matrix(self, matrix):
        self._drum_matrix = matrix
        self._on_drum_matrix_value.subject = matrix
        if self._selected_pads:
            self._selected_pads = []
            self.notify_pressed_pads()
        if matrix:
            matrix.reset()
        self._update_control_from_script()
        self._update_drum_pad_leds()

    def set_select_button(self, button):
        self._select_button = button
        self._on_select_value.subject = button

    def set_mute_button(self, button):
        self._mute_button = button
        self._on_mute_value.subject = button

    def set_solo_button(self, button):
        self._solo_button = button
        self._on_solo_value.subject = button

    def set_quantize_button(self, button):
        self._quantize_button = button
        self._on_quantize_value.subject = button

    def set_delete_button(self, button):
        self._delete_button = button
        self._on_delete_value.subject = button

    @subject_slot('drum_pads_scroll_position')
    def _on_drum_pads_scroll_position_changed(self):
        self.notify_position()

    @subject_slot('chains')
    def _on_chains_changed(self):
        self._update_drum_pad_leds()
        self.notify_contents()

    @subject_slot('visible_drum_pads')
    def _on_visible_drum_pads_changed(self):
        self._update_drum_pad_listeners()
        self._update_drum_pad_leds()

    def _update_drum_pad_listeners(self):
        """
        add and remove listeners for visible drum pads, including
        mute and solo state
        """
        if self._drum_group_device:
            self._all_drum_pads = self._drum_group_device.drum_pads
            self._visible_drum_pads = self._drum_group_device.visible_drum_pads
            self._visible_drum_pad_slots.disconnect()
            for pad in self._visible_drum_pads:
                self._visible_drum_pad_slots.register_slot(pad, self._update_drum_pad_leds, 'mute')
                self._visible_drum_pad_slots.register_slot(pad, self._update_drum_pad_leds, 'solo')

    def _update_drum_pad_leds(self):
        """ update hardware LEDs for drum pads """
        if self.is_enabled() and self._drum_matrix and self._drum_group_device:
            soloed_pads = find_if(lambda pad: pad.solo, self._all_drum_pads)
            for button, (col, row) in ifilter(first, self._drum_matrix.iterbuttons()):
                index = (self._drum_matrix.height() - 1 - row) * self._drum_matrix.width() + col
                if self._visible_drum_pads:
                    pad = self._visible_drum_pads[index]
                    self._update_pad_led(pad, button, soloed_pads)
                else:
                    button.set_light('DrumGroup.PadInvisible')

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
        button.set_on_off_values('DrumGroup.PadAction', button_color)
        button.force_next_send()
        button.turn_off()

    @subject_slot('selected_drum_pad')
    def _on_selected_drum_pad_changed(self):
        self._selected_drum_pad = self._drum_group_device.view.selected_drum_pad if self._drum_group_device else None
        self._update_drum_pad_leds()

    @subject_slot('value')
    def _on_drum_matrix_value(self, value, x, y, is_momentary):
        if self.is_enabled() and self._visible_drum_pads != None:
            drum_index = (3 - y) * 4 + x
            if len(self._visible_drum_pads) > drum_index:
                selected_drum_pad = self._visible_drum_pads[drum_index]
                pad = self._drum_matrix.get_button(x, y)
                if value != 0 or not is_momentary:
                    self._on_press_pad(selected_drum_pad, pad)
                else:
                    self._on_release_pad(selected_drum_pad, pad)

    def _on_release_pad(self, selected_drum_pad, pad):
        self._indicate_action(False, pad)
        if selected_drum_pad in self._selected_pads:
            self._selected_pads.remove(selected_drum_pad)
            if not self._selected_pads:
                self._update_control_from_script()
            self.notify_pressed_pads()

    def _on_press_pad(self, selected_drum_pad, pad):
        if self._mute_button and self._mute_button.is_pressed():
            selected_drum_pad.mute = not selected_drum_pad.mute
        if self._solo_button and self._solo_button.is_pressed():
            selected_drum_pad.solo = not selected_drum_pad.solo
        if self._quantize_button and self._quantize_button.is_pressed():
            self._indicate_action(True, pad)
            self._do_quantize_pitch(selected_drum_pad.note)
        if self._delete_button and self._delete_button.is_pressed():
            self._indicate_action(True, pad)
            self._do_delete_pitch(selected_drum_pad)
        if self._select_button and self._select_button.is_pressed():
            self._drum_group_device.view.selected_drum_pad = selected_drum_pad
            self._do_select_drum_pad(selected_drum_pad)
            self._selected_pads.append(selected_drum_pad)
            if len(self._selected_pads) == 1:
                self._update_control_from_script()
            self.notify_pressed_pads()

    def _indicate_action(self, indicate, pad):
        if pad:
            pad.set_light(indicate)

    def _do_select_drum_pad(self, drum_pad):
        """ Override when you give it a select button """
        pass

    def _do_quantize_pitch(self, note):
        """ Override when you give it a quantize button """
        pass

    def _do_delete_pitch(self, drum_pad):
        clip = self.song().view.detail_clip
        if clip:
            loop_length = clip.loop_end - clip.loop_start
            clip.remove_notes(clip.loop_start, drum_pad.note, loop_length, 1)
            self.show_notification(MessageBoxText.DELETE_NOTES % drum_pad.name)

    @subject_slot('value')
    def _on_delete_value(self, value):
        self._set_control_pads_from_script(bool(value))

    @subject_slot('value')
    def _on_quantize_value(self, value):
        self._set_control_pads_from_script(bool(value))

    @subject_slot('value')
    def _on_select_value(self, value):
        self._set_control_pads_from_script(bool(value))

    @subject_slot('value')
    def _on_mute_value(self, value):
        self._set_control_pads_from_script(bool(value))

    @subject_slot('value')
    def _on_solo_value(self, value):
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
        takeover_drums = self._takeover_drums or self._selected_pads
        profile = 'default' if takeover_drums else 'drums'
        if self._drum_matrix:
            for button, _ in ifilter(first, self._drum_matrix.iterbuttons()):
                translation_channel = PAD_FEEDBACK_CHANNEL
                button.set_channel(translation_channel)
                button.set_enabled(takeover_drums)
                button.sensitivity_profile = profile