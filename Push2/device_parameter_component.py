#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/device_parameter_component.py
from __future__ import absolute_import
from ableton.v2.control_surface.control import ControlList
from pushbase.device_parameter_component import DeviceParameterComponentBase
from .mapped_control import MappedControl

class DeviceParameterComponent(DeviceParameterComponentBase):
    controls = ControlList(MappedControl, 8)

    def set_parameter_controls(self, encoders):
        self.controls.set_control_element(encoders)
        self._connect_parameters()

    def _connect_parameters(self):
        parameters = self._parameter_provider.parameters[:self.controls.control_count]
        for control, parameter_info in map(None, self.controls, parameters):
            parameter = parameter_info.parameter if parameter_info else None
            control.mapped_parameter = parameter
            if parameter:
                control.update_sensitivities(parameter_info.default_encoder_sensitivity, parameter_info.fine_grain_encoder_sensitivity)