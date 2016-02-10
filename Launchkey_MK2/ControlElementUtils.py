#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchkey_MK2/ControlElementUtils.py
from functools import partial
import Live
from _Framework.Dependency import depends
from _Framework.Resource import PrioritizedResource
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.ComboElement import ComboElement
from .consts import STANDARD_CHANNEL

@depends(skin=None)
def make_button(identifier, msg_type = MIDI_NOTE_TYPE, is_momentary = True, skin = None, is_modifier = False, name = ''):
    return ButtonElement(is_momentary, msg_type, STANDARD_CHANNEL, identifier, skin=skin, name=name, resource_type=PrioritizedResource if is_modifier else None)


def make_encoder(identifier, name = ''):
    return EncoderElement(MIDI_CC_TYPE, STANDARD_CHANNEL, identifier, Live.MidiMap.MapMode.absolute, name=name)


def make_slider(identifier, name = '', channel = STANDARD_CHANNEL):
    return SliderElement(MIDI_CC_TYPE, channel, identifier, name=name)