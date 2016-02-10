#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_APC/ControlElementUtils.py
import Live
MapMode = Live.MidiMap.MapMode
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _APC.RingedEncoderElement import RingedEncoderElement

def make_button(channel, identifier, *a, **k):
    return ButtonElement(True, MIDI_NOTE_TYPE, channel, identifier, *a, **k)


def make_pedal_button(identifier, *a, **k):
    return ButtonElement(True, MIDI_CC_TYPE, 0, identifier, *a, **k)


def make_slider(channel, identifier, *a, **k):
    return SliderElement(MIDI_CC_TYPE, channel, identifier, *a, **k)


def make_knob(channel, identifier, *a, **k):
    return SliderElement(MIDI_CC_TYPE, channel, identifier, *a, **k)


def make_ring_encoder(encoder_identifer, button_identifier, name = '', *a, **k):
    button_name = '%s_Ring_Mode_Button' % name
    button = ButtonElement(False, MIDI_CC_TYPE, 0, button_identifier, name=button_name)
    encoder = RingedEncoderElement(MIDI_CC_TYPE, 0, encoder_identifer, MapMode.absolute, name=name, *a, **k)
    encoder.set_ring_mode_button(button)
    encoder.set_feedback_delay(-1)
    return encoder


def make_encoder(channel, identifier, *a, **k):
    return EncoderElement(MIDI_CC_TYPE, channel, identifier, MapMode.relative_two_compliment, *a, **k)