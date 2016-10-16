#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Axiom/Encoders.py
import Live
from consts import *
from _Generic.Devices import *

class Encoders:
    """ Class representing the Encoder section on the Axiom controllers """

    def __init__(self, parent, extended):
        self.__parent = parent
        self.__bank = 0
        self.__selected_device = None
        self.__extended = extended
        self.__modifier = False
        self.__device_locked = False
        self.__show_bank = False

    def disconnect(self):
        if self.__selected_device != None:
            self.__selected_device.remove_parameters_listener(self.__on_device_parameters_changed)
            self.__selected_device = None

    def build_midi_map(self, script_handle, midi_map_handle):
        tracks = self.__parent.song().visible_tracks
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        for channel in range(4):
            for encoder in range(8):
                track_index = encoder + channel * 8
                if len(tracks) > track_index:
                    feedback_rule.channel = 0
                    feedback_rule.cc_no = AXIOM_ENCODERS[encoder]
                    feedback_rule.cc_value_map = tuple()
                    feedback_rule.delay_in_ms = -1.0
                    if self.__extended or self.__modifier:
                        device_parameter = tracks[track_index].mixer_device.panning
                    else:
                        device_parameter = tracks[track_index].mixer_device.volume
                    avoid_takeover = True
                    Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, device_parameter, channel, AXIOM_ENCODERS[encoder], Live.MidiMap.MapMode.relative_smooth_binary_offset, feedback_rule, not avoid_takeover)
                else:
                    break

        self.__connect_to_device(midi_map_handle)

    def set_modifier(self, mod_state):
        self.__modifier = mod_state

    def __connect_to_device(self, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        assignment_necessary = True
        avoid_takeover = True
        if not self.__selected_device == None:
            device_parameters = self.__selected_device.parameters[1:]
            device_bank = 0
            param_bank = 0
            if self.__selected_device.class_name in DEVICE_DICT.keys():
                device_bank = DEVICE_DICT[self.__selected_device.class_name]
                if len(device_bank) > self.__bank:
                    param_bank = device_bank[self.__bank]
                else:
                    assignment_necessary = False
            if assignment_necessary:
                if self.__show_bank:
                    self.__show_bank = False
                    if self.__selected_device.class_name in DEVICE_DICT.keys():
                        if len(list(DEVICE_DICT[self.__selected_device.class_name])) > 1:
                            if self.__selected_device.class_name in BANK_NAME_DICT.keys():
                                bank_names = BANK_NAME_DICT[self.__selected_device.class_name]
                                if bank_names and len(bank_names) > self.__bank:
                                    bank_name = bank_names[self.__bank]
                                    self.__show_bank_select(bank_name)
                            else:
                                self.__show_bank_select('Best of Parameters')
                        else:
                            self.__show_bank_select('Bank' + str(self.__bank + 1))
                free_encoders = 0
                for encoder in range(8):
                    parameter_index = encoder + self.__bank * 8
                    if len(device_parameters) + free_encoders >= parameter_index:
                        feedback_rule.channel = 0
                        feedback_rule.cc_no = AXIOM_ENCODERS[encoder]
                        feedback_rule.cc_value_map = tuple()
                        feedback_rule.delay_in_ms = -1.0
                        parameter = 0
                        if param_bank:
                            if param_bank[encoder] != '':
                                parameter = get_parameter_by_name(self.__selected_device, param_bank[encoder])
                            else:
                                free_encoders += 1
                        elif len(device_parameters) > parameter_index:
                            parameter = device_parameters[parameter_index]
                        if parameter:
                            Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, 15, AXIOM_ENCODERS[encoder], Live.MidiMap.MapMode.relative_smooth_binary_offset, feedback_rule, not avoid_takeover)
                        elif not param_bank:
                            break
                    else:
                        break

    def receive_midi_cc(self, cc_no, cc_value, channel):
        pass

    def lock_to_device(self, device):
        if device:
            self.__device_locked = True
            self.__change_appointed_device(device)

    def unlock_from_device(self, device):
        if device and device == self.__selected_device:
            self.__device_locked = False
            if not self.__parent.song().appointed_device == self.__selected_device:
                self.__parent.request_rebuild_midi_map()

    def set_appointed_device(self, device):
        if self.__device_locked:
            self.__device_locked = False
        self.__change_appointed_device(device)

    def set_bank(self, new_bank):
        result = False
        if self.__selected_device:
            if number_of_parameter_banks(self.__selected_device) > new_bank:
                self.__show_bank = True
                if not self.__device_locked:
                    self.__bank = new_bank
                    result = True
                else:
                    self.__selected_device.store_chosen_bank(self.__parent.instance_identifier(), new_bank)
        return result

    def restore_bank(self, new_bank):
        self.__bank = new_bank
        self.__show_bank = True

    def reset_bank(self):
        self.__bank = 0

    def __show_bank_select(self, bank_name):
        if self.__selected_device:
            self.__parent.show_message(str(self.__selected_device.name + ' Bank: ' + bank_name))

    def __change_appointed_device(self, device):
        if not device == self.__selected_device:
            if self.__selected_device != None:
                self.__selected_device.remove_parameters_listener(self.__on_device_parameters_changed)
            if device != None:
                device.add_parameters_listener(self.__on_device_parameters_changed)
            self.__bank = 0
        self.__show_bank = False
        self.__selected_device = device
        self.__parent.request_rebuild_midi_map()

    def __on_device_parameters_changed(self):
        self.__parent.request_rebuild_midi_map()