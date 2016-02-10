#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Novation_Impulse/ShiftableTransportComponent.py
import Live
from _Framework.ButtonElement import ButtonElement
from _Framework.TransportComponent import TransportComponent

class ShiftableTransportComponent(TransportComponent):
    """ Special transport class handling the seek buttons differently based on a shift button"""

    def __init__(self):
        self._shift_button = None
        self._shift_pressed = False
        TransportComponent.__init__(self)

    def disconnect(self):
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None
        TransportComponent.disconnect(self)

    def set_shift_button(self, button):
        if not (button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            raise AssertionError
            if self._shift_button != button:
                if self._shift_button != None:
                    self._shift_button.remove_value_listener(self._shift_value)
                    self._shift_pressed = False
                self._shift_button = button
                self._shift_button != None and self._shift_button.add_value_listener(self._shift_value)

    def _shift_value(self, value):
        if not self._shift_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self._shift_pressed = self.is_enabled() and value > 0

    def _ffwd_value(self, value):
        if not self._ffwd_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.song().current_song_time = self._shift_pressed and self.song().last_event_time
        else:
            TransportComponent._ffwd_value(self, value)

    def _rwd_value(self, value):
        if not self._rwd_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.song().current_song_time = self._shift_pressed and 0.0
        else:
            TransportComponent._rwd_value(self, value)