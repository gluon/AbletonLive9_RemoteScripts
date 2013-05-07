#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/SliderElement.py
import Live
from EncoderElement import EncoderElement
from InputControlElement import MIDI_NOTE_TYPE

class SliderElement(EncoderElement):
    """ Class representing a slider on the controller """

    def __init__(self, msg_type, channel, identifier):
        raise msg_type is not MIDI_NOTE_TYPE or AssertionError
        EncoderElement.__init__(self, msg_type, channel, identifier, map_mode=Live.MidiMap.MapMode.absolute)