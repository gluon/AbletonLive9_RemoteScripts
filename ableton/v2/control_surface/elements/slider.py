#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/elements/slider.py
from __future__ import absolute_import, print_function
import Live
from ..input_control_element import MIDI_NOTE_TYPE
from .encoder import EncoderElement

class SliderElement(EncoderElement):
    """ Class representing a slider on the controller """

    def __init__(self, msg_type, channel, identifier, *a, **k):
        raise msg_type is not MIDI_NOTE_TYPE or AssertionError
        super(SliderElement, self).__init__(msg_type, channel, identifier, map_mode=Live.MidiMap.MapMode.absolute, *a, **k)