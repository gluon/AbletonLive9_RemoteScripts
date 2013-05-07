#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/DisplayingDeviceComponent.py
from itertools import chain
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.DeviceComponent import DeviceComponent
from _Framework.DisplayDataSource import DisplayDataSource
import consts
DISCRETE_PARAMETERS_DICT = {'GlueCompressor': ('Ratio', 'Attack', 'Release', 'Peak Clip In')}

def is_parameter_quantized(parameter, parent_device):
    is_quantized = False
    if parameter != None:
        device_class = parent_device.class_name
        is_quantized = parameter.is_quantized or device_class in DISCRETE_PARAMETERS_DICT and parameter.name in DISCRETE_PARAMETERS_DICT[device_class]
    return is_quantized


def graphic_bar_for_parameter(parameter):
    if parameter.min == -1 * parameter.max:
        return consts.GRAPH_PAN
    elif parameter.is_quantized:
        return consts.GRAPH_SIN
    return consts.GRAPH_VOL


def convert_parameter_value_to_graphic(param):
    if param != None:
        param_range = param.max - param.min
        param_bar = graphic_bar_for_parameter(param)
        graph_range = len(param_bar) - 1
        value = int((param.value - param.min) / param_range * graph_range)
        graphic_display_string = param_bar[value]
    else:
        graphic_display_string = ' '
    return graphic_display_string


class DisplayingDeviceComponent(DeviceComponent):
    """
    Special device class that displays parameter values
    """

    def __init__(self, *a, **k):
        super(DisplayingDeviceComponent, self).__init__(*a, **k)
        self._parameter_name_data_sources = [ DisplayDataSource(' ') for _ in xrange(8) ]
        self._parameter_value_data_sources = [ DisplayDataSource(' ') for _ in xrange(8) ]
        self._parameter_graphic_data_sources = [ DisplayDataSource(' ') for _ in xrange(8) ]
        self._blank_data_sources = [ DisplayDataSource(' ') for _ in xrange(8) ]
        self._mapped_parameters = []
        self._alternating_display = None
        self._encoder_touch_buttons = []

    def set_device(self, device):
        super(DisplayingDeviceComponent, self).set_device(device)
        if self._device == None:
            for source in chain(self._parameter_name_data_sources, self._parameter_value_data_sources, self._parameter_graphic_data_sources):
                source.set_display_string(' ')

    def set_encoder_touch_buttons(self, encoder_touch_buttons):
        if not encoder_touch_buttons:
            encoder_touch_buttons = []
            self._encoder_touch_buttons = self._encoder_touch_buttons != encoder_touch_buttons and encoder_touch_buttons
        self._on_encoder_touch_value.subject = encoder_touch_buttons or None
        self._try_set_alternate_display()

    def set_alternating_display(self, display):
        if not display:
            display = None
            self._alternating_display = self._alternating_display != display and display
        self._try_set_alternate_display()

    def set_name_display_line(self, line):
        self._set_display_line(line, self._parameter_name_data_sources)

    def set_value_display_line(self, line):
        self._set_display_line(line, self._parameter_value_data_sources)

    def set_graphic_display_line(self, line):
        self._set_display_line(line, self._parameter_graphic_data_sources)

    def _set_display_line(self, line, sources):
        if line:
            line.set_num_segments(len(sources))
            for segment in xrange(len(sources)):
                line.segment(segment).set_data_source(sources[segment])

    def parameter_value_data_source(self, index):
        return self._parameter_value_data_sources[index]

    def parameter_name_data_source(self, index):
        return self._parameter_name_data_sources[index]

    def _is_banking_enabled(self):
        return True

    def _assign_parameters(self):
        super(DisplayingDeviceComponent, self)._assign_parameters()
        self._update_mapping_sensitivity()
        _, self._mapped_parameters = self._current_bank_details()
        parameters = map(self._mapped_parameter, xrange(len(self._parameter_name_data_sources)))
        self._on_parameter_value_changed.replace_subjects(parameters)
        self._update_parameter_values()
        for parameter, name_data_source in zip(parameters, self._parameter_name_data_sources):
            param_name = parameter.name if parameter else ' '
            name_data_source.set_display_string(param_name)

    def _on_device_name_changed(self):
        if self._device_name_data_source != None:
            if self.is_enabled() and self._device != None:
                self._device_name_data_source.set_display_string(self._device.name)
            else:
                self._device_name_data_source.set_display_string('No Device')

    @subject_slot_group('value')
    def _on_parameter_value_changed(self, parameter):
        self._update_parameter_values()

    def _update_parameter_values(self):
        if self.is_enabled():
            for index, data_source in enumerate(self._parameter_value_data_sources):
                parameter = self._mapped_parameter(index)
                data_source.set_display_string(' ' if parameter == None else unicode(parameter))

            for index, data_source in enumerate(self._parameter_graphic_data_sources):
                param = self._mapped_parameter(index)
                graph = convert_parameter_value_to_graphic(param)
                data_source.set_display_string(graph)

    def _update_mapping_sensitivity(self):
        device = self.device()
        if device != None:
            for control in self._parameter_controls:
                if control != None:
                    parameter = control.mapped_parameter()
                    is_quantized = is_parameter_quantized(parameter, device)
                    control.mapping_sensitivity = consts.QUANTIZED_MAPPING_SENSITIVITY if is_quantized else consts.CONTINUOUS_MAPPING_SENSITIVITY

    def _mapped_parameter(self, index):
        return self._mapped_parameters[index] if index < len(self._mapped_parameters) else None

    @subject_slot('value')
    def _on_encoder_touch_value(self, value, x, y, is_momentary):
        self._try_set_alternate_display()

    def _try_set_alternate_display(self):
        if self._alternating_display != None:
            for button in self._encoder_touch_buttons:
                if button and button.is_pressed():
                    self.set_graphic_display_line(self._alternating_display)
                    return
            else:
                self._set_display_line(self._alternating_display, self._blank_data_sources)