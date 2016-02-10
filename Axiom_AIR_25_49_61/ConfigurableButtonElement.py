#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/ConfigurableButtonElement.py
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_CC_STATUS
from consts import *

class ConfigurableButtonElement(ButtonElement):
    """ Special button class that can be configured with custom on- and off-values
    and can send and receive on different channels with different message types """

    def __init__(self, is_momentary, msg_type, channel, identifier, send_channel = None, identifier_send_offset = 0, send_msg_type = None):
        ButtonElement.__init__(self, is_momentary, msg_type, channel, identifier)
        self._send_channel = send_channel
        self._send_msg_type = send_msg_type
        self._identifier_send_offset = identifier_send_offset
        self._on_value = AMB_FULL
        self._off_value = LED_OFF
        self._is_enabled = True
        self._is_notifying = False
        self._force_next_value = False
        self._pending_listeners = []

    def set_on_off_values(self, on_value, off_value):
        self.clear_send_cache()
        self._on_value = on_value
        self._off_value = off_value

    def set_force_next_value(self):
        self._force_next_value = True

    def set_enabled(self, enabled):
        self._is_enabled = enabled

    def turn_on(self):
        self.send_value(self._on_value)

    def turn_off(self):
        self.send_value(self._off_value)

    def reset(self):
        self.send_value(self._off_value)

    def add_value_listener(self, callback, identify_sender = False):
        if not self._is_notifying:
            ButtonElement.add_value_listener(self, callback, identify_sender)
        else:
            self._pending_listeners.append((callback, identify_sender))

    def receive_value(self, value):
        self._is_notifying = True
        ButtonElement.receive_value(self, value)
        self._is_notifying = False
        for listener in self._pending_listeners:
            self.add_value_listener(listener[0], listener[1])

        self._pending_listeners = []

    def send_value(self, value, force = False):
        if force or self._force_next_value or value != self._last_sent_value:
            data_byte1 = self._original_identifier + self._identifier_send_offset
            data_byte2 = value
            status_byte = self._send_channel if self._send_channel else self._original_channel
            if self._send_msg_type:
                if self._send_msg_type == MIDI_NOTE_TYPE:
                    status_byte += MIDI_NOTE_ON_STATUS
                elif self._send_msg_type == MIDI_CC_TYPE:
                    status_byte += MIDI_CC_STATUS
            elif self._msg_type == MIDI_NOTE_TYPE:
                status_byte += MIDI_NOTE_ON_STATUS
            elif self._msg_type == MIDI_CC_TYPE:
                status_byte += MIDI_CC_STATUS
            if self.send_midi((status_byte, data_byte1, data_byte2)):
                self._last_sent_message = (value, None)
                if self._report_output:
                    is_input = True
                    self._report_value(value, not is_input)
        self._force_next_value = False