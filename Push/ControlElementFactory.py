#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/ControlElementFactory.py
from _Framework.Dependency import depends
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Resource import PrioritizedResource
from ConfigurableButtonElement import ConfigurableButtonElement

@depends(skin=None)
def create_button(note, name, skin = None, **k):
    return ConfigurableButtonElement(True, MIDI_CC_TYPE, 0, note, name=name, skin=skin, **k)


def create_modifier_button(note, name, **k):
    return create_button(note, name, resource_type=PrioritizedResource, **k)


@depends(skin=None)
def create_note_button(note, name, skin = None, **k):
    return ConfigurableButtonElement(True, MIDI_NOTE_TYPE, 0, note, skin=skin, name=name, **k)