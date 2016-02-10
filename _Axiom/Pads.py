#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Axiom/Pads.py
import Live
from consts import *

class Pads:
    """ Class representing the Pads section on the Axiom controllers """

    def __init__(self, parent):
        self.__parent = parent

    def build_midi_map(self, script_handle, midi_map_handle):
        for channel in range(4):
            for pad in range(8):
                Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, AXIOM_PADS[pad])

        for pad in range(8):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 15, AXIOM_PADS[pad])

    def receive_midi_cc(self, cc_no, cc_value, channel):
        if list(AXIOM_PADS).count(cc_no) > 0:
            pad_index = list(AXIOM_PADS).index(cc_no)
            index = pad_index + channel * 8
            if cc_value > 0:
                if channel in range(4):
                    if self.__parent.application().view.is_view_visible('Session'):
                        tracks = self.__parent.song().visible_tracks
                        if len(tracks) > index:
                            current_track = tracks[index]
                            clip_index = list(self.__parent.song().scenes).index(self.__parent.song().view.selected_scene)
                            current_track.clip_slots[clip_index].fire()
                    elif self.__parent.application().view.is_view_visible('Arranger'):
                        if len(self.__parent.song().cue_points) > index:
                            self.__parent.song().cue_points[index].jump()
                elif channel == 15:
                    self.__parent.bank_changed(pad_index)