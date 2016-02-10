#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_APC/DeviceComponent.py
from itertools import ifilter
from _Framework.CompoundComponent import CompoundComponent
from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase

class DeviceComponent(DeviceComponentBase, CompoundComponent):

    def __init__(self, use_fake_banks = False, *a, **k):
        super(DeviceComponent, self).__init__(*a, **k)
        self._use_fake_banks = use_fake_banks

    def set_parameter_controls(self, controls):
        super(DeviceComponent, self).set_parameter_controls(controls)
        self._update_parameter_controls()

    def _current_bank_details(self):
        bank_name = ''
        bank = []
        if self._bank_index in range(len(self._parameter_banks())):
            bank_name, bank = super(DeviceComponent, self)._current_bank_details()
        return (bank_name, bank)

    def _number_of_parameter_banks(self):
        num = super(DeviceComponent, self)._number_of_parameter_banks()
        if self._use_fake_banks:
            return max(num, 8)
        return num

    def _on_device_bank_changed(self, device, bank):
        super(DeviceComponent, self)._on_device_bank_changed(device, bank)
        self._update_parameter_controls()

    def _update_parameter_controls(self):
        for control in ifilter(None, self._parameter_controls or []):
            control.set_channel(self._bank_index)

    def update(self):
        super(DeviceComponent, self).update()
        if self.is_enabled():
            self._update_parameter_controls()