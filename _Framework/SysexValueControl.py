#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/SysexValueControl.py
from __future__ import absolute_import
from .InputControlElement import InputControlElement, MIDI_SYSEX_TYPE

class SysexValueControl(InputControlElement):
    """
    Sysex value control receives a sysex message, identified by a
    prefix.  The value can be requested with a value_enquiry MIDI
    message to the controller.
    """

    def __init__(self, message_prefix = None, value_enquiry = None, default_value = None, *a, **k):
        super(SysexValueControl, self).__init__(msg_type=MIDI_SYSEX_TYPE, sysex_identifier=message_prefix, *a, **k)
        self._value_enquiry = value_enquiry
        self._default_value = default_value

    def send_value(self, value_bytes):
        self.send_midi(self.message_sysex_identifier() + value_bytes + (247,))

    def enquire_value(self):
        raise self._value_enquiry != None or AssertionError
        self.send_midi(self._value_enquiry)

    def reset(self):
        if self._default_value != None:
            self.send_value(self._default_value)