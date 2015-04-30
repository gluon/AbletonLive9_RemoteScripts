#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_Framework/EncoderElement.py
from __future__ import absolute_import
import Live
from .CompoundElement import CompoundElement
from .InputControlElement import InputControlElement, MIDI_CC_TYPE, InputSignal
from .SubjectSlot import SubjectEvent
from .Util import nop, const

def _not_implemented(value):
    raise NotImplementedError


_map_modes = map_modes = Live.MidiMap.MapMode
ENCODER_VALUE_NORMALIZER = {_map_modes.relative_smooth_two_compliment: lambda v: v if v <= 64 else v - 128,
 _map_modes.relative_smooth_signed_bit: lambda v: v if v <= 64 else 64 - v}

class EncoderElement(InputControlElement):
    """
    Class representing a continuous control on the controller.
    
    The normalized value notifies a delta in the range:
        (-encoder_sensitivity, +encoder_sensitvity)
    """

    class ProxiedInterface(InputControlElement.ProxiedInterface):
        normalize_value = nop

    __subject_events__ = (SubjectEvent(name='normalized_value', signal=InputSignal),)
    encoder_sensitivity = 1.0

    def __init__(self, msg_type, channel, identifier, map_mode, encoder_sensitivity = None, *a, **k):
        super(EncoderElement, self).__init__(msg_type, channel, identifier, *a, **k)
        if encoder_sensitivity is not None:
            self.encoder_sensitivity = encoder_sensitivity
        self.__map_mode = map_mode
        self.__value_normalizer = ENCODER_VALUE_NORMALIZER.get(map_mode, _not_implemented)

    def message_map_mode(self):
        raise self.message_type() is MIDI_CC_TYPE or AssertionError
        return self.__map_mode

    def relative_value_to_delta(self, value):
        raise value >= 0 and value < 128 or AssertionError
        return self.__value_normalizer(value)

    def normalize_value(self, value):
        return self.relative_value_to_delta(value) / 64.0 * self.encoder_sensitivity

    def notify_value(self, value):
        super(EncoderElement, self).notify_value(value)
        if self.normalized_value_listener_count():
            self.notify_normalized_value(self.normalize_value(value))


class TouchEncoderElementBase(EncoderElement):
    """
    Defines the interface necessary to implement a touch encoder, so that it works in
    combination with other parts of the framework (like the EncoderControl).
    """

    class ProxiedInterface(EncoderElement.ProxiedInterface):
        is_pressed = const(False)
        add_touch_value_listener = nop
        remove_touch_value_listener = nop
        touch_value_has_listener = nop

    __subject_events__ = ('touch_value',)

    def is_pressed(self):
        raise NotImplementedError


class TouchEncoderElement(CompoundElement, TouchEncoderElementBase):
    """
    Encoder that implements the TouchEncoderElementBase interface, by taking a
    touch_element and forwarding its value event to the touch_event.
    The touch_element is registered as a nested element and respects ownership
    properly.
    """

    def __init__(self, channel = 0, identifier = 0, map_mode = _map_modes.absolute, touch_element = None, *a, **k):
        super(TouchEncoderElement, self).__init__(MIDI_CC_TYPE, channel, identifier, map_mode, *a, **k)
        raise touch_element is not None or AssertionError
        self._touch_element = self.register_control_element(touch_element)

    def add_touch_value_listener(self, *a, **k):
        if self.value_listener_count() == 0:
            self.request_listen_nested_control_elements()
        super(TouchEncoderElement, self).add_touch_value_listener(*a, **k)

    def remove_touch_value_listener(self, *a, **k):
        super(TouchEncoderElement, self).remove_touch_value_listener(*a, **k)
        if self.value_listener_count() == 0:
            self.unrequest_listen_nested_control_elements()

    def on_nested_control_element_value(self, value, control):
        self.notify_touch_value(value)

    def is_pressed(self):
        return self.owns_control_element(self._touch_element) and self._touch_element.is_pressed()

    def on_nested_control_element_received(self, control):
        pass

    def on_nested_control_element_lost(self, control):
        pass