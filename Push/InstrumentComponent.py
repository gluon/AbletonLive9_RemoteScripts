#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/InstrumentComponent.py
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ModesComponent import DisplayingModesComponent, ModesComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.Util import recursive_map, forward_property
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ScrollComponent import ScrollComponent, Scrollable
from MelodicComponent import MelodicPattern, Modus
from MatrixMaps import NON_FEEDBACK_CHANNEL
from functools import partial
import consts
INSTRUMENT_PRESETS_DISPLAY = (('',) * 8, ('4th ^',
  '4th >',
  '3rd ^',
  '3rd >',
  'Sequent ^',
  'Sequent >',
  ' ',
  ' '))

class InstrumentPresetsComponent(DisplayingModesComponent):
    octave_index_offset = 0
    is_horizontal = True
    interval = 3

    def __init__(self, *a, **k):
        super(InstrumentPresetsComponent, self).__init__(*a, **k)
        self._unused_button_slots = self.register_slot_manager()
        self._unused_buttons = []
        self._line_names = recursive_map(DisplayDataSource, INSTRUMENT_PRESETS_DISPLAY)
        self.add_mode('scale_p4_vertical', partial(self._set_scale_mode, 0, True, 3), self._line_names[1][0])
        self.add_mode('scale_p4_horizontal', partial(self._set_scale_mode, 0, False, 3), self._line_names[1][1])
        self.add_mode('scale_m3_vertical', partial(self._set_scale_mode, 0, True, 2), self._line_names[1][2])
        self.add_mode('scale_m3_horizontal', partial(self._set_scale_mode, 0, False, 2), self._line_names[1][3])
        self.add_mode('scale_m6_vertical', partial(self._set_scale_mode, -2, True, None), self._line_names[1][4])
        self.add_mode('scale_m6_horizontal', partial(self._set_scale_mode, -2, False, None), self._line_names[1][5])

    def _update_data_sources(self, selected):
        if self.is_enabled():
            for name, (source, string) in self._mode_data_sources.iteritems():
                source.set_display_string(consts.CHAR_SELECT + string if name == selected else string)

    def _set_scale_mode(self, octave_index_offset, is_horizontal, interval):
        self.octave_index_offset = octave_index_offset
        self.is_horizontal = is_horizontal
        self.interval = interval

    def set_top_blank_line(self, display):
        if display:
            display.reset()

    def set_bottom_blank_line(self, display):
        if display:
            display.reset()

    def set_top_display_line(self, display):
        if display:
            self._set_display_line(display, 0)

    def set_bottom_display_line(self, display):
        if display:
            self._set_display_line(display, 1)

    def _set_display_line(self, display, line):
        if display:
            display.set_num_segments(8)
            for idx in xrange(8):
                display.segment(idx).set_data_source(self._line_names[line][idx])

    def set_bottom_buttons(self, buttons):
        self._on_bottom_buttons_value.subject = buttons
        if buttons:
            for button in filter(bool, buttons):
                button.reset()

    def set_top_buttons(self, buttons):
        if buttons:
            self._scales_preset_buttons = buttons[0:7]
            self._unused_top_buttons = buttons[6:8]
        else:
            self._scales_preset_buttons = None
            self._unused_top_buttons = None
        if self._scales_preset_buttons:
            self._set_scales_preset_buttons(self._scales_preset_buttons)
        else:
            self._set_scales_preset_buttons(tuple())
        if self._unused_top_buttons:
            self._set_unused_top_buttons(self._unused_top_buttons)
        else:
            self._set_unused_top_buttons([])

    def _set_unused_top_buttons(self, buttons):
        if not buttons:
            buttons = []
            self._unused_buttons = self._unused_buttons != buttons and buttons
            self._unused_button_slots.disconnect()
            for button in buttons:
                button.reset()
                self._unused_button_slots.register_slot(button, self._on_unused_top_button_value, 'value')

    def _set_scales_preset_buttons(self, buttons):
        modes = ('scale_p4_vertical', 'scale_p4_horizontal', 'scale_m3_vertical', 'scale_m3_horizontal', 'scale_m6_vertical', 'scale_m6_horizontal')
        self._set_mode_buttons(buttons, modes)

    def _set_mode_buttons(self, buttons, modes):
        if buttons:
            for button, mode in zip(buttons, modes):
                button.set_on_off_values('Scales.Selected', 'Scales.Unselected')
                self.set_mode_button(mode, button)

        else:
            for mode in modes:
                self.set_mode_button(mode, None)

    @subject_slot('value')
    def _on_unused_top_button_value(self, value):
        pass

    @subject_slot('value')
    def _on_bottom_buttons_value(self, value, x, y, is_momentary):
        pass


