#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk1\MaschineSessionComponent.py
import Live
from MIDI_Map import *
from _Framework.InputControlElement import *
from _Framework.ButtonElement import *
from _Framework.SessionComponent import *

class MaschineSessionComponent(SessionComponent):
    __module__ = __name__
    __doc__ = 'Controller Map for Soft Step Foot Controller'

    def __init__(self):
        SessionComponent.__init__(self, 4, 4)
        self._matrix = None
        self._advance = STEP4
        self._mode_button = None
        self._set_mode_button(ButtonElement(False, MIDI_CC_TYPE, 0, 80))
        self._linkoff = 0
        self.set_track_banking_increment(STEP4)

    def _link(self):
        pass

    def get_track_offset(self):
        return self._track_offset + self._linkoff

    def get_scene_offset(self):
        return self._scene_offset

    def set_matrix(self, matrix):
        self._matrix = matrix

    def _set_mode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._mode_button != None:
                self._mode_button.remove_value_listener(self._do_matrix_adv_mode)
            self._mode_button = button
            if self._mode_button != None:
                self._mode_button.add_value_listener(self._do_matrix_adv_mode)
            self._advance == STEP4 and self._mode_button.send_value(127)
        else:
            self._mode_button.send_value(0)

    def _do_matrix_adv_mode(self, value):
        if not self._mode_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self._advance = value != 0 and self._advance == STEP1 and STEP4
                self._mode_button.send_value(127, True)
                self.set_track_banking_increment(STEP4)
            else:
                self._advance = STEP1
                self._mode_button.send_value(0, True)
                self.set_track_banking_increment(STEP1)

    def set_advance(self, val):
        self._advance = val
        if self._advance == STEP4:
            self._mode_button.send_value(127)
        else:
            self._mode_button.send_value(0)

    def update(self):
        SessionComponent.update(self)
        try:
            self._advance
        except AttributeError:
            pass
        else:
            if self._advance == STEP4:
                self._mode_button.send_value(127)
            else:
                self._mode_button.send_value(0)

    def notify_b(self, blink):
        if blink > 5:
            blinkslow = 0
        else:
            blinkslow = 1
        blinkfast = blink % 2
        for scene_index in range(4):
            scene = self.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)._clip_slot
                if clip_slot != None and clip_slot.has_clip:
                    button = self._matrix[scene_index][track_index]
                    if button != None:
                        if clip_slot.clip.is_triggered:
                            button.send_value(blinkfast * 1)
                        elif clip_slot.clip.is_playing:
                            button.send_value(blinkslow * 1)
                elif clip_slot != None:
                    button = self._matrix[scene_index][track_index]
                    if button != None:
                        if clip_slot.is_triggered:
                            button.send_value(blinkfast * 1)
                        elif clip_slot.is_playing:
                            button.send_value(blinkslow * 1)

    def bank_down(self):
        if self.is_enabled():
            newoff = max(0, self._scene_offset - 1)
            self.set_offsets(self._track_offset, newoff)

    def bank_up(self):
        if self.is_enabled():
            self.set_offsets(self._track_offset, self._scene_offset + 1)

    def bank_left(self):
        if self.is_enabled():
            self.set_offsets(max(0, self._track_offset - 1), self._scene_offset)

    def bank_right(self):
        if self.is_enabled():
            self.set_offsets(self._track_offset + 1, self._scene_offset)

    def disconnect(self):
        self._matrix = None
        self._mode_button = None
        SessionComponent.disconnect(self)