#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/APC40_MkII/TransportComponent.py
import Live
from _Framework.Control import ButtonControl
from _Framework.SubjectSlot import subject_slot
from _Framework.TransportComponent import TransportComponent as TransportComponentBase
from _Framework.Util import clamp

class TransportComponent(TransportComponentBase):
    shift_button = ButtonControl()

    def __init__(self, *a, **k):

        def play_toggle_model_transform(val):
            return False if self.shift_button.is_pressed else val

        k['play_toggle_model_transform'] = play_toggle_model_transform
        super(TransportComponent, self).__init__(*a, **k)
        self._tempo_encoder_control = None

    def set_tempo_encoder(self, control):
        if not (not control or control.message_map_mode() in (Live.MidiMap.MapMode.relative_smooth_two_compliment, Live.MidiMap.MapMode.relative_two_compliment)):
            raise AssertionError
            self._tempo_encoder_control = control != self._tempo_encoder_control and control
            self._tempo_encoder_value.subject = control
            self.update()

    @subject_slot('value')
    def _tempo_encoder_value(self, value):
        if self.is_enabled():
            step = 0.1 if self.shift_button.is_pressed else 1.0
            amount = value - 128 if value >= 64 else value
            self.song().tempo = clamp(self.song().tempo + amount * step, 20, 999)