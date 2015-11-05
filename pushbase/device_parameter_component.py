#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/pushbase/device_parameter_component.py
from __future__ import absolute_import
from itertools import chain, repeat
import Live
from ableton.v2.base import listens_group, listens
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.elements import DisplayDataSource
from . import consts
from .parameter_provider import ParameterProvider
AutomationState = Live.DeviceParameter.AutomationState

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


def update_encoder_sensitivity(encoder, parameter_info):
    if hasattr(encoder, 'set_sensitivities'):
        encoder.set_sensitivities(parameter_info.default_encoder_sensitivity, parameter_info.fine_grain_encoder_sensitivity)
    else:
        encoder.mapping_sensitivity = parameter_info.default_encoder_sensitivity


class DeviceParameterComponentBase(Component):

    def __init__(self, parameter_provider = None, *a, **k):
        super(DeviceParameterComponentBase, self).__init__(*a, **k)
        self._parameter_controls = []
        self.parameter_provider = parameter_provider

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

    @property
    def parameters(self):
        return map(lambda p: p and p.parameter, self._parameter_provider.parameters)

    @property
    def parameter_names(self):
        return map(lambda p: p and p.name or '', self.parameters)

    def _update_parameters(self):
        if self.is_enabled():
            self._connect_parameters()

    def _release_parameters(self):
        for encoder in self._parameter_controls or []:
            encoder.release_parameter()

    def _connect_parameters(self):
        for info, encoder in zip(self._parameter_provider.parameters, self._parameter_controls):
            if encoder:
                encoder.connect_to(info.parameter)
                update_encoder_sensitivity(encoder, info)

    @listens('parameters')
    def _on_parameters_changed(self):
        self._update_parameters()

    def update(self):
        super(DeviceParameterComponentBase, self).update()
        self._update_parameters()


class DeviceParameterComponent(DeviceParameterComponentBase):
    """
    Maps the display and encoders to the parameters provided by a
    ParameterProvider.
    """

    def __init__(self, *a, **k):
        self._parameter_name_data_sources = map(DisplayDataSource, ('', '', '', '', '', '', '', ''))
        self._parameter_value_data_sources = map(DisplayDataSource, ('', '', '', '', '', '', '', ''))
        self._parameter_graphic_data_sources = map(DisplayDataSource, ('', '', '', '', '', '', '', ''))
        super(DeviceParameterComponent, self).__init__(*a, **k)

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

    def _update_parameters(self):
        super(DeviceParameterComponent, self)._update_parameters()
        if self.is_enabled():
            parameters = self.parameters
            self._on_parameter_value_changed.replace_subjects(parameters)
            self._on_parameter_automation_state_changed.replace_subjects(parameters)
            self._update_parameter_names()
            self._update_parameter_values()

    @listens_group('value')
    def _on_parameter_value_changed(self, parameter):
        self._update_parameter_values()

    @listens_group('automation_state')
    def _on_parameter_automation_state_changed(self, parameter):
        self._update_parameter_names()
        self._update_parameter_values()

    def _update_parameter_names(self):
        if self.is_enabled():
            params = zip(chain(self.parameter_provider.parameters, repeat(None)), self._parameter_name_data_sources)
            for info, name_data_source in params:
                if info:
                    parameter = info.parameter
                    name = info and info.name or ''
                    name = parameter and parameter.automation_state != AutomationState.none and consts.CHAR_FULL_BLOCK + name
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