#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/automation_component.py
from __future__ import absolute_import, print_function
import Live
from ableton.v2.base import clamp, task, liveobj_valid
from ableton.v2.control_surface.control import EncoderControl, control_list
from .device_parameter_component import DeviceParameterComponent
from .setting import EnumerableSetting
AutomationState = Live.DeviceParameter.AutomationState

class AutomationComponent(DeviceParameterComponent):
    ENCODER_SENSITIVITY_FACTOR = 1.0
    _clip = None
    encoders = control_list(EncoderControl)

    @staticmethod
    def parameter_is_automateable(parameter):
        return liveobj_valid(parameter) and isinstance(parameter, Live.DeviceParameter.DeviceParameter)

    def __init__(self, *a, **k):
        super(AutomationComponent, self).__init__(*a, **k)
        self._selected_time = []
        self._parameter_floats = []
        self._update_parameter_values_task = self._tasks.add(task.run(self._update_parameter_values))
        self._update_parameter_values_task.kill()

    def _get_clip(self):
        return self._clip

    def _set_clip(self, value):
        self._clip = value
        self._update_parameter_values_task.restart()

    clip = property(_get_clip, _set_clip)

    def _get_selected_time(self):
        return self._selected_time

    def _set_selected_time(self, value):
        self._selected_time = value or []
        self._update_parameter_values()
        self._update_parameter_floats()

    selected_time = property(_get_selected_time, _set_selected_time)

    @property
    def parameters(self):
        return map(lambda info: (info.parameter if info else None), self._parameter_infos_to_use())

    @property
    def parameter_infos(self):
        return self._parameter_infos_to_use()

    def _parameter_infos_to_use(self):
        return map(lambda info: (info if self.parameter_is_automateable(info.parameter if info else None) else None), self._parameter_provider.parameters)

    @property
    def can_automate_parameters(self):
        return self._can_automate_parameters()

    def _can_automate_parameters(self):
        return self.parameter_provider.parameters and liveobj_valid(self._clip) and not self._clip.is_arrangement_clip and len(self._selected_time) > 0

    def set_parameter_controls(self, encoders):
        self.encoders.set_control_element(encoders)

    def _update_parameters(self):
        super(AutomationComponent, self)._update_parameters()
        self._update_parameter_floats()

    def _connect_parameters(self):
        pass

    def parameter_to_string(self, parameter):
        if not parameter:
            return ''
        if len(self._selected_time) == 0:
            return '-'
        return parameter.str_for_value(self.parameter_to_value(parameter))

    def parameter_to_value(self, parameter):
        if self._clip and len(self.selected_time) > 0:
            envelope = self._clip.automation_envelope(parameter)
            if liveobj_valid(envelope):
                return self._value_at_time(envelope, self.selected_time[0])
        return 0.0

    def _value_at_time(self, envelope, time_range):
        return envelope.value_at_time((time_range[0] + time_range[1]) / 2)

    def _can_edit_clip_envelope(self, parameter_index):
        parameters = self.parameters
        return 0 <= parameter_index < len(parameters) and self._clip and self._parameter_for_index(parameters, parameter_index)

    def _parameter_for_index(self, parameters, index):
        return parameters[index]

    @encoders.value
    def encoders(self, value, encoder):
        index = encoder.index
        parameters = self.parameters
        if self._can_edit_clip_envelope(index):
            param = self._parameter_for_index(parameters, index)
            envelope = self._clip.automation_envelope(param)
            if liveobj_valid(envelope):
                if param.automation_state == AutomationState.overridden:
                    param.re_enable_automation()
                for time_index, time_range in enumerate(self.selected_time):
                    self._insert_step(time_range, time_index, index, envelope, value)

            self._update_parameter_values()

    @encoders.touched
    def encoders(self, encoder):
        index = encoder.index
        parameters = self.parameters
        if self._can_edit_clip_envelope(index):
            self._clip.view.select_envelope_parameter(self._parameter_for_index(parameters, index))
            self._update_parameter_floats()

    def _update_parameter_floats(self):
        if self._clip and self.is_enabled():
            parameters = self.parameters
            envelopes = [ (self._clip.automation_envelope(self._parameter_for_index(parameters, index)) if param != None else None) for index, param in enumerate(parameters) ]
            self._parameter_floats = [ [ (self._value_at_time(envelope, step) if envelope != None else 0.0) for envelope in envelopes ] for step in self.selected_time ]
        else:
            self._parameter_floats = []

    def _insert_step(self, time_range, time_index, param_index, envelope, value):
        param = self._parameter_for_index(self.parameters, param_index)
        envelope_value = self._parameter_floats[time_index][param_index]
        sensitivity = self.parameter_infos[param_index].default_encoder_sensitivity * self.ENCODER_SENSITIVITY_FACTOR
        if param.is_quantized:
            value_to_insert = clamp(envelope_value + value / EnumerableSetting.STEP_SIZE, param.min, param.max)
        else:
            value_range = param.max - param.min
            value_to_insert = clamp(envelope_value + value * value_range * sensitivity, param.min, param.max)
        self._parameter_floats[time_index][param_index] = value_to_insert
        envelope.insert_step(time_range[0], time_range[1] - time_range[0], value_to_insert)