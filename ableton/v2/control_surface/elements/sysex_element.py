#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/elements/sysex_element.py
from __future__ import absolute_import, print_function
from ..input_control_element import InputControlElement, MIDI_SYSEX_TYPE
from .. import midi

class SysexElement(InputControlElement):
    """
    Control element for sending and receiving sysex message.
    
    Set sysex_identifier to the unique static part of the sysex message, to notify
    the value event about incoming sysex messages.
    
    send_message_generator should be a function object that takes the arguments of
    send_value and generates a valid sysex message. send_value will raise an error
    if the generated message is not valid.
    
    enquire_message is the sysex message for requesting a value. Use enquire_value to
    send out the message.
    
    default_value is being used when calling reset on the element. The value is passed
    as an argument to send_value. Setting the property to None will disable sending
    a value when resetting the element (default).
    """

    def __init__(self, send_message_generator = None, enquire_message = None, default_value = None, *a, **k):
        super(SysexElement, self).__init__(msg_type=MIDI_SYSEX_TYPE, *a, **k)
        self._send_message_generator = send_message_generator
        self._enquire_message = enquire_message
        self._default_value = default_value

    def send_value(self, *arguments):
        raise self._send_message_generator is not None or AssertionError
        message = self._send_message_generator(*arguments)
        raise midi.is_valid_sysex(message) or AssertionError('Trying to send sysex message %r, which is not valid.' % map(hex, message))
        self.send_midi(message)

    def enquire_value(self):
        raise self._enquire_message is not None or AssertionError
        self.send_midi(self._enquire_message)

    def reset(self):
        if self._default_value is not None:
            self.send_value(self._default_value)