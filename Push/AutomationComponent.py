#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/AutomationComponent.py
from itertools import count
import Live
AutomationState = Live.DeviceParameter.AutomationState
from _Framework import Task
from _Framework.Util import clamp
from _Framework.SubjectSlot import subject_slot_group
from DeviceParameterComponent import DeviceParameterComponent
from Setting import EnumerableSetting

class AutomationComponent(DeviceParameterComponent):
    _clip = None

    def __init__(self, *a, **k):
        super(AutomationComponent, self).__init__(*a, **k)
        self._selected_time = []
        self._parameter_floats = []
        self._update_parameter_values_task = self._tasks.add(Task.run(self._update_parameter_values))
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
    def can_automate_parameters(self):
        return self.parameter_provider.parameters and self._clip and not self._clip.is_arrangement_clip

    def set_parameter_controls(self, encoders):
        self._on_encoder_value.replace_subjects(encoders or [], count())
        self._on_encoder_touch.replace_subjects(encoders or [], count())

    def _update_parameters(self):
        super(AutomationComponent, self)._update_parameters()
        self._update_parameter_floats()

    def _connect_parameters(self):
        pass

    def parameter_to_string(self, parameter):
        if not parameter:
            return ''
        elif len(self._selected_time) == 0:
            return '-'
        return parameter.str_for_value(self.parameter_to_value(parameter))

    def parameter_to_value(self, parameter):
        if self._clip and len(self.selected_time) > 0:
            envelope = self._clip.automation_envelope(parameter)
            if envelope != None:
                return self._value_at_time(envelope, self.selected_time[0])
        return 0.0

    def _value_at_time(self, envelope, time_range):
        return envelope.value_at_time((time_range[0] + time_range[1]) / 2)

    @subject_slot_group('normalized_value')
    def _on_encoder_value(self, value, index):
        if self.is_enabled():
            parameters = self.parameters
            if 0 <= index < len(parameters) and self._clip and parameters[index]:
                param = parameters[index]
                envelope = self._clip.automation_envelope(param)
                if envelope != None:
                    if param.automation_state == AutomationState.overridden:
                        param.re_enable_automation()
                    self._clip.view.select_envelope_parameter(param)
                    for time_index, time_range in enumerate(self.selected_time):
                        self._insert_step(time_range, time_index, index, envelope, value)

                self._update_parameter_values()

    @subject_slot_group('touch_value')
    def _on_encoder_touch(self, value, index):
        if self.is_enabled() and value:
            parameters = self.parameters
            if 0 <= index < len(parameters) and parameters[index] and self._clip:
                self._clip.view.select_envelope_parameter(parameters[index])
                self._update_parameter_floats()

    def _update_parameter_floats(self):
        if self._clip and self.is_enabled():
            envelopes = [ (self._clip.automation_envelope(param) if param != None else None) for param in self.parameters ]
            self._parameter_floats = [ [ (self._value_at_time(envelope, step) if envelope != None else 0.0) for envelope in envelopes ] for step in self.selected_time ]
        else:
            self._parameter_floats = []

    def _insert_step(self, time_range, time_index, param_index, envelope, value):
        param = self.parameters[param_index]
        envelope_value = self._parameter_floats[time_index][param_index]
        if param.is_quantized:
            value_to_insert = clamp(envelope_value + value / EnumerableSetting.STEP_SIZE, param.min, param.max)
        else:
            value_range = param.max - param.min
            value_to_insert = clamp(envelope_value + value * value_range, param.min, param.max)
        self._parameter_floats[time_index][param_index] = value_to_insert
        envelope.insert_step(time_range[0], time_range[1] - time_range[0], value_to_insert)