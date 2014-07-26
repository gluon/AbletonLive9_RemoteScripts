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

class Pads:
    __module__ = __name__
    __doc__ = ' Class representing the bottom row of buttons on the NanoKontrol '

    def __init__(self, parent):
        self._Pads__parent = parent
        self._Pads__mod_pressed = False
        self._Pads__view = 0

    def tuple_idx(self, tuple, obj):
        for i in xrange(0,len(tuple)):
            if (tuple[i] == obj):
                return i

    def tracks(self):
        tracks = list(self._Pads__parent.song().visible_tracks + self._Pads__parent.song().return_tracks)
        tracks.append(self._Pads__parent.song().master_track)

        return tracks

    def track_idx(self, track):
        return self.tuple_idx(self.tracks(), track)

    def track_right(self, size = 1):
        tid = self.track_idx(self._Pads__parent.song().view.selected_track)

        if len(self.tracks()) > tid + size:
            self._Pads__parent.song().view.selected_track = self.tracks()[tid + size]
        else:
            self._Pads__parent.song().view.selected_track = self.tracks()[-1]

    def track_left(self, size = 1):
        tid = self.track_idx(self._Pads__parent.song().view.selected_track)

        if tid - size > 0:
            self._Pads__parent.song().view.selected_track = self.tracks()[tid - size]
        else:
            self._Pads__parent.song().view.selected_track = self.tracks()[0]


    def build_midi_map(self, script_handle, midi_map_handle):
        for channel in range(4):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, NANOKONTROL_PAD9)
            for pad in range(8):
                Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, NANOKONTROL_PADS[pad])


        for pad in range(9):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 15, NANOKONTROL_PADS[pad])




    def receive_midi_cc(self, cc_no, cc_value, channel):
        if (list(NANOKONTROL_PADS).count(cc_no) > 0):
            pad_index = list(NANOKONTROL_PADS).index(cc_no)
            if (cc_no == NANOKONTROL_PAD9):
                self._Pads__mod_pressed = (cc_value == 127)
            elif (cc_value > 0):
                index = (pad_index + (channel * 8))
                if (channel in range(4)):
                    if self._Pads__parent.application().view.is_view_visible('Session'):
                        if (len(self._Pads__parent.song().tracks) > index):
                            current_track = self._Pads__parent.song().tracks[index]
                            clip_index = list(self._Pads__parent.song().scenes).index(self._Pads__parent.song().view.selected_scene)
                            if (not self._Pads__mod_pressed):
                                current_track.clip_slots[clip_index].fire()
                            elif self._Pads__mod_pressed:
                                track = self._Pads__parent.song().tracks[index]
                                track.solo = (not track.solo)
                    elif self._Pads__parent.application().view.is_view_visible('Arranger'):
                        if (len(self._Pads__parent.song().cue_points) > index):
                            self._Pads__parent.song().cue_points[index].jump()
                elif (channel == 15):
                    if (cc_no == NANOKONTROL_PAD1):
                        self.track_left()
                        
                    elif (cc_no == NANOKONTROL_PAD2):
                        self.track_right()

                    elif (cc_no == NANOKONTROL_PAD3):
                        track = self._Pads__parent.song().view.selected_track
                        did   = self.tuple_idx(track.devices, track.view.selected_device)

                        if did > 0:
                            self._Pads__parent.song().view.select_device(track.devices[did - 1])

                    elif (cc_no == NANOKONTROL_PAD4):
                        track = self._Pads__parent.song().view.selected_track
                        did   = self.tuple_idx(track.devices, track.view.selected_device)

                        if len(track.devices) > did + 1:
                            self._Pads__parent.song().view.select_device(track.devices[did + 1])

                    elif (cc_no == NANOKONTROL_PAD5):
                        if (not self._Pads__mod_pressed):
                            self._Pads__parent.bank_changed(pad_index - 4)
                        elif (cc_value > 0):
                            self._Pads__parent.bank_changed(pad_index - 2)
                    
                    elif (cc_no == NANOKONTROL_PAD6):
                        if (not self._Pads__mod_pressed):
                            self._Pads__parent.bank_changed(pad_index - 4)
                        elif (cc_value > 0):
                            self._Pads__parent.bank_changed(pad_index - 2)

                    elif (cc_no == NANOKONTROL_PAD7):
                        track = self._Pads__parent.song().view.selected_track
                        device = track.view.selected_device

                        if device != None:
                            if device.parameters[0].value == 1:
                                device.parameters[0].value = 0
                            else:
                                device.parameters[0].value = 1

                    elif (cc_no == NANOKONTROL_PAD8):
                        if self._Pads__view == 1:
                            Live.Application.get_application().view.show_view("Detail/Clip")
                            self._Pads__view = 0
                        else:
                            Live.Application.get_application().view.show_view("Detail/DeviceChain")
                            self._Pads__view = 1
                                