CIRCLE_OF_FIFTHS = [ 7 * k % 12 for k in range(12) ]
KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]
SCALES_DISPLAY_STRINGS = (('',) * 8, ('',) * 8)

class InstrumentScalesComponent(CompoundComponent, Scrollable):
    __subject_events__ = ('scales_changed',)
    release_info_display_with_encoders = True
    is_absolute = False
    is_diatonic = True
    key_center = 0

    def __init__(self, *a, **k):
        super(InstrumentScalesComponent, self).__init__(*a, **k)
        self._key_center_slots = self.register_slot_manager()
        self._key_center_buttons = []
        self._encoder_touch_button_slots = self.register_slot_manager()
        self._encoder_touch_buttons = []
        self._top_key_center_buttons = None
        self._bottom_key_center_buttons = None
        self._absolute_relative_button = None
        self._diatonic_chromatic_button = None
        table = consts.MUSICAL_MODES
        self._modus_list = [ Modus(table[k], table[k + 1]) for k in xrange(0, len(consts.MUSICAL_MODES), 2) ]
        self._selected_modus = 0
        self._line_sources = recursive_map(DisplayDataSource, SCALES_DISPLAY_STRINGS)
        self._presets = self.register_component(InstrumentPresetsComponent())
        self._presets.set_enabled(False)
        self._presets_modes = self.register_component(ModesComponent())
        self._presets_modes.add_mode('disabled', None)
        self._presets_modes.add_mode('enabled', self._presets, 'Scales.PresetsEnabled')
        self._presets_modes.selected_mode = 'disabled'
        self._presets_modes.momentary_toggle = True
        self._presets.selected_mode = 'scale_p4_vertical'
        self._scales_info = self.register_component(ScalesInfoComponent())
        self._scales_info.set_enabled(True)
        self._modus_scroll = self.register_component(ScrollComponent())
        self._modus_scroll.scrollable = self
        self._update_data_sources()

    presets_layer = forward_property('_presets')('layer')
    scales_info_layer = forward_property('_scales_info')('layer')

    @property
    def modus(self):
        return self._modus_list[self._selected_modus]

    @property
    def available_scales(self):
        return self.modus.scales(KEY_CENTERS)

    @property
    def notes(self):
        return self.modus.scale(self.key_center).notes

    def set_top_display_line(self, display):
        if display:
            self._set_display_line(display, 0)

    def set_bottom_display_line(self, display):
        if display:
            self._set_display_line(display, 1)

    def _set_display_line(self, display, line):
        if display:
            display.set_num_segments(8)
            for idx in xrange(8):
                display.segment(idx).set_data_source(self._line_sources[line][idx])

    def set_presets_toggle_button(self, button):
        raise button is None or button.is_momentary() or AssertionError
        self._presets_modes.set_toggle_button(button)

    def set_top_buttons(self, buttons):
        if buttons:
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
        if button:
            button.set_on_off_values('List.ScrollerOn', 'List.ScrollerOff')
        self._modus_scroll.set_scroll_down_button(button)

    def set_modus_up_button(self, button):
        if button:
            button.set_on_off_values('List.ScrollerOn', 'List.ScrollerOff')
        self._modus_scroll.set_scroll_up_button(button)

    def set_key_center_buttons(self, buttons):
        if not (not buttons or len(buttons) == 12):
            raise AssertionError
            buttons = buttons or []
            self._key_center_buttons = self._key_center_buttons != buttons and buttons
            self._key_center_slots.disconnect()
            for button in buttons:
                self._key_center_slots.register_slot(button, self._on_key_center_button_value, 'value', extra_kws=dict(identify_sender=True))

            self._update_key_center_buttons()

    def set_absolute_relative_button(self, absolute_relative_button):
        if absolute_relative_button != self._absolute_relative_button:
            self._absolute_relative_button = absolute_relative_button
            self._on_absolute_relative_value.subject = absolute_relative_button
            self._update_absolute_relative_button()

    def set_diatonic_chromatic_button(self, diatonic_chromatic_button):
        if diatonic_chromatic_button != self._diatonic_chromatic_button:
            self._diatonic_chromatic_button = diatonic_chromatic_button
            self._on_diatonic_chromatic_value.subject = diatonic_chromatic_button
            self._update_diatonic_chromatic_button()

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

    def can_scroll_up(self):
        return self._selected_modus > 0

    def can_scroll_down(self):
        return self._selected_modus < len(self._modus_list) - 1

    def scroll_up(self):
        self._set_selected_modus(self._selected_modus - 1)

    def scroll_down(self):
        self._set_selected_modus(self._selected_modus + 1)

    def _set_selected_modus(self, n):
        if n > -1 and n < len(self._modus_list):
            self._selected_modus = n
            self._update_data_sources()
            self.notify_scales_changed()

    def update(self):
        if self.is_enabled():
            self._update_key_center_buttons()
            self._update_absolute_relative_button()
            self._update_diatonic_chromatic_button()
            self._update_scales_info()

    def _update_key_center_buttons(self):
        if self.is_enabled():
            for index, button in enumerate(self._key_center_buttons):
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
        key_sources = self._line_sources[0][1:7] + self._line_sources[1][1:7]
        key_names = [ scale.name for scale in self.available_scales ]
        for idx, (source, orig) in enumerate(zip(key_sources, key_names)):
            source.set_display_string('   ' + consts.CHAR_SELECT + orig if idx == key_index else '    ' + orig)

        self._line_sources[0][7].set_display_string('Fixed: Y' if self.is_absolute else 'Fixed: N')
        self._line_sources[1][7].set_display_string('In Key' if self.is_diatonic else 'Chromatic')
        self._line_sources[0][0].set_display_string(consts.CHAR_SELECT + self._modus_list[self._selected_modus].name)
        if self._selected_modus + 1 < len(self._modus_list):
            self._line_sources[1][0].set_display_string(' ' + self._modus_list[self._selected_modus + 1].name)
        else:
            self._line_sources[1][0].set_display_string(' ')
        self._scales_info.set_info_display_string('Scale Selection:')
        self._scales_info.set_info_display_string(self._modus_list[self._selected_modus].name, 1)

    def set_encoder_touch_buttons(self, encoder_touch_buttons):
        self._encoder_touch_buttons = encoder_touch_buttons or []
        self._on_encoder_touch_buttons_value.replace_subjects(self._encoder_touch_buttons)
        self._update_scales_info()

    @subject_slot_group('value')
    def _on_encoder_touch_buttons_value(self, value, sender):
        self._update_scales_info()

    def _update_scales_info(self):
        if self.is_enabled():
            self._scales_info.set_enabled(not self.release_info_display_with_encoders or not any(map(lambda button: button.is_pressed(), self._encoder_touch_buttons)))


