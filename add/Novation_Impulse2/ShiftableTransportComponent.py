#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Novation_Impulse/ShiftableTransportComponent.py
import Live
from _Framework.ButtonElement import ButtonElement
from _Framework.TransportComponent import TransportComponent

class ShiftableTransportComponent(TransportComponent):
    """ Special transport class handling the seek buttons differently based on a shift button"""

    def __init__(self, c_instance):
        self.c_instance = c_instance
        self._shift_button = None
        self._shift_pressed = False
        TransportComponent.__init__(self)

    def disconnect(self):
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None
        TransportComponent.disconnect(self)

    def set_shift_button(self, button):
        self.log("set_shift_button")
        if not (button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            raise AssertionError
            if self._shift_button != button:
                if self._shift_button != None:
                    self._shift_button.remove_value_listener(self._shift_value)
                    self._shift_pressed = False
                self._shift_button = button
                self._shift_button != None and self._shift_button.add_value_listener(self._shift_value)

    def _shift_value(self, value):
        self.log("shift handler")
        if not self._shift_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self._shift_pressed = self.is_enabled() and value > 0
            if self._shift_pressed:
                TransportComponent.log_message("shift handler pressed")
                self.set_session_overdub_button(rec_button)
                self.set_overdub_button(rec_button)
                self.set_arrangement_overdub_button(rec_button)
                self.set_record_button(none)
            else:
                TransportComponent.log_message("shift handler unpressed")
                self.set_session_overdub_button(none)
                self.set_arrangement_overdub_button(none)
                self.set_overdub_button(none)
                self.set_record_button(rec_button)



    def _ffwd_value(self, value):
        self.log("ffwd handler")
        if not self._ffwd_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.song().current_song_time = self._shift_pressed and self.song().last_event_time
        else:
            TransportComponent._ffwd_value(self, value)

    def _rwd_value(self, value):
        self.log("rwd handler")
        if not self._rwd_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.song().current_song_time = self._shift_pressed and 0.0
        else:
            TransportComponent._rwd_value(self, value)


    def log(self, message):
	    self.c_instance.log_message(message)
