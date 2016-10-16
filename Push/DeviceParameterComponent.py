#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/DeviceParameterComponent.py
from itertools import chain, repeat, ifilter
import Live
AutomationState = Live.DeviceParameter.AutomationState
from _Framework.Util import first, second
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot_group, subject_slot, Subject
import consts

def graphic_bar_for_parameter(parameter):
    if parameter.min == -1 * parameter.max:
        return consts.GRAPH_PAN
    elif parameter.is_quantized:
        return consts.GRAPH_SIN
    return consts.GRAPH_VOL


def convert_parameter_value_to_graphic(param, param_to_value = lambda p: p.value):
    if param != None:
        param_range = param.max - param.min
        param_bar = graphic_bar_for_parameter(param)
        graph_range = len(param_bar) - 1
        value = int((param_to_value(param) - param.min) / param_range * graph_range)
        graphic_display_string = param_bar[value]
    else:
        graphic_display_string = ' '
    return graphic_display_string


DISCRETE_PARAMETERS_DICT = {'GlueCompressor': ('Ratio', 'Attack', 'Release', 'Peak Clip In')}

def is_parameter_quantized(parameter, parent_device):
    is_quantized = False
    if parameter != None:
        device_class = getattr(parent_device, 'class_name', None)
        is_quantized = parameter.is_quantized or device_class in DISCRETE_PARAMETERS_DICT and parameter.name in DISCRETE_PARAMETERS_DICT[device_class]
    return is_quantized


def parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    return consts.QUANTIZED_MAPPING_SENSITIVITY if is_quantized else consts.CONTINUOUS_MAPPING_SENSITIVITY


def fine_grain_parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    return consts.QUANTIZED_MAPPING_SENSITIVITY if is_quantized else consts.FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY


def _update_encoder_sensitivity(encoder, parameter):
    default = parameter_mapping_sensitivity(parameter)
    if hasattr(encoder, 'set_sensitivities'):
        encoder.set_sensitivities(default, fine_grain_parameter_mapping_sensitivity(parameter))
    else:
        encoder.mapping_sensitivity = default


class ParameterProvider(Subject):
    __subject_events__ = ('parameters',)

    @property
    def parameters(self):
        return []


class DeviceParameterComponent(ControlSurfaceComponent):
    """
    Maps the display and encoders to the parameters provided by a
    ParameterProvider.
    """

    def __init__(self, parameter_provider = None, *a, **k):
        super(DeviceParameterComponent, self).__init__(*a, **k)
        self._parameter_controls = []
        self._parameter_name_data_sources = map(DisplayDataSource, ('', '', '', '', '', '', '', ''))
        self._parameter_value_data_sources = map(DisplayDataSource, ('', '', '', '', '', '', '', ''))
        self._parameter_graphic_data_sources = map(DisplayDataSource, ('', '', '', '', '', '', '', ''))
        self.parameter_provider = parameter_provider

    @property
    def parameters(self):
        return map(second, self._parameter_provider.parameters)

    @property
    def parameter_names(self):
        return map(first, self._parameter_provider.parameters)

    def _get_parameter_provider(self):
        return self._parameter_provider

    def _set_parameter_provider(self, provider):
        self._parameter_provider = provider or ParameterProvider()
        self._on_parameters_changed.subject = self._parameter_provider
        self._update_parameters()

    parameter_provider = property(_get_parameter_provider, _set_parameter_provider)

    def set_parameter_controls(self, encoders):
        self._release_parameters()
        self._parameter_controls = encoders or []
        self._connect_parameters()

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

    def clear_display(self):
        for source in chain(self._parameter_name_data_sources, self._parameter_value_data_sources, self._parameter_graphic_data_sources):
            source.set_display_string('')

    def _release_parameters(self):
        for encoder in ifilter(None, self._parameter_controls or []):
            encoder.release_parameter()

    def _connect_parameters(self):
        for parameter, encoder in zip(self.parameters, self._parameter_controls):
            if encoder:
                encoder.connect_to(parameter)
                _update_encoder_sensitivity(encoder, parameter)

    def _update_parameters(self):
        if self.is_enabled():
            parameters = self.parameters
            self._on_parameter_value_changed.replace_subjects(parameters)
            self._on_parameter_automation_state_changed.replace_subjects(parameters)
            self._update_parameter_names()
            self._update_parameter_values()
            self._connect_parameters()

    @subject_slot('parameters')
    def _on_parameters_changed(self):
        self._update_parameters()

    @subject_slot_group('value')
    def _on_parameter_value_changed(self, parameter):
        self._update_parameter_values()

    @subject_slot_group('automation_state')
    def _on_parameter_automation_state_changed(self, parameter):
        self._update_parameter_names()
        self._update_parameter_values()

    def _update_parameter_names(self):
        if self.is_enabled():
            params = zip(chain(self.parameter_provider.parameters, repeat(('', None))), self._parameter_name_data_sources)
            for (name, parameter), name_data_source in params:
                if parameter and parameter.automation_state != AutomationState.none:
                    name = consts.CHAR_FULL_BLOCK + name
                name_data_source.set_display_string(name or '')

    def _update_parameter_values(self):
        if self.is_enabled():
            for parameter, data_source in map(None, self.parameters, self._parameter_value_data_sources):
                value_string = self.parameter_to_string(parameter)
                if parameter and parameter.automation_state == AutomationState.overridden:
                    value_string = '[%s]' % value_string
                if data_source:
                    data_source.set_display_string(value_string)

            for param, data_source in map(None, self.parameters, self._parameter_graphic_data_sources):
                graph = convert_parameter_value_to_graphic(param, self.parameter_to_value)
                if data_source:
                    data_source.set_display_string(graph)

    def parameter_to_string(self, parameter):
        return '' if parameter == None else unicode(parameter)

    def parameter_to_value(self, parameter):
        return parameter.value

    def update(self):
        super(DeviceParameterComponent, self).update()
        if self.is_enabled():
            self._update_parameters()