class ScalesInfoComponent(ControlSurfaceComponent):
    """
    Class that masks/unmasks two display lines at a time.
    """
    num_segments = 4

    def __init__(self, *a, **k):
        super(ScalesInfoComponent, self).__init__(*a, **k)
        self._blank_data_sources = (DisplayDataSource(),)
        self._selection_data_sources = [ DisplayDataSource() for _ in xrange(self.num_segments) ]

    def set_info_line(self, display):
        if display:
            display.set_data_sources(self._selection_data_sources)

    def set_blank_line(self, display):
        if display:
            display.reset()

    def set_info_display_string(self, string, segment = 0):
        if segment < self.num_segments:
            self._selection_data_sources[segment].set_display_string(string)

    def update(self):
        pass


class InstrumentComponent(CompoundComponent):
    """
    Class that sets up the button matrix as a piano, using different
    selectable layouts for the notes.
    """
    midi_channels = range(5, 13)

    def __init__(self, *a, **k):
        super(InstrumentComponent, self).__init__(*a, **k)
        self._matrix = None
        self._octave_index = 3
        self._scales = self.register_component(InstrumentScalesComponent())
        self._scales.set_enabled(False)
        self._scales_modes = self.register_component(ModesComponent())
        self._scales_modes.add_mode('disabled', None)
        self._scales_modes.add_mode('enabled', self._scales, 'DefaultButton.On')
        self._scales_modes.selected_mode = 'disabled'
        self._paginator = self.register_component(ScrollComponent())
        self._paginator.can_scroll_up = self._can_scroll_octave_up
        self._paginator.can_scroll_down = self._can_scroll_octave_down
        self._paginator.scroll_up = self._scroll_octave_up
        self._paginator.scroll_down = self._scroll_octave_down
        self.register_slot(self._scales, self._update_matrix, 'scales_changed')
        self.register_slot(self._scales._presets, lambda _: self._update_matrix(), 'selected_mode')

    scales_layer = forward_property('_scales')('layer')

    @subject_slot('value')
    def _on_matrix_value(self, *a):
        pass

    def set_matrix(self, matrix):
        self._matrix = matrix
        self._on_matrix_value.subject = matrix
        if matrix:
            matrix.reset()
        self._update_matrix()

    def set_touch_strip(self, control):
        if control:
            control.reset()

    def set_scales_toggle_button(self, button):
        raise button is None or button.is_momentary() or AssertionError
        self._scales_modes.set_toggle_button(button)

    def set_presets_toggle_button(self, button):
        self._scales.set_presets_toggle_button(button)

    def set_octave_up_button(self, button):
        self._paginator.set_scroll_up_button(button)

    def set_octave_down_button(self, button):
        self._paginator.set_scroll_down_button(button)

    def _can_scroll_octave_up(self):
        return self._octave_index + self._scales._presets.octave_index_offset < 10

    def _can_scroll_octave_down(self):
        return self._octave_index + self._scales._presets.octave_index_offset > -2

    def _scroll_octave_up(self):
        if self._can_scroll_octave_up():
            self._octave_index += 1
            self._update_matrix()

    def _scroll_octave_down(self):
        if self._can_scroll_octave_down():
            self._octave_index -= 1
            self._update_matrix()

    def update(self):
        if self.is_enabled():
            self._update_matrix()

    def _update_matrix(self):
        self._setup_instrument_mode(self._scales._presets.interval)

    def _setup_instrument_mode(self, interval):
        if self.is_enabled() and self._matrix:
            for button, _ in self._matrix.iterbuttons():
                if button:
                    button.use_default_message()
                    button.force_next_send()

            pattern = self._get_pattern(interval)
            max_j = self._matrix.width() - 1
            for button, (i, j) in self._matrix.iterbuttons():
                if button:
                    note_info = pattern.note(i, max_j - j)
                    if note_info.index != None:
                        button.set_on_off_values(note_info.color, 'Instrument.NoteOff')
                        button.turn_on()
                        button.set_enabled(False)
                        button.set_channel(note_info.channel)
                        button.set_identifier(note_info.index)
                    else:
                        button.set_channel(NON_FEEDBACK_CHANNEL)
                        button.set_light(note_info.color)
                        button.set_enabled(True)

    def _get_pattern(self, interval):
        notes = self._scales.notes
        if not self._scales.is_absolute:
            origin = 0
        elif self._scales.is_diatonic:
            origin = 0
            for k in xrange(len(notes)):
                if notes[k] >= 12:
                    origin = k - len(notes)
                    break

        else:
            origin = -notes[0]
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
            origin = [origin, 0]
        else:
            steps = [interval, 1]
            origin = [0, origin]
        return MelodicPattern(steps=steps, scale=notes, origin=origin, base_note=self._octave_index * 12, chromatic_mode=not self._scales.is_diatonic)