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
from consts import *
class NocturnComponent:
    __module__ = __name__
    __doc__ = "Base class for a component."
    
    def __init__(self, nocturn_parent):
        self._parent = nocturn_parent

    def disconnect(self):
        pass

    def parent(self):
        return self._parent
    
    def application(self):
        return self._parent.application()

    def song(self):
        return self._parent.song()
        
    def show_message(self, message):
        self._parent.show_message(message)
        
    def log(self, message):
        self._parent.log(message)

    def request_rebuild_midi_map(self):
        self._parent.request_rebuild_midi_map()
    
    def refresh_state(self):
        pass

    def update_display(self):
        pass

    def send_midi(self, midi_event_bytes):
        self._parent.send_midi(midi_event_bytes)

    
    def track_bank_index(self):
        return self._parent.track_bank_index()
    
    def bank_tracks(self):
        return self._parent.bank_tracks()
    
    def bank_clip_slots(self):
        return self._parent.bank_clip_slots()
    
    def set_track_bank(self, index):
        self._parent.set_track_bank(index)
    
    def map_parameter(self, midi_map_handle, parameter, feedback_rule):
        Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, feedback_rule.channel, feedback_rule.cc_no, Live.MidiMap.MapMode.absolute, feedback_rule, False)
        Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter)


    def receive_pitchbend(self, channel, pb_value):
        pass
    
    def receive_midi_cc(self, channel, cc_no, cc_value):
        pass
        
    def receive_note(self, channel, note, velocity):
        pass        
    
    def build_midi_map(self, script_handle, midi_map_handle):
        pass
        
    def on_selected_track_bank(self):
        pass
