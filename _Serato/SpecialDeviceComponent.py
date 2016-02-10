#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Serato/SpecialDeviceComponent.py
import Live
import libInterprocessCommsAPIPython
from PySCAClipControl import *
from _Framework.DeviceComponent import DeviceComponent

class SpecialDeviceComponent(DeviceComponent):

    def __init__(self):
        DeviceComponent.__init__(self)
        self._serato_interface = None
        self._parameter_listeners = []

    def disconnect(self):
        self._remove_parameter_listeners()
        self._on_device_name_changed()
        DeviceComponent.disconnect(self)
        self._serato_interface = None
        self._parameter_listeners = None

    def set_device(self, device):
        if not self._locked_to_device and device != self._device:
            self._remove_parameter_listeners()
        DeviceComponent.set_device(self, device)

    def set_serato_interface(self, serato_interface):
        raise serato_interface != 0 or AssertionError
        self._serato_interface = serato_interface
        self._on_device_name_changed()

    def set_parameter_value(self, parameter_index, value):
        if not parameter_index in range(len(self._parameter_controls)):
            raise AssertionError
            raise 0.0 <= value and value <= 1.0 or AssertionError
            parameter = self._parameter_controls[parameter_index].mapped_parameter()
            adapted_value = parameter != None and parameter.is_enabled and value * abs(parameter.max - parameter.min)
            parameter.value = adapted_value + parameter.min

    def update(self):
        if self.is_enabled() and self._device != None:
            self._device_bank_registry[self._device] = self._bank_index
            if self._parameter_controls != None:
                self._remove_parameter_listeners()
                self._assign_parameters()
                self._add_parameter_listeners()
        elif self._parameter_controls != None:
            for control in self._parameter_controls:
                control.release_parameter()

        self._on_on_off_changed()

    def _on_parameter_name_changed(self, index):
        if not self._parameter_controls != None:
            raise AssertionError
            if not index in range(len(self._parameter_controls)):
                raise AssertionError
                parameter = self._serato_interface != None and self._parameter_controls[index].mapped_parameter()
                name = ''
                name = parameter != None and parameter.name
            self._serato_interface.PySCA_SetDeviceParamLabel(index + 1, name)

    def _on_device_name_changed(self):
        if self._serato_interface != None:
            name = 'No Device'
            if self._device != None:
                name = self._device.name
            self._serato_interface.PySCA_SetDeviceLabel(name)

    def _on_parameter_changed(self, index):
        if not self._parameter_controls != None:
            raise AssertionError
            if not index in range(len(self._parameter_controls)):
                raise AssertionError
                parameter = self._serato_interface != None and self._parameter_controls[index].mapped_parameter()
                value_to_send = 0
                value_to_send = parameter != None and (parameter.value - parameter.min) / (parameter.max - parameter.min)
            self._serato_interface.PySCA_SetDeviceParamValue(index + 1, value_to_send)

    def _on_on_off_changed(self):
        if self.is_enabled() and self._serato_interface != None:
            state = 0
            if self._device != None:
                parameter = self._on_off_parameter()
                if parameter != None and parameter.value > 0.0:
                    state = 1
            self._serato_interface.PySCA_SetDeviceActive(state)

    def _add_parameter_listeners(self):
        if self._parameter_controls != None:
            for index in range(len(self._parameter_controls)):
                parameter = self._parameter_controls[index].mapped_parameter()
                value_listener = lambda index = index: self._on_parameter_changed(index)
                name_listener = lambda index = index: self._on_parameter_name_changed(index)
                if parameter != None:
                    if not parameter.value_has_listener(value_listener):
                        parameter.add_value_listener(value_listener)
                        self._parameter_listeners.append((parameter, value_listener))
                value_listener()
                name_listener()

    def _remove_parameter_listeners(self):
        if self._parameter_controls != None:
            for index in range(len(self._parameter_listeners)):
                pair = self._parameter_listeners[index]
                parameter = pair[0]
                if parameter != None:
                    value_listener = pair[1]
                    if parameter.value_has_listener(value_listener):
                        parameter.remove_value_listener(value_listener)
                if self._serato_interface != None:
                    self._serato_interface.PySCA_SetDeviceParamValue(index + 1, 0)
                    self._serato_interface.PySCA_SetDeviceParamLabel(index + 1, '')

            self._parameter_listeners = []