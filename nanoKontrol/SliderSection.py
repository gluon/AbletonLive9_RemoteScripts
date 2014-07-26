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
import MidiMap
from consts import *

class SliderSection:
    __module__ = __name__
    __doc__ = ' Class representing the sliders on the NanoKontrol  '

    def __init__(self, parent):
        self._SliderSection__parent = parent
        self._SliderSection__mod_pressed = False



    def build_midi_map(self, script_handle, midi_map_handle):
        feedback_rule = MidiMap.CCFeedbackRule()
        feedback_rule.channel = 0
        feedback_rule.cc_no = NANOKONTROL_SLI9
        feedback_rule.cc_value_map = tuple()
        feedback_rule.delay_in_ms = -1.0
        for channel in range(16):
            MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self._SliderSection__parent.song().master_track.mixer_device.volume, channel, NANOKONTROL_SLI9, MidiMap.MapMode.absolute_14_bit, feedback_rule, 1)

        for channel in range(4):
            MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, NANOKONTROL_BUT9)
            for slider in range(8):
                track_index = (slider + (channel * 8))
                if (len(self._SliderSection__parent.song().tracks) > track_index):
                    feedback_rule.channel = 0
                    feedback_rule.cc_no = NANOKONTROL_SLIDERS[slider]
                    feedback_rule.cc_value_map = tuple()
                    feedback_rule.delay_in_ms = -1.0
                    MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self._SliderSection__parent.song().tracks[track_index].mixer_device.volume, channel, NANOKONTROL_SLIDERS[slider], MidiMap.MapMode.absolute_14_bit, feedback_rule, 1)
                    MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, NANOKONTROL_BUTTONS[slider])
                else:
                    break

        for button in range(8):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 15, NANOKONTROL_BUTTONS[button])

        for slider in range(8):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 15, NANOKONTROL_SLIDERS[slider])


    def receive_midi_cc(self, cc_no, cc_value, channel):
        if (list(NANOKONTROL_BUTTONS).count(cc_no) > 0):
            button_index = list(NANOKONTROL_BUTTONS).index(cc_no)
            if (cc_no == NANOKONTROL_BUT9):
                self._SliderSection__mod_pressed = (cc_value == 127)
            elif (button_index in range(8)) and (not channel == 15):
                track_index = (button_index + (8 * channel))
                if (len(self._SliderSection__parent.song().tracks) > track_index):
                    track = self._SliderSection__parent.song().tracks[track_index]
                    if (track):
                        if self._SliderSection__mod_pressed:
                            track.mute = (not track.mute)
                        elif track.can_be_armed:
                            track.arm = (not track.arm)
                            if self._SliderSection__parent.song().exclusive_arm:
                                for t in self._SliderSection__parent.song().tracks:
                                    if (t.can_be_armed and (t.arm and (not (t == track)))):
                                        t.arm = False

                            if track.arm:
                                if track.view.select_instrument():
                                    self._SliderSection__parent.song().view.selected_track = track

            elif (channel == 15):
                track_index = (button_index + (8 * 0))
                track = self._SliderSection__parent.song().tracks[track_index]
                self._SliderSection__parent.song().view.selected_track = track

        '''elif (channel == 15):
            slider_index = list(NANOKONTROL_SLIDERS).index(cc_no)
            track_index = (slider_index + (8 * 0))
            track = self._SliderSection__parent.song().tracks[track_index]
            self._SliderSection__parent.song().tracks[track_index].mixer_device.sends[0]'''

