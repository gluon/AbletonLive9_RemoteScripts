#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/control_element_factory.py
from __future__ import absolute_import, print_function
from ableton.v2.base import depends
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE, PrioritizedResource, midi
from ableton.v2.control_surface.elements import SysexElement
from .configurable_button_element import ConfigurableButtonElement

@depends(skin=None)
def create_button(note, name, skin = None, **k):
    return ConfigurableButtonElement(True, MIDI_CC_TYPE, 0, note, name=name, skin=skin, **k)


def create_modifier_button(note, name, **k):
    return create_button(note, name, resource_type=PrioritizedResource, **k)


@depends(skin=None)
def create_note_button(note, name, skin = None, **k):
    return ConfigurableButtonElement(True, MIDI_NOTE_TYPE, 0, note, skin=skin, name=name, **k)


def make_send_message_generator(prefix):
    return lambda value_bytes: prefix + value_bytes + (midi.SYSEX_END,)


def create_sysex_element(message_prefix, enquire_message = None, default_value = None):
    return SysexElement(sysex_identifier=message_prefix, send_message_generator=make_send_message_generator(message_prefix), enquire_message=enquire_message, default_value=default_value)