#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_static/midi-remote-scripts/_Framework/EncoderElement.py
import Live
from SubjectSlot import SubjectEvent
from InputControlElement import InputControlElement, MIDI_CC_TYPE, InputSignal
from Util import nop

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