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
# Revision 2009-10-14:
#    Loop control improvements, Guillermo R. Troyano
# Revision 2009-10-18:
#    Now it transports MIDI clips, Guillermo R. Troyano
#

import Live
from consts import *
from NocturnComponent import NocturnComponent
class SceneController(NocturnComponent):
    __module__ = __name__
    __doc__ = "Buttons show the playing state of a scene, encoders control scene, track and clip parameters."
    
    def __init__(self, nocturn_parent):
        NocturnComponent.__init__(self, nocturn_parent)
        self._scene_sel_count = 0
        self._track_sel_count = 0
        self._quant_sel_count = 0
        self._refresh_count = 0
        self.scene_slots = self.bank_clip_slots()
        beat = 4.0
        triplet = beat*4.0/3.0
        self._quant_values = [ beat/64.0,
            beat*8, beat*4, beat*2, beat,
            beat/2, triplet/2,
            beat/4, triplet/4.0,
            beat/8.0, triplet/8.0,
            beat/16.0, triplet/16.0,
            beat/32.0 ]
        self._add_listeners()

    def disconnect(self):
        self._remove_listeners()

    
    def _add_listeners(self):
        if (not self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
            self.song().add_visible_tracks_listener(self._on_visible_tracks_changed)
        if (not self.song().view.selected_scene_has_listener(self._on_selected_scene)):
            self.song().view.add_selected_scene_listener(self._on_selected_scene)
    
    def _remove_listeners(self):
        self._remove_clip_listeners()
        if (self.song().view.selected_scene_has_listener(self._on_selected_scene)):
            self.song().view.remove_selected_scene_listener(self._on_selected_scene)
        if (self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
            self.song().remove_visible_tracks_listener(self._on_visible_tracks_changed)
    
    def _add_clip_listeners(self):
        for slot in self.scene_slots:
            if (not slot.has_clip_has_listener(self._on_has_clip)):
                slot.add_has_clip_listener(self._on_has_clip)
            if (slot.has_clip):
                if (not slot.clip.playing_status_has_listener(self._on_playing_status)):
                    slot.clip.add_playing_status_listener(self._on_playing_status)
            else:
                if (not slot.playing_status_has_listener(self._on_playing_status)):
                    slot.add_playing_status_listener(self._on_playing_status)

    def _remove_clip_listeners(self):
        for slot in self.scene_slots:
            if (slot):
                if (slot.has_clip_has_listener(self._on_has_clip)):
                    slot.remove_has_clip_listener(self._on_has_clip)
                if (slot.has_clip):
                    if (slot.clip.playing_status_has_listener(self._on_playing_status)):
                        slot.clip.remove_playing_status_listener(self._on_playing_status)
                else:
                    if (slot.playing_status_has_listener(self._on_playing_status)):
                        slot.remove_playing_status_listener(self._on_playing_status)

    def setup_clip_slots(self):
        self._remove_clip_listeners()
        self.scene_slots = self.bank_clip_slots()
        self._add_clip_listeners()
    
    
    def build_midi_map(self, script_handle, midi_map_handle):
        self.setup_clip_slots()
        for index in range(0,NUM_STRIPS):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, SCENE_CH, SCENE_BASE_NO+index)
        for index in range(0,NUM_STRIPS):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, SCENE_CH, SCENE_BASE_CC+index)
            self.send_midi((CC_STATUS+SCENE_CH,SCENE_BASE_CC+index,64))
        self.update_fire_buttons()

    
    def receive_midi_cc(self, channel, cc_no, cc_value):
        if (channel == SCENE_CH):
            if (cc_no == SCENE_BASE_CC):
                self._scene_sel_count += 1
                if (self._scene_sel_count >= 4):
                    index = list(self.song().scenes).index(self.song().view.selected_scene)
                    if (cc_value < 64):
                        index += 1
                    else:
                        index -= 1
                    index = max(0,min(index,len(self.song().scenes)-1))
                    self.song().view.selected_scene = self.song().scenes[index]             
                    self._scene_sel_count = 0
            elif (cc_no == SCENE_BASE_CC+1):
                self._track_sel_count += 1
                if (self._track_sel_count >= 4):
                    tracks = list(self.song().visible_tracks)
                    returns = self.song().return_tracks
                    if (len(returns) > 0):
                        tracks.extend(returns)
                    tracks.append(self.song().master_track)
                    index = tracks.index(self.song().view.selected_track)
                    if (cc_value < 64):
                        index += 1
                    else:
                        index -= 1
                    index = max(0,min(index,len(tracks)-1))
                    detail_clip = self.application().view.is_view_visible('Detail/Clip')
                    self.song().view.selected_track = tracks[index]             
                    self.song().view.selected_track.view.select_instrument()
                    if (detail_clip):
                        self.application().view.show_view('Detail/Clip')
                    self._track_sel_count = 0
            elif (cc_no == SCENE_BASE_CC+2):
                self._quant_sel_count += 1
                if (self._quant_sel_count >= 4):
                    quant = self.song().clip_trigger_quantization
                    index = list(quant.values).index(quant)
                    if (cc_value < 64):
                        index += 1
                    else:
                        index -= 1
                    index = max(0,min(index,len(quant.values)-1))
                    self.song().clip_trigger_quantization = quant.values[index]
                    self._quant_sel_count = 0
            elif (cc_no == SCENE_BASE_CC+3):
                step = self.quantization_step()
                if (cc_value < 64):
                    self.song().scrub_by(step)
                else:
                    self.song().scrub_by(-step)
            elif (cc_no == SCENE_BASE_CC+4):
                clip = self.song().view.detail_clip
                if (clip):
                    step = self.quantization_step()
                    if (cc_value < 64):
                        clip.move_playing_pos(step)
                    else:
                        clip.move_playing_pos(-step)
            elif (cc_no == SCENE_BASE_CC+5):
                clip = self.song().view.detail_clip
                step = self.quantization_step()
                if (clip):
                    div,mod = divmod(clip.loop_start, step)
                    if (cc_value < 64):
                        clip.loop_end += step-mod
                        clip.loop_start += step-mod
                    elif (mod):
                        clip.loop_start -= mod
                        clip.loop_end -= mod
                    elif (div > 0):
                        clip.loop_start -= step
                        clip.loop_end -= step
                else:
                    div,mod = divmod(self.song().loop_start, step)
                    if (cc_value < 64):
                        self.song().loop_start += step-mod
                    elif (mod):
                        self.song().loop_start -= mod
                    elif (div > 0):
                        self.song().loop_start -= step
            elif (cc_no == SCENE_BASE_CC+6):
                clip = self.song().view.detail_clip
                step = self.quantization_step()
                if (clip):
                    div,mod = divmod(clip.loop_end-clip.loop_start, step)
                    if ((cc_value < 64) or (div < 1)):
                        clip.loop_end += step-mod
                    elif (mod):
                        clip.loop_end -= mod
                    elif (div > 1):
                        clip.loop_end -= step
                else:
                    div,mod = divmod(self.song().loop_length, step)
                    if ((cc_value < 64) or (div < 1)):
                        self.song().loop_length += step-mod
                    elif (mod):
                        self.song().loop_length -= mod
                    elif (div > 1):
                        self.song().loop_length -= step
            elif (cc_no == SCENE_BASE_CC+7):
                clip = self.song().view.detail_clip
                if (clip):
                    if (clip.is_audio_clip):
                        if ((cc_value < 64) and (clip.pitch_coarse < 48)):
                            clip.pitch_coarse += 1
                        elif (clip.pitch_coarse > -48):
                            clip.pitch_coarse -= 1
                    else:
                        trans = 1
                        if (cc_value >= 64):
                            trans = -1
                        notes = clip.get_selected_notes()
                        if (len(notes) > 0):
                            notes = self.transpose_notes(notes, trans)
                            if (len(notes) > 0):
                                clip.replace_selected_notes(notes)
                        else:
                            notes = clip.select_all_notes()
                            notes = clip.get_selected_notes()
                            notes = self.transpose_notes(notes, trans)
                            if (len(notes) > 0):
                                clip.replace_selected_notes(notes)
                            clip.deselect_all_notes()
    
    def transpose_notes(self, selection, trans):
        notes = list()
        for note in selection:
            pitch = note[0]+trans
            if ((pitch > 127) or (pitch < 0)):
                return ()
            else:
                notes.append((pitch, note[1], note[2], note[3], note[4]))
        return tuple(notes)
    
    def quantization_step(self):
        index = int(self.song().clip_trigger_quantization)
        step = self._quant_values[index]
        step *= float(self.song().signature_numerator)/self.song().signature_denominator
        return step
    
    def receive_note(self, channel, note, vel):
        if (channel == SCENE_CH):
            index = note-SCENE_BASE_NO
            vel = 0
            if (index < len(self.scene_slots)):
                slot = self.scene_slots[index]
                playing = (((slot.has_clip) and (slot.clip.is_playing)) or (slot.playing_status > 0))
                if (playing):
                    slot.stop()
                    vel = 127
                else:
                    slot.fire()
            elif (index < NUM_STRIPS):
                self.song().view.selected_scene.fire()
            self.send_midi((NOTE_ON_STATUS+SCENE_CH, note, vel)) 
    

    def update_display(self):
        self._refresh_count += 1
        num_slots = len(self.scene_slots)
        for index in range(0,num_slots):
            slot = self.scene_slots[index]
            track = self.bank_tracks()[index]
            if ((slot.is_triggered) or (track.fired_slot_index == -2)):
                vel = 0
                if (self._refresh_count&3 == 0):
                    self._refresh_count = 0
                    self.send_midi((NOTE_ON_STATUS+SCENE_CH, SCENE_BASE_NO+index, 127))
                elif (self._refresh_count&1 == 0):
                    self.send_midi((NOTE_ON_STATUS+SCENE_CH, SCENE_BASE_NO+index, 0))
    
    def update_fire_buttons(self):
        for index in range(0,NUM_STRIPS):
            state = False
            if (index < len(self.scene_slots)):
                slot = self.scene_slots[index]
                state = (((slot.has_clip) and (slot.clip.is_playing)) or (slot.playing_status > 0))
            self.send_midi((NOTE_ON_STATUS+SCENE_CH, SCENE_BASE_NO+index, state and 127))

    def on_selected_track_bank(self):
        self.setup_clip_slots()
        self.update_fire_buttons()

    def _on_selected_scene(self):
        self.setup_clip_slots()
        self.update_fire_buttons()
            
    def _on_playing_status(self):
        self.update_fire_buttons()
    
    def _on_has_clip(self):
        self.setup_clip_slots()
        self.update_fire_buttons()
        
    def _on_visible_tracks_changed(self):
        self.setup_clip_slots()
        self.update_fire_buttons()
