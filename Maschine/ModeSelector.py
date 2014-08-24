#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\ModeSelector.py
from __future__ import with_statement
import Live
from contextlib import contextmanager
from _Framework.CompoundComponent import CompoundComponent
from _Framework.InputControlElement import *
from StateButton import StateButton
from SceneMode import SceneMode
from DrumMode import DrumMode
from PadMode import PadMode
from ControlMode import ControlMode
from TrackModMode import *
from MaschineColorSelectMode import MaschineColorSelectMode
from GatedColorButton import GatedColorButton
from MaschineMode import MaschineMode, StudioClipMode, find_drum_device
from MIDI_Map import *
from _Framework.SubjectSlot import subject_slot

class ModeSelector(CompoundComponent):
    """
    Class Handling the switch between Modes.
    """
    __module__ = __name__
    mikro_shift = False
    _md_select_mode = None
    _md_solo_mode = None
    _md_mute_mode = None
    _knob_section = None
    _clip_mode_down = False
    _monochrome = False

    def __init__(self, monochrome = False, *a, **k):
        super(ModeSelector, self).__init__(*a, **k)
        is_momentary = True
        self._monochrome = monochrome
        self._scene_mode = SceneMode(0)
        self._clip_mode = StudioClipMode(1)
        self._pad_mode = PadMode(2, monochrome)
        self._drum_mode = DrumMode(2, monochrome)
        self._control_mode = ControlMode(2, monochrome)
        self._pad_mode.set_alternate_mode(self._drum_mode)
        self._drum_mode.set_alternate_mode(self._pad_mode)
        self._tracks_assign = TrackAssign()
        self._arm_mode = TrackArmMode(self._tracks_assign)
        self._solo_mode = TrackSoloMode(self._tracks_assign)
        self._stop_mode = TrackStopMode(self._tracks_assign)
        self._mute_mode = TrackMuteMode(self._tracks_assign)
        self._select_mode = TrackSelectMode(self._tracks_assign)
        self._xfade_mode = TrackXFadeMode(self._tracks_assign)
        self._color_select_mode = MaschineColorSelectMode(5)
        self._mode = self._clip_mode
        self._return_mode = None

        def create_button(ccval, channel = 0):
            return StateButton(is_momentary, MIDI_CC_TYPE, channel, ccval)

        self._scene_mode_button = create_button(112)
        self._clip_mode_button = create_button(113)
        self._pad_mode_button = create_button(114)
        self._select_button = create_button(117)
        self._solo_button = create_button(118)
        self._mute_button = create_button(119)
        self._xfade_button = self.canonical_parent.create_gated_button(84, 5)
        self._stop_button = self.canonical_parent.create_gated_button(94, 16)
        self._arm_button = self.canonical_parent.create_gated_button(83, 0)
        self._solo_button = StateButton(False, MIDI_CC_TYPE, 0, 118)
        self._clip_mode_button.send_value(127, True)
        self._select_clip_mode.subject = self._clip_mode_button
        self._select_scene_mode.subject = self._scene_mode_button
        self._select_pad_mode.subject = self._pad_mode_button
        self._select_arm.subject = self._arm_button
        self._select_solo.subject = self._solo_button
        self._select_stop.subject = self._stop_button
        self._select_xfade.subject = self._xfade_button
        self._select_mute.subject = self._mute_button
        self._select_select.subject = self._select_button
        self._arm_exclusive_button = create_button(51, 2)
        self._action_arm_exclusive.subject = self._arm_exclusive_button
        self._solo_exclusive_button = create_button(52, 2)
        self._action_solo_exclusive.subject = self._solo_exclusive_button
        self._scene_mode_button.send_value(0, True)
        self._clip_mode_button.send_value(1, True)
        self._pad_mode_button.send_value(0, True)
        self._mode._active = True

    def mode(self):
        return self._mode

    def update(self):
        pass

    def get_color_manager(self):
        return self._color_select_mode

    def get_color(self, value, column_index, row_index):
        return self._mode.get_color(value, column_index, row_index)

    def connect_main_knob(self, knobsection):
        self._control_mode.connect_main_knob(knobsection)

    def assign_edit_section(self, editsection):
        self._scene_mode.set_edit_mode(editsection)
        self._pad_mode.set_edit_mode(editsection)
        self._drum_mode.set_edit_mode(editsection)

    def navigate(self, dir, modifier, alt_modifier = False):
        self._mode.navigate(dir, modifier, alt_modifier)

    def notify(self, blink_state):
        self._mode.notify(blink_state)
        if self._mode == self._clip_mode or self._mode == self._color_select_mode:
            if self.canonical_parent._editsection.is_color_edit():
                if self._color_select_mode.in_track_scene_mode():
                    bval = blink_state % 2
                else:
                    bval = blink_state / 2
                self._clip_mode_button.send_value(bval)
            else:
                self._clip_mode_button.send_value(1)

    def notify_mono(self, blink_state):
        self._mode.notify_mono(blink_state)

    def enter_edit_mode(self, type):
        self._mode.enter_edit_mode(type)

    def exit_edit_mode(self, type):
        self._mode.exit_edit_mode(type)

    def enter_clear_state(self):
        self._mode.enter_clear_state()

    def exit_clear_state(self):
        self._mode.exit_clear_state()

    def _device_changed(self):
        self._mode._device_changed()

    def refresh(self):
        self._mode.refresh()
        self._stop_button.activate()
        self._arm_button.activate()
        self._xfade_button.activate()

    @contextmanager
    def rebuild(self):
        self.canonical_parent._set_suppress_rebuild_requests(True)
        yield
        self.canonical_parent._set_suppress_rebuild_requests(False)
        self.canonical_parent.request_rebuild_midi_map()

    def _light_button(self, which):
        self._scene_mode_button.send_value(which == 0 and 1 or 0, True)
        self._clip_mode_button.send_value(which == 1 and 1 or 0, True)
        self._pad_mode_button.send_value(which == 2 and 1 or 0, True)

    def change_mode(self, nextmode):
        return self._mode != nextmode and (self._mode == None or self._mode.is_lock_mode())

    def set_shift_state(self, state):
        self.mikro_shift = state

    def show_messsage(self, msg):
        self.canonical_parent.show_message(msg)

    def handle_push(self, value):
        if self._mode:
            self._mode.handle_push(value)

    def pick_color(self, cscomponent):
        shift_down = self.canonical_parent.isShiftDown()

        def set_color(rgb_value):
            if self.canonical_parent.isShiftDown():
                if shift_down:
                    track = cscomponent._clip_slot.canonical_parent
                    scenes = self.song().scenes
                    index = vindexof(track.clip_slots, cscomponent._clip_slot)
                    scenes[index].color = rgb_value
                else:
                    track = cscomponent._clip_slot.canonical_parent
                    for cs in track.clip_slots:
                        if cs.has_clip:
                            cs.clip.color = rgb_value

            elif shift_down:
                track = cscomponent._clip_slot.canonical_parent
                track.color = rgb_value
            elif cscomponent._clip_slot.clip != None:
                cscomponent._clip_slot.clip.color = rgb_value

        def color_picked(color_rgb):
            set_color(color_rgb)
            if self._mode == self._color_select_mode:
                with self.rebuild():
                    self._mode.exit()
                    self._mode = self._clip_mode
                    self._mode.enter()

        self._color_select_mode.set_pick_callback(color_picked, shift_down)
        self._into_mode(self._color_select_mode, 'Color Chooser')

    def _into_mode(self, mode, info):
        if self._mode != None and self._mode != mode and not self._mode.is_lock_mode():
            return
        with self.rebuild():
            self._return_mode = self._mode
            self._mode.exit()
            self._mode = mode
            self._mode.enter()

    @subject_slot('value')
    def _select_scene_mode(self, value):
        if value > 0:
            if self.mikro_shift:
                if self.change_mode(self._control_mode):
                    with self.rebuild():
                        self._mode.exit()
                        self._mode = self._control_mode
                        self._light_button(0)
                        self._mode.enter()
            elif self.change_mode(self._scene_mode):
                with self.rebuild():
                    self._mode.exit()
                    self._mode = self._scene_mode
                    self._light_button(0)
                    self._mode.enter()

    @subject_slot('value')
    def _select_clip_mode(self, value):
        click = value != 0
        if click and self._mode == self._color_select_mode:
            self._into_mode(self._clip_mode, 'CLIP MODE')
            return
        if click:
            if self.change_mode(self._clip_mode):
                with self.rebuild():
                    self._mode.exit()
                    self._mode = self._clip_mode
                    self._light_button(1)
                    self._mode.enter()
            if not self._monochrome:
                if self.canonical_parent.isShiftDown() or self.mikro_shift:
                    self.canonical_parent.to_color_edit_mode(True)
                    self._clip_mode_button.send_value(1, True)
                else:
                    self.canonical_parent.to_color_edit_mode(False)
        self._clip_mode_down = click

    @subject_slot('value')
    def _select_pad_mode(self, value):
        if value > 0 and self.change_mode(self._pad_mode):
            track = self.song().view.selected_track
            newmode = self._pad_mode.fitting_mode(track)
            with self.rebuild():
                self._mode.exit()
                self._mode = newmode
                self._light_button(2)
                self._mode.enter()

    def _select_drum_mode(self, value):
        if value > 0 and self.change_mode(self._drum_mode):
            with self.rebuild():
                self._mode.exit()
                self._mode = self._drum_mode
                self._light_button(2)
                self._mode.enter()

    def _into_hold_mode(self, value, button, mode, info):
        if self._mode != None and self._mode != mode and not self._mode.is_lock_mode():
            return
        button.send_value(value, True)
        if value > 0 and self._mode != mode:
            with self.rebuild():
                self._mode.exit()
                self._return_mode = self._mode
                self._mode = mode
                self._mode.enter()
        elif value == 0 and self._mode == mode:
            with self.rebuild():
                self._mode.exit()
                self._mode = self._return_mode
                self._return_mode = None
                self._mode.enter()

    @subject_slot('value')
    def _select_arm(self, value):
        if value != 0:
            self.show_messsage('Current Mode : Track ARM')
        self._into_hold_mode(value, self._arm_button, self._arm_mode, 'ARM')

    @subject_slot('value')
    def _select_stop(self, value):
        if value != 0:
            self.show_messsage('Current Mode : Track STOP')
        self._into_hold_mode(value, self._stop_button, self._stop_mode, 'STOP')

    @subject_slot('value')
    def _select_solo(self, value):
        if value != 0:
            if self.mikro_shift:
                self._into_hold_mode(value, self._solo_button, self._stop_mode, 'STOP')
                self._md_solo_mode = self._stop_mode
                self.show_messsage('Current Mode : Track STOP')
            else:
                self._into_hold_mode(value, self._solo_button, self._solo_mode, 'SOLO')
                self._md_solo_mode = self._solo_mode
                self.show_messsage('Current Mode : Track SOLO')
        else:
            self._into_hold_mode(value, self._solo_button, self._md_solo_mode, 'SOLO')

    @subject_slot('value')
    def _select_mute(self, value):
        if value != 0:
            if self.mikro_shift:
                self._into_hold_mode(value, self._mute_button, self._arm_mode, 'ARM')
                self.show_messsage('Current Mode : Track ARM')
                self._md_mute_mode = self._arm_mode
            else:
                self._into_hold_mode(value, self._mute_button, self._mute_mode, 'Mute')
                self.show_messsage('Current Mode : Track MUTE')
                self._md_mute_mode = self._mute_mode
        else:
            self._into_hold_mode(value, self._mute_button, self._md_mute_mode, 'SOLO')

    @subject_slot('value')
    def _select_select(self, value):
        if value != 0:
            if self.mikro_shift:
                self._md_select_mode = self._xfade_mode
                self._into_hold_mode(value, self._select_button, self._xfade_mode, 'XFADE')
                self.show_messsage('Current Mode : Track Crossfader Assign')
            else:
                self._md_select_mode = self._select_mode
                self._into_hold_mode(value, self._select_button, self._select_mode, 'Select')
                self.show_messsage('Current Mode : Track SELECT')
        else:
            self._into_hold_mode(value, self._select_button, self._md_select_mode, 'Select')

    @subject_slot('value')
    def _select_xfade(self, value):
        if value != 0:
            self.show_messsage('Current Mode : Track Crossfader Assign')
        self._into_hold_mode(value, self._xfade_button, self._xfade_mode, 'XFADE')

    def _action_octave(self, value):
        pass

    def _action_scale(self, value):
        pass

    def _action_base_note(self, value):
        pass

    def isClipDown(self):
        return self._clip_mode_down

    def _action_key_color(self, value):
        pass

    def is_solo_exclusive(self):
        return self._solo_mode.exclusive

    def is_arm_exclusive(self):
        return self._arm_mode.exclusive

    def set_solo_exclusive(self, value):
        self._solo_mode.exclusive = value
        self._solo_exclusive_button.send_value(value > 0 and 127 or 0, True)

    def set_arm_exclusive(self, value):
        self._arm_mode.exclusive = value
        self._arm_exclusive_button.send_value(value > 0 and 127 or 0, True)

    @subject_slot('value')
    def _action_arm_exclusive(self, value):
        if value > 0:
            self.set_arm_exclusive(not self._arm_mode.exclusive)

    @subject_slot('value')
    def _action_solo_exclusive(self, value):
        if value > 0:
            self.set_solo_exclusive(not self._solo_mode.exclusive)

    def on_selected_scene_changed(self):
        pass

    def on_selected_track_changed(self):
        track = self.song().view.selected_track
        newmode = self._mode.fitting_mode(track)
        if track and newmode != self._mode:
            with self.rebuild():
                self._light_button(newmode.button_index)
                self._mode.exit()
                self._mode = newmode
                self._mode.enter()

    def disconnect(self):
        self._clip_mode.unbind()
        self._drum_mode.unbind()
        self._scene_mode.unbind()
        self._pad_mode.unbind()
        super(ModeSelector, self).disconnect()

    def on_selected_scene_changed(self):
        pass