#Embedded file name: /Applications/Ableton Live 8.app/Contents/App-Resources/MIDI Remote Scripts/QuNeo/SpecialTransportComponent.py
import Live
from _Framework.TransportComponent import TransportComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import InputControlElement
from MIDI_Map import TEMPO_TOP
from MIDI_Map import TEMPO_BOTTOM

class SpecialTransportComponent(TransportComponent):
    """ TransportComponent that only uses certain buttons if a shift button is pressed """

    def __init__(self):
        TransportComponent.__init__(self)
        self._tempo_encoder_control = None
        self._tempo_down_button = None
        self._tempo_up_button = None
        self._tempo_session_value = self.song().tempo

    def disconnect(self):
        TransportComponent.disconnect(self)
        if self._tempo_encoder_control != None:
            self._tempo_encoder_control.remove_value_listener(self._tempo_encoder_value)
            self._tempo_encoder_control = None
        if self._tempo_down_button != None:
            self._tempo_down_button.remove_value_listener(self._tempo_down_value)
            self._tempo_down_button = None
        if self._tempo_up_button != None:
            self._tempo_up_button.remove_value_listener(self._tempo_up_value)
            self._tempo_up_button = None

    def _tempo_encoder_value(self, value):
        if not self._tempo_encoder_control != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            backwards = value >= 64
            step = 0.1
            amount = backwards and value - 128
        else:
            amount = value
        tempo = max(20, min(999, self.song().tempo + amount * step))
        self.song().tempo = tempo

    def _tempo_up_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._tempo_up_button != None:
                raise AssertionError
                if self.is_enabled():
                    new_tempo = value != 0 and 1.0
                    real_tempo = new_tempo + self.song().tempo
                    real_tempo = real_tempo < 20.0 and 20.0
                self.update_tempo(real_tempo)
            else:
                None

    def _tempo_down_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._tempo_up_button != None:
                raise AssertionError
                if self.is_enabled():
                    new_tempo = value != 0 and -1.0
                    real_tempo = new_tempo + self.song().tempo
                    real_tempo = real_tempo > 200.0 and 200.0
                self.update_tempo(real_tempo)
            else:
                None

    def update_tempo(self, value):
        if value != None:
            new_tempo = value
            self.song().tempo = new_tempo

    def set_tempo_buttons(self, up_button, down_button):
        if not (up_button == None or isinstance(up_button, ButtonElement)):
            raise AssertionError
            if not (down_button == None or isinstance(down_button, ButtonElement)):
                raise AssertionError
                if self._tempo_up_button != None:
                    self._tempo_up_button.remove_value_listener(self._tempo_up_value)
                self._tempo_up_button = up_button
                if self._tempo_up_button != None:
                    self._tempo_up_button.add_value_listener(self._tempo_up_value)
                self._tempo_down_button != None and self._tempo_down_button.remove_value_listener(self._tempo_down_value)
            self._tempo_down_button = down_button
            self._tempo_down_button != None and self._tempo_down_button.add_value_listener(self._tempo_down_value)
        self.update()

    def set_tempo_encoder(self, control):
        if not (control == None or isinstance(control, EncoderElement) and control.message_map_mode() is Live.MidiMap.MapMode.relative_two_compliment):
            raise AssertionError
            if self._tempo_encoder_control != None:
                self._tempo_encoder_control.remove_value_listener(self._tempo_encoder_value)
            self._tempo_encoder_control = control
            self._tempo_encoder_control != None and self._tempo_encoder_control.add_value_listener(self._tempo_encoder_value)
        self.update()

    def _tempo_value(self, value):
        if not self._tempo_control != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            fraction = self.is_enabled() and (TEMPO_TOP - TEMPO_BOTTOM) / 127.0
            self.song().tempo = fraction * value + TEMPO_BOTTOM