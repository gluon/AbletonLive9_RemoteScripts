#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/DeviceComponent.py
from __future__ import absolute_import
import Live
from _Generic.Devices import device_parameters_to_map, number_of_parameter_banks, parameter_banks, parameter_bank_names, best_of_parameter_bank
from .ButtonElement import ButtonElement
from .ControlSurfaceComponent import ControlSurfaceComponent
from .DeviceBankRegistry import DeviceBankRegistry
from .DisplayDataSource import DisplayDataSource
from .SubjectSlot import subject_slot, subject_slot_group, Subject

def device_to_appoint(device):
    appointed_device = device
    if device != None and device.can_have_drum_pads and not device.has_macro_mappings and len(device.chains) > 0 and device.view.selected_chain != None and len(device.view.selected_chain.devices) > 0:
        appointed_device = device_to_appoint(device.view.selected_chain.devices[0])
    return appointed_device


def select_and_appoint_device(song, device_to_select, ignore_unmapped_macros = True):
    """
    Convenience function for selecting a device for a control surface to control.
    
    This takes care of selecting the device and appointing it for remote control, which
    is important, because these are two concepts, that are not exactly the same.
    
    The device component always controls the appointed device. It's possible to select
    another device, but not appoint it for control. The behaviour in this function
    appoints a drum rack's selected chain's first device if none of the macros are mapped
    for the drum rack. Though, it's still possible to select the drum rack, we just do
    not display its controls in this scenario.
    """
    appointed_device = device_to_select
    if ignore_unmapped_macros:
        appointed_device = device_to_appoint(device_to_select)
    song.appointed_device = appointed_device
    song.view.select_device(device_to_select, False)


