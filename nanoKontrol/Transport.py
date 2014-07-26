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

class Transport:
    __module__ = __name__
    __doc__ = ' Class representing the transport section on the NanoKontrol '

    def __init__(self, parent):
        self._Transport__parent = parent
        self._Transport__ffwd_held = False
        self._Transport__rwd_held = False
        self._Transport__delay_counter = 0
        self._Transport__mod_pressed = False



    def build_midi_map(self, script_handle, midi_map_handle):
        for cc_no in NANOKONTROL_TRANSPORT:
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 15, cc_no)




    def receive_midi_cc(self, cc_no, cc_value):
        if (cc_no == NANOKONTROL_LOOP):
            self._Transport__mod_pressed = (cc_value == 127)
        elif (cc_no == NANOKONTROL_STOP):
            if (cc_value > 0) and (not self._Transport__mod_pressed):
                self._Transport__parent.song().is_playing = False
            elif (cc_value > 0):
                self._Transport__parent.song().stop_all_clips()
        elif (cc_no == NANOKONTROL_PLAY):
            if (cc_value > 0) and (not self._Transport__mod_pressed):
                self._Transport__parent.song().is_playing = True
            elif (cc_value > 0):
                self._Transport__parent.song().view.selected_scene.fire_as_selected()
        elif (cc_no == NANOKONTROL_REC):
            if (cc_value > 0) and (not self._Transport__mod_pressed):
                self._Transport__parent.song().record_mode = (not self._Transport__parent.song().record_mode)
            elif (cc_value > 0):
                self._Transport__parent.song().overdub = (not self._Transport__parent.song().overdub)
        elif self._Transport__parent.application().view.is_view_visible('Session'):
            if (cc_value > 0):
                self._Transport__cc_in_session(cc_no)
        else:
            self._Transport__cc_in_arranger(cc_no, cc_value)



    def __cc_in_session(self, cc_no):
        index = list(self._Transport__parent.song().scenes).index(self._Transport__parent.song().view.selected_scene)
        if (cc_no == NANOKONTROL_LOOP):
            self._Transport__mod_pressed = (cc_value == 127)
        elif (cc_no == NANOKONTROL_RWD):
            if (index > 0) and (not self._Transport__mod_pressed):
                index = (index - 1)
                self._Transport__parent.song().view.selected_scene = self._Transport__parent.song().scenes[index]
            elif (index > 0):
                  index = (index - 5)
                  self._Transport__parent.song().view.selected_scene = self._Transport__parent.song().scenes[index]
        elif (cc_no == NANOKONTROL_FFWD):
            if (index < (len(self._Transport__parent.song().scenes) - 1)) and (not self._Transport__mod_pressed):
                index = (index + 1)
                self._Transport__parent.song().view.selected_scene = self._Transport__parent.song().scenes[index]
            elif (index < (len(self._Transport__parent.song().scenes) - 1)):
                  index = (index + 5)
                  self._Transport__parent.song().view.selected_scene = self._Transport__parent.song().scenes[index]



    def __cc_in_arranger(self, cc_no, cc_value):
        if (cc_no == NANOKONTROL_LOOP):
            if (cc_value > 0):
                self._Transport__parent.song().loop = (not self._Transport__parent.song().loop)
        elif (cc_no == NANOKONTROL_RWD):
            if (not self._Transport__ffwd_held):
                if (cc_value > 0):
                    self._Transport__rwd_held = True
                    self._Transport__delay_counter = 0
                    self._Transport__parent.song().jump_by((-1 * self._Transport__parent.song().signature_denominator))
                else:
                    self._Transport__rwd_held = False
        elif (cc_no == NANOKONTROL_FFWD):
            if (not self._Transport__rwd_held):
                if (cc_value > 0):
                    self._Transport__ffwd_held = True
                    self._Transport__delay_counter = 0
                    self._Transport__parent.song().jump_by(self._Transport__parent.song().signature_denominator)
                else:
                    self._Transport__ffwd_held = False



    def refresh_state(self):
        if self._Transport__ffwd_held:
            self._Transport__delay_counter += 1
            if ((self._Transport__delay_counter % 5) == 0):
                self._Transport__parent.song().jump_by(self._Transport__parent.song().signature_denominator)
        if self._Transport__rwd_held:
            self._Transport__delay_counter += 1
            if ((self._Transport__delay_counter % 5) == 0):
                self._Transport__parent.song().jump_by((-1 * self._Transport__parent.song().signature_denominator))



