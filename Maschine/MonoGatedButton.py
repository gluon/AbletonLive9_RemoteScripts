#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\MonoGatedButton.py
import Live
from _Framework.ButtonElement import *
from _Framework.InputControlElement import *
from MIDI_Map import *
import time

class MonoGatedButton(ButtonElement):
    __module__ = __name__
    __doc__ = ' Special button class that has on, off, color an can also be a None Color Button '

    def __init__(self, is_momentary, midi_type, identifier):
        ButtonElement.__init__(self, is_momentary, midi_type, 0, identifier)
        self._msg_identifier = identifier
        self.last_value = 0
        self.hue = 0

    def set_color(self, hue):
        self.send_value(127, True)

    def send_color(self, value):
        self.send_value(value)

    def switch_off(self):
        self.send_value(0)

    def activate(self):
        pass

    def update(self):
        pass

    def turn_on(self):
        self.send_value(127, True)

    def turn_off(self):
        self.send_value(0, True)

    def disconnect(self):
        InputControlElement.disconnect(self)