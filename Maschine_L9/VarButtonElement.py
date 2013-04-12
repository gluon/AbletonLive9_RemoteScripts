#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk1\VarButtonElement.py
import Live
from _Framework.ButtonElement import *
from _Framework.InputControlElement import *
from MIDI_Map import *
import time

class VarButtonElement(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that can be configured with custom on- and off-values '

    def __init__(self, is_momentary, channel, scene_index, track_index, parent):
        ButtonElement.__init__(self, is_momentary, MIDI_NOTE_TYPE, channel, CLIPNOTEMAP[scene_index][track_index])
        self._is_enabled = True
        self._is_notifying = False
        self.surface = parent
        self._report_input = False
        self._scene_index = scene_index
        self._track_index = track_index

    def get_identifier(self):
        return self._msg_identifier

    def turn_off(self):
        self.send_value(0)

    def turn_on(self):
        self.send_value(127)

    def message_map_mode(self):
        raise self.message_type() is MIDI_CC_TYPE or AssertionError
        return Live.MidiMap.MapMode.absolute

    def set_enabled(self, enabled):
        self._is_enabled = enabled

    def set_send_note(self, note):
        if note in range(128):
            self._msg_identifier = note
            if not self._is_enabled:
                self.surface._translate_message(self._msg_type, self._original_identifier, self._original_channel, self._msg_identifier, self._msg_channel)

    def receive_value(self, value):
        if self._is_enabled:
            ButtonElement.receive_value(self, value)

    def send_value(self, value, force_send = False):
        raise value != None or AssertionError
        raise isinstance(value, int) or AssertionError
        raise value in range(128) or AssertionError
        ButtonElement.send_value(self, value, True)

    def set_to_notemode(self, notemode):
        self._is_enabled = not notemode
        if notemode:
            self.surface._translate_message(self._msg_type, self._original_identifier, self._original_channel, self._msg_identifier, self._msg_channel)

    def disconnect(self):
        ButtonElement.disconnect(self)
        self._is_enabled = None
        self._is_notifying = None
        self.surface = None
        self._report_input = None
        self._scene_index = None
        self._track_index = None


class TwinButton(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that can be configured with custom on- and off-values '

    def __init__(self, is_momentary, channel, partner):
        raise isinstance(partner, VarButtonElement) or AssertionError
        ButtonElement.__init__(self, is_momentary, MIDI_NOTE_TYPE, channel, partner._original_identifier)
        self._partner = partner

    def fire(self, value):
        self._partner.send_value(value, True)


class ColorButton(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that dealwith Colors '

    def __init__(self, is_momentary, midi_type, identifier):
        ButtonElement.__init__(self, is_momentary, midi_type, 0, identifier)
        self.hue = 2
        self.sat = 127
        self.bright = 127
        self._msg_identifier = identifier

    def send_value(self, value, force_send = False):
        if not value != None:
            raise AssertionError
            raise isinstance(value, int) or AssertionError
            if not value in range(128):
                raise AssertionError
                (force_send or self._is_being_forwarded) and self.send_color(value)
                is_input = self._report_output and True
                self._report_value(value, not is_input)

    def send_hue(self, hue):
        data_byte1 = self._original_identifier
        self.hue = hue
        self.send_midi((MIDI_CC_STATUS + 0, data_byte1, hue))

    def send_bright(self, brightness):
        data_byte1 = self._original_identifier
        self.bright = brightness
        self.send_midi((MIDI_CC_STATUS + 0, data_byte1, brightness))

    def send_color(self, value):
        data_byte1 = self._original_identifier
        self.send_midi((MIDI_CC_STATUS + 2, data_byte1, self.bright))
        self.send_midi((MIDI_CC_STATUS + 1, data_byte1, self.sat))
        self.send_midi((MIDI_CC_STATUS + 0, data_byte1, self.hue))

    def disconnect(self):
        ButtonElement.disconnect(self)