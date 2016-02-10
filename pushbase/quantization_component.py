#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/quantization_component.py
from __future__ import absolute_import, print_function
import Live
from ableton.v2.base import clamp, listenable_property, listens
from ableton.v2.control_surface import Component, CompoundComponent
from ableton.v2.control_surface.control import ButtonControl, EncoderControl, StepEncoderControl, ToggleButtonControl
from .consts import MessageBoxText, SIDE_BUTTON_COLORS
from .message_box_component import Messenger
RecordingQuantization = Live.Song.RecordingQuantization
QUANTIZATION_OPTIONS = [RecordingQuantization.rec_q_quarter,
 RecordingQuantization.rec_q_eight,
 RecordingQuantization.rec_q_eight_triplet,
 RecordingQuantization.rec_q_eight_eight_triplet,
 RecordingQuantization.rec_q_sixtenth,
 RecordingQuantization.rec_q_sixtenth_triplet,
 RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
 RecordingQuantization.rec_q_thirtysecond]
DEFAULT_QUANTIZATION_INDEX = QUANTIZATION_OPTIONS.index(RecordingQuantization.rec_q_sixtenth)
QUANTIZATION_NAMES = ('1/4', '1/8', '1/8t', '1/8+t', '1/16', '1/16t', '1/16+t', '1/32')
QUANTIZATION_NAMES_UNICODE = (u'\xbc', u'\u215b', u'\u215bt', u'\u215b+t', u'\ue001', u'\ue001t', u'\ue001+t', u'\ue002')

def quantize_amount_to_string(amount):
    """
    Converts a quantize amount [0. to 1.] into a string in percent
    """
    return '%i%%' % int(amount * 100.0)


class QuantizationSettingsComponent(Component):
    swing_amount_encoder = EncoderControl()
    quantize_to_encoder = StepEncoderControl()
    quantize_amount_encoder = EncoderControl()
    record_quantization_encoder = StepEncoderControl()
    record_quantization_toggle_button = ToggleButtonControl(toggled_color='Recording.FixedLengthRecordingOn', untoggled_color='Recording.FixedLengthRecordingOff')
    quantize_amount = listenable_property.managed(1.0)
    quantize_to_index = listenable_property.managed(DEFAULT_QUANTIZATION_INDEX)
    record_quantization_index = listenable_property.managed(DEFAULT_QUANTIZATION_INDEX)

    def __init__(self, quantization_names = QUANTIZATION_NAMES, *a, **k):
        super(QuantizationSettingsComponent, self).__init__(*a, **k)
        self._quantization_names = quantization_names
        self.__on_swing_amount_changed.subject = self.song
        self.__on_record_quantization_changed.subject = self.song
        self.__on_record_quantization_changed()

    @property
    def quantize_to(self):
        return QUANTIZATION_OPTIONS[self.quantize_to_index]

    @listenable_property
    def swing_amount(self):
        return self.song.swing_amount

    @listenable_property
    def record_quantization_enabled(self):
        return self.record_quantization_toggle_button.is_toggled

    @property
    def quantization_option_names(self):
        return self._quantization_names

    @property
    def selected_quantization_name(self):
        return self.quantization_option_names[self.quantize_to_index]

    @swing_amount_encoder.value
    def swing_amount_encoder(self, value, encoder):
        self.song.swing_amount = clamp(self.song.swing_amount + value * 0.5, 0.0, 0.5)

    @staticmethod
    def _clamp_quantization_index(index):
        return clamp(index, 0, len(QUANTIZATION_OPTIONS) - 1)

    @quantize_to_encoder.value
    def quantize_to_encoder(self, value, encoder):
        self.quantize_to_index = self._clamp_quantization_index(self.quantize_to_index + value)

    @quantize_amount_encoder.value
    def quantize_amount_encoder(self, value, encoder):
        self.quantize_amount = clamp(self.quantize_amount + value, 0.0, 1.0)

    @record_quantization_encoder.value
    def record_quantization_encoder(self, value, encoder):
        self.record_quantization_index = self._clamp_quantization_index(self.record_quantization_index + value)
        self._update_record_quantization()

    @record_quantization_toggle_button.toggled
    def record_quantization_toggle_button(self, value, button):
        self._update_record_quantization()

    @listens('swing_amount')
    def __on_swing_amount_changed(self):
        self.notify_swing_amount()

    @listens('midi_recording_quantization')
    def __on_record_quantization_changed(self):
        quant_value = self.song.midi_recording_quantization
        quant_on = quant_value != RecordingQuantization.rec_q_no_q
        if quant_value in QUANTIZATION_OPTIONS:
            self.record_quantization_index = QUANTIZATION_OPTIONS.index(quant_value)
        self.record_quantization_toggle_button.is_toggled = quant_on
        self.notify_record_quantization_enabled(quant_on)

    def _update_record_quantization(self):
        index = QUANTIZATION_OPTIONS[self.record_quantization_index]
        self.song.midi_recording_quantization = index if self.record_quantization_toggle_button.is_toggled else RecordingQuantization.rec_q_no_q


class QuantizationComponent(CompoundComponent, Messenger):
    action_button = ButtonControl(**SIDE_BUTTON_COLORS)

    def __init__(self, settings = None, *a, **k):
        raise settings is not None or AssertionError
        super(QuantizationComponent, self).__init__(*a, **k)
        self._settings = self.register_component(settings)
        self._settings.set_enabled(False)
        self._cancel_quantize = False

    def quantize_pitch(self, note):
        clip = self.song.view.detail_clip
        if clip:
            clip.quantize_pitch(note, self._settings.quantize_to, self._settings.quantize_amount)
            self.show_notification(MessageBoxText.QUANTIZE_CLIP_PITCH % dict(amount=quantize_amount_to_string(self._settings.quantize_amount), to=self._settings.selected_quantization_name))
        self._cancel_quantize = True

    @action_button.pressed_delayed
    def action_button(self, button):
        self._settings.set_enabled(True)

    @action_button.released_delayed
    def hide_settings(self, button):
        self._settings.set_enabled(False)
        self._cancel_quantize = False

    @action_button.released_immediately
    def action_button(self, button):
        clip = self.song.view.detail_clip
        if clip and not self._cancel_quantize:
            clip.quantize(self._settings.quantize_to, self._settings.quantize_amount)
            self.show_notification(MessageBoxText.QUANTIZE_CLIP % dict(amount=quantize_amount_to_string(self._settings.quantize_amount), to=self._settings.selected_quantization_name))
        self._cancel_quantize = False