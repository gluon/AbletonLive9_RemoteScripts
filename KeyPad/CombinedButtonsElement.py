#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/KeyPad/CombinedButtonsElement.py
from __future__ import with_statement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import OFF_VALUE
from _Framework.Util import const, BooleanContext

class CombinedButtonsElement(ButtonMatrixElement):

    def __init__(self, buttons = None, *a, **k):
        super(CombinedButtonsElement, self).__init__(rows=[buttons], *a, **k)
        self._is_pressed = BooleanContext(False)

    def is_momentary(self):
        return True

    def is_pressed(self):
        return any(map(lambda b: b[0].is_pressed(), self.iterbuttons())) or bool(self._is_pressed)

    def on_nested_control_element_value(self, value, sender):
        with self._is_pressed():
            self.notify_value(value)
        if value != OFF_VALUE and not getattr(sender, 'is_momentary', const(False))():
            self.notify_value(OFF_VALUE)

    def send_value(self, value):
        for button, _ in self.iterbuttons():
            button.send_value(value)

    def set_light(self, value):
        for button, _ in self.iterbuttons():
            button.set_light(value)