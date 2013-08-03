#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/ButtonSliderElement.py
from SliderElement import SliderElement
from InputControlElement import InputControlElement, MIDI_INVALID_TYPE
from ButtonElement import ButtonElement

class ButtonSliderElement(SliderElement):
    """ Class representing a set of buttons used as a slider """
    _last_sent_value = -1

    def __init__(self, buttons):
        raise buttons != None or AssertionError
        raise isinstance(buttons, tuple) or AssertionError
        raise len(buttons) > 1 or AssertionError
        SliderElement.__init__(self, MIDI_INVALID_TYPE, 0, 0)
        self._buttons = buttons
        self._last_button_lit = -1
        identify_sender = True
        for new_button in self._buttons:
            raise new_button != None or AssertionError
            raise isinstance(new_button, ButtonElement) or AssertionError
            new_button.add_value_listener(self._button_value, identify_sender)

    def disconnect(self):
        if self._parameter_to_map_to != None:
            self._parameter_to_map_to.remove_value_listener(self._on_parameter_changed)
        SliderElement.disconnect(self)
        self._buttons = None

    def message_channel(self):
        raise NotImplementedError, 'message_channel() should not be called directly on ButtonSliderElement'

    def message_identifier(self):
        raise NotImplementedError, 'message_identifier() should not be called directly on ButtonSliderElement'

    def message_map_mode(self):
        raise NotImplementedError, 'message_map_mode() should not be called directly on ButtonSliderElement'

    def install_connections(self, install_translation_callback, install_mapping_callback, install_forwarding_callback):
        pass

    def connect_to(self, parameter):
        if self._parameter_to_map_to != None:
            self._parameter_to_map_to.remove_value_listener(self._on_parameter_changed)
        InputControlElement.connect_to(self, parameter)
        if self._parameter_to_map_to != None:
            self._parameter_to_map_to.add_value_listener(self._on_parameter_changed)
            self._on_parameter_changed()

    def release_parameter(self):
        if self._parameter_to_map_to != None:
            self._parameter_to_map_to.remove_value_listener(self._on_parameter_changed)
        InputControlElement.release_parameter(self)

    def identifier_bytes(self):
        raise RuntimeWarning, 'identifier_bytes() should not be called on ButtonSliderElement'

    def send_value(self, value):
        if value != self._last_sent_value:
            index_to_light = 0
            if value > 0:
                index_to_light = int((len(self._buttons) - 1) * value / 127)
            for index in xrange(len(self._buttons)):
                if index == index_to_light:
                    self._buttons[index].turn_on()
                else:
                    self._buttons[index].turn_off()

            self._last_sent_value = value
            self._last_button_lit = index_to_light

    def _button_value(self, value, sender):
        self.clear_send_cache()
        if value != 0 or not sender.is_momentary():
            index_of_sender = list(self._buttons).index(sender)
            midi_value = int(127 * index_of_sender / (len(self._buttons) - 1))
            if self._parameter_to_map_to != None and self._parameter_to_map_to.is_enabled:
                param_range = self._parameter_to_map_to.max - self._parameter_to_map_to.min
                param_value = param_range * index_of_sender / (len(self._buttons) - 1) + self._parameter_to_map_to.min
                if index_of_sender > 0:
                    param_value += param_range / (4 * len(self._buttons))
                    if param_value > self._parameter_to_map_to.max:
                        param_value = self._parameter_to_map_to.max
                self._parameter_to_map_to.value = param_value
            self._last_button_lit = index_of_sender
            self.notify_value(midi_value)

    def _on_parameter_changed(self):
        raise self._parameter_to_map_to != None or AssertionError
        param_range = abs(self._parameter_to_map_to.max - self._parameter_to_map_to.min)
        midi_value = int(127 * abs(self._parameter_to_map_to.value - self._parameter_to_map_to.min) / param_range)
        self.send_value(midi_value)