#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/scales_component.py
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.base import forward_property, listens, listens_group, recursive_map
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.mode import ModesComponent
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.elements import DisplayDataSource, adjust_string_crop
from pushbase import consts
from pushbase.melodic_pattern import ROOT_NOTES, SCALES
from pushbase.scrollable_list import ListComponent

class DisplayingModesComponent(ModesComponent):
    """
    A modes component that displays the selected option.
    """

    def __init__(self, *a, **k):
        super(DisplayingModesComponent, self).__init__(*a, **k)
        self._mode_data_sources = {}

    def add_mode(self, name, mode_or_component, data_source):
        """
        Adds a mode.  The mode will be displayed in the given data
        source. The display name of the data source is its value when
        added.
        """
        super(DisplayingModesComponent, self).add_mode(name, mode_or_component)
        self._mode_data_sources[name] = (data_source, data_source.display_string())

    def update(self):
        super(DisplayingModesComponent, self).update()
        self._update_data_sources(self.selected_mode)

    def _do_enter_mode(self, name):
        super(DisplayingModesComponent, self)._do_enter_mode(name)
        self._update_data_sources(name)

    def _update_data_sources(self, selected):
        if self.is_enabled():
            for name, (source, string) in self._mode_data_sources.iteritems():
                source.set_display_string('*' + string if name == selected else string)


class InstrumentPresetsComponent(DisplayingModesComponent):

    def __init__(self, note_layout = None, *a, **k):
        raise note_layout is not None or AssertionError
        super(InstrumentPresetsComponent, self).__init__(*a, **k)
        self._note_layout = note_layout
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
        if self._note_layout.is_horizontal != is_horizontal or self._note_layout.interval != interval:
            self._note_layout.is_horizontal = is_horizontal
            self._note_layout.interval = interval

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
                self.get_mode_button(mode).set_control_element(button)
                if button:
                    button.set_on_off_values('Scales.Selected', 'Scales.Unselected')

        else:
            for mode in modes:
                self.get_mode_button(mode).set_control_element(None)

        self.update()


