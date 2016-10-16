#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/automation.py
from __future__ import absolute_import, print_function
from itertools import ifilter
from ableton.v2.base import liveobj_valid, listenable_property
from pushbase.automation_component import AutomationComponent as AutomationComponentBase
from pushbase.internal_parameter import InternalParameterBase
from pushbase.parameter_provider import ParameterInfo

class StepAutomationParameter(InternalParameterBase):

    def __init__(self, parameter = None, *a, **k):
        raise liveobj_valid(parameter) or AssertionError
        super(StepAutomationParameter, self).__init__(name=parameter.name, *a, **k)
        self._parameter = parameter
        self._value = self._parameter.value

    @listenable_property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def max(self):
        return self._parameter.max

    @property
    def min(self):
        return self._parameter.min

    @property
    def display_value(self):
        return self._parameter.str_for_value(self.value)

    @property
    def canonical_parent(self):
        return self._parameter.canonical_parent

    @property
    def original_parameter(self):
        return self._parameter

    @property
    def is_quantized(self):
        return self._parameter.is_quantized

    @property
    def value_items(self):
        return self._parameter.value_items

    @property
    def automation_state(self):
        return self._parameter.automation_state


def make_automation_parameter(parameter_info):
    wrapped_parameter = None
    if parameter_info and liveobj_valid(parameter_info.parameter):
        parameter = parameter_info.parameter
        wrapped_parameter = ParameterInfo(parameter=StepAutomationParameter(parameter=parameter), name=parameter_info.name, default_encoder_sensitivity=parameter_info.default_encoder_sensitivity, fine_grain_encoder_sensitivity=parameter_info.fine_grain_encoder_sensitivity)
    return wrapped_parameter


class AutomationComponent(AutomationComponentBase):
    ENCODER_SENSITIVITY_FACTOR = 0.5
    __events__ = ('parameters',)

    def __init__(self, *a, **k):
        self._parameter_infos = []
        super(AutomationComponent, self).__init__(*a, **k)
        self._drum_pad_selected = False

    @property
    def deviceType(self):
        device_type = 'default'
        if hasattr(self.parameter_provider, 'device'):
            device = self.parameter_provider.device()
            device_type = device.class_name if liveobj_valid(device) else device_type
        return device_type

    @property
    def parameters(self):
        return map(lambda info: (info.parameter if info else None), self._parameter_infos)

    @property
    def parameter_infos(self):
        return self._parameter_infos

    def set_drum_pad_selected(self, value):
        if self._drum_pad_selected != value:
            self._drum_pad_selected = value
            self.notify_can_automate_parameters()

    @listenable_property
    def can_automate_parameters(self):
        return self._can_automate_parameters() and not self._drum_pad_selected

    def update(self):
        super(AutomationComponent, self).update()
        if self.is_enabled():
            self._rebuild_parameter_list()
            self._update_parameter_values()

    def _update_parameters(self):
        self._rebuild_parameter_list()
        super(AutomationComponent, self)._update_parameters()

    def _rebuild_parameter_list(self):
        if self.is_enabled():
            self._parameter_infos = map(make_automation_parameter, self._parameter_infos_to_use())
        else:
            self._parameter_infos = []

    def _update_parameter_values(self):
        for info in ifilter(lambda p: p is not None, self._parameter_infos):
            if len(self._selected_time) > 0:
                wrapped_parameter = info.parameter
                wrapped_parameter.value = self.parameter_to_value(wrapped_parameter.original_parameter)

        self.notify_parameters()

    def _parameter_for_index(self, parameters, index):
        if parameters[index]:
            return parameters[index].original_parameter