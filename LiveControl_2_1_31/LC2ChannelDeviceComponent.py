#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2ChannelDeviceComponent.py
from _Framework.DeviceComponent import DeviceComponent
from LC2Sysex import LC2Sysex

class LC2ChannelDeviceComponent(DeviceComponent):

    def __init__(self):
        DeviceComponent.__init__(self)
        self._device_banks = {}

    def bank(self, ud):
        if self._device is not None:
            LC2Sysex.log_message('device')
            if ud:
                num_banks = self.number_of_parameter_banks(self._device)
                LC2Sysex.log_message('up' + str(num_banks))
                if num_banks > self._bank_index + 1:
                    self._bank_name = ''
                    self._bank_index += 1
                    self.update()
            elif self._bank_index > 0:
                self._bank_name = ''
                self._bank_index -= 1
                self.update()

    def number_of_parameter_banks(self, device):
        result = 0
        if device != None:
            param_count = len(list(device.parameters))
            result = param_count / 4
            if not param_count % 4 == 0:
                result += 1
        return result

    def _assign_parameters(self):
        raise self.is_enabled() or AssertionError
        raise self._device != None or AssertionError
        raise self._parameter_controls != None or AssertionError
        parameters = self._device_parameters_to_map()
        num_controls = len(self._parameter_controls)
        index = self._bank_index * num_controls
        for control in self._parameter_controls:
            if index < len(parameters):
                control.connect_to(parameters[index])
            else:
                control.release_parameter()
            index += 1