class InstrumentScalesComponent(CompoundComponent):
    presets_toggle_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    def __init__(self, note_layout = None, *a, **k):
        raise note_layout is not None or AssertionError
        super(InstrumentScalesComponent, self).__init__(*a, **k)
        self._note_layout = note_layout
        self._key_center_buttons = []
        self._encoder_touch_button_slots = self.register_slot_manager()
        self._encoder_touch_buttons = []
        self._top_key_center_buttons = None
        self._bottom_key_center_buttons = None
        self._absolute_relative_button = None
        self._diatonic_chromatic_button = None
        self._info_sources = map(DisplayDataSource, ('Scale selection:', '', ''))
        self._line_sources = recursive_map(DisplayDataSource, (('', '', '', '', '', '', ''), ('', '', '', '', '', '', '')))
        self._scale_sources = map(partial(DisplayDataSource, adjust_string_fn=adjust_string_crop), ('', '', '', ''))
        self._presets = self.register_component(InstrumentPresetsComponent(self._note_layout, is_enabled=False))
        self._presets.selected_mode = 'scale_p4_vertical'
        self._scale_list = self.register_component(ListComponent(data_sources=self._scale_sources))
        self._scale_list.scrollable_list.fixed_offset = 1
        self._scale_list.scrollable_list.assign_items(SCALES)
        self._scale_list.scrollable_list.select_item_index_with_offset(list(SCALES).index(self._note_layout.scale), 1)
        self._on_selected_scale.subject = self._scale_list.scrollable_list
        self._update_data_sources()

    presets_layer = forward_property('_presets')('layer')

    @property
    def available_scales(self):
        return self._note_layout.scale.scale_for_notes(ROOT_NOTES)

    def set_scale_line1(self, display):
        self._set_scale_line(display, 0)

    def set_scale_line2(self, display):
        self._set_scale_line(display, 1)

    def set_scale_line3(self, display):
        self._set_scale_line(display, 2)

    def set_scale_line4(self, display):
        self._set_scale_line(display, 3)

    def _set_scale_line(self, display, index):
        if display:
            display.set_data_sources([self._scale_sources[index]])
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
            self.set_scale_up_button(buttons[0])
        else:
            self.set_absolute_relative_button(None)
            self._top_key_center_buttons = None
            self.set_scale_up_button(None)
        if self._top_key_center_buttons and self._bottom_key_center_buttons:
            self.set_key_center_buttons(self._top_key_center_buttons + self._bottom_key_center_buttons)
        else:
            self.set_key_center_buttons(tuple())

    def set_bottom_buttons(self, buttons):
        if buttons:
            buttons.reset()
            self.set_diatonic_chromatic_button(buttons[7])
            self._bottom_key_center_buttons = buttons[1:7]
            self.set_scale_down_button(buttons[0])
        else:
            self.set_diatonic_chromatic_button(None)
            self._bottom_key_center_buttons = None
            self.set_scale_down_button(None)
        if self._top_key_center_buttons and self._bottom_key_center_buttons:
            self.set_key_center_buttons(self._top_key_center_buttons + self._bottom_key_center_buttons)
        else:
            self.set_key_center_buttons([])

    def set_scale_down_button(self, button):
        self._scale_list.select_next_button.set_control_element(button)

    def set_scale_up_button(self, button):
        self._scale_list.select_prev_button.set_control_element(button)

    def set_encoder_controls(self, encoders):
        self._scale_list.encoders.set_control_element([encoders[0]] if encoders else [])

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

    @listens_group('value')
    def _on_key_center_button_value(self, value, sender):
        if self.is_enabled() and (value or not sender.is_momentary()):
            index = list(self._key_center_buttons).index(sender)
            self._note_layout.root_note = ROOT_NOTES[index]
            self._update_key_center_buttons()
            self._update_data_sources()

    @listens('value')
    def _on_absolute_relative_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._absolute_relative_button.is_momentary():
                self._note_layout.is_fixed = not self._note_layout.is_fixed
                self._update_absolute_relative_button()
                self._update_data_sources()

    @listens('value')
    def _on_diatonic_chromatic_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._diatonic_chromatic_button.is_momentary():
                self._note_layout.is_in_key = not self._note_layout.is_in_key
                self._update_diatonic_chromatic_button()
                self._update_data_sources()

    @listens('selected_item')
    def _on_selected_scale(self):
        self._note_layout.scale = self._scale_list.scrollable_list.selected_item.content
        self._update_data_sources()

    def update(self):
        super(InstrumentScalesComponent, self).update()
        if self.is_enabled():
            self._update_key_center_buttons()
            self._update_absolute_relative_button()
            self._update_diatonic_chromatic_button()
        else:
            self._presets.set_enabled(False)

    def _update_key_center_buttons(self):
        if self.is_enabled():
            for index, button in enumerate(self._key_center_buttons):
                if button:
                    button.set_on_off_values('Scales.Selected', 'Scales.Unselected')
                    button.set_light(self._note_layout.root_note == ROOT_NOTES[index])

    def _update_absolute_relative_button(self):
        if self.is_enabled() and self._absolute_relative_button != None:
            self._absolute_relative_button.set_on_off_values('Scales.FixedOn', 'Scales.FixedOff')
            self._absolute_relative_button.set_light(self._note_layout.is_fixed)

    def _update_diatonic_chromatic_button(self):
        if self.is_enabled() and self._diatonic_chromatic_button != None:
            self._diatonic_chromatic_button.set_on_off_values('Scales.Diatonic', 'Scales.Chromatic')
            self._diatonic_chromatic_button.set_light(self._note_layout.is_in_key)

    def _update_data_sources(self):
        key_index = list(ROOT_NOTES).index(self._note_layout.root_note)
        key_sources = self._line_sources[0][:6] + self._line_sources[1][:6]
        key_names = [ scale.name for scale in self.available_scales ]
        for idx, (source, orig) in enumerate(zip(key_sources, key_names)):
            source.set_display_string('   ' + consts.CHAR_SELECT + orig if idx == key_index else '    ' + orig)

        self._line_sources[0][6].set_display_string('Fixed: Y' if self._note_layout.is_fixed else 'Fixed: N')
        self._line_sources[1][6].set_display_string('In Key' if self._note_layout.is_in_key else 'Chromatc')
        self._info_sources[1].set_display_string(str(self._scale_list.scrollable_list.selected_item))