class DeviceComponent(ControlSurfaceComponent, Subject):
    """ Class representing a device in Live """
    __subject_events__ = ('device',)

    def __init__(self, device_bank_registry = None, *a, **k):
        super(DeviceComponent, self).__init__(*a, **k)
        self._device_bank_registry = device_bank_registry or DeviceBankRegistry()
        self._device = None
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

        def make_property_slot(name, alias = None):
            alias = alias or name
            return self.register_slot(None, getattr(self, '_on_%s_changed' % alias), name)

        self._on_off_property_slot = make_property_slot('value', alias='device_on_off')
        self._name_property_slot = make_property_slot('name', alias='device_name')
        self._parameters_property_slot = make_property_slot('parameters')
        self._device_bank_property_slot = make_property_slot('device_bank')

        def make_button_slot(name):
            return self.register_slot(None, getattr(self, '_%s_value' % name), 'value')

        self._bank_up_button_slot = make_button_slot('bank_up')
        self._bank_down_button_slot = make_button_slot('bank_down')
        self._lock_button_slot = make_button_slot('lock')
        self._on_off_button_slot = make_button_slot('on_off')
        song = self.song()
        view = song.view
        self._device_bank_property_slot.subject = self._device_bank_registry
        self.__on_appointed_device_changed.subject = song
        self.__on_selected_track_changed.subject = view
        self.__on_selected_device_changed.subject = view.selected_track.view

    def disconnect(self):
        self._device_bank_registry = None
        self._lock_callback = None
        self._release_parameters(self._parameter_controls)
        self._parameter_controls = None
        self._bank_up_button = None
        self._bank_down_button = None
        self._bank_buttons = None
        self._on_off_button = None
        self._lock_button = None
        self._device = None
        super(DeviceComponent, self).disconnect()

    def on_enabled_changed(self):
        self.update()

    def device(self):
        return self._device

    @subject_slot('appointed_device')
    def __on_appointed_device_changed(self):
        self.set_device(device_to_appoint(self.song().appointed_device))

    def set_device(self, device):
        if not self._locked_to_device and (device != self._device or type(device) != type(self._device)):
            if self._device != None:
                self._release_parameters(self._parameter_controls)
            self._device = device
            self._name_property_slot.subject = device
            self._parameters_property_slot.subject = device
            self._on_off_property_slot.subject = self._on_off_parameter()
            if self._device != None:
                self._bank_index = 0
            self._bank_index = self._device_bank_registry.get_device_bank(self._device)
            self._bank_name = '<No Bank>'
            self._on_device_name_changed()
            self.update()
            self.notify_device()

    @subject_slot('has_macro_mappings')
    def __on_has_macro_mappings_changed(self):
        self.song().appointed_device = device_to_appoint(self.__on_has_macro_mappings_changed.subject)

    @subject_slot('selected_track')
    def __on_selected_track_changed(self):
        self.__on_selected_device_changed.subject = self.song().view.selected_track.view

    @subject_slot('chains')
    def __on_chains_changed(self):
        self._update_appointed_device()

    @subject_slot('selected_device')
    def __on_selected_device_changed(self):
        self._update_appointed_device()

    def _update_appointed_device(self):
        song = self.song()
        device = song.view.selected_track.view.selected_device
        if device != None:
            song.appointed_device = device_to_appoint(device)
        rack_device = device if isinstance(device, Live.RackDevice.RackDevice) else None
        self.__on_has_macro_mappings_changed.subject = rack_device
        self.__on_chains_changed.subject = rack_device

    def set_bank_prev_button(self, button):
        if button != self._bank_down_button:
            self._bank_down_button = button
            self._bank_down_button_slot.subject = button
            self.update()

    def set_bank_next_button(self, button):
        if button != self._bank_up_button:
            self._bank_up_button = button
            self._bank_up_button_slot.subject = button
            self.update()

    def set_bank_nav_buttons(self, down_button, up_button):
        self.set_bank_prev_button(down_button)
        self.set_bank_next_button(up_button)

    def set_bank_buttons(self, buttons):
        self._bank_buttons = buttons
        self._on_bank_value.replace_subjects(buttons or [])
        self.update()

    def set_parameter_controls(self, controls):
        self._release_parameters(self._parameter_controls)
        self._parameter_controls = controls
        self.update()

    def set_lock_to_device(self, lock, device):
        if lock:
            self.set_device(device)
        self._locked_to_device = lock
        self._update_lock_button()

    def set_lock_button(self, button):
        raise button == None or isinstance(button, ButtonElement) or AssertionError
        self._lock_button = button
        self._lock_button_slot.subject = button
        self._update_lock_button()

    def set_on_off_button(self, button):
        self._on_off_button = button
        self._on_off_button_slot.subject = button
        self._update_on_off_button()

    def set_lock_callback(self, callback):
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

    def update(self):
        super(DeviceComponent, self).update()
        if self.is_enabled() and self._device != None:
            self._device_bank_registry.set_device_bank(self._device, self._bank_index)
            if self._parameter_controls != None:
                old_bank_name = self._bank_name
                self._assign_parameters()
                if self._bank_name != old_bank_name:
                    self._show_msg_callback(self._device.name + ' Bank: ' + self._bank_name)
        elif self._parameter_controls != None:
            self._release_parameters(self._parameter_controls)
        if self.is_enabled():
            self._update_on_off_button()
            self._update_lock_button()
            self._update_device_bank_buttons()
            self._update_device_bank_nav_buttons()

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

    @subject_slot_group('value')
    def _on_bank_value(self, value, button):
        self._bank_value(value, button)

    def _bank_value(self, value, button):
        if self.is_enabled() and self._device != None:
            if not button.is_momentary() or value is not 0:
                bank = list(self._bank_buttons).index(button)
                if bank != self._bank_index:
                    if self._number_of_parameter_banks() > bank:
                        self._bank_name = ''
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

    def _on_device_on_off_changed(self):
        self._update_on_off_button()

    def _on_device_name_changed(self):
        if self._device_name_data_source != None:
            self._device_name_data_source.set_display_string(self._device.name if self.is_enabled() and self._device != None else 'No Device')

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

    def _update_on_off_button(self):
        if self.is_enabled() and self._on_off_button != None:
            turn_on = False
            if self._device != None:
                parameter = self._on_off_parameter()
                turn_on = parameter != None and parameter.value > 0.0
            self._on_off_button.set_light(turn_on)

    def _update_lock_button(self):
        if self.is_enabled() and self._lock_button != None:
            self._lock_button.set_light(self._locked_to_device)

    def _update_device_bank_buttons(self):
        if self.is_enabled():
            for index, button in enumerate(self._bank_buttons or []):
                if button:
                    button.set_light(index == self._bank_index and self._device)

    def _update_device_bank_nav_buttons(self):
        if self.is_enabled():
            if self._bank_up_button != None and self._bank_down_button != None:
                can_bank_up = self._bank_index == None or self._number_of_parameter_banks() > self._bank_index + 1
                can_bank_down = self._bank_index == None or self._bank_index > 0
                self._bank_up_button.set_light(self._device and can_bank_up)
                self._bank_down_button.set_light(self._device and can_bank_down)

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