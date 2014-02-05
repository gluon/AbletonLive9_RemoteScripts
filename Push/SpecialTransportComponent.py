#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/SpecialTransportComponent.py
import Live
from _Framework.SubjectSlot import subject_slot
from _Framework.TransportComponent import TransportComponent
from _Framework.Util import clamp
from consts import MessageBoxText
from MessageBoxComponent import Messenger
INITIAL_SCROLLING_DELAY = 5
INTERVAL_SCROLLING_DELAY = 1

class SpecialTransportComponent(TransportComponent, Messenger):
    """ Transport component that takes buttons for Undo and Redo """

    def __init__(self, *a, **k):
        super(SpecialTransportComponent, self).__init__(*a, **k)
        self._undo_button = None
        self._redo_button = None
        self._shift_button = None
        self._tempo_encoder_control = None
        self._shift_pressed = False
        self._seek_ticks_delay = -1
        self._play_toggle.model_transform = lambda val: False if self._shift_button and self._shift_button.is_pressed() else val

    def update(self):
        super(SpecialTransportComponent, self).update()
        self._update_undo_button()

    def set_shift_button(self, button):
        if self._shift_button != button:
            self._shift_button = button
            self._shift_value.subject = button
            self.update()

    def set_undo_button(self, undo_button):
        if undo_button != self._undo_button:
            self._undo_button = undo_button
            self._undo_value.subject = undo_button
            self._update_undo_button()

    def set_redo_button(self, redo_button):
        if redo_button != self._redo_button:
            self._redo_button = redo_button
            self._redo_value.subject = redo_button
            self.update()

    def set_tempo_encoder(self, control):
        if not (not control or control.message_map_mode() is Live.MidiMap.MapMode.relative_smooth_two_compliment):
            raise AssertionError
            self._tempo_encoder_control = control != self._tempo_encoder_control and control
            self._tempo_encoder_value.subject = control
            self.update()

    @subject_slot('value')
    def _shift_value(self, value):
        self._shift_pressed = value != 0
        if self.is_enabled():
            self.update()

    @subject_slot('value')
    def _undo_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._undo_button.is_momentary():
                if self._shift_button and self._shift_button.is_pressed():
                    if self.song().can_redo:
                        self.song().redo()
                        self.show_notification(MessageBoxText.REDO)
                elif self.song().can_undo:
                    self.song().undo()
                    self.show_notification(MessageBoxText.UNDO)
            self._update_undo_button()

    def _update_undo_button(self):
        if self.is_enabled() and self._undo_button:
            self._undo_button.set_light(self._undo_button.is_pressed())

    @subject_slot('value')
    def _redo_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._redo_button.is_momentary():
                if self.song().can_redo:
                    self.song().redo()

    @subject_slot('value')
    def _tempo_encoder_value(self, value):
        if self.is_enabled():
            step = 0.1 if self._shift_pressed else 1.0
            amount = value - 128 if value >= 64 else value
            self.song().tempo = clamp(self.song().tempo + amount * step, 20, 999)