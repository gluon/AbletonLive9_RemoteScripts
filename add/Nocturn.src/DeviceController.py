#
# Copyright (C) 2009 Guillermo Ruiz Troyano
#
# This file is part of Nocturn Remote Script for Live (Nocturn RS4L).
#
#    Nocturn RS4L is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nocturn RS4L is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nocturn RS4L.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact info:
#    Guillermo Ruiz Troyano, ruiztroyano@gmail.com
# Revision 2009-09-01:
#    Bug fixed, Guillermo Ruiz Troyano
#

import Live
from NocturnComponent import NocturnComponent
from _Generic.Devices import *
from consts import *
class DeviceController(NocturnComponent):
    __module__ = __name__
    __doc__ = "Control device parameters."
    
    def __init__(self, nocturn_parent):
        NocturnComponent.__init__(self, nocturn_parent)
        self._bank_index = 0
        self._num_banks = 0

    def disconnect(self):
        pass

    def device(self):
        return self.song().appointed_device
        
    def set_appointed_device(self, device):
        self.request_rebuild_midi_map()

    def lock_to_device(self, device):
        pass

    def unlock_from_device(self, device):
        pass

    def receive_note(self, channel, note, vel):
        if (channel == DEV_BANK_CH):
            index = note-DEV_BANK_BASE_NO
            if ((index >= 0) and (index < NUM_STRIPS)):
                if (index < self._num_banks):
                    self._bank_index = index
                    self.request_rebuild_midi_map()
                else:
                    self.send_midi((NOTE_ON_STATUS+DEV_BANK_CH,DEV_BANK_BASE_NO+index,0))

    def build_midi_map(self, script_handle, midi_map_handle):
        dev = self.device()
        if (dev):
            map_mode = Live.MidiMap.MapMode.absolute
            feedback_rule = Live.MidiMap.CCFeedbackRule()
            feedback_rule.delay_in_ms = 0
            feedback_rule.cc_value_map = tuple()
            feedback_rule.channel = DEV_CH
            
            params = 0
            if (list(DEVICE_DICT.keys()).count(dev.class_name) > 0):
                param_banks = DEVICE_DICT[dev.class_name]
                self._num_banks = len(param_banks)
                params = param_banks[self._bank_index]
            else:
                self._num_banks = int((len(dev.parameters)+NUM_STRIPS-2)/NUM_STRIPS)

            for index in range(0,NUM_STRIPS):
                if ((params and (index < len(params))) or (index+self._bank_index*NUM_STRIPS+1 < len(dev.parameters))):
                    parameter = 0
                    if (params):
                        parameter = get_parameter_by_name(dev, params[index])
                    else:
                        parameter = dev.parameters[index+self._bank_index*NUM_STRIPS+1]
                    feedback_rule.cc_no = DEV_BASE_CC+index
                    if (parameter):
                        self.map_parameter(midi_map_handle, parameter, feedback_rule)
                else:
                    Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, DEV_CH, DEV_BASE_CC+index)
                    self.send_midi((CC_STATUS+DEV_CH,DEV_BASE_CC+index,0))

                Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, DEV_BANK_CH, DEV_BANK_BASE_NO+index)
                is_bank = (index == self._bank_index)
                self.send_midi((NOTE_ON_STATUS+DEV_BANK_CH,DEV_BANK_BASE_NO+index,is_bank and 127))

