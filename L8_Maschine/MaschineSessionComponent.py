#Embedded file name: C:\ProgramData\Ableton\Live 8\Resources\MIDI Remote Scripts\Maschine_Mk1\MaschineSessionComponent.py
import Live
from MIDI_Map import *
from _Framework.InputControlElement import *
from _Framework.ButtonElement import *
from _Framework.SessionComponent import *

class MaschineSessionComponent(SessionComponent):
    __module__ = __name__
    __doc__ = 'Controller Map for Soft Step Foot Controller'

    def __init__(self, parent):
        SessionComponent.__init__(self, 4, 4)
        self._parent = parent
        self._matrix = None
        self._advance = STEP4
        self._mode_button = None
        self._set_mode_button(ButtonElement(False, MIDI_CC_TYPE, 0, 80))
        self._linkoff = 0

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
                self._mode_button.send_value(127)
            else:
                self._advance = STEP1
                self._mode_button.send_value(0)

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

    def _bank_up_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._bank_up_button != None:
                raise AssertionError
                if self.is_enabled():
                    button_is_momentary = self._bank_up_button.is_momentary()
                    if button_is_momentary:
                        self._scroll_up_ticks_delay = value != 0 and INITIAL_SCROLLING_DELAY
                    else:
                        self._scroll_up_ticks_delay = -1
                not self._is_scrolling() and (value is not 0 or not button_is_momentary) and self.set_offsets(self._track_offset, self._scene_offset + self._advance)

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

    def _bank_down_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._bank_down_button != None:
                raise AssertionError
                if self.is_enabled():
                    button_is_momentary = self._bank_down_button.is_momentary()
                    if button_is_momentary:
                        if value != 0:
                            self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
                        else:
                            self._scroll_down_ticks_delay = -1
                    newoff = not self._is_scrolling() and (value is not 0 or not button_is_momentary) and self._scene_offset - self._advance
                    newoff = newoff < 0 and 0
                self.set_offsets(self._track_offset, newoff)

    def _bank_right_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._bank_right_button != None:
                raise AssertionError
                if self.is_enabled():
                    button_is_momentary = self._bank_right_button.is_momentary()
                    if button_is_momentary:
                        self._scroll_right_ticks_delay = value != 0 and INITIAL_SCROLLING_DELAY
                    else:
                        self._scroll_right_ticks_delay = -1
                not self._is_scrolling() and (value is not 0 or not button_is_momentary) and self.set_offsets(self._track_offset + self._advance, self._scene_offset)
                self._parent.notify_track_scroll()

    def _bank_left_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._bank_left_button != None:
                raise AssertionError
                if self.is_enabled():
                    button_is_momentary = self._bank_left_button.is_momentary()
                    if button_is_momentary:
                        self._scroll_left_ticks_delay = value != 0 and INITIAL_SCROLLING_DELAY
                    else:
                        self._scroll_left_ticks_delay = -1
                not self._is_scrolling() and (value is not 0 or not button_is_momentary) and self.set_offsets(max(0, self._track_offset - self._advance), self._scene_offset)
                self._parent.notify_track_scroll()

    def disconnect(self):
        self._parent.remove_listener(self._mode_button, self._do_matrix_adv_mode)
        self._parent = None
        self._matrix = None
        self._mode_button = None
        SessionComponent.disconnect(self)