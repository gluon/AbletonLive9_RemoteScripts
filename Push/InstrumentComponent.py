#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/InstrumentComponent.py
from itertools import ifilter
from functools import partial
from _Framework.Control import ButtonControl, ToggleButtonControl
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ModesComponent import DisplayingModesComponent, EnablingModesComponent
from _Framework.DisplayDataSource import DisplayDataSource, adjust_string_crop
from _Framework.Util import recursive_map, index_if, forward_property, first
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.SlideComponent import SlideComponent, Slideable
from MessageBoxComponent import Messenger
from ScrollableList import ListComponent
from MelodicPattern import MelodicPattern, Modus, pitch_index_to_string
from MatrixMaps import NON_FEEDBACK_CHANNEL
from SlideableTouchStripComponent import SlideableTouchStripComponent
from TouchStripElement import TouchStripElement, TouchStripModes, MODWHEEL_BEHAVIOUR, DEFAULT_BEHAVIOUR
import Sysex
import consts

class InstrumentPresetsComponent(DisplayingModesComponent):
    is_horizontal = True
    interval = 3
    __subject_events__ = ('scale_mode',)

    def __init__(self, *a, **k):
        super(InstrumentPresetsComponent, self).__init__(*a, **k)
        self._line_names = recursive_map(DisplayDataSource, (('Scale layout:',), ('4th ^', '4th >', '3rd ^', '3rd >', 'Sequent ^', 'Sequent >', '', '')))
        self.add_mode('scale_p4_vertical', partial(self._set_scale_mode, True, 3), self._line_names[1][0])
        self.add_mode('scale_p4_horizontal', partial(self._set_scale_mode, False, 3), self._line_names[1][1])
        self.add_mode('scale_m3_vertical', partial(self._set_scale_mode, True, 2), self._line_names[1][2])
        self.add_mode('scale_m3_horizontal', partial(self._set_scale_mode, False, 2), self._line_names[1][3])
        self.add_mode('scale_m6_vertical', partial(self._set_scale_mode, True, None), self._line_names[1][4])
        self.add_mode('scale_m6_horizontal', partial(self._set_scale_mode, False, None), self._line_names[1][5])

    def _update_data_sources(self, selected):
        if self.is_enabled():
            for name, (source, string) in self._mode_data_sources.iteritems():
                source.set_display_string(consts.CHAR_SELECT + string if name == selected else string)

    def _set_scale_mode(self, is_horizontal, interval):
        if self.is_horizontal != is_horizontal or self.interval != interval:
            self.is_horizontal = is_horizontal
            self.interval = interval
            self.notify_scale_mode()

    def set_top_display_line(self, display):
        if display:
            self._set_display_line(display, 0)

    def set_bottom_display_line(self, display):
        if display:
            self._set_display_line(display, 1)

    def _set_display_line(self, display, line):
        if display:
            display.set_data_sources(self._line_names[line])

    def set_top_buttons(self, buttons):
        if buttons:
            buttons.reset()
        self._set_scales_preset_buttons(buttons[:6] if buttons else None)

    def _set_scales_preset_buttons(self, buttons):
        modes = ('scale_p4_vertical', 'scale_p4_horizontal', 'scale_m3_vertical', 'scale_m3_horizontal', 'scale_m6_vertical', 'scale_m6_horizontal')
        self._set_mode_buttons(buttons, modes)

    def _set_mode_buttons(self, buttons, modes):
        if buttons:
            for button, mode in zip(buttons, modes):
                self.set_mode_button(mode, button)
                if button:
                    button.set_on_off_values('Scales.Selected', 'Scales.Unselected')

        else:
            for mode in modes:
                self.set_mode_button(mode, None)

        self.update()


CIRCLE_OF_FIFTHS = tuple([ 7 * k % 12 for k in range(12) ])
KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]

