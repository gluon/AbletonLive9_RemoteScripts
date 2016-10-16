#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/QuantizationComponent.py
import Live
RecordingQuantization = Live.Song.RecordingQuantization
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import clamp, forward_property, recursive_map
from ActionWithOptionsComponent import ActionWithSettingsComponent
from consts import MessageBoxText
from MessageBoxComponent import Messenger
QUANTIZATION_OPTIONS = [RecordingQuantization.rec_q_quarter,
 RecordingQuantization.rec_q_eight,
 RecordingQuantization.rec_q_eight_triplet,
 RecordingQuantization.rec_q_eight_eight_triplet,
 RecordingQuantization.rec_q_sixtenth,
 RecordingQuantization.rec_q_sixtenth_triplet,
 RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
 RecordingQuantization.rec_q_thirtysecond]
QUANTIZATION_NAMES = ('1/4', '1/8', '1/8t', '1/8+t', '1/16', '1/16t', '1/16+t', '1/32')

def record_quantization_to_float(quantize):
    return float(list(QUANTIZATION_OPTIONS).index(quantize)) / float(len(QUANTIZATION_OPTIONS) - 1)


def float_to_record_quantization(quantize):
    return QUANTIZATION_OPTIONS[int(quantize * (len(QUANTIZATION_OPTIONS) - 1))]


class QuantizationSettingsComponent(ControlSurfaceComponent):

    def __init__(self, *a, **k):
        super(QuantizationSettingsComponent, self).__init__(*a, **k)
        self._display_lines = recursive_map(DisplayDataSource, (('', '', '', '', '', '', '', ''),
         ('Swing', 'Quantize', 'Quantize', '', '', '', '', 'Record'),
         ('Amount', 'To', 'Amount', '', '', '', '', 'Quantize'),
         ('', '', '', '', '', '', '', '')))
        self._swing_amount_display = self._display_lines[0][0]
        self._quantize_to_display = self._display_lines[0][1]
        self._quantize_amount_display = self._display_lines[0][2]
        self._record_quantization_display = self._display_lines[0][7]
        self._record_quantization_on_display = self._display_lines[3][7]
        default_quantize = RecordingQuantization.rec_q_sixtenth
        self._record_quantization = default_quantize
        self._quantize_to = default_quantize
        self._quantize_amount = 1.0
        default_quantize_float = record_quantization_to_float(default_quantize)
        self._record_quantization_float = default_quantize_float
        self._quantize_to_float = default_quantize_float
        self._on_swing_amount_changed_in_live.subject = self.song()
        self._on_swing_amount_changed_in_live()
        self._on_record_quantization_changed_in_live.subject = self.song()
        self._on_record_quantization_changed_in_live()
        self._update_swing_amount_display()
        self._update_quantize_to_display()
        self._update_quantize_amount_display()

    def update(self):
        super(QuantizationSettingsComponent, self).update()
        self._update_record_quantization_button()

    def set_display_line1(self, line):
        self._set_display_line(line, 0)

    def set_display_line2(self, line):
        self._set_display_line(line, 1)

    def set_display_line3(self, line):
        self._set_display_line(line, 2)

    def set_display_line4(self, line):
        self._set_display_line(line, 3)

    def _set_display_line(self, line, index):
        if line:
            line.set_num_segments(8)
            for segment in xrange(8):
                line.segment(segment).set_data_source(self._display_lines[index][segment])

    def set_encoder_controls(self, encoders):
        if encoders:
            self._on_swing_amount_value.subject = encoders[0]
            self._on_quantize_to_value.subject = encoders[1]
            self._on_quantize_amount_value.subject = encoders[2]
            self._on_record_quantization_value.subject = encoders[7]
        else:
            self._on_swing_amount_value.subject = None
            self._on_quantize_to_value.subject = None
            self._on_quantize_amount_value.subject = None
            self._on_record_quantization_value.subject = None

    def set_select_buttons(self, buttons):
        self._on_record_quantization_on_value.subject = buttons[7] if buttons else None
        if buttons:
            for button in filter(bool, buttons):
                button.reset()

        self._update_record_quantization_button()

    def set_state_buttons(self, buttons):
        if buttons:
            buttons.reset()

    def _update_record_quantization(self):
        self.song().midi_recording_quantization = self._record_quantization if self._record_quantization_on else RecordingQuantization.rec_q_no_q

    def _update_swing_amount_display(self):
        display = str(int(self.song().swing_amount * 200.0)) + '%'
        self._swing_amount_display.set_display_string(display)

    def _update_record_quantization_display(self):
        index = QUANTIZATION_OPTIONS.index(self._record_quantization)
        self._record_quantization_display.set_display_string(QUANTIZATION_NAMES[index])
        self._record_quantization_on_display.set_display_string('[  On  ]' if self._record_quantization_on else '[  Off ]')

    def _update_record_quantization_button(self):
        if self.is_enabled():
            button = self._on_record_quantization_on_value.subject
            if button:
                button.set_on_off_values('Option.On', 'Option.Off')
                if self._record_quantization_on:
                    self._on_record_quantization_on_value.subject.turn_on()
                else:
                    self._on_record_quantization_on_value.subject.turn_off()

    def _update_quantize_to_display(self):
        index = QUANTIZATION_OPTIONS.index(self._quantize_to)
        self._quantize_to_display.set_display_string(QUANTIZATION_NAMES[index])

    def _update_quantize_amount_display(self):
        self._quantize_amount_display.set_display_string(str(int(self._quantize_amount * 100)) + '%')

    @subject_slot('normalized_value')
    def _on_swing_amount_value(self, value):
        self.song().swing_amount = clamp(self.song().swing_amount + value * 0.5, 0.0, 0.5)

    @subject_slot('normalized_value')
    def _on_quantize_to_value(self, value):
        self._quantize_to_float = clamp(self._quantize_to_float + value, 0.0, 1.0)
        self._quantize_to = float_to_record_quantization(self._quantize_to_float)
        self._update_quantize_to_display()

    @subject_slot('normalized_value')
    def _on_quantize_amount_value(self, value):
        self._quantize_amount = clamp(self._quantize_amount + value, 0.0, 1.0)
        self._update_quantize_amount_display()

    @subject_slot('normalized_value')
    def _on_record_quantization_value(self, value):
        self._record_quantization_float = clamp(self._record_quantization_float + value, 0.0, 1.0)
        self._record_quantization = float_to_record_quantization(self._record_quantization_float)
        self._update_record_quantization()
        self._update_record_quantization_display()

    @subject_slot('value')
    def _on_record_quantization_on_value(self, value):
        if value:
            self._record_quantization_on = not self._record_quantization_on
            self._update_record_quantization()

    @subject_slot('swing_amount')
    def _on_swing_amount_changed_in_live(self):
        self._update_swing_amount_display()

    @subject_slot('midi_recording_quantization')
    def _on_record_quantization_changed_in_live(self):
        quant_value = self.song().midi_recording_quantization
        quant_on = quant_value != RecordingQuantization.rec_q_no_q
        if quant_value in QUANTIZATION_OPTIONS:
            self._record_quantization = quant_value
            if self._on_record_quantization_value.subject:
                quant_value_float = self._on_record_quantization_value.subject.is_pressed() or record_quantization_to_float(quant_value)
                self._record_quantization_float = quant_value_float
        self._record_quantization_on = quant_on
        self._update_record_quantization_display()
        self._update_record_quantization_button()


