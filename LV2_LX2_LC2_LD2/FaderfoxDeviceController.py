#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/LV2_LX2_LC2_LD2/FaderfoxDeviceController.py
import Live
from FaderfoxComponent import FaderfoxComponent
from consts import *
import sys
from Devices import *
from DevicesXY import *
from ParamMap import ParamMap

class FaderfoxDeviceController(FaderfoxComponent):
    __module__ = __name__
    __doc__ = 'Class representing the device controller section of Faderfox controllers'
    __filter_funcs__ = ['update_display', 'log']

    def __init__(self, parent):
        FaderfoxDeviceController.realinit(self, parent)

    def realinit(self, parent):
        FaderfoxComponent.realinit(self, parent)
        self.log('device controller %s' % parent)
        self.device = None
        if hasattr(self.parent.song(), 'appointed_device'):
            self.device = self.parent.song().appointed_device
        self.log('device %s' % self.device)
        self.device_locked = False
        self.bank = 0
        self.show_bank = False
        self.selected_clip = None
        self.on_track_selected_callback = lambda : self.on_track_selected()
        self.parent.song().view.add_selected_track_listener(self.on_track_selected_callback)
        self.parent.song().view.add_detail_clip_listener(self.on_selected_clip)
        self.selected_track = None

    def on_loop_end(self):
        pass

    def on_loop_pass(self):
        pass

    def on_pitch_change(self):
        pass

    def on_selected_clip(self):
        self.selected_clip = self.parent.song().view.detail_clip

    def build_midi_map(self, script_handle, midi_map_handle):

        def forward_note(chan, note):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, chan, note)

        def forward_cc(chan, cc):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, chan, cc)

        for note in FX3_NOTES:
            forward_note(CHANNEL_SETUP2, note)

        for note in FX4_NOTES:
            forward_note(CHANNEL_SETUP2, note)

        self.log('midi rebuild map')
        tracks = tuple(self.parent.song().tracks) + tuple(self.parent.song().return_tracks)
        for idx in range(0, 16):
            if len(tracks) > idx:
                track = tracks[idx]
                eq = self.helper.track_find_last_eq(track)
                self.log('found eq %s on track %s' % (eq, track))
                if eq:
                    params = self.helper.eq_params(eq)
                    for i in range(0, 4):
                        if params[i] != None:
                            self.log('map %s to %s' % (EQ_CCS[idx][i], params[i]))
                            ParamMap.map_with_feedback(midi_map_handle, AUX_CHANNEL_SETUP2, EQ_CCS[idx][i], params[i], Live.MidiMap.MapMode.absolute)

            master_eq = self.helper.track_find_last_eq(self.parent.song().master_track)
            if master_eq:
                params = self.helper.eq_params(master_eq)
                for i in range(0, 4):
                    if params[i] != None:
                        ParamMap.map_with_feedback(midi_map_handle, AUX_CHANNEL_SETUP2, MASTER_EQ_CCS[i], params[i], Live.MidiMap.MapMode.absolute)

        self.map_device_params(script_handle, midi_map_handle)
        forward_cc(CHANNEL_SETUP2, CLIP_TRANSPOSE_CC)

    def map_device_params(self, script_handle, midi_map_handle):

        def map_params_by_number(device):
            ccs = []
            channel = CHANNEL_SETUP2
            mode = Live.MidiMap.MapMode.relative_two_compliment
            if self.parent.is_lv1:
                ccs = LV1_FX3_CCS + LV1_FX4_CCS
                channel = TRACK_CHANNEL_SETUP2
                mode = Live.MidiMap.MapMode.absolute
            else:
                ccs = FX3_CCS + FX4_CCS
                channel = CHANNEL_SETUP2
            for encoder in range(8):
                if len(device.parameters) >= encoder + 1:
                    ParamMap.map_with_feedback(midi_map_handle, channel, ccs[encoder], device.parameters[encoder + 1], mode)

        def map_params_by_name(device, param_bank):
            ccs = []
            channel = CHANNEL_SETUP2
            mode = Live.MidiMap.MapMode.relative_two_compliment
            if self.parent.is_lv1:
                ccs = LV1_FX3_CCS + LV1_FX4_CCS
                channel = TRACK_CHANNEL_SETUP2
                mode = Live.MidiMap.MapMode.absolute
            else:
                ccs = FX3_CCS + FX4_CCS
                channel = CHANNEL_SETUP2
            for encoder in range(8):
                if len(params) >= encoder:
                    if param_bank[encoder] == '':
                        continue
                    param_name = param_bank[encoder]
                    parameter = None
                    parameter = self.helper.get_parameter_by_name(self.device, param_bank[encoder])
                    if parameter:
                        mode2 = mode
                        fullname = self.helper.device_name(device) + '.' + parameter.name
                        if parameter.is_quantized and not self.parent.is_lv1 and not INVERT_QUANT_PARAM.has_key(fullname):
                            mode2 = Live.MidiMap.MapMode.relative_binary_offset
                        self.logfmt('parameter %s %s to %s (quant %s)', parameter, parameter.name, ccs[encoder], parameter.is_quantized)
                        ParamMap.map_with_feedback(midi_map_handle, channel, ccs[encoder], parameter, mode2)
                    else:
                        self.log('Could not find parameter %s' % param_bank[encoder])

        self.log('map device params %s' % self.device)
        if self.device:
            params = self.device.parameters
            device_bank = 0
            param_bank = 0
            device_name = self.helper.device_name(self.device)
            self.log("device name '%s'" % device_name)
            if device_name in XY_DEVICE_DICT.keys():
                xys = XY_DEVICE_DICT[device_name]
                if len(xys) > 0:
                    param1 = self.helper.get_parameter_by_name(self.device, xys[0][0])
                    param2 = self.helper.get_parameter_by_name(self.device, xys[0][1])
                    ccx = FX1_JOY_X_CC
                    ccy = FX1_JOY_Y_CC
                    channel = CHANNEL_SETUP2
                    if self.parent.is_lv1:
                        ccx = LV1_FX1_JOY_X_CC
                        ccy = LV1_FX1_JOY_Y_CC
                        channel = TRACK_CHANNEL_SETUP2
                    if param1:
                        ParamMap.map_with_feedback(midi_map_handle, channel, ccx, param1, Live.MidiMap.MapMode.absolute)
                    if param2:
                        ParamMap.map_with_feedback(midi_map_handle, channel, ccy, param2, Live.MidiMap.MapMode.absolute)
                if len(xys) > 1:
                    param1 = self.helper.get_parameter_by_name(self.device, xys[1][0])
                    param2 = self.helper.get_parameter_by_name(self.device, xys[1][1])
                    ccx = FX2_JOY_X_CC
                    ccy = FX2_JOY_Y_CC
                    channel = CHANNEL_SETUP2
                    if self.parent.is_lv1:
                        ccx = LV1_FX2_JOY_X_CC
                        ccy = LV1_FX2_JOY_Y_CC
                        channel = TRACK_CHANNEL_SETUP2
                    ParamMap.map_with_feedback(midi_map_handle, channel, ccx, param1, Live.MidiMap.MapMode.absolute)
                    ParamMap.map_with_feedback(midi_map_handle, channel, ccy, param2, Live.MidiMap.MapMode.absolute)
            if device_name in DEVICE_BOB_DICT.keys():
                param_bank = DEVICE_BOB_DICT[device_name]
                if device_name == 'Compressor2' and self.helper.get_parameter_by_name(self.device, 'Ext. In Gain'):
                    param_bank = CP2_BANK1_LIVE7
                self.log('class %s bank: %s' % (device_name, param_bank))
                self.show_bank_select('Best of parameters')
                map_params_by_name(self.device, param_bank)
            elif self.helper.device_is_plugin(self.device):
                self.show_bank_select('First eight parameters')
                map_params_by_number(self.device)
            else:
                self.log('Could not find %s in %s' % (device_name, DEVICE_BOB_DICT.keys()))
                return

    def show_bank_select(self, bank_name):
        if self.show_bank:
            self.show_bank = False
            if self.device:
                self.parent.show_message(str(self.device.name + ' Bank: ' + bank_name))

    def receive_midi_note(self, channel, status, note_no, note_vel):

        def index_of(list, elt):
            for i in range(0, len(list)):
                if list[i] == elt:
                    return i

        if not self.device:
            return
        device_name = self.helper.device_name(self.device)
        if channel == CHANNEL_SETUP2 and status == NOTEON_STATUS:
            notes = FX3_NOTES + FX4_NOTES
            if note_no not in notes:
                return
            idx = index_of(notes, note_no)
            parameter = None
            if device_name in DEVICE_BOB_DICT.keys():
                param_bank = DEVICE_BOB_DICT[device_name]
                parameter = self.helper.get_parameter_by_name(self.device, param_bank[idx])
            elif self.helper.device_is_plugin(self.device):
                if len(self.device.parameters) >= idx + 1:
                    parameter = self.device.parameters[idx + 1]
            else:
                return
            if parameter:
                if parameter.is_quantized:
                    if parameter.value + 1 > parameter.max:
                        parameter.value = parameter.min
                    else:
                        parameter.value += 1
                else:
                    parameter.value = parameter.default_value
            self.log('device %s, index %s, parameter %s' % (self.device, idx, parameter.name))

    def receive_midi_cc(self, chan, cc_no, cc_value):

        def rel_to_offs(cc_value):
            if cc_value >= 64:
                return cc_value - 128
            else:
                return cc_value

        def round_to(x, step):
            return step * round(x / step)

        if chan == CHANNEL_SETUP2 and self.selected_clip:
            if cc_no == CLIP_TRANSPOSE_CC and self.selected_clip.is_audio_clip:
                self.selected_clip.pitch_coarse = max(-48, min(self.selected_clip.pitch_coarse + rel_to_offs(cc_value), 48))
            elif cc_no == CLIP_LOOP_START_CC:
                new_start = self.selected_clip.loop_start + rel_to_offs(cc_value) * self.helper.current_q_step()
                new_start = round_to(new_start, self.helper.current_q_step())
                if new_start >= self.selected_clip.length or new_start >= self.selected_clip.loop_end:
                    new_start = self.selected_clip.loop_start
                if new_start < 0.0:
                    new_start = 0.0
                self.selected_clip.loop_start = new_start
            elif cc_no == CLIP_LOOP_END_CC:
                new_end = self.selected_clip.loop_end + rel_to_offs(cc_value) * self.helper.current_q_step()
                new_end = round_to(new_end, self.helper.current_q_step())
                if new_end >= self.selected_clip.length:
                    new_end = self.selected_clip.length
                if new_end <= 0.0 or new_end <= self.selected_clip.loop_start:
                    new_end = self.selected_clip.loop_end
                self.selected_clip.loop_end = new_end

    def lock_to_device(self, device):
        if device:
            self.device_locked = True
            if not device == self.device:
                self.bank = 0
                self.show_bank = True
            self.device = device
            self.parent.request_rebuild_midi_map()

    def unlock_from_device(self, device):
        if device and device == self.device:
            self.device_locked = False
        if hasattr(self.parent.song(), 'appointed_device'):
            if not self.parent.song().appointed_device == self_device:
                self.parent.request_rebuild_midi_map()

    def set_appointed_device(self, device):
        if self.device_locked:
            self.device_locked = False
        if not device == self.device:
            self.bank = 0
            self.show_bank = True
        self.device = device
        self.parent.request_rebuild_midi_map()

    def refresh_state(self):
        pass

    def update_display(self):
        pass

    def disconnect(self):
        self.parent.song().view.remove_selected_track_listener(self.on_track_selected_callback)
        self.parent.song().view.remove_detail_clip_listener(self.on_selected_clip)

    def on_device_selected(self):
        self.log('selected device %s' % self.selected_track.view.selected_device)
        self.set_appointed_device(self.selected_track.view.selected_device)

    def on_track_selected(self):
        if self.parent.is_live_5():
            self.log('add a listener to selected device on track %s' % self.parent.song().view.selected_track)
            self.selected_track = self.parent.song().view.selected_track
        self.parent.request_rebuild_midi_map()