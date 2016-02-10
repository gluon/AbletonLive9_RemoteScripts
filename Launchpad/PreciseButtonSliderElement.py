#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad/PreciseButtonSliderElement.py
from _Framework.ButtonSliderElement import ButtonSliderElement
from _Framework.InputControlElement import *
SLIDER_MODE_SINGLE = 0
SLIDER_MODE_VOLUME = 1
SLIDER_MODE_PAN = 2

class PreciseButtonSliderElement(ButtonSliderElement):
    """ Class representing a set of buttons used as a slider """

    def __init__(self, buttons):
        ButtonSliderElement.__init__(self, buttons)
        num_buttons = len(buttons)
        self._disabled = False
        self._mode = SLIDER_MODE_VOLUME
        self._value_map = tuple([ float(index / num_buttons) for index in range(num_buttons) ])

    def set_disabled(self, disabled):
        raise isinstance(disabled, type(False)) or AssertionError
        self._disabled = disabled

    def set_mode(self, mode):
        if not mode in (SLIDER_MODE_SINGLE, SLIDER_MODE_VOLUME, SLIDER_MODE_PAN):
            raise AssertionError
            self._mode = mode != self._mode and mode

    def set_value_map(self, map):
        raise isinstance(map, (tuple, type(None))) or AssertionError
        raise len(map) == len(self._buttons) or AssertionError
        self._value_map = map

    def send_value(self, value):
        raise self._disabled or value != None or AssertionError
        raise isinstance(value, int) or AssertionError
        if not value in range(128):
            raise AssertionError
            if value != self._last_sent_value:
                if self._mode == SLIDER_MODE_SINGLE:
                    ButtonSliderElement.send_value(self, value)
                elif self._mode == SLIDER_MODE_VOLUME:
                    self._send_value_volume(value)
                elif self._mode == SLIDER_MODE_PAN:
                    self._send_value_pan(value)
                else:
                    raise False or AssertionError
                self._last_sent_value = value

    def connect_to(self, parameter):
        ButtonSliderElement.connect_to(self, parameter)
        if self._parameter_to_map_to != None:
            self._last_sent_value = -1
            self._on_parameter_changed()

    def release_parameter(self):
        old_param = self._parameter_to_map_to
        ButtonSliderElement.release_parameter(self)
        if not self._disabled and old_param != None:
            for button in self._buttons:
                button.reset()

    def reset(self):
        if not self._disabled and self._buttons != None:
            for button in self._buttons:
                if button != None:
                    button.reset()

    def _send_value_volume(self, value):
        index_to_light = -1
        normalised_value = float(value) / 127.0
        if normalised_value > 0.0:
            for index in range(len(self._value_map)):
                if normalised_value <= self._value_map[index]:
                    index_to_light = index
                    break

        self._send_mask(tuple([ index <= index_to_light for index in range(len(self._buttons)) ]))

    def _send_value_pan(self, value):
        num_buttons = len(self._buttons)
        button_bits = [ False for index in range(num_buttons) ]
        normalised_value = float(2 * value / 127.0) - 1.0
        if value in (63, 64):
            normalised_value = 0.0
        if normalised_value < 0.0:
            for index in range(len(self._buttons)):
                button_bits[index] = self._value_map[index] >= normalised_value
                if self._value_map[index] >= 0:
                    break

        elif normalised_value > 0.0:
            for index in range(len(self._buttons)):
                r_index = len(self._buttons) - 1 - index
                button_bits[r_index] = self._value_map[r_index] <= normalised_value
                if self._value_map[r_index] <= 0:
                    break

        else:
            for index in range(len(self._buttons)):
                button_bits[index] = self._value_map[index] == normalised_value

        self._send_mask(tuple(button_bits))

    def _send_mask(self, mask):
        raise isinstance(mask, tuple) or AssertionError
        raise len(mask) == len(self._buttons) or AssertionError
        for index in range(len(self._buttons)):
            if mask[index]:
                self._buttons[index].turn_on()
            else:
                self._buttons[index].turn_off()

    def _button_value(self, value, sender):
        if not isinstance(value, int):
            raise AssertionError
            if not sender in self._buttons:
                raise AssertionError
                self._last_sent_value = -1
                index_of_sender = (value != 0 or not sender.is_momentary()) and list(self._buttons).index(sender)
                self._parameter_to_map_to.value = self._parameter_to_map_to != None and self._parameter_to_map_to.is_enabled and self._value_map[index_of_sender]
            self.notify_value(value)

    def _on_parameter_changed(self):
        raise self._parameter_to_map_to != None or AssertionError
        param_range = abs(self._parameter_to_map_to.max - self._parameter_to_map_to.min)
        param_value = self._parameter_to_map_to.value
        param_min = self._parameter_to_map_to.min
        param_mid = param_range / 2 + param_min
        midi_value = 0
        if self._mode == SLIDER_MODE_PAN:
            if param_value == param_mid:
                midi_value = 64
            else:
                diff = abs(param_value - param_mid) / param_range * 127
                if param_value > param_mid:
                    midi_value = 64 + int(diff)
                else:
                    midi_value = 63 - int(diff)
        else:
            midi_value = int(127 * abs(param_value - self._parameter_to_map_to.min) / param_range)
        self.send_value(midi_value)