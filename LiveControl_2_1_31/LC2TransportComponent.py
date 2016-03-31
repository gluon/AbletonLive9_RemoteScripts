#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2TransportComponent.py
from _Framework.TransportComponent import TransportComponent
from LC2Sysex import LC2Sysex
import Live

class LC2TransportComponent(TransportComponent):

    def __init__(self):
        self._launch_quant_button = None
        self._record_quant_button = None
        self._back_to_arranger_button = None
        self._follow_button = None
        self._tempo_up_button = None
        self._tempo_down_button = None
        TransportComponent.__init__(self)
        self.song().add_midi_recording_quantization_listener(self._on_record_quantisation_changed)
        self.song().add_clip_trigger_quantization_listener(self._on_launch_quantisation_changed)
        self.song().add_back_to_arranger_listener(self._on_back_to_arranger_changed)
        self.song().view.add_follow_song_listener(self._on_follow_changed)
        self.send_init()

    def send_init(self):
        self._on_record_quantisation_changed()
        self._on_launch_quantisation_changed()
        self._on_back_to_arranger_changed()
        self._on_follow_changed()

    def disconnect(self):
        self.song().remove_midi_recording_quantization_listener(self._on_record_quantisation_changed)
        self.song().remove_clip_trigger_quantization_listener(self._on_launch_quantisation_changed)
        self.song().remove_back_to_arranger_listener(self._on_back_to_arranger_changed)
        self.song().view.remove_follow_song_listener(self._on_follow_changed)
        if self._record_quant_button is not None:
            self._record_quant_button.remove_value_listener(self._record_quant_value)
        if self._launch_quant_button is not None:
            self._launch_quant_button.remove_value_listener(self._launch_quant_value)
        if self._back_to_arranger_button is not None:
            self._back_to_arranger_button.remove_value_listener(self._back_to_arranger_value)
        if self._follow_button is not None:
            self._follow_button.remove_value_listener(self._follow_value)

    def _on_launch_quantisation_changed(self):
        if self.is_enabled():
            if self._launch_quant_button is not None:
                self._launch_quant_button.send_value(list(Live.Song.Quantization.values).index(self.song().clip_trigger_quantization))

    def set_launch_quant_button(self, button):
        if self._launch_quant_button is not None:
            self._launch_quant_button.remove_value_listener(self._launch_quant_value)
        self._launch_quant_button = button
        if button is not None:
            self._launch_quant_button.add_value_listener(self._launch_quant_value)

    def _launch_quant_value(self, value):
        if self.is_enabled():
            if self._launch_quant_button is not None:
                LC2Sysex.log_message('valu' + str(value))
                self.song().clip_trigger_quantization = Live.Song.Quantization.values[value]

    def _on_record_quantisation_changed(self):
        if self.is_enabled():
            if self._record_quant_button is not None:
                self._record_quant_button.send_value(list(Live.Song.RecordingQuantization.values).index(self.song().midi_recording_quantization))

    def set_record_quant_button(self, button):
        if self._record_quant_button is not None:
            self._record_quant_button.remove_value_listener(self._record_quant_value)
        self._record_quant_button = button
        if button is not None:
            self._record_quant_button.add_value_listener(self._record_quant_value)

    def _record_quant_value(self, value):
        if self.is_enabled():
            if self._launch_quant_button is not None:
                self.song().midi_recording_quantization = Live.Song.RecordingQuantization.values[value]

    def _on_follow_changed(self):
        if self.is_enabled():
            if self._follow_button is not None:
                self._follow_button.send_value(self.song().view.follow_song)

    def set_follow_button(self, button):
        if self._follow_button is not None:
            self._follow_button.remove_value_listener(self._follow_value)
        self._follow_button = button
        if button is not None:
            self._follow_button.add_value_listener(self._follow_value)

    def _follow_value(self, value):
        if self.is_enabled():
            if self._follow_button is not None:
                if not self._follow_button.is_momentary() or value is not 0:
                    self.song().view.follow_song = not self.song().view.follow_song

    def _on_back_to_arranger_changed(self):
        if self.is_enabled():
            if self._back_to_arranger_button is not None:
                self._back_to_arranger_button.send_value(self.song().back_to_arranger)

    def set_back_to_arranger_button(self, button):
        if self._back_to_arranger_button is not None:
            self._back_to_arranger_button.remove_value_listener(self._back_to_arranger_value)
        self._back_to_arranger_button = button
        if button is not None:
            self._back_to_arranger_button.add_value_listener(self._back_to_arranger_value)

    def _back_to_arranger_value(self, value):
        if self.is_enabled():
            if not self._back_to_arranger_button.is_momentary() or value is not 0:
                self.song().back_to_arranger = not self.song().back_to_arranger

    def set_tempo_buttons(self, up, down):
        if self._tempo_up_button is not None:
            self._tempo_up_button.remove_value_listener(self._tempo_up_value)
        if self._tempo_down_button is not None:
            self._tempo_down_button.remove_value_listener(self._tempo_down_value)
        self._tempo_up_button = up
        self._tempo_down_button = down
        if up is not None:
            self._tempo_up_button.add_value_listener(self._tempo_up_value)
        if down is not None:
            self._tempo_down_button.add_value_listener(self._tempo_down_value)

    def _tempo_up_value(self, value):
        if self.is_enabled():
            if value:
                if self.song().tempo < 999:
                    self.song().tempo = self.song().tempo + 1

    def _tempo_down_value(self, value):
        if self.is_enabled():
            if value:
                if self.song().tempo > 0:
                    self.song().tempo = self.song().tempo - 1