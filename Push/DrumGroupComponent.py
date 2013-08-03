#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/DrumGroupComponent.py
from itertools import imap
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if, clamp
from _Framework.ScrollComponent import ScrollComponent
from TouchStripElement import TouchStripElement
from MatrixMaps import PAD_FEEDBACK_CHANNEL

class DrumGroupComponent(ScrollComponent):
    """
    Class representing a drum group pads in a matrix.
    """
    __subject_events__ = ('pressed_pads',)

    def __init__(self, *a, **k):
        super(DrumGroupComponent, self).__init__(*a, **k)
        self._select_button = None
        self._quantize_button = None
        self._mute_button = None
        self._solo_button = None
        self._shift_button = None
        self._drum_matrix = None
        self._drum_group_device = None
        self._visible_drum_pads = []
        self._all_drum_pads = []
        self._selected_drum_pad = None
        self._selected_pads = []
        self._visible_drum_pad_slots = self.register_slot_manager()
        self._takeover_drums = False
        self._touch_strip_state = []

    @property
    def pressed_pads(self):
        return self._selected_pads

    def update(self):
        super(DrumGroupComponent, self).update()
        self._set_control_pads_from_script(False)
        self._update_drum_pad_leds()
        self._update_touch_strip()

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
            self._update_touch_strip()
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

    def set_shift_button(self, button):
        self._shift_button = button

    def set_mute_button(self, button):
        self._mute_button = button
        self._on_mute_value.subject = button

    def set_solo_button(self, button):
        self._solo_button = button
        self._on_solo_value.subject = button

    def set_quantize_button(self, button):
        self._quantize_button = button
        self._on_quantize_value.subject = button

    def set_touch_strip(self, touch_strip):
        self._on_touch_strip_value.subject = touch_strip
        self._update_touch_strip()

    def _scroll_to_led_position(self, scroll_pos):
        num_leds = self._on_touch_strip_value.subject.STATE_COUNT
        num_pad_rows = 32
        return min(int((scroll_pos + 1) / float(num_pad_rows) * num_leds), num_leds)

    def _touch_strip_to_scroll_position(self, value, offset):
        detailed = self._shift_button and self._shift_button.is_pressed()
        max_pitchbend = 16384.0
        num_pad_rows = 32
        max_pad_row = 28
        bank_size = 4
        offsetted_value = clamp(value - offset, 0, max_pitchbend)
        return min(int(offsetted_value / max_pitchbend * num_pad_rows), max_pad_row) if detailed else clamp(int(int(value / max_pitchbend * num_pad_rows + 3) / float(bank_size)) * bank_size - 3, 0, max_pad_row)

    def _scroll_to_touch_strip_position(self, scroll_pos):
        max_pitchbend = 16384.0
        num_pad_rows = 32.0
        return min(int(scroll_pos / num_pad_rows * max_pitchbend), int(max_pitchbend))

    @subject_slot('value')
    def _on_touch_strip_value(self, value):
        drum_group_view = self._on_drum_pads_scroll_position_changed.subject
        if self.is_enabled() and drum_group_view:
            position = self._touch_strip_to_scroll_position(value, self._on_touch_strip_value.subject.drag_offset)
            drum_group_view.drum_pads_scroll_position = position

    @subject_slot('drum_pads_scroll_position')
    def _on_drum_pads_scroll_position_changed(self):
        self._update_touch_strip_state()

    def _update_touch_strip_state(self):
        drum_group_view = self._on_drum_pads_scroll_position_changed.subject
        touch_strip = self._on_touch_strip_value.subject
        if self.is_enabled() and touch_strip:
            if drum_group_view != None:
                position = self._scroll_to_led_position(drum_group_view.drum_pads_scroll_position)
                pp_position = self._scroll_to_touch_strip_position(drum_group_view.drum_pads_scroll_position)
                touch_strip.drag_range = xrange(pp_position, pp_position + 2048)
                state = list(self._touch_strip_state)
                state[position:position + 3] = [touch_strip.STATE_FULL] * len(state[position:position + 3])
                touch_strip.send_state(state)
            else:
                touch_strip.turn_off()

    def _update_touch_strip(self):
        strip = self._on_touch_strip_value.subject
        drum = self._drum_group_device
        if self.is_enabled() and strip:
            strip.mode = TouchStripElement.MODE_CUSTOM_FREE
            if drum:

                def pads_for_led(index):
                    num_pads = 128
                    num_leds = strip.STATE_COUNT
                    pads_per_led = float(num_pads) / num_leds
                    first_pad = max(int((index - 0.25) * pads_per_led), 0)
                    last_pad = int((index + 1 - 0.25) * pads_per_led) if index != num_leds - 1 else num_pads
                    return slice(first_pad, last_pad)

                def led_has_content(index):
                    return any(imap(lambda pad: pad.chains, drum.drum_pads[pads_for_led(index)]))

                state = [ (strip.STATE_HALF if led_has_content(i) else strip.STATE_OFF) for i in xrange(24) ]
            else:
                state = (strip.STATE_OFF,) * strip.STATE_COUNT
            self._touch_strip_state = state
            self._update_touch_strip_state()

    def can_scroll_up(self):
        if self._drum_group_device:
            position = self._drum_group_device.view.drum_pads_scroll_position
            return position < 28
        return False

    def can_scroll_down(self):
        if self._drum_group_device:
            position = self._drum_group_device.view.drum_pads_scroll_position
            return position > 0
        return False

    def scroll_up(self):
        if self.is_enabled() and self._drum_group_device:
            drum_view = self._drum_group_device.view
            position = drum_view.drum_pads_scroll_position
            if self._shift_button != None and self._shift_button.is_pressed():
                increment = 1
            else:
                remainder = (position - 1) % 4
                increment = 4 - remainder
            drum_view.drum_pads_scroll_position += min(increment, 28 - position)

    def scroll_down(self):
        if self.is_enabled() and self._drum_group_device:
            drum_view = self._drum_group_device.view
            position = drum_view.drum_pads_scroll_position
            if self._shift_button != None and self._shift_button.is_pressed():
                increment = 1
            else:
                remainder = remainder = (position - 1) % 4
                increment = 4 - remainder
            drum_view.drum_pads_scroll_position -= min(increment, position)

    @subject_slot('chains')
    def _on_chains_changed(self):
        self._update_drum_pad_leds()
        self._update_touch_strip()

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
            for button, (col, row) in self._drum_matrix.iterbuttons():
                if button:
                    index = (self._drum_matrix.height() - 1 - row) * self._drum_matrix.width() + col
                    if self._visible_drum_pads:
                        pad = self._visible_drum_pads[index]
                        self._update_pad_led(pad, button, soloed_pads)
                    else:
                        button.set_light('DrumGroup.PadInvisible')

    def _update_pad_led(self, pad, button, soloed_pads):
        is_enabled = True
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
            is_enabled = False
        button.set_on_off_values(button_color, 'DrumGroup.PadEmpty')
        button.force_next_send()
        button.set_light(is_enabled)

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
                if value != 0 or not is_momentary:
                    self._on_press_pad(selected_drum_pad)
                else:
                    self._on_release_pad(selected_drum_pad)

    def _on_release_pad(self, selected_drum_pad):
        if selected_drum_pad in self._selected_pads:
            self._selected_pads.remove(selected_drum_pad)
            if not self._selected_pads:
                self._update_control_from_script()
            self.notify_pressed_pads()

    def _on_press_pad(self, selected_drum_pad):
        if self._mute_button and self._mute_button.is_pressed():
            selected_drum_pad.mute = not selected_drum_pad.mute
        if self._solo_button and self._solo_button.is_pressed():
            selected_drum_pad.solo = not selected_drum_pad.solo
        if self._quantize_button and self._quantize_button.is_pressed():
            self._do_quantize_pitch(selected_drum_pad.note)
        if self._select_button and self._select_button.is_pressed():
            self._drum_group_device.view.selected_drum_pad = selected_drum_pad
            self._do_select_drum_pad(selected_drum_pad)
        self._selected_pads.append(selected_drum_pad)
        if len(self._selected_pads) == 1:
            self._update_control_from_script()
        self.notify_pressed_pads()

    def _do_select_drum_pad(self, drum_pad):
        """ Override when you give it a select button """
        pass

    def _do_quantize_pitch(self, note):
        """ Override when you give it a quantize button """
        pass

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
            for button, _ in self._drum_matrix.iterbuttons():
                if button:
                    translation_channel = PAD_FEEDBACK_CHANNEL
                    button.set_channel(translation_channel)
                    button.set_enabled(takeover_drums)
                    button.sensitivity_profile = profile