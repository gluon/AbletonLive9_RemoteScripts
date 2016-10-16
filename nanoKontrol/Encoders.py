"""
# Copyright (C) 2009 Myralfur <james@waterworth.org.uk>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Myralfur <james@waterworth.org.uk>
"""

import Live
from consts import *
from _Generic.Devices import *

class Encoders:
    __module__ = __name__
    __doc__ = ' Class representing the Encoder section on the NanoKontrol '

    def __init__(self, parent, extended):
        self._Encoders__parent = parent
        self._Encoders__bank = 0
        self._Encoders__selected_device = None
        self._Encoders__extended = extended
        self._Encoders__modifier = False
        self._Encoders__device_locked = False
        self._Encoders__show_bank = False



    def build_midi_map(self, script_handle, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        feedback_rule.channel = 0
        feedback_rule.cc_no = NANOKONTROL_ENC9
        feedback_rule.cc_value_map = tuple()
        feedback_rule.delay_in_ms = -1.0
        for channel in range(16):
            Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self._Encoders__parent.song().master_track.mixer_device.cue_volume, channel, NANOKONTROL_ENC9, Live.MidiMap.MapMode.absolute_14_bit, feedback_rule, 1)

        for channel in range(4):
            for encoder in range(8):
                track_index = (encoder + (channel * 8))
                if (len(self._Encoders__parent.song().tracks) > track_index):
                    feedback_rule.channel = 0
                    feedback_rule.cc_no = NANOKONTROL_ENCODERS[encoder]
                    feedback_rule.cc_value_map = tuple()
                    feedback_rule.delay_in_ms = -1.0
                    if (self._Encoders__extended or self._Encoders__modifier):
                        device_parameter = self._Encoders__parent.song().tracks[track_index].mixer_device.panning
                    else:
                        device_parameter = self._Encoders__parent.song().tracks[track_index].mixer_device.volume
                    Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, device_parameter, channel, NANOKONTROL_ENCODERS[encoder], Live.MidiMap.MapMode.absolute, feedback_rule, 1)
                else:
                    break


        self._Encoders__connect_to_device(midi_map_handle)



    def set_modifier(self, mod_state):
        self._Encoders__modifier = mod_state



    def __connect_to_device(self, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        assignment_necessary = True
        if (not (self._Encoders__selected_device == None)):
            device_parameters = self._Encoders__selected_device.parameters
            device_bank = 0
            param_bank = 0
            if (self._Encoders__selected_device.class_name in DEVICE_DICT.keys()):
                device_bank = DEVICE_DICT[self._Encoders__selected_device.class_name]
                if (len(device_bank) > self._Encoders__bank):
                    param_bank = device_bank[self._Encoders__bank]
                else:
                    assignment_necessary = False
            if assignment_necessary:
                if self._Encoders__show_bank:
                    self._Encoders__show_bank = False
                    if (self._Encoders__selected_device.class_name in DEVICE_DICT.keys()):
                        if (len(list(DEVICE_DICT[self._Encoders__selected_device.class_name])) > 1):
                            if (self._Encoders__selected_device.class_name in BANK_NAME_DICT.keys()):
                                bank_names = BANK_NAME_DICT[self._Encoders__selected_device.class_name]
                                if (bank_names and (len(bank_names) > self._Encoders__bank)):
                                    bank_name = bank_names[self._Encoders__bank]
                                    self._Encoders__show_bank_select(bank_name)
                            else:
                                self._Encoders__show_bank_select('Best of Parameters')
                        else:
                            self._Encoders__show_bank_select(('Bank' + str((self._Encoders__bank + 1))))
                free_encoders = 0
                for encoder in range(8):
                    parameter_index = (encoder + (self._Encoders__bank * 8))
                    if ((len(device_parameters) + free_encoders) >= parameter_index):
                        feedback_rule.channel = 0
                        feedback_rule.cc_no = NANOKONTROL_ENCODERS[encoder]
                        feedback_rule.cc_value_map = tuple()
                        feedback_rule.delay_in_ms = -1.0
                        parameter = 0
                        if param_bank:
                            if (param_bank[encoder] != ''):
                                parameter = get_parameter_by_name(self._Encoders__selected_device, param_bank[encoder])
                            else:
                                free_encoders += 1
                        elif (len(device_parameters) > parameter_index):
                            parameter = device_parameters[parameter_index]
                        if parameter:
                            Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, 15, NANOKONTROL_ENCODERS[encoder], Live.MidiMap.MapMode.absolute, feedback_rule, 1)
                        elif (not param_bank):
                            break
                    else:
                        break




    def receive_midi_cc(self, cc_no, cc_value, channel):
        pass


    def lock_to_device(self, device):
        if device:
            self._Encoders__device_locked = True
            if (not (device == self._Encoders__selected_device)):
                self._Encoders__bank = 0
            self._Encoders__show_bank = False
            self._Encoders__selected_device = device
            self._Encoders__parent.request_rebuild_midi_map()



    def unlock_from_device(self, device):
        if (device and (device == self._Encoders__selected_device)):
            self._Encoders__device_locked = False
            if (not (self._Encoders__parent.song().appointed_device == self._Encoders__selected_device)):
                self._Encoders__parent.request_rebuild_midi_map()



    def set_appointed_device(self, device):
        if self._Encoders__device_locked:
            self._Encoders__device_locked = False
        if (not (device == self._Encoders__selected_device)):
            self._Encoders__bank = 0
        self._Encoders__show_bank = False
        self._Encoders__selected_device = device
        self._Encoders__parent.request_rebuild_midi_map()



    def set_bank(self, new_bank):
        result = False
        if self._Encoders__selected_device:
            if (number_of_parameter_banks(self._Encoders__selected_device) > new_bank):
                self._Encoders__show_bank = True
                if (not self._Encoders__device_locked):
                    self._Encoders__bank = new_bank
                    result = True
                else:
                    self._Encoders__selected_device.store_chosen_bank(self._Encoders__parent.instance_identifier(), new_bank)
        return result



    def restore_bank(self, new_bank):
        self._Encoders__bank = new_bank
        self._Encoders__show_bank = True



    def reset_bank(self):
        self._Encoders__bank = 0



    def __show_bank_select(self, bank_name):
        if self._Encoders__selected_device:
            self._Encoders__parent.show_message(str(((self._Encoders__selected_device.name + ' Bank: ') + bank_name)))



