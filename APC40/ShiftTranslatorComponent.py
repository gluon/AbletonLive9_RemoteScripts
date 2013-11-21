#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC40/ShiftTranslatorComponent.py
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from _Framework.ButtonElement import ButtonElement
from _Framework.MixerComponent import MixerComponent

class ShiftTranslatorComponent(ChannelTranslationSelector):
    """ Class that translates the channel of some buttons as long as a shift button is held """

    def __init__(self):
        ChannelTranslationSelector.__init__(self)
        self._shift_button = None
        self._shift_pressed = False

    def disconnect(self):
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None
        ChannelTranslationSelector.disconnect(self)

    def set_shift_button(self, button):
        if not (button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            raise AssertionError
            if self._shift_button != None:
                self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = button
            self._shift_button != None and self._shift_button.add_value_listener(self._shift_value)
        self.set_mode(0)

    def on_enabled_changed(self):
        if self.is_enabled():
            self.set_mode(int(self._shift_pressed))

    def number_of_modes(self):
        return 2

    def _shift_value(self, value):
        if not self._shift_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self._shift_pressed = value != 0
            self.is_enabled() and self.set_mode(int(self._shift_pressed))