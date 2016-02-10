#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/OpenLabs/SpecialDeviceComponent.py
import Live
from _Framework.DeviceComponent import DeviceComponent

class SpecialDeviceComponent(DeviceComponent):

    def __init__(self):
        DeviceComponent.__init__(self)

    def _device_parameters_to_map(self):
        raise self.is_enabled() or AssertionError
        raise self._device != None or AssertionError
        raise self._parameter_controls != None or AssertionError
        return self._device.parameters[1:]