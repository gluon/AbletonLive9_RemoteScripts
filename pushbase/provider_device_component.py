#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/pushbase/provider_device_component.py
from __future__ import absolute_import, with_statement
from ableton.v2.base import BooleanContext
from ableton.v2.control_surface.components import DeviceComponent
from .parameter_provider import ParameterProvider, generate_info

class ProviderDeviceComponent(ParameterProvider, DeviceComponent):
    """
    Device component that serves as parameter provider for the
    DeviceParameterComponent.
    """
    _provided_parameters = tuple()

    def __init__(self, *a, **k):
        super(ProviderDeviceComponent, self).__init__(*a, **k)
        self.set_parameter_controls([])
        self._suppress_parameter_notification = BooleanContext()

    @property
    def parameters(self):
        return self._provided_parameters

    def set_device(self, device):
        with self._suppress_parameter_notification():
            super(ProviderDeviceComponent, self).set_device(device)
        self._provided_parameters = self._get_provided_parameters()
        self.notify_parameters()

    def _is_banking_enabled(self):
        return True

    def _assign_parameters(self):
        super(ProviderDeviceComponent, self)._assign_parameters()
        self._provided_parameters = self._get_provided_parameters()
        if not self._suppress_parameter_notification:
            self.notify_parameters()

    def _get_provided_parameters(self):
        _, parameters = self._current_bank_details() if self._device else (None, ())
        return [ generate_info(p) for p in parameters ]