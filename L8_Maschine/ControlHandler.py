#Embedded file name: C:\ProgramData\Ableton\Live 8\Resources\MIDI Remote Scripts\Maschine_Mk1\ControlHandler.py
import Live
import time
from _Generic.Devices import *
from _Framework.ButtonElement import *
from _Framework.CompoundComponent import *
from MIDI_Map import *
from SceneElement import SceneElement
N_PARM_RANGE = 127

class ControlHandler:
    __module__ = __name__
    __doc__ = ' Special button class that can be configured with custom on- and off-values '

    def __init__(self, surface, matrix):
        self.surface = surface
        self.matrix = matrix
        self.mode = CONTROL_LEVEL
        self.sel_track_parm_index = 0
        self.track = None
        self.selected_sends_index = 0
        self.selected_device = None
        self.selected_bank = 0
        self.selected_device_parm_index = 0
        self.parm = None
        self.parm_is_quant = False
        self.parm_raster_value = 0
        self.parm_range = 0

    def get_mode_color(self, value, mode):
        if value == 0:
            bright = 8
        else:
            bright = 127
        if mode == CONTROL_LEVEL:
            return [27, 127, bright]
        elif mode == CONTROL_PAN:
            return [4, 127, bright]
        elif mode == CONTROL_SEND:
            return [10, 127, bright]
        elif mode == CONTROL_DEVICE:
            return [85, 127, bright]

    def nr_of_parms_in_bank(self):
        if self.selected_device == None:
            return 0
        nr_of_parms = len(self.selected_device.parameters)
        bip = nr_of_parms - 8 * self.selected_bank
        if bip < 8:
            return bip
        return 8

    def inc_bank_nr(self):
        if self.selected_device == None or self.selected_bank + 1 >= self.nr_of_banks():
            return False
        self.selected_bank += 1
        self.surface.show_message('Bank ' + str(self.selected_bank + 1) + ' : ' + str(self.selected_device.name))
        self.reassign_device_parm()
        parminfo = ''
        if self.parm != None:
            parminfo = str(self.parm.name)
        self.surface.show_message(str(self.selected_device.name) + 'Bank ' + str(self.selected_bank + 1) + ' : ' + parminfo)
        return True

    def dec_bank_nr(self):
        if self.selected_device == None or self.selected_bank == 0:
            return False
        self.selected_bank -= 1
        self.reassign_device_parm()
        parminfo = ''
        if self.parm != None:
            parminfo = str(self.parm.name)
        self.surface.show_message(str(self.selected_device.name) + 'Bank ' + str(self.selected_bank + 1) + ' : ' + parminfo)
        return True

    def nr_of_banks(self):
        if self.selected_device == None:
            return 0
        parms = len(self.selected_device.parameters)
        if parms == 0:
            return 0
        return parms / 8 + 1

    def index_parm_id(self, index):
        if index > 11:
            return index - 12
        else:
            return index - 4
        return 0

    def index_mode_id(self, index):
        if index > 4 and index < 8:
            return index - 4
        return 0

    def set_device(self, device):
        self.selected_device = device
        self.selected_bank = 0
        self.reassign_device_parm()

    def set_track(self, index):
        self.track = self.surface._mixer._channel_strips[index]._track

    def reassign_mix_parm(self):
        self.assign_mix_parm(self.track, self.sel_track_parm_index)

    def message_current_parm(self):
        if self.track == None:
            return
        message = 'Control Track : ' + str(self.track.name) + ': '
        if self.mode == CONTROL_LEVEL:
            self.surface.show_message(message + 'Volume')
        elif self.mode == CONTROL_PAN:
            self.surface.show_message(message + 'Pan')
        elif self.mode == CONTROL_SEND:
            self.surface.show_message(message + 'Send ' + SENDS[self.selected_sends_index])
        elif self.mode == CONTROL_DEVICE:
            return 'Device'

    def assign_mix_parm(self, track, index):
        prev = self.parm
        if track == None:
            self.parm = None
            return prev != self.parm
        self.track = track
        self.parm_is_quant = False
        if self.mode == CONTROL_LEVEL:
            self.parm = track.mixer_device.volume
        elif self.mode == CONTROL_PAN:
            self.parm = track.mixer_device.panning
        elif self.mode == CONTROL_SEND:
            nr_of_ret_tracks = len(track.mixer_device.sends)
            if self.selected_sends_index < nr_of_ret_tracks and self.selected_sends_index != -1:
                self.parm = track.mixer_device.sends[self.selected_sends_index]
        self.set_knob_int_value(self.parm)
        self.sel_track_parm_index = index
        return prev != self.parm

    def reassign_device_parm(self):
        self.assign_device_parm(self.selected_device_parm_index, False)

    def assign_device_parm(self, index, showmessage = True):
        prev = self.parm
        if self.mode != CONTROL_DEVICE or self.selected_device == None:
            self.parm = None
            return prev != self.parm
        parms = self.selected_device.parameters
        self.selected_device_parm_index = min(index, self.nr_of_parms_in_bank() - 1)
        parm = parms[self.selected_bank * 8 + self.selected_device_parm_index]
        if parm.is_quantized:
            self.parm_is_quant = True
        else:
            self.parm_is_quant = False
            self.set_knob_int_value(parm)
        if showmessage:
            self.surface.show_message('Device : ' + str(self.selected_device.name) + ' : ' + str(parm.name))
        self.parm = parm
        self.parm_range = parm.max - parm.min
        return prev != self.parm

    def set_knob_int_value(self, parm):
        parm_range = parm.max - parm.min
        self.parm_raster_value = int((parm.value - parm.min) / parm_range * N_PARM_RANGE + 0.1)

    def is_quantized(self, parm):
        self.set_knob_int_value(parm)
        return False

    def mod_value(self, delta, shift):
        if self.parm == None:
            return
        if self.mode == CONTROL_DEVICE:
            if self.parm_is_quant:
                self.parm.value = self.change_parm(self.parm, delta)
                if shift and self.parm_range > 30:
                    self.repeat(self.parm, delta)
            else:
                new_value = self.change_parm(self.parm, delta)
                self.parm.value = new_value
                if not self.is_equal(self.parm.value, new_value):
                    self.parm_is_quant = True
                if not self.parm_is_quant and shift:
                    self.repeat(self.parm, delta)
            self.surface.show_message(' ' + str(self.selected_device.name) + ' : ' + str(self.parm.name) + ' : ' + str(self.parm))
        else:
            self.parm.value = self.change_parm(self.parm, delta)
            if shift:
                self.repeat(self.parm, delta)

    def is_equal(self, val1, val2):
        if val1 == val2:
            return True
        if abs(val1 - val2) < 0.005:
            return True
        return False

    def repeat(self, parm, delta):
        count = 0
        while count < SHIFT_INC - 1:
            parm.value = self.change_parm(parm, delta)
            count += 1

    def change_parm(self, parm, delta):
        if self.parm_is_quant:
            parm_range = parm.max - parm.min + 1
            new_val = min(parm.max, max(parm.min, parm.value + delta))
            return float(new_val)
        else:
            parm_range = parm.max - parm.min
            self.parm_raster_value = min(N_PARM_RANGE, max(0, self.parm_raster_value + delta))
            return float(self.parm_raster_value) / float(N_PARM_RANGE) * parm_range + parm.min

    def disconnect(self):
        self.surface = None
        self.matrix = None
        self.track = None
        self.selected_device = None
        self.parm = None