class QuantizationComponent(ActionWithSettingsComponent, Messenger):
    settings_layer = forward_property('_settings')('layer')

    def __init__(self, *a, **k):
        super(QuantizationComponent, self).__init__(*a, **k)
        self._settings = self.register_component(QuantizationSettingsComponent())
        self._settings.set_enabled(False)
        self._cancel_quantize = False

    def quantize_pitch(self, note):
        clip = self.song().view.detail_clip
        if clip:
            clip.quantize_pitch(note, self._settings._quantize_to, self._settings._quantize_amount)
            self.show_notification(MessageBoxText.QUANTIZE_CLIP_PITCH % dict(amount=self._settings._quantize_amount_display.display_string(), to=self._settings._quantize_to_display.display_string()))
        self._cancel_quantize = True

    def show_settings(self):
        self._settings.set_enabled(True)
        return True

    def hide_settings(self):
        self._settings.set_enabled(False)
        self._cancel_quantize = False

    def post_trigger_action(self):
        clip = self.song().view.detail_clip
        if clip and not self._cancel_quantize:
            clip.quantize(self._settings._quantize_to, self._settings._quantize_amount)
            self.show_notification(MessageBoxText.QUANTIZE_CLIP % dict(amount=self._settings._quantize_amount_display.display_string(), to=self._settings._quantize_to_display.display_string()))
        self._cancel_quantize = False