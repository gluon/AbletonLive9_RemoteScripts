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
# Revision 2009-10-12:
#    Transport controls added.
#    Free buttons of User section (last page) now stop all clips.
#

import Live
from consts import *
from NocturnComponent import NocturnComponent
class PlayingController(NocturnComponent):
    __module__ = __name__
    __doc__ = "Buttons that show when a track is playing a clip."
    
    def __init__(self, nocturn_parent):
        NocturnComponent.__init__(self, nocturn_parent)
        self._refresh_count = 0
        self.playing_slots = list()
        self._add_listeners()

    def disconnect(self):
        self._remove_listeners()

    
    def _add_listeners(self):
        if (not self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
            self.song().add_visible_tracks_listener(self._on_visible_tracks_changed)
        if (not self.song().view.selected_scene_has_listener(self._on_selected_scene)):
            self.song().view.add_selected_scene_listener(self._on_selected_scene)
        if (not self.song().metronome_has_listener(self._on_metronome)):
            self.song().add_metronome_listener(self._on_metronome)
        if (not self.song().is_playing_has_listener(self._on_is_playing)):
            self.song().add_is_playing_listener(self._on_is_playing)
        if (not self.song().record_mode_has_listener(self._on_record_mode)):
            self.song().add_record_mode_listener(self._on_record_mode)
        if (not self.song().overdub_has_listener(self._on_overdub)):
            self.song().add_overdub_listener(self._on_overdub)
        if (not self.song().punch_in_has_listener(self._on_punch_in)):
            self.song().add_punch_in_listener(self._on_punch_in)
        if (not self.song().loop_has_listener(self._on_loop)):
            self.song().add_loop_listener(self._on_loop)
        if (not self.song().punch_out_has_listener(self._on_punch_out)):
            self.song().add_punch_out_listener(self._on_punch_out)
        
    def _remove_listeners(self):
        self._remove_clip_listeners()
        if (self.song().view.selected_scene_has_listener(self._on_selected_scene)):
            self.song().view.remove_selected_scene_listener(self._on_selected_scene)
        if (self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
            self.song().remove_visible_tracks_listener(self._on_visible_tracks_changed)
        if (self.song().metronome_has_listener(self._on_metronome)):
            self.song().remove_metronome_listener(self._on_metronome)
        if (self.song().is_playing_has_listener(self._on_is_playing)):
            self.song().remove_is_playing_listener(self._on_is_playing)
        if (self.song().record_mode_has_listener(self._on_record_mode)):
            self.song().remove_record_mode_listener(self._on_record_mode)
        if (self.song().overdub_has_listener(self._on_overdub)):
            self.song().remove_overdub_listener(self._on_overdub)
        if (self.song().punch_in_has_listener(self._on_punch_in)):
            self.song().remove_punch_in_listener(self._on_punch_in)
        if (self.song().loop_has_listener(self._on_loop)):
            self.song().remove_loop_listener(self._on_loop)
        if (self.song().punch_out_has_listener(self._on_punch_out)):
            self.song().remove_punch_out_listener(self._on_punch_out)
    
    def _add_clip_listeners(self):
        for slot in self.playing_slots:
            if (not slot.has_clip_has_listener(self._on_has_clip)):
                slot.add_has_clip_listener(self._on_has_clip)
            if (slot.has_clip):
                if (not slot.clip.playing_status_has_listener(self._on_playing_status)):
                    slot.clip.add_playing_status_listener(self._on_playing_status)
            else:
                if (not slot.playing_status_has_listener(self._on_playing_status)):
                    slot.add_playing_status_listener(self._on_playing_status)

    def _remove_clip_listeners(self):
        for slot in self.playing_slots:
            if (slot):
                if (slot.has_clip_has_listener(self._on_has_clip)):
                    slot.remove_has_clip_listener(self._on_has_clip)
                if (slot.has_clip):
                    if (slot.clip.playing_status_has_listener(self._on_playing_status)):
                        slot.clip.remove_playing_status_listener(self._on_playing_status)
                else:
                    if (slot.playing_status_has_listener(self._on_playing_status)):
                        slot.remove_playing_status_listener(self._on_playing_status)

    def _setup_playing_clips(self):
        self._remove_clip_listeners()
        self.playing_slots = self.bank_clip_slots()
        tracks = self.bank_tracks()
        for i in range(0,len(self.playing_slots)):
            for s in tracks[i].clip_slots:
                if ((s.playing_status > 0) or (s.has_clip and s.clip.is_playing)):
                    self.playing_slots[i] = s
        self._add_clip_listeners()
        
    
    def build_midi_map(self, script_handle, midi_map_handle):
        self._setup_playing_clips()
        for index in range(0,NUM_STRIPS):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, PLAYING_CH, PLAYING_BASE_NO+index)
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, TRANSPORT_CH, TRANSPORT_BASE_NO+index)
        self.update_metronome()
        self.update_is_playing()
        self.update_record_mode()
        self.update_overdub()
        self.update_punch_in()
        self.update_loop()
        self.update_punch_out()
        self.update_playing_buttons()

    
    def receive_note(self, channel, note, vel):
        if (channel == PLAYING_CH):
            index = note-PLAYING_BASE_NO
            if ((index >= 0) and (index < NUM_STRIPS)):
                vel = 0
                if (index < len(self.playing_slots)):
                    slot = self.playing_slots[index]
                    playing = (((slot.has_clip) and (slot.clip.is_playing)) or (slot.playing_status > 0))
                    if (playing):
                        slot.stop()
                        vel = 127
                    else:
                        slot.fire()
                else:
                    self.song().master_track.stop_all_clips()
                self.send_midi((NOTE_ON_STATUS+PLAYING_CH, note, vel))
        if (channel == TRANSPORT_CH):
            index = note-TRANSPORT_BASE_NO
            if ((index >= 0) and (index < NUM_STRIPS)):
                if (index == 0):
                    self.song().metronome = vel and True
                elif (index == 1):
                    self.song().start_playing()
                    if (vel == 0):
                        self.update_is_playing()
                elif (index == 2):
                    self.song().stop_playing()
                elif (index == 3):
                    self.song().record_mode = vel and True
                elif (index == 4):
                    self.song().overdub = vel and True
                elif (index == 5):
                    self.song().punch_in = vel and True
                elif (index == 6):
                    self.song().loop = vel and True
                elif (index == 7):
                    self.song().punch_out = vel and True

    def update_display(self):
        self._refresh_count += 1
        tracks = self.bank_tracks()
        for index in range(0,len(self.playing_slots)):
            track = tracks[index]
            if (track.fired_slot_index != -1):
                vel = 0
                if (self._refresh_count&3 == 0):
                    self._refresh_count = 0
                    self.send_midi((NOTE_ON_STATUS+PLAYING_CH, PLAYING_BASE_NO+index, 127))
                elif (self._refresh_count&1 == 0):
                    self.send_midi((NOTE_ON_STATUS+PLAYING_CH, PLAYING_BASE_NO+index, 0))
    
    def update_playing_buttons(self):
        for index in range(0,NUM_STRIPS):
            state = False
            if (index < len(self.playing_slots)):
                slot = self.playing_slots[index]
                state = (((slot.has_clip) and (slot.clip.is_playing)) or (slot.playing_status > 0))
            self.send_midi((NOTE_ON_STATUS+PLAYING_CH, PLAYING_BASE_NO+index, state and 127))
    
    def _on_visible_tracks_changed(self):
        self._setup_playing_clips()
        self.update_playing_buttons()
 
    def on_selected_track_bank(self):
        self._setup_playing_clips()
        self.update_playing_buttons()

    def _on_selected_scene(self):
        self._setup_playing_clips()
            
    def _on_playing_status(self):
        self._setup_playing_clips()
        self.update_playing_buttons()
    
    def _on_has_clip(self):
        self._remove_clip_listeners()
        self._add_clip_listeners()
        
    def update_metronome(self):
        state = self.song().metronome
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO, state and 127))

    def update_is_playing(self):
        state = self.song().is_playing
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO+1, state and 127))

    def update_record_mode(self):
        state = self.song().record_mode
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO+3, state and 127))

    def update_overdub(self):
        state = self.song().overdub
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO+4, state and 127))

    def update_punch_in(self):
        state = self.song().punch_in
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO+5, state and 127))

    def update_loop(self):
        state = self.song().loop
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO+6, state and 127))

    def update_punch_out(self):
        state = self.song().punch_out
        self.send_midi((NOTE_ON_STATUS+TRANSPORT_CH, TRANSPORT_BASE_NO+7, state and 127))
        
    def _on_metronome(self):
        self.update_metronome()

    def _on_is_playing(self):
        self.update_is_playing()

    def _on_record_mode(self):
        self.update_record_mode()

    def _on_overdub(self):
        self.update_overdub()

    def _on_punch_in(self):
        self.update_punch_in()
        
    def _on_loop(self):
        self.update_loop()

    def _on_punch_out(self):
        self.update_punch_out()