class InstrumentScalesComponent(CompoundComponent):
    __subject_events__ = ('scales_changed',)
    presets_toggle_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    is_absolute = False
    is_diatonic = True
    key_center = 0

    def __init__(self, *a, **k):
        super(InstrumentScalesComponent, self).__init__(*a, **k)
        self._key_center_buttons = []
        self._encoder_touch_button_slots = self.register_slot_manager()
        self._encoder_touch_buttons = []
        self._top_key_center_buttons = None
        self._bottom_key_center_buttons = None
        self._absolute_relative_button = None
        self._diatonic_chromatic_button = None
        table = consts.MUSICAL_MODES
        self._info_sources = map(DisplayDataSource, ('Scale selection:', '', ''))
        self._line_sources = recursive_map(DisplayDataSource, (('', '', '', '', '', '', ''), ('', '', '', '', '', '', '')))
        self._modus_sources = map(partial(DisplayDataSource, adjust_string_fn=adjust_string_crop), ('', '', '', ''))
        self._presets = self.register_component(InstrumentPresetsComponent(is_enabled=False))
        self._presets.selected_mode = 'scale_p4_vertical'
        self._modus_list = self.register_component(ListComponent(data_sources=self._modus_sources))
        self._modus_list.scrollable_list.fixed_offset = 1
        self._modus_list.scrollable_list.assign_items([ Modus(name=table[i], notes=table[i + 1]) for i in xrange(0, len(consts.MUSICAL_MODES), 2) ])
        self._on_selected_modus.subject = self._modus_list.scrollable_list
        self._update_data_sources()

    presets_layer = forward_property('_presets')('layer')

    @property
    def modus(self):
        return self._modus_list.scrollable_list.selected_item.content

    @property
    def available_scales(self):
        return self.modus.scales(KEY_CENTERS)

    @property
    def notes(self):
        return self.modus.scale(self.key_center).notes

    def set_modus_line1(self, display):
        self._set_modus_line(display, 0)

    def set_modus_line2(self, display):
        self._set_modus_line(display, 1)

    def set_modus_line3(self, display):
        self._set_modus_line(display, 2)

    def set_modus_line4(self, display):
        self._set_modus_line(display, 3)

    def _set_modus_line(self, display, index):
        if display:
            display.set_data_sources([self._modus_sources[index]])
            for segment in display.segments:
                segment.separator = ''

    def set_info_line(self, display):
        if display:
            display.set_data_sources(self._info_sources)

    def set_top_display_line(self, display):
        self._set_display_line(display, 0)

    def set_bottom_display_line(self, display):
        self._set_display_line(display, 1)

    def _set_display_line(self, display, line):
        if display:
            display.set_data_sources(self._line_sources[line])

    def set_presets_toggle_button(self, button):
        self.presets_toggle_button.set_control_element(button)
        if button is None:
            self._presets.set_enabled(False)

    @presets_toggle_button.pressed
    def presets_toggle_button(self, button):
        self._presets.set_enabled(True)

    @presets_toggle_button.released
    def presets_toggle_button(self, button):
        self._presets.set_enabled(False)

    def set_top_buttons(self, buttons):
        if buttons:
            buttons.reset()
            self.set_absolute_relative_button(buttons[7])
            self._top_key_center_buttons = buttons[1:7]
            self.set_modus_up_button(buttons[0])
        else:
            self.set_absolute_relative_button(None)
            self._top_key_center_buttons = None
            self.set_modus_up_button(None)
        if self._top_key_center_buttons and self._bottom_key_center_buttons:
            self.set_key_center_buttons(self._top_key_center_buttons + self._bottom_key_center_buttons)
        else:
            self.set_key_center_buttons(tuple())

    def set_bottom_buttons(self, buttons):
        if buttons:
            buttons.reset()
            self.set_diatonic_chromatic_button(buttons[7])
            self._bottom_key_center_buttons = buttons[1:7]
            self.set_modus_down_button(buttons[0])
        else:
            self.set_diatonic_chromatic_button(None)
            self._bottom_key_center_buttons = None
            self.set_modus_down_button(None)
        if self._top_key_center_buttons and self._bottom_key_center_buttons:
            self.set_key_center_buttons(self._top_key_center_buttons + self._bottom_key_center_buttons)
        else:
            self.set_key_center_buttons([])

    def set_modus_down_button(self, button):
        self._modus_list.select_next_button.set_control_element(button)

    def set_modus_up_button(self, button):
        self._modus_list.select_prev_button.set_control_element(button)

    def set_encoder_controls(self, encoders):
        self._modus_list.encoders.set_control_element([encoders[0]] if encoders else [])

    def set_key_center_buttons(self, buttons):
        raise not buttons or len(buttons) == 12 or AssertionError
        buttons = buttons or []
        self._key_center_buttons = buttons
        self._on_key_center_button_value.replace_subjects(buttons)
        self._update_key_center_buttons()

    def set_absolute_relative_button(self, absolute_relative_button):
        self._absolute_relative_button = absolute_relative_button
        self._on_absolute_relative_value.subject = absolute_relative_button
        self._update_absolute_relative_button()

    def set_diatonic_chromatic_button(self, diatonic_chromatic_button):
        self._diatonic_chromatic_button = diatonic_chromatic_button
        self._on_diatonic_chromatic_value.subject = diatonic_chromatic_button
        self._update_diatonic_chromatic_button()

    @subject_slot_group('value')
    def _on_key_center_button_value(self, value, sender):
        if self.is_enabled() and (value or not sender.is_momentary()):
            index = list(self._key_center_buttons).index(sender)
            self.key_center = KEY_CENTERS[index]
            self._update_key_center_buttons()
            self._update_data_sources()
            self.notify_scales_changed()

    @subject_slot('value')
    def _on_absolute_relative_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._absolute_relative_button.is_momentary():
                self.is_absolute = not self.is_absolute
                self._update_absolute_relative_button()
                self._update_data_sources()
                self.notify_scales_changed()

    @subject_slot('value')
    def _on_diatonic_chromatic_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._diatonic_chromatic_button.is_momentary():
                self.is_diatonic = not self.is_diatonic
                self._update_diatonic_chromatic_button()
                self._update_data_sources()
                self.notify_scales_changed()

    @subject_slot('selected_item')
    def _on_selected_modus(self):
        self._update_data_sources()
        self.notify_scales_changed()

    def update(self):
        super(InstrumentScalesComponent, self).update()
        if self.is_enabled():
            self._update_key_center_buttons()
            self._update_absolute_relative_button()
            self._update_diatonic_chromatic_button()

    def _update_key_center_buttons(self):
        if self.is_enabled():
            for index, button in enumerate(self._key_center_buttons):
                if button:
                    button.set_on_off_values('Scales.Selected', 'Scales.Unselected')
                    button.set_light(self.key_center == KEY_CENTERS[index])

    def _update_absolute_relative_button(self):
        if self.is_enabled() and self._absolute_relative_button != None:
            self._absolute_relative_button.set_on_off_values('Scales.FixedOn', 'Scales.FixedOff')
            self._absolute_relative_button.set_light(self.is_absolute)

    def _update_diatonic_chromatic_button(self):
        if self.is_enabled() and self._diatonic_chromatic_button != None:
            self._diatonic_chromatic_button.set_on_off_values('Scales.Diatonic', 'Scales.Chromatic')
            self._diatonic_chromatic_button.set_light(self.is_diatonic)

    def _update_data_sources(self):
        key_index = list(KEY_CENTERS).index(self.key_center)
        key_sources = self._line_sources[0][:6] + self._line_sources[1][:6]
        key_names = [ scale.name for scale in self.available_scales ]
        for idx, (source, orig) in enumerate(zip(key_sources, key_names)):
            source.set_display_string('   ' + consts.CHAR_SELECT + orig if idx == key_index else '    ' + orig)

        self._line_sources[0][6].set_display_string('Fixed: Y' if self.is_absolute else 'Fixed: N')
        self._line_sources[1][6].set_display_string('In Key' if self.is_diatonic else 'Chromatc')
        self._info_sources[1].set_display_string(str(self._modus_list.scrollable_list.selected_item))


