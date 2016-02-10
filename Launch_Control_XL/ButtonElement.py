#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/ButtonElement.py
from _Framework.ButtonElement import ON_VALUE, OFF_VALUE, ButtonElement as ButtonElementBase

class ButtonElement(ButtonElementBase):
    _on_value = None
    _off_value = None

    def reset(self):
        self._on_value = None
        self._off_value = None
        super(ButtonElement, self).reset()

    def set_on_off_values(self, on_value, off_value):
        self._on_value = on_value
        self._off_value = off_value

    def send_value(self, value, **k):
        if value is ON_VALUE and self._on_value is not None:
            self._skin[self._on_value].draw(self)
        elif value is OFF_VALUE and self._off_value is not None:
            self._skin[self._off_value].draw(self)
        else:
            super(ButtonElement, self).send_value(value, **k)