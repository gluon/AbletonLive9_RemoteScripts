#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\MaschineColorSelectMode.py
import Live
from _Framework.SubjectSlot import subject_slot
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from MIDI_Map import *
from PadScale import *
from MaschineMode import MaschineMode
LIVE_COLOR_SET = (15549221, 12411136, 11569920, 8754719, 5480241, 695438, 31421, 197631, 3101346, 6441901, 8092539, 3947580, 16712965, 12565097, 10927616, 8046132, 4047616, 49071, 1090798, 5538020, 8940772, 10701741, 12008809, 9852725, 16149507, 12581632, 8912743, 1769263, 2490280, 6094824, 1698303, 9160191, 9611263, 12094975, 14183652, 16726484, 16753961, 16773172, 14939139, 14402304, 12492131, 9024637, 15810688, 8962746, 10204100, 8758722, 13011836, 16749734, 16753524, 16772767, 13821080, 12243060, 11119017, 13958625, 13496824, 12173795, 13482980, 13684944, 14673637, 16777215, 15549221, 12411136, 11569920, 8754719)
BASE_COLOR_TABLE = ((115, 127, 127, 16726484),
 (124, 73, 127, 15810688),
 (3, 127, 118, 15549221),
 (0, 125, 127, 16712965),
 (81, 110, 114, 5538020),
 (85, 126, 127, 197631),
 (90, 115, 124, 8940772),
 (105, 115, 114, 14183652),
 (33, 100, 127, 8912743),
 (44, 124, 119, 1769263),
 (55, 119, 127, 2490280),
 (67, 110, 127, 6094824),
 (9, 125, 123, 16149507),
 (12, 107, 127, 16753961),
 (17, 120, 127, 16773172),
 (24, 118, 110, 14939139))
BASE_COLOR_TABLE_2 = ((0, 127, 127, 16712965),
 (9, 125, 123, 16149507),
 (12, 107, 127, 16753961),
 (20, 57, 120, 16772767),
 (20, 127, 127, 14939139),
 (33, 120, 127, 8912743),
 (39, 120, 127, 1769263),
 (46, 127, 90, 5480241),
 (50, 127, 127, 2490280),
 (62, 127, 127, 6094824),
 (74, 127, 127, 9160191),
 (85, 126, 127, 197631),
 (91, 127, 107, 10701741),
 (111, 127, 127, 16726484),
 (124, 127, 107, 12008809),
 (127, 86, 127, 16749734))
MColorMode = 1

class MaschineColorSelectMode(MaschineMode):
    __module__ = __name__
    _palette_off = 0
    _pick_callback = None
    _track_scene_mode = False
    _color_table = None
    _rgb_table = []
    _color_lookup = {}

    def __init__(self, button_index, *a, **k):
        super(MaschineColorSelectMode, self).__init__(button_index, *a, **k)
        list = []
        for c in BASE_COLOR_TABLE:
            color = ((c[0], c[1], c[2]), (c[0], c[1], max(c[2] - 100, 10)))
            list.append(color)
            self._rgb_table.append(c[3])
            self._color_lookup[c[3]] = color

        self._color_table = tuple(list)

    def get_color(self, value, column_index, row_index):
        return PColor.OFF[cindex]

    def notify(self, blink_state):
        pass

    def notify_mono(self, blink_state):
        pass

    def enter_edit_mode(self, type):
        pass

    def exit_edit_mode(self, type):
        pass

    def get_mode_id(self):
        return CLIP_MODE

    def handle_push(self, value):
        if value and self._track_scene_mode:
            self._track_scene_mode = False
            self._pick_callback(0)

    def convertToHSB(self, rgb_color):
        if rgb_color in self._color_lookup:
            return self._color_lookup[rgb_color]
        return toHSB(rgb_color)

    def navigate(self, dir, modifier, alt_modifier = False):
        pass

    def _set_colors_restrict(self, index, button):
        color = self._color_table[index][0]
        button._color = self._rgb_table[index]
        button.send_color_direct(color)

    def _set_colors_full(self, index, button):
        color = LIVE_COLOR_SET[self._palette_off * 12 + index]
        button._color = color
        if self._track_scene_mode and self._palette_off == 4 and index == 15:
            button.send_color_direct((0, 0, 0))
        else:
            button.send_color_direct(toHSB(color)[0])

    def _assign_colors(self):
        bmatrix = self.canonical_parent._bmatrix
        self._encoder_mode_buttons = []
        for button, (column, row) in bmatrix.iterbuttons():
            index = row * 4 + column
            self._set_colors_restrict(index, button)

    def _assign(self, register = True):
        bmatrix = self.canonical_parent._bmatrix
        self._encoder_mode_buttons = []
        for button, (column, row) in bmatrix.iterbuttons():
            if button:
                if register:
                    self.canonical_parent._forwarding_registry[MIDI_NOTE_ON_STATUS, button.get_identifier()] = button
                    self.canonical_parent._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button
                    button.set_to_notemode(False)
                    index = row * 4 + column
                    button._cindex = index
                    self._set_colors_restrict(index, button)
                    button.add_value_listener(self._do_color_assign, True)

    def set_pick_callback(self, callback, track_scene_mode):
        self._pick_callback = callback
        self._track_scene_mode = track_scene_mode

    def in_track_scene_mode(self):
        return self._track_scene_mode

    def _do_color_assign(self, value, button):
        if value != 0 and self._pick_callback:
            if self._track_scene_mode and button._cindex == 15 and self._palette_off == 4:
                self._track_scene_mode = False
                self._pick_callback(0)
            else:
                self._track_scene_mode = False
                self._pick_callback(button._color)

    def _release(self):
        bmatrix = self.canonical_parent._bmatrix
        for button, (column, row) in bmatrix.iterbuttons():
            if button:
                button.remove_value_listener(self._do_color_assign)

    def enter(self):
        self._active = True
        self._assign(True)

    def is_lock_mode(self):
        return True

    def refresh(self):
        if self._active:
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    button.reset()
                    button.refresh()

    def exit(self):
        self._active = False
        self._release()