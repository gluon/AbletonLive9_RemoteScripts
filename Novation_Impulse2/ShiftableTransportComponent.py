#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Novation_Impulse/ShiftableTransportComponent.py
import Live
from _Framework.ButtonElement import ButtonElement
from _Framework.TransportComponent import TransportComponent

class ShiftableTransportComponent(TransportComponent):
    """ Special transport class handling the seek buttons differently based on a shift button"""

    def __init__(self, c_instance):
        self.c_instance = c_instance
        self._shift_pressed = False
        self._mixer9_button = None
        TransportComponent.__init__(self)

    def disconnect(self):
        TransportComponent.disconnect(self)

    def set_record_buttonOnInit(self, button):
        self.log("set_record_buttonOnInit 1")
        self.record_button = button
        self.set_record_button(self.record_button)
        self.log("set_record_buttonOnInit 2")

    def set_mixer9_button(self, button):
        self.log("set_mixer9_button 1")
        self._mixer9_button = button
        self.set_overdub_button(self._mixer9_button)
        self.log("set_mixer9_button 2")


    def _shift_value(self, value):
        self.log("shift handler transport component " + str(value))
        if not value in range(128):
            raise AssertionError
        self.log("shift handler 2")
        self._shift_pressed = self.is_enabled() and value > 0
        self.log("shift handler 3")


    def _ffwd_value(self, value):
        self.log("ffwd handler main")
        if not self._ffwd_button != None:
            raise AssertionError
        if not value in range(128):
            raise AssertionError
        else:
            if self._shift_pressed:
                self.log("ffwd shifted handler")
                self.song().current_song_time = self._shift_pressed and self.song().last_event_time
            else:
                self.log("ffwd normal handler")
                TransportComponent._ffwd_value(self, value)

    def _rwd_value(self, value):
        self.log("rwd handler main")
        if not self._rwd_button != None:
            raise AssertionError
        if not value in range(128):
            raise AssertionError
        else:
            if self._shift_pressed:
                self.song().current_song_time = self._shift_pressed and 0.0
                self.log("rwd shifted handler")
            else:
                self.log("rwd normal handler")
                TransportComponent._rwd_value(self, value)

    def log(self, message):
#        pass
        self.c_instance.log_message(message)
