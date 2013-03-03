#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC40/ShiftableTransportComponent.py
import Live
from _Framework.TransportComponent import TransportComponent
from _Framework.ButtonElement import ButtonElement

class ShiftableTransportComponent(TransportComponent):
    """ TransportComponent that only uses certain buttons if a shift button is pressed """

    def __init__(self):
        TransportComponent.__init__(self)
        self._shift_button = None
        self._quant_toggle_button = None
        self._shift_pressed = False
        self._last_quant_value = Live.Song.RecordingQuantization.rec_q_eight
        self.song().add_midi_recording_quantization_listener(self._on_quantisation_changed)
        self._on_quantisation_changed()

    def disconnect(self):
        TransportComponent.disconnect(self)
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None
        if self._quant_toggle_button != None:
            self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
            self._quant_toggle_button = None
        self.song().remove_midi_recording_quantization_listener(self._on_quantisation_changed)

    def set_shift_button(self, button):
        if not (button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            raise AssertionError
            if self._shift_button != button:
                if self._shift_button != None:
                    self._shift_button.remove_value_listener(self._shift_value)
                self._shift_button = button
                self._shift_button != None and self._shift_button.add_value_listener(self._shift_value)
            self.update()

    def set_quant_toggle_button(self, button):
        if not (button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            raise AssertionError
            if self._quant_toggle_button != button:
                if self._quant_toggle_button != None:
                    self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
                self._quant_toggle_button = button
                self._quant_toggle_button != None and self._quant_toggle_button.add_value_listener(self._quant_toggle_value)
            self.update()

    def update(self):
        pass

    def _shift_value(self, value):
        self._shift_pressed = value != 0
        if self.is_enabled():
            self._overdub_toggle.set_enabled(not self._shift_pressed)
            self._metronome_toggle.set_enabled(not self._shift_pressed)
            self.update()

    def _quant_toggle_value(self, value):
        if not self._last_quant_value != Live.Song.RecordingQuantization.rec_q_no_q:
            raise AssertionError
            if self.is_enabled() and not self._shift_pressed:
                if value != 0 or not self._quant_toggle_button.is_momentary():
                    quant_value = self.song().midi_recording_quantization
                    self._last_quant_value = quant_value != Live.Song.RecordingQuantization.rec_q_no_q and quant_value
                    self.song().midi_recording_quantization = Live.Song.RecordingQuantization.rec_q_no_q
                else:
                    self.song().midi_recording_quantization = self._last_quant_value

    def _on_quantisation_changed(self):
        if self.is_enabled():
            quant_value = self.song().midi_recording_quantization
            quant_on = quant_value != Live.Song.RecordingQuantization.rec_q_no_q
            if quant_on:
                self._last_quant_value = quant_value
            if not self._shift_pressed and self._quant_toggle_button != None:
                if quant_on:
                    self._quant_toggle_button.turn_on()
                else:
                    self._quant_toggle_button.turn_off()