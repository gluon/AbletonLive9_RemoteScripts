#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/LV2_LX2_LC2_LD2/FaderfoxMixerController.py
import Live
from ParamMap import ParamMap
from FaderfoxComponent import FaderfoxComponent
from consts import *

class FaderfoxMixerController(FaderfoxComponent):
    __module__ = __name__
    __doc__ = 'Mixer parameters of LX2'
    __filter_funcs__ = ['update_display', 'log']

    def __init__(self, parent):
        FaderfoxMixerController.realinit(self, parent)

    def realinit(self, parent):
        FaderfoxComponent.realinit(self, parent)
        self.on_track_selected_callback = lambda : self.on_track_selected()
        self.parent.song().view.add_selected_track_listener(self.on_track_selected_callback)
        self.track_selected = 0
        self.lv1_track_idx = -1

    def disconnect(self):
        self.parent.song().view.remove_selected_track_listener(self.on_track_selected_callback)

    def receive_midi_cc(self, channel, cc_no, cc_value):
        pass

    def handle_status_note(self, note_no, arr, attr):

        def index_of(list, elt):
            for i in range(0, len(list)):
                if list[i] == elt:
                    return i

        if note_no in arr:
            idx = index_of(arr, note_no)
            tracks = tuple(self.parent.song().tracks) + tuple(self.parent.song().return_tracks)
            if len(tracks) > idx:
                track = tracks[idx]
                if attr == 'solo':
                    self.helper.solo_track(track)
                elif attr == 'arm':
                    self.helper.arm_track(track)
                elif attr == 'monitor':
                    self.helper.switch_monitor_track(track)
                elif attr == 'cross_ab':
                    self.helper.switch_crossfader_ab(track)
                else:
                    self.helper.toggle_track_attribute(track, attr)

    def receive_midi_note(self, channel, status, note_no, note_vel):
        if status == NOTEOFF_STATUS:
            return
        if channel == CHANNEL_SETUP2:
            self.log('received note %s' % note_no)
        if channel == CHANNEL_SETUP2 and note_no in TRACK_SELECT_NOTES:
            idx = note_no - TRACK_SELECT_NOTES[0]
            self.lv1_track_idx = note_no
            tracks = tuple(self.parent.song().tracks) + tuple(self.parent.song().return_tracks)
            if idx < len(tracks):
                track = tracks[idx]
            elif self.helper.is_master_track_selected():
                track = tracks[-1]
            else:
                track = self.parent.song().master_track
            self.set_selected_track(track)
        if channel == CHANNEL_SETUP2 and note_no == MASTER_TRACK_SELECT_NOTE:
            self.lv1_track_idx = note_no
            self.log('select master track')
            self.set_selected_track(self.parent.song().master_track)
        if channel == TRACK_CHANNEL_SETUP2 and status == NOTEON_STATUS:
            self.handle_status_note(note_no, MUTE_NOTES, 'mute')
            self.handle_status_note(note_no, ARM_NOTES, 'arm')
            self.handle_status_note(note_no, SOLO_NOTES, 'solo')
            self.handle_status_note(note_no, MONITOR_NOTES, 'monitor')
            self.handle_status_note(note_no, CROSS_AB_NOTES, 'cross_ab')

    def set_selected_track(self, track):
        if track and self.track_selected and not self.parent.song().view.selected_track == track:
            self.track_selected = 0
            self.parent.song().view.selected_track = track

    def build_midi_map(self, script_handle, midi_map_handle):

        def forward_note(chan, note):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, chan, note)

        def forward_cc(chan, cc):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, chan, cc)

        idx = 0
        self.map_track_params(script_handle, midi_map_handle)
        for note in TRACK_SELECT_NOTES:
            forward_note(CHANNEL_SETUP2, note)

        forward_note(CHANNEL_SETUP2, MASTER_TRACK_SELECT_NOTE)
        for note in MUTE_NOTES:
            forward_note(TRACK_CHANNEL_SETUP2, note)

        for note in SOLO_NOTES:
            forward_note(TRACK_CHANNEL_SETUP2, note)

        for note in ARM_NOTES:
            forward_note(TRACK_CHANNEL_SETUP2, note)

        for note in MONITOR_NOTES:
            forward_note(TRACK_CHANNEL_SETUP2, note)

        for note in CROSS_AB_NOTES:
            forward_note(TRACK_CHANNEL_SETUP2, note)

        self.on_track_selected()

    def refresh_state(self):
        pass

    def update_display(self):
        pass

    def on_track_selected(self):
        self.track_selected = 1
        if self.helper.is_master_track_selected():
            if self.lv1_track_idx == MASTER_TRACK_SELECT_NOTE:
                return
            self.lv1_track_idx = MASTER_TRACK_SELECT_NOTE
            self.parent.send_midi((175, 16, 16))
            if self.parent.is_live_5():
                self.parent.send_midi((NOTEON_STATUS + CHANNEL_SETUP2, MASTER_TRACK_SELECT_NOTE, 64))
        else:
            idx = self.helper.selected_track_idx()
            if idx < 16:
                note_no = TRACK_SELECT_NOTES[0] + idx
                if self.lv1_track_idx == note_no:
                    return
                self.lv1_track_idx = note_no
                self.parent.send_midi((175, 16, self.helper.selected_track_idx()))
                if self.parent.is_live_5():
                    self.log('send track note %s' % TRACK_SELECT_NOTES[self.helper.selected_track_idx()])
                    self.parent.send_midi((NOTEON_STATUS + CHANNEL_SETUP2, TRACK_SELECT_NOTES[self.helper.selected_track_idx()], 64))

    def map_track_params(self, script_handle, midi_map_handle):
        for idx in range(0, 16):
            tracks = tuple(self.parent.song().tracks) + tuple(self.parent.song().return_tracks)
            if len(tracks) > idx:
                track = tracks[idx]
                mixer_device = track.mixer_device
                parameter = mixer_device.volume
                ParamMap.map_with_feedback(midi_map_handle, CHANNEL_SETUP2, VOLUME_CCS[idx], parameter, Live.MidiMap.MapMode.absolute)
                sends = mixer_device.sends
                for send_idx in range(0, 4):
                    if len(sends) > send_idx:
                        parameter = sends[send_idx]
                        ParamMap.map_with_feedback(midi_map_handle, TRACK_CHANNEL_SETUP2, SEND_CCS[idx][send_idx], parameter, Live.MidiMap.MapMode.absolute)

                parameter = mixer_device.panning
                ParamMap.map_with_feedback(midi_map_handle, TRACK_CHANNEL_SETUP2, PAN_X_CC[idx], parameter, Live.MidiMap.MapMode.absolute)

        track = self.parent.song().master_track
        parameter = track.mixer_device.panning
        ParamMap.map_with_feedback(midi_map_handle, TRACK_CHANNEL_SETUP2, PAN_X_MASTER_CC, parameter, Live.MidiMap.MapMode.absolute)
        parameter = track.mixer_device.volume
        cc = MAIN_VOLUME_CC
        if self.parent.is_lv1:
            cc = LV1_MAIN_VOLUME_CC
        ParamMap.map_with_feedback(midi_map_handle, CHANNEL_SETUP2, cc, parameter, Live.MidiMap.MapMode.absolute)
        if hasattr(track.mixer_device, 'cue_volume'):
            parameter = track.mixer_device.cue_volume
            cc = CUE_VOLUME_CC
            if self.parent.is_lv1:
                cc = LV1_CUE_VOLUME_CC
            ParamMap.map_with_feedback(midi_map_handle, CHANNEL_SETUP2, cc, parameter, Live.MidiMap.MapMode.absolute)
        if hasattr(track.mixer_device, 'crossfader'):
            parameter = track.mixer_device.crossfader
            cc = CROSSFADER_CC
            ParamMap.map_with_feedback(midi_map_handle, CHANNEL_SETUP2, cc, parameter, Live.MidiMap.MapMode.absolute)
            if self.parent.is_lv1:
                cc = LV1_CROSSFADER_CC
                ParamMap.map_with_feedback(midi_map_handle, CHANNEL_SETUP2, cc, parameter, Live.MidiMap.MapMode.absolute)