class InstrumentComponent(CompoundComponent, Slideable, Messenger):
    """
    Class that sets up the button matrix as a piano, using different
    selectable layouts for the notes.
    """
    touch_strip_toggle = ToggleButtonControl()
    midi_channels = range(5, 13)

    def __init__(self, *a, **k):
        super(InstrumentComponent, self).__init__(*a, **k)
        self._scales = self.register_component(InstrumentScalesComponent())
        self._matrix = None
        self._delete_button = None
        self._first_note = self.page_length * 3 + self.page_offset
        self._last_page_length = self.page_length
        self._delete_button = None
        self._last_page_offset = self.page_offset
        self._touch_strip = None
        self._touch_strip_indication = None
        self._detail_clip = None
        self._has_notes = [False] * 128
        self._has_notes_pattern = self._get_pattern(0)
        self._takeover_pads = False
        self._aftertouch_control = None
        self._scales_menu = self.register_component(EnablingModesComponent(component=self._scales, toggle_value='DefaultButton.On'))
        self._slider, self._touch_slider = self.register_components(SlideComponent(self), SlideableTouchStripComponent(self))
        self._on_scales_changed.subject = self._scales
        self._on_scales_mode_changed.subject = self._scales._presets
        self._update_pattern()

    def set_detail_clip(self, clip):
        if clip != self._detail_clip:
            self._detail_clip = clip
            self._on_clip_notes_changed.subject = clip
            self._on_loop_start_changed.subject = clip
            self._on_loop_end_changed.subject = clip
            self._on_clip_notes_changed()

    @subject_slot('notes')
    def _on_clip_notes_changed(self):
        if self._detail_clip:
            self._has_notes = [False] * 128
            loop_start = self._detail_clip.loop_start
            loop_length = self._detail_clip.loop_end - loop_start
            notes = self._detail_clip.get_notes(loop_start, 0, loop_length, 128)
            for note in notes:
                self._has_notes[note[0]] = True

        self.notify_contents()

    @subject_slot('loop_start')
    def _on_loop_start_changed(self):
        self._on_loop_selection_changed()

    @subject_slot('loop_end')
    def _on_loop_end_changed(self):
        self._on_loop_selection_changed()

    def _on_loop_selection_changed(self):
        self._on_clip_notes_changed()

    def contents(self, index):
        if self._detail_clip:
            note = self._has_notes_pattern[index].index
            return self._has_notes[note] if note is not None else False
        return False

    @property
    def page_length(self):
        return len(self._scales.notes) if self._scales.is_diatonic else 12

    @property
    def position_count(self):
        if not self._scales.is_diatonic:
            return 139
        else:
            offset = self.page_offset
            octaves = 11 if self._scales.notes[0] < 8 else 10
            return offset + len(self._scales.notes) * octaves

    def _first_scale_note_offset(self):
        if not self._scales.is_diatonic:
            return self._scales.notes[0]
        elif self._scales.notes[0] == 0:
            return 0
        else:
            return len(self._scales.notes) - index_if(lambda n: n >= 12, self._scales.notes)

    @property
    def page_offset(self):
        return 0 if self._scales.is_absolute else self._first_scale_note_offset()

    def _get_position(self):
        return self._first_note

    def _set_position(self, note):
        self._first_note = note
        self._update_pattern()
        self._update_matrix()
        self.notify_position()

    position = property(_get_position, _set_position)

    @property
    def scales(self):
        return self._scales

    @property
    def scales_menu(self):
        return self._scales_menu

    @property
    def pattern(self):
        return self._pattern

    @subject_slot('value')
    def _on_matrix_value(self, value, x, y, is_momentary):
        if self._delete_button and self._delete_button.is_pressed():
            if value:
                max_y = self._matrix.width() - 1
                pitch = self._get_pattern().note(x, max_y - y).index
                if pitch and self._detail_clip:
                    self._matrix.get_button(x, y).turn_on()
                    self._do_delete_pitch(pitch)
            else:
                self._matrix.get_button(x, y).turn_off()

    def _do_delete_pitch(self, pitch):
        clip = self._detail_clip
        if clip:
            note_name = pitch_index_to_string(pitch)
            loop_length = clip.loop_end - clip.loop_start
            clip.remove_notes(clip.loop_start, pitch, loop_length, 1)
            self.show_notification(consts.MessageBoxText.DELETE_NOTES % note_name)

    @subject_slot('value')
    def _on_delete_value(self, value):
        self._set_control_pads_from_script(bool(value))

    def set_matrix(self, matrix):
        self._matrix = matrix
        self._on_matrix_value.subject = matrix
        if matrix:
            matrix.reset()
        self._update_matrix()

    @touch_strip_toggle.toggled
    def touch_strip_toggle(self, toggled, button):
        self._update_touch_strip()
        self._update_touch_strip_indication()
        self.show_notification(consts.MessageBoxText.TOUCHSTRIP_MODWHEEL_MODE if toggled else consts.MessageBoxText.TOUCHSTRIP_PITCHBEND_MODE)

    def set_touch_strip(self, control):
        self._touch_strip = control
        self._update_touch_strip()

    def _update_touch_strip(self):
        if self._touch_strip:
            self._touch_strip.behaviour = MODWHEEL_BEHAVIOUR if self.touch_strip_toggle.is_toggled else DEFAULT_BEHAVIOUR

    def set_touch_strip_indication(self, control):
        self._touch_strip_indication = control
        self._update_touch_strip_indication()

    def _update_touch_strip_indication(self):
        if self._touch_strip_indication:
            self._touch_strip_indication.set_mode(TouchStripModes.CUSTOM_FREE)
            self._touch_strip_indication.send_state([ (TouchStripElement.STATE_FULL if self.touch_strip_toggle.is_toggled else TouchStripElement.STATE_HALF) for _ in xrange(24) ])

    def set_note_strip(self, strip):
        self._touch_slider.set_scroll_strip(strip)

    def set_octave_strip(self, strip):
        self._touch_slider.set_page_strip(strip)

    def set_scales_toggle_button(self, button):
        raise button is None or button.is_momentary() or AssertionError
        self._scales_menu.set_toggle_button(button)

    def set_octave_up_button(self, button):
        self._slider.set_scroll_page_up_button(button)

    def set_octave_down_button(self, button):
        self._slider.set_scroll_page_down_button(button)

    def set_scale_up_button(self, button):
        self._slider.set_scroll_up_button(button)

    def set_scale_down_button(self, button):
        self._slider.set_scroll_down_button(button)

    def set_aftertouch_control(self, control):
        self._aftertouch_control = control
        self._update_aftertouch()

    def set_delete_button(self, button):
        self._delete_button = button
        self._on_delete_value.subject = button
        self._set_control_pads_from_script(button and button.is_pressed())

    def _align_first_note(self):
        self._first_note = self.page_offset + (self._first_note - self._last_page_offset) * float(self.page_length) / float(self._last_page_length)
        if self._first_note >= self.position_count:
            self._first_note -= self.page_length
        self._last_page_length = self.page_length
        self._last_page_offset = self.page_offset

    @subject_slot('scales_changed')
    def _on_scales_changed(self):
        self._update_scale()

    @subject_slot('scale_mode')
    def _on_scales_mode_changed(self):
        self._update_scale()

    def _update_scale(self):
        self._align_first_note()
        self._update_pattern()
        self._update_matrix()
        self.notify_position_count()
        self.notify_position()
        self.notify_contents()

    def update(self):
        super(InstrumentComponent, self).update()
        if self.is_enabled():
            self._update_matrix()
            self._update_aftertouch()
            self._update_touch_strip()
            self._update_touch_strip_indication()

    def _update_pattern(self):
        self._pattern = self._get_pattern()
        self._has_notes_pattern = self._get_pattern(0)

    def _update_matrix(self):
        self._setup_instrument_mode()

    def _setup_instrument_mode(self):
        if self.is_enabled() and self._matrix:
            self._matrix.reset()
            pattern = self._pattern
            max_j = self._matrix.width() - 1
            for button, (i, j) in ifilter(first, self._matrix.iterbuttons()):
                profile = 'default' if self._takeover_pads else 'instrument'
                button.sensitivity_profile = profile
                note_info = pattern.note(i, max_j - j)
                if note_info.index != None:
                    button.set_on_off_values('Instrument.NoteAction', 'Instrument.' + note_info.color)
                    button.turn_off()
                    button.set_enabled(self._takeover_pads)
                    button.set_channel(note_info.channel)
                    button.set_identifier(note_info.index)
                else:
                    button.set_channel(NON_FEEDBACK_CHANNEL)
                    button.set_light('Instrument.' + note_info.color)
                    button.set_enabled(True)

    def _get_pattern(self, first_note = None):
        if first_note is None:
            first_note = int(round(self._first_note))
        interval = self._scales._presets.interval
        notes = self._scales.notes
        octave = first_note / self.page_length
        offset = first_note % self.page_length - self._first_scale_note_offset()
        if interval == None:
            interval = 8
        elif not self._scales.is_diatonic:
            interval = [0,
             2,
             4,
             5,
             7,
             9,
             10,
             11][interval]
        if self._scales._presets.is_horizontal:
            steps = [1, interval]
            origin = [offset, 0]
        else:
            steps = [interval, 1]
            origin = [0, offset]
        return MelodicPattern(steps=steps, scale=notes, origin=origin, base_note=octave * 12, chromatic_mode=not self._scales.is_diatonic)

    def _update_aftertouch(self):
        if self.is_enabled() and self._aftertouch_control != None:
            self._aftertouch_control.send_value(Sysex.MONO_AFTERTOUCH)

    def _set_control_pads_from_script(self, takeover_pads):
        """
        If takeover_pads is True, the matrix buttons will be controlled from
        the script. Otherwise they send midi notes to the track.
        """
        if takeover_pads != self._takeover_pads:
            self._takeover_pads = takeover_pads
            self._update_matrix()