#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/ProviderDeviceComponent.py
from _Framework.DeviceComponent import DeviceComponent
from DeviceParameterComponent import ParameterProvider

class ProviderDeviceComponent(ParameterProvider, DeviceComponent):
    """
    Device component that serves as parameter provider for the
    DeviceParameterComponent.
    """
    _provided_parameters = tuple()

    def __init__(self, *a, **k):
        super(ProviderDeviceComponent, self).__init__(*a, **k)
        self.set_parameter_controls([])

    @property
    def parameters(self):
        return self._provided_parameters

    def set_device(self, device):
        super(ProviderDeviceComponent, self).set_device(device)
        self._provided_parameters = self._get_provided_parameters()
        self.notify_parameters()

    def _is_banking_enabled(self):
        return True

    def _assign_parameters(self):
        super(ProviderDeviceComponent, self)._assign_parameters()
        self._provided_parameters = self._get_provided_parameters()
        self.notify_parameters()

    def _get_provided_parameters(self):
        _, parameters = self._current_bank_details() if self._device else (None, ())
        return zip([ (param.name if param else '') for param in parameters ], parameters)