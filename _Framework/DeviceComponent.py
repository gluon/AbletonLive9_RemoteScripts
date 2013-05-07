#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/DeviceComponent.py
import Live
from _Generic.Devices import device_parameters_to_map, number_of_parameter_banks, parameter_banks, parameter_bank_names, best_of_parameter_bank
from ControlSurfaceComponent import ControlSurfaceComponent
from ButtonElement import ButtonElement
from DisplayDataSource import DisplayDataSource
from DeviceBankRegistry import DeviceBankRegistry

class DeviceComponent(ControlSurfaceComponent):
    """ Class representing a device in Live """

    def __init__(self, device_bank_registry = None, *a, **k):
        super(DeviceComponent, self).__init__(*a, **k)
        self._device_bank_registry = device_bank_registry or DeviceBankRegistry()
        self._device_bank_registry.add_device_bank_listener(self._on_device_bank_changed)
        self._device = None
        self._device_listeners = []
        self._parameter_controls = None
        self._bank_up_button = None
        self._bank_down_button = None
        self._bank_buttons = None
        self._on_off_button = None
        self._lock_button = None
        self._lock_callback = None
        self._device_name_data_source = None
        self._bank_index = 0
        self._bank_name = '<No Bank>'
        self._locked_to_device = False

    def disconnect(self):
        self._device_bank_registry.remove_device_bank_listener(self._on_device_bank_changed)
        self._device_bank_registry = None
        self._lock_callback = None
        self._release_parameters(self._parameter_controls)
        self._parameter_controls = None
        if self._bank_up_button != None:
            self._bank_up_button.remove_value_listener(self._bank_up_value)
            self._bank_up_button = None
        if self._bank_down_button != None:
            self._bank_down_button.remove_value_listener(self._bank_down_value)
            self._bank_down_button = None
        if self._bank_buttons != None:
            for button in self._bank_buttons:
                button.remove_value_listener(self._bank_value)

        self._bank_buttons = None
        if self._on_off_button != None:
            self._on_off_button.remove_value_listener(self._on_off_value)
            self._on_off_button = None
        if self._lock_button != None:
            self._lock_button.remove_value_listener(self._lock_value)
            self._lock_button = None
        if self._device != None:
            parameter = self._on_off_parameter()
            if parameter != None:
                parameter.remove_value_listener(self._on_on_off_changed)
            self._device.remove_name_listener(self._on_device_name_changed)
            self._device.remove_parameters_listener(self._on_parameters_changed)
            self._device = None
        self._device_listeners = None
        super(DeviceComponent, self).disconnect()

    def on_enabled_changed(self):
        self.update()

    def device(self):
        return self._device

    def set_device(self, device):
        if not (device == None or isinstance(device, Live.Device.Device)):
            raise AssertionError
            if not self._locked_to_device and device != self._device:
                if self._device != None:
                    self._device.remove_name_listener(self._on_device_name_changed)
                    self._device.remove_parameters_listener(self._on_parameters_changed)
                    parameter = self._on_off_parameter()
                    if parameter != None:
                        parameter.remove_value_listener(self._on_on_off_changed)
                    self._release_parameters(self._parameter_controls)
                self._device = device
                if self._device != None:
                    self._bank_index = 0
                    self._device.add_name_listener(self._on_device_name_changed)
                    self._device.add_parameters_listener(self._on_parameters_changed)
                    parameter = self._on_off_parameter()
                    parameter != None and parameter.add_value_listener(self._on_on_off_changed)
            self._bank_index = self._device_bank_registry.get_device_bank(self._device)
            self._bank_name = '<No Bank>'
            self._on_device_name_changed()
            self.update()
            for listener in self._device_listeners:
                listener()

    def set_bank_nav_buttons(self, down_button, up_button):
        if not (up_button != None or down_button == None):
            raise AssertionError
            if not (up_button == None or isinstance(up_button, ButtonElement)):
                raise AssertionError
                if not (down_button == None or isinstance(down_button, ButtonElement)):
                    raise AssertionError
                    do_update = False
                    if up_button != self._bank_up_button:
                        do_update = True
                        if self._bank_up_button != None:
                            self._bank_up_button.remove_value_listener(self._bank_up_value)
                        self._bank_up_button = up_button
                        if self._bank_up_button != None:
                            self._bank_up_button.add_value_listener(self._bank_up_value)
                    if down_button != self._bank_down_button:
                        do_update = True
                        self._bank_down_button != None and self._bank_down_button.remove_value_listener(self._bank_down_value)
                    self._bank_down_button = down_button
                    self._bank_down_button != None and self._bank_down_button.add_value_listener(self._bank_down_value)
            do_update and self.update()

    def set_bank_buttons(self, buttons):
        if not (buttons == None or isinstance(buttons, tuple)):
            raise AssertionError
            if self._bank_buttons != None:
                for button in self._bank_buttons:
                    button.remove_value_listener(self._bank_value)

            self._bank_buttons = buttons
            identify_sender = self._bank_buttons != None and True
            for button in self._bank_buttons:
                button.add_value_listener(self._bank_value, identify_sender)

        self.update()

    def set_parameter_controls(self, controls):
        self._release_parameters(self._parameter_controls)
        self._parameter_controls = controls
        self.update()

    def set_lock_to_device(self, lock, device):
        if lock:
            self.set_device(device)
        self._locked_to_device = lock
        if self.is_enabled() and self._lock_button != None:
            self._lock_button.set_light(self._locked_to_device)

    def set_lock_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._lock_button != None:
                self._lock_button.remove_value_listener(self._lock_value)
                self._lock_button = None
            self._lock_button = button
            self._lock_button != None and self._lock_button.add_value_listener(self._lock_value)
        self.update()

    def set_on_off_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._on_off_button != None:
                self._on_off_button.remove_value_listener(self._on_off_value)
                self._on_off_button = None
            self._on_off_button = button
            self._on_off_button != None and self._on_off_button.add_value_listener(self._on_off_value)
        self.update()

    def set_lock_callback(self, callback):
        raise self._lock_callback == None or AssertionError
        raise callback != None or AssertionError
        raise dir(callback).count('im_func') is 1 or AssertionError
        self._lock_callback = callback

    def restore_bank(self, bank_index):
        if self._device != None and self._is_banking_enabled() and self._locked_to_device and self._number_of_parameter_banks() > bank_index and self._bank_index != bank_index:
            self._bank_index = bank_index
            self.update()

    def device_name_data_source(self):
        if self._device_name_data_source == None:
            self._device_name_data_source = DisplayDataSource()
            self._on_device_name_changed()
        return self._device_name_data_source

    def device_has_listener(self, listener):
        return listener in self._device_listeners

    def add_device_listener(self, listener):
        raise not self.device_has_listener(listener) or AssertionError
        self._device_listeners.append(listener)

    def remove_device_listener(self, listener):
        raise self.device_has_listener(listener) or AssertionError
        self._device_listeners.remove(listener)

    def update(self):
        if self.is_enabled() and self._device != None:
            self._device_bank_registry.set_device_bank(self._device, self._bank_index)
            if self._parameter_controls != None:
                old_bank_name = self._bank_name
                self._assign_parameters()
                if self._bank_name != old_bank_name:
                    self._show_msg_callback(self._device.name + ' Bank: ' + self._bank_name)
            if self._bank_up_button != None and self._bank_down_button != None:
                can_bank_up = self._bank_index == None or self._number_of_parameter_banks() > self._bank_index + 1
                can_bank_down = self._bank_index == None or self._bank_index > 0
                self._bank_up_button.set_light(can_bank_up)
                self._bank_down_button.set_light(can_bank_down)
            if self._bank_buttons != None:
                for index, button in enumerate(self._bank_buttons):
                    button.set_light(index == self._bank_index)

        else:
            if self._lock_button != None:
                self._lock_button.turn_off()
            if self._bank_up_button != None:
                self._bank_up_button.turn_off()
            if self._bank_down_button != None:
                self._bank_down_button.turn_off()
            if self._bank_buttons != None:
                for button in self._bank_buttons:
                    button.turn_off()

            if self._parameter_controls != None:
                self._release_parameters(self._parameter_controls)

    def _bank_up_value(self, value):
        raise self._bank_up_button != None or AssertionError
        raise value != None or AssertionError
        raise isinstance(value, int) or AssertionError
        if self.is_enabled():
            if not self._bank_up_button.is_momentary() or value is not 0:
                if self._device != None:
                    num_banks = self._number_of_parameter_banks()
                    if self._bank_down_button == None:
                        self._bank_name = ''
                        self._bank_index = (self._bank_index + 1) % num_banks if self._bank_index != None else 0
                        self.update()
                    elif self._bank_index == None or num_banks > self._bank_index + 1:
                        self._bank_name = ''
                        self._bank_index = self._bank_index + 1 if self._bank_index != None else 0
                        self.update()

    def _bank_down_value(self, value):
        if not self._bank_down_button != None:
            raise AssertionError
            raise value != None or AssertionError
            if not isinstance(value, int):
                raise AssertionError
                if self.is_enabled():
                    self._bank_name = (not self._bank_down_button.is_momentary() or value is not 0) and self._device != None and (self._bank_index == None or self._bank_index > 0) and ''
                    self._bank_index = self._bank_index - 1 if self._bank_index != None else max(0, self._number_of_parameter_banks() - 1)
                    self.update()

    def _lock_value(self, value):
        if not self._lock_button != None:
            raise AssertionError
            raise self._lock_callback != None or AssertionError
            raise value != None or AssertionError
            raise isinstance(value, int) or AssertionError
            (not self._lock_button.is_momentary() or value is not 0) and self._lock_callback()

    def _on_off_value(self, value):
        if not self._on_off_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                parameter = (not self._on_off_button.is_momentary() or value is not 0) and self._on_off_parameter()
                parameter.value = parameter != None and parameter.is_enabled and float(int(parameter.value == 0.0))

    def _bank_value(self, value, button):
        if not self._bank_buttons != None:
            raise AssertionError
            raise value != None or AssertionError
            raise button != None or AssertionError
            raise isinstance(value, int) or AssertionError
            raise isinstance(button, ButtonElement) or AssertionError
            if not list(self._bank_buttons).count(button) == 1:
                raise AssertionError
                if self.is_enabled() and self._device != None:
                    if not button.is_momentary() or value is not 0:
                        bank = list(self._bank_buttons).index(button)
                        self._bank_name = bank != self._bank_index and self._number_of_parameter_banks() > bank and ''
                        self._bank_index = bank
                        self.update()
                else:
                    self._show_msg_callback(self._device.name + ' Bank: ' + self._bank_name)

    def _is_banking_enabled(self):
        direct_banking = self._bank_buttons != None
        roundtrip_banking = self._bank_up_button != None
        increment_banking = self._bank_up_button != None and self._bank_down_button != None
        return direct_banking or roundtrip_banking or increment_banking

    def _assign_parameters(self):
        raise self.is_enabled() or AssertionError
        raise self._device != None or AssertionError
        raise self._parameter_controls != None or AssertionError
        self._bank_name, bank = self._current_bank_details()
        for control, parameter in zip(self._parameter_controls, bank):
            if control != None:
                if parameter != None:
                    control.connect_to(parameter)
                else:
                    control.release_parameter()

        self._release_parameters(self._parameter_controls[len(bank):])

    def _on_device_name_changed(self):
        if self._device_name_data_source != None:
            if self.is_enabled() and self._device != None:
                self._device_name_data_source.set_display_string(self._device.name)
            else:
                self._device_name_data_source.set_display_string('No Device')

    def _on_parameters_changed(self):
        self.update()

    def _on_off_parameter(self):
        result = None
        if self._device != None:
            for parameter in self._device.parameters:
                if str(parameter.name).startswith('Device On'):
                    result = parameter
                    break

        return result

    def _on_on_off_changed(self):
        if self.is_enabled() and self._on_off_button != None:
            turn_on = False
            if self._device != None:
                parameter = self._on_off_parameter()
                if parameter != None:
                    turn_on = parameter.value > 0.0
                turn_on and self._on_off_button.turn_on()
            else:
                self._on_off_button.turn_off()

    def _best_of_parameter_bank(self):
        return best_of_parameter_bank(self._device)

    def _parameter_banks(self):
        return parameter_banks(self._device)

    def _parameter_bank_names(self):
        return parameter_bank_names(self._device)

    def _device_parameters_to_map(self):
        return device_parameters_to_map(self._device)

    def _number_of_parameter_banks(self):
        return number_of_parameter_banks(self._device)

    def _current_bank_details(self):
        bank_name = self._bank_name
        bank = []
        best_of = self._best_of_parameter_bank()
        banks = self._parameter_banks()
        if banks:
            if self._bank_index != None and self._is_banking_enabled() or not best_of:
                index = self._bank_index if self._bank_index != None else 0
                bank = banks[index]
                bank_name = self._parameter_bank_names()[index]
            else:
                bank = best_of
                bank_name = 'Best of Parameters'
        return (bank_name, bank)

    def _on_device_bank_changed(self, device, bank):
        if device == self._device:
            self._bank_index = bank
            self.update()

    def _release_parameters(self, controls):
        if controls != None:
            for control in controls:
                if control != None:
                    control.release_parameter()