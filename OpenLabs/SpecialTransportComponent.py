#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/OpenLabs/SpecialTransportComponent.py
import Live
from _Framework.TransportComponent import TransportComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement

class SpecialTransportComponent(TransportComponent):
    """ Transport component that takes buttons for Undo and Redo """

    def __init__(self):
        TransportComponent.__init__(self)
        self._undo_button = None
        self._redo_button = None
        self._bts_button = None

    def disconnect(self):
        TransportComponent.disconnect(self)
        if self._undo_button != None:
            self._undo_button.remove_value_listener(self._undo_value)
            self._undo_button = None
        if self._redo_button != None:
            self._redo_button.remove_value_listener(self._redo_value)
            self._redo_button = None
        if self._bts_button != None:
            self._bts_button.remove_value_listener(self._bts_value)
            self._bts_button = None

    def set_undo_button(self, undo_button):
        if not isinstance(undo_button, (ButtonElement, type(None))):
            raise AssertionError
            if undo_button != self._undo_button:
                if self._undo_button != None:
                    self._undo_button.remove_value_listener(self._undo_value)
                self._undo_button = undo_button
                self._undo_button != None and self._undo_button.add_value_listener(self._undo_value)
            self.update()

    def set_redo_button(self, redo_button):
        if not isinstance(redo_button, (ButtonElement, type(None))):
            raise AssertionError
            if redo_button != self._redo_button:
                if self._redo_button != None:
                    self._redo_button.remove_value_listener(self._redo_value)
                self._redo_button = redo_button
                self._redo_button != None and self._redo_button.add_value_listener(self._redo_value)
            self.update()

    def set_bts_button(self, bts_button):
        if not isinstance(bts_button, (ButtonElement, type(None))):
            raise AssertionError
            if bts_button != self._bts_button:
                if self._bts_button != None:
                    self._bts_button.remove_value_listener(self._bts_value)
                self._bts_button = bts_button
                self._bts_button != None and self._bts_button.add_value_listener(self._bts_value)
            self.update()

    def _undo_value(self, value):
        if not self._undo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled():
                    (value != 0 or not self._undo_button.is_momentary()) and self.song().can_undo and self.song().undo()

    def _redo_value(self, value):
        if not self._redo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled():
                    (value != 0 or not self._redo_button.is_momentary()) and self.song().can_redo and self.song().redo()

    def _bts_value(self, value):
        if not self._bts_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self.song().current_song_time = self.is_enabled() and (value != 0 or not self._bts_button.is_momentary()) and 0.0