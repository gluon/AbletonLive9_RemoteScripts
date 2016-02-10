#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AIRA_MX_1/ControlElementUtils.py
import Live
from _Framework.Resource import PrioritizedResource
from _Framework.Dependency import depends
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.ComboElement import ComboElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement

@depends(skin=None)
def make_button(name, identifier, channel = 0, msg_type = MIDI_NOTE_TYPE, is_momentary = True, is_modifier = False, skin = None):
    return ButtonElement(is_momentary, msg_type, channel, identifier, name=name, resource_type=PrioritizedResource if is_modifier else None, skin=skin)


def make_encoder(name, identifier, channel = 0):
    return EncoderElement(MIDI_CC_TYPE, channel, identifier, Live.MidiMap.MapMode.absolute, name=name)


def with_modifier(control, modifier):
    return ComboElement(control, modifiers=[modifier], name=control.name + '_With_Modifier')