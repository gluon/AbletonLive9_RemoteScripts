#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2Modulator.py
from _Generic.Devices import *
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.InputControlElement import *
from LC2ParameterElement import LC2ParameterElement
from LC2Sysex import LC2Sysex, LC2SysexParser
import Live

class LC2Modulator(DeviceComponent):

    def __init__(self):
        self._parameter_offset = 0
        self._selected_param = 0
        self._selected_parameter = None
        DeviceComponent.__init__(self)
        LC2ParameterElement.set_select_param(self.select_parameter)
        self._xys = [ LC2ParameterElement(MIDI_PB_TYPE, i, 0) for i in range(8) ]
        self._device_banks = {}
        self.song().view.add_selected_parameter_listener(self._on_selected_parameter_changed)

    def send_xy_map(self):
        sysex = LC2Sysex('XY_MAP')
        for p in self._xys:
            sysex.byte(int(p.mapped_parameter() is not None))

        sysex.send()

    def send_params(self):
        if self._parameter_controls is not None:
            for p in self._parameter_controls:
                p._send_param_val(True)

        self._on_device_name_changed()

    def _on_device_name_changed(self):
        DeviceComponent._on_device_name_changed(self)
        name = 'Please select a device in Live'
        if self._device is not None:
            if self._device.canonical_parent.name:
                pre = self._device.canonical_parent.name
            else:
                pre = 'Chain'
            name = pre + ': ' + unicode(self._device.name)
        sysex = LC2Sysex('DEVICE_NAME')
        sysex.ascii(name)
        sysex.send()

    def select_parameter(self, param):
        self._selected_parameter = param
        self._send_id_param()

    def _on_selected_parameter_changed(self):
        self._selected_parameter = self.song().view.selected_parameter
        self._send_id_param()

    def handle_sysex(self, sysex):
        cmds = [self._select_xy,
         self._set_param,
         self._select_param,
         self._select_chain,
         self._select_chain_device,
         self._select_parent]
        if sysex[0] < len(cmds):
            cmds[sysex[0]](LC2SysexParser(sysex[1:]))

    def disconnect(self):
        self.song().view.remove_selected_parameter_listener(self._on_selected_parameter_changed)

    def _select_chain(self, sysex):
        self._selected_chain_id = sysex.parse('b')
        self._send_chain_devices()

    def _select_chain_device(self, sysex):
        id = sysex.parse('b')
        if self._device is not None:
            if self._selected_chain_id < len(self._device.chains):
                if id < len(self._device.chains[self._selected_chain_id].devices):
                    self.song().view.select_device(self._device.chains[self._selected_chain_id].devices[id])

    def _select_parent(self, sysex):
        if self._device is not None:
            parent = self._device.canonical_parent.canonical_parent
            if isinstance(parent, Live.Device.Device):
                self.song().view.select_device(parent)

    def _select_param(self, sysex):
        id = sysex.parse('b')
        if id < len(self._parameter_controls):
            p = self._parameter_controls[id].mapped_parameter()
            if p is not None:
                self._selected_parameter = p
                self._send_id_param()

    def _set_param(self, sysex):
        v = sysex.parse('b')
        if v:
            if self._selected_parameter is not None:
                for xy in self._xys:
                    if xy.mapped_parameter() == self._selected_parameter:
                        xy.release_parameter()

                self._xys[self._selected_param].connect_to(self._selected_parameter)
        else:
            self._xys[self._selected_param].release_parameter()
        self.send_xy_map()

    def _select_xy(self, sysex):
        pid = sysex.parse('b')
        LC2Sysex.log_message('SELECTING XY ' + str(pid))
        if pid < len(self._xys):
            self._selected_param = pid
            param = self._xys[pid]
            if param.mapped_parameter() is not None:
                if isinstance(param.mapped_parameter().canonical_parent, Live.Device.Device):
                    self.song().view.select_device(param.mapped_parameter().canonical_parent)
            self._send_id_param()

    def _send_id_param(self):
        param = self._xys[self._selected_param]
        if param.mapped_parameter() is not None:
            mapped = 1
            pid, name = param.settings()
        else:
            mapped = 0
            if self._selected_parameter is not None:
                if hasattr(self._selected_parameter, 'canonical_parent'):
                    parent = self._selected_parameter.canonical_parent
                    if not hasattr(parent, 'name'):
                        if hasattr(parent, 'canonical_parent'):
                            parent = parent.canonical_parent
                    pid = unicode(parent.name)
                    name = unicode(self._selected_parameter.name)
                else:
                    pid = ''
                    name = ''
            else:
                pid = ''
                name = ''
        sysex = LC2Sysex('XY_ID_NAME')
        sysex.byte(mapped)
        sysex.ascii(pid)
        sysex.ascii(name)
        sysex.send()

    def update(self):
        DeviceComponent.update(self)
        if self.is_enabled():
            if self._lock_button != None:
                if self._locked_to_device:
                    self._lock_button.turn_on()
                else:
                    self._lock_button.turn_off()
        if LC2Sysex.l9():
            self._update_on_off_button()
        else:
            self._on_on_off_changed()

    def set_device(self, device):
        DeviceComponent.set_device(self, device)
        if device is not None:
            if hasattr(device, 'chains'):
                LC2Sysex.log_message(str(len(device.chains)))
            if hasattr(device, 'drum_pads'):
                LC2Sysex.log_message(str(len(device.drum_pads)))
                LC2Sysex.log_message(str(len(device.drum_pads[0].chains)))
        cl = 0
        par = False
        if self._device is not None:
            if hasattr(self._device, 'canonical_parent'):
                par = isinstance(self._device.canonical_parent, Live.Device.Device) or isinstance(self._device.canonical_parent, Live.Chain.Chain)
            else:
                par = False
            if hasattr(self._device, 'chains'):
                if len(self._device.chains) > 0:
                    chains = [ i < len(self._device.chains) and (self._device.chains[i].name == '' and 'Chain ' + str(i + 1) or self._device.chains[i].name) or '' for i in range(8) ]
                    cl = min(8, len(self._device.chains))
                else:
                    chains = [ '' for i in range(8) ]
            else:
                chains = [ '' for i in range(8) ]
        else:
            chains = [ '' for i in range(8) ]
        sysex = LC2Sysex('CHAIN_NAMES')
        sysex.byte(cl)
        sysex.byte(int(par))
        for i in range(8):
            sysex.ascii(chains[i])

        sysex.send()
        self._selected_chain_id = 0
        self._send_chain_devices()

    def _send_chain_devices(self):
        cdl = 0
        if self._device is not None:
            if hasattr(self._device, 'chains'):
                if self._selected_chain_id < len(self._device.chains):
                    devices = [ i < len(self._device.chains[self._selected_chain_id].devices) and self._device.chains[self._selected_chain_id].devices[i].name or '' for i in range(8) ]
                    cdl = min(8, len(self._device.chains[self._selected_chain_id].devices))
                else:
                    devices = [ '' for i in range(8) ]
            else:
                devices = [ '' for i in range(8) ]
        else:
            devices = [ '' for i in range(8) ]
        sysex = LC2Sysex('CHAIN_DEVICES')
        sysex.byte(cdl)
        for i in range(8):
            sysex.ascii(devices[i])

        sysex.send()

    def set_device_select_buttons(self, buttons):
        raise isinstance(tuple, buttons) or AssertionError
        self._device_select_buttons = buttons

    def _bank_up_value(self, value):
        if self.is_enabled():
            if not self._bank_up_button.is_momentary() or value is not 0:
                if self._device != None:
                    num_banks = self.number_of_parameter_banks(self._device)
                    if num_banks > self._bank_index + 1:
                        self._bank_index += 1
                        self.update()
                    if num_banks == self._bank_index + 1:
                        self._bank_up_button.turn_off()

    def _bank_down_value(self, value):
        DeviceComponent._bank_down_value(self, value)
        if self._bank_index == 0:
            self._bank_down_button.turn_off()

    def number_of_parameter_banks(self, device):
        result = 0
        if device != None:
            param_count = len(list(device.parameters))
            result = param_count / 16
            if not param_count % 16 == 0:
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