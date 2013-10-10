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
#

import Live
import Nocturn
from NocturnComponent import NocturnComponent
from consts import *
class MixerController(NocturnComponent):
    __module__ = __name__
    __doc__ = "Control volume, panning, sends, mute, solo, channel bank, return and master section."
    
    def __init__(self, nocturn_parent):
        NocturnComponent.__init__(self, nocturn_parent)
        self._arm_enabled = True
        self.tracks = self.bank_tracks()
        self._add_listeners()

    def disconnect(self):
        self._remove_listeners()

    def _add_listeners(self):
        if (not self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
            self.song().add_visible_tracks_listener(self._on_visible_tracks_changed)
        if (not self.song().view.selected_track_has_listener(self._on_selected_track)):
            self.song().add_nudge_down_listener(self._on_nudge_down)
        if (not self.song().nudge_down_has_listener(self._on_nudge_down)):
            self.song().add_nudge_up_listener(self._on_nudge_up)
        if (not self.song().nudge_up_has_listener(self._on_nudge_up)):
            self.song().view.add_selected_track_listener(self._on_selected_track)
    
    def _remove_listeners(self):
        self._remove_track_listeners()
        if (self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
            self.song().remove_visible_tracks_listener(self._on_visible_tracks_changed)
        if (self.song().view.selected_track_has_listener(self._on_selected_track)):
            self.song().view.remove_selected_track_listener(self._on_selected_track)
        if (self.song().nudge_down_has_listener(self._on_nudge_down)):
            self.song().remove_nudge_down_listener(self._on_nudge_down)
        if (self.song().nudge_up_has_listener(self._on_nudge_up)):
            self.song().remove_nudge_up_listener(self._on_nudge_up)
    
    def _add_track_listeners(self):
        for t in self.tracks:
            if (t.can_be_armed and (not t.arm_has_listener(self._on_arm_changed))):
                t.add_arm_listener(self._on_arm_changed)
            if (not t.solo_has_listener(self._on_solo_changed)):
                t.add_solo_listener(self._on_solo_changed)
            if (not t.mute_has_listener(self._on_mute_changed)):
                t.add_mute_listener(self._on_mute_changed)
            if (not t.current_input_routing_has_listener(self._on_input_routing_changed)):
                t.add_current_input_routing_listener(self._on_input_routing_changed)
    
    def _remove_track_listeners(self):
        for t in self.tracks:
            if (t):
                if (t.can_be_armed and t.arm_has_listener(self._on_arm_changed)):
                    t.remove_arm_listener(self._on_arm_changed)
                if (t.mute_has_listener(self._on_mute_changed)):
                    t.remove_mute_listener(self._on_mute_changed)
                if (t.solo_has_listener(self._on_solo_changed)):
                    t.remove_solo_listener(self._on_solo_changed)
                if (t.current_input_routing_has_listener(self._on_input_routing_changed)):
                    t.remove_current_input_routing_listener(self._on_input_routing_changed)
    
    
    def receive_pitchbend(self, channel, pb_value):
        val = (pb_value-8192.0)/8192.0
        self.song().master_track.mixer_device.crossfader.value = val
    
    def receive_midi_cc(self, channel, cc_no, cc_value):
        if ((channel == MASTER_CH) and (cc_no == MASTER_BASE_CC+7)):
            if (cc_value < 64):
                self.song().tempo += 1
            else:
                self.song().tempo -= 1
    
    def receive_note(self, channel, note, velocity):
        if ((channel == ARM_CH) and (note >= ARM_BASE_NO) and (note < ARM_BASE_NO+NUM_STRIPS)):
            i = note-ARM_BASE_NO
            if (i < len(self.tracks)):
                t = self.tracks[i]
                if (self._arm_enabled):
                    arm = (velocity > 0)
                    self.arm_track(t, arm)
                    if (not t.can_be_armed):
                        self.send_midi((NOTE_ON_STATUS+ARM_CH, ARM_BASE_NO+i, 0))
                self.select_track(t)
            elif (velocity > 0):
                self.send_midi((NOTE_ON_STATUS+ARM_CH, ARM_BASE_NO+i, 0))
        elif ((channel == SOLO_CH) and (note >= SOLO_BASE_NO) and (note < SOLO_BASE_NO+NUM_STRIPS)):
            i = note-SOLO_BASE_NO;
            if (i < len(self.tracks)):
                solo = (velocity > 0)
                self.solo_track(self.tracks[i], solo)
            elif (velocity > 0):
                self.send_midi((NOTE_ON_STATUS+SOLO_CH, SOLO_BASE_NO+i, 0))
        elif ((channel == MUTE_CH) and (note >= MUTE_BASE_NO) and (note < MUTE_BASE_NO+NUM_STRIPS)):
            i = note-MUTE_BASE_NO;
            if (i < len(self.tracks)):
                mute = (velocity == 0)
                self.mute_track(self.tracks[i], mute)   
            elif (velocity > 0):
                self.send_midi((NOTE_ON_STATUS+MUTE_CH, MUTE_BASE_NO+i, 0))
        elif ((channel == BANK_CH) and (note >= BANK_BASE_NO) and (note < BANK_BASE_NO+NUM_STRIPS)):
            i = note-BANK_BASE_NO;
            if (i*NUM_STRIPS < len(self.song().visible_tracks)):
                self.set_track_bank(i)
                if (velocity == 0):
                    self.send_midi((NOTE_ON_STATUS+BANK_CH, BANK_BASE_NO+i, 127))
            else:
                self.send_midi((NOTE_ON_STATUS+BANK_CH, BANK_BASE_NO+i, 0))
        elif (channel == MASTER_CH):
            if ((note >= MASTER_BASE_NO) and (note < MASTER_BASE_NO+4)):
                i = note-MASTER_BASE_NO;
                if (i < len(self.song().return_tracks)):
                    mute = (velocity == 0)
                    self.mute_track(self.song().return_tracks[i], mute) 
                elif (velocity > 0):
                    self.send_midi((NOTE_ON_STATUS+MASTER_CH, MASTER_BASE_NO+i, 0))
            elif (note == MASTER_BASE_NO+4):
                self._arm_enabled = (velocity > 0)
            elif (note == MASTER_BASE_NO+5):
                self.song().nudge_down = (velocity > 0)
            elif (note == MASTER_BASE_NO+6):
                self.song().nudge_up = (velocity > 0)
            elif (note == MASTER_BASE_NO+7):
                self.song().tap_tempo()
                self.send_midi((NOTE_ON_STATUS+MASTER_CH,MASTER_BASE_NO+7,0))
        
    
    def select_track(self, track):
        if (not self._arm_enabled):
            for i in range(0,NUM_STRIPS):
                if ((i >= len(self.tracks)) or (track != self.tracks[i])):
                    self.send_midi((NOTE_ON_STATUS+ARM_CH,ARM_BASE_NO+i,0))
        track.view.select_instrument()
        self.song().view.selected_track = track
    
    def arm_track(self, track, arm):
        if (self.song().exclusive_arm):
            for t in self.tracks:
                if ((t.can_be_armed) and (t != track) and (t.arm)):
                    t.arm = False
        if ((track.can_be_armed) and (track.arm != arm)):
            track.arm = arm

    def mute_track(self, track, mute):
        if (track.mute != mute):
            track.mute = mute

    def solo_track(self, track, solo):
        if (self.song().exclusive_solo):
            for t in self.song().tracks:
                if ((t != track) and (t.solo)):
                    t.solo = 0
        if (track.solo != solo):
            track.solo = solo


    def build_midi_map(self, script_handle, midi_map_handle):
        self._remove_track_listeners()
        self.tracks = self.bank_tracks()
        self._add_track_listeners()

        map_mode = Live.MidiMap.MapMode.absolute
        num_sends = 0
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        feedback_rule.delay_in_ms = 0
        feedback_rule.cc_value_map = tuple()
        
        for index in range(0,NUM_STRIPS):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, ARM_CH, ARM_BASE_NO+index)
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, SOLO_CH, SOLO_BASE_NO+index)
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, MUTE_CH, MUTE_BASE_NO+index)
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, BANK_CH, BANK_BASE_NO+index)
            Live.MidiMap.forward_midi_pitchbend(script_handle, midi_map_handle, VOL_CH)
            if (DEV_CH != VOL_CH):
                Live.MidiMap.forward_midi_pitchbend(script_handle, midi_map_handle, DEV_CH)
            if ((SEND_CH != VOL_CH) and (SEND_CH != DEV_CH)):
                Live.MidiMap.forward_midi_pitchbend(script_handle, midi_map_handle, SEND_CH)
            if ((SCENE_CH != VOL_CH) and (SCENE_CH != DEV_CH) and (SCENE_CH != SEND_CH)):
                Live.MidiMap.forward_midi_pitchbend(script_handle, midi_map_handle, SCENE_CH)

            if (index < len(self.tracks)):
                t = self.tracks[index]
                feedback_rule.channel = VOL_CH
                feedback_rule.cc_no = VOL_BASE_CC+index
                self.map_parameter(midi_map_handle, t.mixer_device.volume, feedback_rule)
                feedback_rule.channel = PAN_CH
                feedback_rule.cc_no = PAN_BASE_CC+index;
                self.map_parameter(midi_map_handle, t.mixer_device.panning, feedback_rule)
                feedback_rule.channel = SEND_CH
                for send_index in range(0,4):
                    cc_no = SEND_BASE_CC+index+(send_index*NUM_STRIPS)
                    if (send_index < len(t.mixer_device.sends)):
                        feedback_rule.cc_no = cc_no
                        self.map_parameter(midi_map_handle, t.mixer_device.sends[send_index], feedback_rule)
                    else:
                        self.send_midi((CC_STATUS+SEND_CH,SEND_BASE_CC+index+(send_index*NUM_STRIPS),0))
            else:
                self.send_midi((CC_STATUS+VOL_CH,VOL_BASE_CC+index,0))          
                self.send_midi((CC_STATUS+PAN_CH,PAN_BASE_CC+index,64))         
                for i in range(0,num_sends):
                    self.send_midi((CC_STATUS+SEND_CH,SEND_BASE_CC+index+(i*NUM_STRIPS),0))
        
        feedback_rule.channel = MASTER_CH
        feedback_rule.cc_no = MASTER_BASE_CC
        for index in range(0,4):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, MASTER_CH, MASTER_BASE_NO+index)
            vel = 0
            if (index < len(self.song().return_tracks)):
                rtn_track = self.song().return_tracks[index]
                self.map_parameter(midi_map_handle, rtn_track.mixer_device.volume, feedback_rule)
                if (not rtn_track.mute):
                    vel = 127
            else:
                self.send_midi((CC_STATUS+MASTER_CH,MASTER_BASE_CC+index,0))
            self.send_midi((NOTE_ON_STATUS+MASTER_CH,MASTER_BASE_NO+index,vel))
            feedback_rule.cc_no += 1
        
        self.map_parameter(midi_map_handle, self.song().master_track.mixer_device.volume, feedback_rule)
        feedback_rule.cc_no += 1
        self.map_parameter(midi_map_handle, self.song().master_track.mixer_device.panning, feedback_rule)
        feedback_rule.cc_no += 1
        self.map_parameter(midi_map_handle, self.song().master_track.mixer_device.cue_volume, feedback_rule)
        Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, MASTER_CH, MASTER_BASE_CC+7)
        self.send_midi((CC_STATUS,MASTER_BASE_CC+7,64))
        for index in range(0,4):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, MASTER_CH, MASTER_BASE_NO+4+index)
        self.send_midi((NOTE_ON_STATUS,MASTER_BASE_NO+4,self._arm_enabled and 127))
        self._on_nudge_down()
        self._on_nudge_up()
        self.send_midi((NOTE_ON_STATUS,MASTER_BASE_NO+7,0))
        
        self.update_arm_buttons()
        self.update_solo_buttons()
        self.update_mute_buttons()
        self.update_bank_buttons()

    
    def update_arm_buttons(self):
        if (self._arm_enabled):
            for i in range(0,NUM_STRIPS):
                vel = 0
                if (i < len(self.tracks)):
                    t = self.tracks[i]
                    if (t and t.can_be_armed and t.arm):
                        vel = 127
                self.send_midi((NOTE_ON_STATUS+ARM_CH, ARM_BASE_NO+i, vel))
        else:
            for i in range(0,NUM_STRIPS):
                sel = ((i < len(self.tracks)) and (self.tracks[i] == self.song().view.selected_track))
                self.send_midi((NOTE_ON_STATUS+ARM_CH, ARM_BASE_NO+i, sel and 127))

    def update_solo_buttons(self):
        for i in range(0,NUM_STRIPS):
            solo = ((i < len(self.tracks)) and (self.tracks[i].solo))
            self.send_midi((NOTE_ON_STATUS+SOLO_CH, SOLO_BASE_NO+i, solo and 127))

    def update_mute_buttons(self):
        for i in range(0,NUM_STRIPS):
            on = ((i < len(self.tracks)) and (not self.tracks[i].mute))
            self.send_midi((NOTE_ON_STATUS+MUTE_CH, MUTE_BASE_NO+i, on and 127))

    def update_bank_buttons(self):
        for i in range(0,NUM_STRIPS):
            is_bank = (i == self.track_bank_index())
            self.send_midi((NOTE_ON_STATUS+BANK_CH, BANK_BASE_NO+i, is_bank and 127))
    
    
    def on_selected_track_bank(self):
        self.request_rebuild_midi_map()

    def _on_visible_tracks_changed(self):
        self.request_rebuild_midi_map()

    def _on_arm_changed(self):
        self.update_arm_buttons()

    def _on_solo_changed(self):
        self.update_solo_buttons()

    def _on_mute_changed(self):
        self.update_mute_buttons()
    
    def _on_bank_changed(self):
        self.update_bank_buttons()
        
    def _on_input_routing_changed(self):
        self._remove_track_listeners()
        self._add_track_listeners()
    
    def _on_nudge_down(self):
        state = (self.song().nudge_down)
        self.send_midi((NOTE_ON_STATUS,MASTER_BASE_NO+5,state and 127))

    def _on_nudge_up(self):
        state = (self.song().nudge_up)
        self.send_midi((NOTE_ON_STATUS,MASTER_BASE_NO+6,state and 127))

    def _on_selected_track(self):
        self.update_arm_buttons()


