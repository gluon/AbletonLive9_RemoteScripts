#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\VarButtonElement.py
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
        self.last_value = 0
        self.last_color = [None, None, None]

    def get_identifier(self):
        return self._msg_identifier

    def reset(self):
        self.last_color = [None, None, None]

    def turn_off(self):
        self.send_value(0, True)

    def turn_on(self):
        self.send_value(1, True)

    def refresh(self):
        self.send_value(self.last_value, True)

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

    def set_to_notemode(self, notemode):
        self._is_enabled = not notemode
        if notemode:
            self.surface._translate_message(self._msg_type, self._original_identifier, self._original_channel, self._msg_identifier, self._msg_channel)
        else:
            self._is_being_forwarded = True

    def send_value_bright(self, value, force_send = False):
        if not value != None:
            raise AssertionError
            raise isinstance(value, int) or AssertionError
            raise value in range(128) or AssertionError
            self.last_value = value
            (force_send or self._is_being_forwarded) and self.send_color_brightness(value)
            self.last_value = value

    def send_value(self, value, force_send = False):
        if not value != None:
            raise AssertionError
            raise isinstance(value, int) or AssertionError
            raise value in range(128) or AssertionError
            (force_send or self._is_being_forwarded) and self.send_color(value)
            self.last_value = value

    def send_color_brightness(self, value):
        data_byte1 = self._original_identifier
        color = self.surface.get_color(value, self._track_index, self._scene_index)
        if color == None:
            self.send_c_midi(2, 0)
        else:
            self.send_c_midi(2, color[2])

    def send_color(self, value):
        data_byte1 = self._original_identifier
        color = self.surface.get_color(value, self._track_index, self._scene_index)
        if color == None:
            self.send_c_midi(0, 0, True)
            self.send_c_midi(1, 0, True)
            self.send_c_midi(2, 0, True)
        else:
            self.send_c_midi(0, color[0])
            self.send_c_midi(1, color[1])
            self.send_c_midi(2, color[2])

    def send_color_direct(self, color):
        data_byte1 = self._original_identifier
        if color == None:
            self.send_c_midi(0, 0, True)
            self.send_c_midi(1, 0, True)
            self.send_c_midi(2, 0, True)
        else:
            self.send_c_midi(2, color[2])
            self.send_c_midi(1, color[1])
            self.send_c_midi(0, color[0])

    def send_c_midi(self, channel, colorvalue, force = False):
        stat = MIDI_CC_STATUS + channel
        prevColor = self.last_color[channel]
        self.send_midi((stat, self._original_identifier, colorvalue))

    def send_hue(self, noteval, value):
        self.send_midi((MIDI_CC_STATUS + 0, noteval, value), False)

    def disconnect(self):
        ButtonElement.disconnect(self)
        self._is_enabled = None
        self._is_notifying = None
        self.surface = None
        self._report_input = None
        self._scene_index = None
        self._track_index = None
        self.surface = None


class TwinButton(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that can be configured with custom on- and off-values '

    def __init__(self, is_momentary, channel, partner):
        raise isinstance(partner, VarButtonElement) or AssertionError
        ButtonElement.__init__(self, is_momentary, MIDI_NOTE_TYPE, channel, partner._original_identifier)
        self._partner = partner

    def fire(self, value):
        self._partner.send_value(value, True)


class GatedColorButton(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that has on, off, color an can also be a None Color Button '

    def __init__(self, is_momentary, midi_type, identifier, hue):
        ButtonElement.__init__(self, is_momentary, midi_type, 0, identifier)
        self._msg_identifier = identifier
        self.hue = hue
        self.last_value = 0

    def send_value(self, value, force_send = False):
        if not value != None:
            raise AssertionError
            raise isinstance(value, int) or AssertionError
            raise value in range(128) or AssertionError
            (force_send or self._is_being_forwarded) and self.send_color(value)

    def send_color(self, value):
        data_byte1 = self._msg_identifier
        self.last_value = value
        if value == 0:
            brightness = 10
        else:
            brightness = 127
        self.send_midi((MIDI_CC_STATUS + 0, data_byte1, self.hue))
        self.send_midi((MIDI_CC_STATUS + 2, data_byte1, brightness))
        self.send_midi((MIDI_CC_STATUS + 1, data_byte1, 127))

    def switch_off(self):
        data_byte = self._msg_identifier
        self.send_midi((MIDI_CC_STATUS + 2, data_byte, 0))
        self.send_midi((MIDI_CC_STATUS + 1, data_byte, 0))
        self.send_midi((MIDI_CC_STATUS + 0, data_byte, 0))

    def activate(self):
        self.send_value(0)

    def update(self):
        self.state_init = False
        self.send_value(self.last_value, True)

    def disconnect(self):
        InputControlElement.disconnect(self)


class ColorButton(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that deals with Colors '

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
            raise value in range(128) or AssertionError
            (force_send or self._is_being_forwarded) and self.send_color(value)

    def set_color(self, hue, sat, bright):
        self.hue = hue
        self.bright = bright
        self.sat = sat

    def send_hue(self, hue):
        data_byte1 = self._original_identifier
        self.hue = hue
        self.send_midi((MIDI_CC_STATUS + 0, data_byte1, hue))

    def send_color(self, value):
        data_byte1 = self._original_identifier
        self.send_midi((MIDI_CC_STATUS + 2, data_byte1, self.bright))
        self.send_midi((MIDI_CC_STATUS + 1, data_byte1, self.sat))
        self.send_midi((MIDI_CC_STATUS + 0, data_byte1, self.hue))

    def disconnect(self):
        ButtonElement.disconnect(self)