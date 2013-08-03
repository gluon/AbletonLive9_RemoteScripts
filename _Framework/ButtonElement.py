#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/ButtonElement.py
import Live
from InputControlElement import InputControlElement, MIDI_CC_TYPE
ON_VALUE = int(127)
OFF_VALUE = int(0)

class DummyUndoStepHandler(object):

    def begin_undo_step(self):
        pass

    def end_undo_step(self):
        pass


class ButtonElementMixin(object):
    """
    Mixin for sending values to button-like control-elements elements.
    """

    def set_light(self, is_turned_on):
        if is_turned_on:
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        self.send_value(ON_VALUE)

    def turn_off(self):
        self.send_value(OFF_VALUE)


class ButtonElement(InputControlElement, ButtonElementMixin):
    """
    Class representing a button a the controller
    """

    def __init__(self, is_momentary, msg_type, channel, identifier, undo_step_handler = DummyUndoStepHandler(), *a, **k):
        super(ButtonElement, self).__init__(msg_type, channel, identifier, *a, **k)
        self.__is_momentary = bool(is_momentary)
        self._last_received_value = -1
        self._undo_step_handler = undo_step_handler

    def is_momentary(self):
        """ returns true if the buttons sends a message on being released """
        return self.__is_momentary

    def message_map_mode(self):
        raise self.message_type() is MIDI_CC_TYPE or AssertionError
        return Live.MidiMap.MapMode.absolute

    def is_pressed(self):
        return self.__is_momentary and self._last_received_value > 0

    def receive_value(self, value):
        pressed_before = self.is_pressed()
        self._last_received_value = value
        if not pressed_before and self.is_pressed():
            self._undo_step_handler.begin_undo_step()
        super(ButtonElement, self).receive_value(value)
        if pressed_before and not self.is_pressed():
            self._undo_step_handler.end_undo_step()