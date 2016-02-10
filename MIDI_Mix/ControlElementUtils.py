#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MIDI_Mix/ControlElementUtils.py
import Live
from _Framework.Dependency import depends
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.EncoderElement import EncoderElement

@depends(skin=None)
def make_button(identifier, name, skin = None):
    return ButtonElement(True, MIDI_NOTE_TYPE, 0, identifier, name=name, skin=skin)


def make_slider(identifier, name):
    return SliderElement(MIDI_CC_TYPE, 0, identifier, name=name)


def make_encoder(identifier, name):
    return EncoderElement(MIDI_CC_TYPE, 0, identifier, map_mode=Live.MidiMap.MapMode.absolute, name=name)


def make_button_row(identifier_sequence, element_factory, name):
    return ButtonMatrixElement(rows=[ [element_factory(identifier, name + '_%d' % index)] for index, identifier in enumerate(identifier_sequence) ])