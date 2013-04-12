#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\SceneElement.py
import time
from _Framework.ButtonElement import *
from MIDI_Map import *

class SceneElement:
    __module__ = __name__
    __doc__ = ' Special button class that can be configured with custom on- and off-values '

    def __init__(self, index, matrix):
        self._matrix = matrix
        self._launch_button = None
        self.index = index
        self._scene = None
        self.active = False
        self.blinking = False
        self._track = None
        self._pressAction = self._launch_scene
        self.oncolor = None
        self.offcolor = None
        self.eval = self._eval_scene_states

    def set_launch_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if button != self._launch_button:
                if self._launch_button != None:
                    self._launch_button.remove_value_listener(self._launch_value)
                self._launch_button = button
                self._launch_button != None and self._launch_button.add_value_listener(self._launch_value)

    def notify(self, blinking_state):
        if blinking_state == 0 and self.blinking:
            self._launch_button.send_value_bright(0)
        elif blinking_state > 0 and self.blinking:
            self._launch_button.send_value_bright(1)
        elif self.active:
            self._launch_button.send_value_bright(1)

    def set_value(self, force = False):
        if self._launch_button != None:
            if self.active:
                self._launch_button.send_value(1, force)
            else:
                self._launch_button.send_value(0, force)

    def force_value(self, value):
        if self._launch_button != None:
            if self.active:
                self._launch_button.send_value(value, True)

    def set_scene(self, scene):
        self._scene = scene

    def set_track(self, track):
        if self._track != None:
            if self._track.can_be_armed:
                self._track.remove_arm_listener(self._got_arm)
            self._track.remove_mute_listener(self._got_mute)
            self._track.remove_solo_listener(self._got_solo)
            self._track.remove_playing_slot_index_listener(self._got_playing)
            self._track.remove_fired_slot_index_listener(self._got_slot_fired)
            if self._track.mixer_device.crossfade_assign_has_listener(self._got_xfade):
                self._track.mixer_device.remove_crossfade_assign_listener(self._got_xfade)
        self._track = track
        if track != None:
            if self._track.can_be_armed:
                self._track.add_arm_listener(self._got_arm)
            self._track.add_mute_listener(self._got_mute)
            self._track.add_solo_listener(self._got_solo)
            self._track.add_playing_slot_index_listener(self._got_playing)
            self._track.mixer_device.add_crossfade_assign_listener(self._got_xfade)
            self._track.add_fired_slot_index_listener(self._got_slot_fired)

    def _got_xfade(self):
        if self._track != None and self._matrix.mode == SCENE_MODE_XFADE:
            self.eval()
            self.set_value()

    def _got_arm(self):
        if self._track != None and self._matrix.mode == SCENE_MODE_ARM:
            self.eval()

    def _got_mute(self):
        if self._track != None and self._matrix.mode == SCENE_MODE_MUTE:
            self.eval()

    def _got_solo(self):
        if self._track != None and self._matrix.mode == SCENE_MODE_SOLO:
            self.eval()

    def _got_playing(self):
        if self._track != None and self._matrix.mode == SCENE_MODE_STOP:
            self._matrix.update()

    def _got_slot_fired(self):
        if self._track != None and self._matrix.mode == SCENE_MODE_STOP:
            self._matrix.update()

    def assign_mode(self, mode):
        self.active = False
        if mode == SCENE_MODE_NORMAL:
            self.eval = self._eval_scene_states
        elif mode == SCENE_MODE_CONTROL:
            self.eval = self._eval_control_mode
        elif mode == SCENE_MODE_MUTE:
            self.eval = self._eval_mute
        elif mode == SCENE_MODE_SOLO:
            self.eval = self._eval_solo
        elif mode == SCENE_MODE_SELECT:
            self.eval = self._eval_select
        elif mode == SCENE_MODE_ARM:
            self.eval = self._eval_arm
        elif mode == SCENE_MODE_STOP:
            self.eval = self._eval_stop
        elif mode == SCENE_MODE_XFADE:
            self.eval = self._eval_xfade_assign

    def get_color(self, value):
        if value == 0:
            return self.offcolor
        else:
            return self.oncolor

    def _eval_xfade_assign(self):
        self.blinking = False
        self._pressAction = self._inaktion
        if self._track != None and self._track.mixer_device != None:
            xfade = self._track.mixer_device.crossfade_assign
            if xfade == 0:
                self.assign_color(PColor.XFADE_A)
            elif xfade == 1:
                self.assign_color(PColor.XFADE_BOTH)
            elif xfade == 2:
                self.assign_color(PColor.XFADE_B)
            self._pressAction = self._switch_xfade_assign
        else:
            self.disable_color()
            self._pressAction = self._inaktion

    def _switch_xfade_assign(self, value):
        if self._track != None:
            self._track.mixer_device.crossfade_assign = (self._track.mixer_device.crossfade_assign + 1) % 3
            if self._track.mixer_device.crossfade_assign == 0:
                self.assign_color(PColor.XFADE_A)
            elif self._track.mixer_device.crossfade_assign == 1:
                self.assign_color(PColor.XFADE_BOTH)
            elif self._track.mixer_device.crossfade_assign == 2:
                self.assign_color(PColor.XFADE_B)
            self.set_value()

    def _eval_stop(self):
        self._pressAction = self._stop_track
        self.blinking = False
        self.active = True
        if self._track != None:
            clipslots = self._track.clip_slots
            stop_fired = self._track.fired_slot_index == -2
            play_fired = self._track.fired_slot_index >= 0
            clip_playing = False
            has_clip = False
            if clipslots != None:
                for cs_index in range(len(clipslots)):
                    clip_slot = clipslots[cs_index]
                    if clip_slot.has_clip:
                        has_clip = True
                        if clip_slot.clip.is_playing:
                            clip_playing = True
                    elif clip_slot.controls_other_clips:
                        has_clip = True
                        if clip_slot.is_playing:
                            clip_playing = True
                        if clip_slot.is_triggered:
                            play_fired = True
                    elif clip_slot.is_triggered:
                        stop_fired = True

            is_group = self._track.is_foldable
            if stop_fired or play_fired:
                self.blinking = True
            if is_group:
                if clip_playing:
                    self.assign_color(PColor.STOP_G_PLAY)
                else:
                    self.assign_color(PColor.STOP_G_NO_PLAY)
            elif clip_playing:
                self.assign_color(PColor.STOP_PLAY)
            elif has_clip:
                self.assign_color(PColor.STOP_NO_PLAY)
            else:
                self.assign_color(PColor.STOP_NO_CLIPS)
        else:
            self.disable_color()
        self.set_value()

    def _eval_arm(self):
        prevstate = self.active
        self._pressAction = self._arm_track
        self.blinking = False
        if self._track == None:
            self.active = False
            self.disable_color()
        elif self._track.can_be_armed:
            if self._track.arm:
                self.active = True
            else:
                self.active = False
            if self._track.has_midi_input:
                self.assign_color(PColor.ARM_MIDI)
            elif self._track.has_audio_input:
                self.assign_color(PColor.ARM_AUDIO)
            else:
                self.assign_color(PColor.ARM_OTHER)
        else:
            self.active = False
            self.assign_color(PColor.ARM_NO_ARM)
        if prevstate != self.active:
            self.set_value()

    def _eval_mute(self):
        prevstate = self.active
        self._pressAction = self._mute_track
        self.blinking = False
        if self._track == None:
            self.active = False
            self.disable_color()
        elif self._track.mute:
            self.active = False
            self.assign_color(PColor.MUTE_TRACK)
        else:
            self.active = True
            self.assign_color(PColor.MUTE_TRACK)
        if prevstate != self.active:
            self.set_value()

    def _eval_solo(self):
        prevstate = self.active
        self._pressAction = self._solo_track
        self.blinking = False
        if self._track == None:
            self.active = False
            self.disable_color()
        elif self._track.solo:
            self.active = True
            self.assign_color(PColor.SOLO_TRACK)
        else:
            self.active = False
            self.assign_color(PColor.SOLO_TRACK)
        if prevstate != self.active:
            self.set_value()

    def _eval_select(self):
        prevstate = self.active
        self._pressAction = self._select_track
        self.blinking = False
        if self._track == None:
            self.active = False
            self.disable_color()
        elif self._track == self._matrix.getSelectedTrack():
            self.active = True
            self.assign_color(PColor.SELECT)
        else:
            self.active = False
            self.assign_color(PColor.SELECT)
        if prevstate != self.active:
            self.set_value()

    def _eval_control_mode(self):
        prevstate = self.active
        self.active = False
        if self.index > 7:
            if self._matrix.control_handler.mode == CONTROL_DEVICE:
                parm_index = self._matrix.control_handler.index_parm_id(self.index)
                self._eval_device_buttons(parm_index)
            else:
                track_index = self._matrix.control_handler.index_parm_id(self.index)
                self._eval_mixer_button(track_index)
        elif self.index > 3:
            mode = self.index - 4
            self.oncolor = device_get_mode_color(mode, 0)
            self.offcolor = device_get_mode_color(mode, 1)
            if mode == self._matrix.control_handler.mode:
                self.active = True
                self.value = 1
            else:
                self.active = False
                self.value = 0
            self._pressAction = self._select_dev_mode
        elif self._matrix.control_handler.mode == CONTROL_SEND:
            self._set_up_control_send()
        elif self._matrix.control_handler.mode == CONTROL_DEVICE:
            self._set_up_device_nav()
        else:
            self.disable_color()
            self._pressAction = self._inaktion
        self.blinking = False
        if prevstate != self.active:
            self.set_value()

    def _eval_device_buttons(self, index):
        valid = True
        if self._matrix.control_handler.selected_device == None:
            valid = False
        elif index >= self._matrix.control_handler.nr_of_parms_in_bank():
            valid = False
        if valid:
            if index == 0 and self._matrix.control_handler.selected_bank == 0:
                self.assign_color(PColor.DEVICE_ON_OFF)
            else:
                mode = self._matrix.control_handler.mode
                self.oncolor = device_get_color(mode, 0)
                self.offcolor = device_get_color(mode, 1)
            if index == self._matrix.control_handler.selected_device_parm_index:
                self.active = True
                self.value = 1
            else:
                self.active = False
                self.value = 0
            self._pressAction = self._select_knob_assign_device
        else:
            self.disable_color()
            self.active = True
            self.value = 1
            self._pressAction = self._inaktion

    def _eval_mixer_button(self, index):
        track = self._matrix._control._mixer._channel_strips[index]._track
        if track == None:
            self.disable_color()
            self._pressAction = self._inaktion
        else:
            mode = self._matrix.control_handler.mode
            self.oncolor = device_get_color(mode, 0)
            self.offcolor = device_get_color(mode, 1)
            if index == self._matrix.control_handler.sel_track_parm_index:
                self.active = True
                self.value = 1
            else:
                self.active = False
                self.value = 0
            self._pressAction = self._select_knob_assign

    def _set_up_device_nav(self):
        if self.index == 0:
            self.assign_color(PColor.DEVICE_LEFT)
            self._pressAction = self._nav_device_left
        elif self.index == 1:
            self.assign_color(PColor.DEVICE_RIGHT)
            self._pressAction = self._nav_device_right
        elif self.index == 2:
            self.assign_color(PColor.BANK_LEFT)
            self._pressAction = self._nav_bank_left
            if self._matrix.control_handler.selected_bank == 0:
                self.mark_off()
            else:
                self.mark_on()
        elif self.index == 3:
            self.assign_color(PColor.BANK_RIGHT)
            self._pressAction = self._nav_bank_right
            if self._matrix.control_handler.selected_bank < self._matrix.control_handler.nr_of_banks() - 1:
                self.mark_on()
            else:
                self.mark_off()

    def mark_off(self):
        self.active = False
        self.value = 0

    def mark_on(self):
        self.active = True
        self.value = 1

    def disable_color(self):
        self.oncolor = None
        self.offcolor = None

    def assign_color(self, color):
        self.oncolor = color[0]
        self.offcolor = color[1]

    def _nav_device_left(self, value):
        if value > 0:
            self._matrix._control._nav_value_left(1)

    def _nav_device_right(self, value):
        if value > 0:
            self._matrix._control._nav_value_right(1)

    def _nav_bank_left(self, value):
        if value > 0 and self._matrix.control_handler.dec_bank_nr():
            self._matrix.update_on_device_parm_changed()

    def _nav_bank_right(self, value):
        if value > 0 and self._matrix.control_handler.inc_bank_nr():
            self._matrix.update_on_device_parm_changed()

    def _set_up_control_send(self):
        nr_of_tracks = len(self._matrix._control.song().return_tracks)
        self.assign_color(PColor.MIX_SELECT_SEND)
        if self.index < nr_of_tracks:
            if nr_of_tracks > 3 and self.index == 3:
                col = max(21, (21 + (self._matrix.control_handler.selected_sends_index - 3) * 20) % 127)
                self.oncolor = (col, 120, 127)
                self.offcolor = (21, 120, 30)
            if self.index == self._matrix.control_handler.selected_sends_index:
                self.value = 1
                self.active = True
            elif self.index == 3 and self._matrix.control_handler.selected_sends_index >= 3:
                self.value = 1
                self.active = True
            else:
                self.value = 0
                self.active = False
        else:
            self.disable_color()
            self._pressAction = self._inaktion
        self._pressAction = self._select_sub_sends

    def _select_sub_sends(self, value):
        self._matrix._control._master_knob.switch_to_matrix_mode()
        nr_of_tracks = len(self._matrix._control.song().return_tracks)
        new_index = self.index
        fire = False
        if self.index == 3:
            fire = True
            if self._matrix.control_handler.selected_sends_index < 3:
                new_index = 3
            elif self._matrix.control_handler.selected_sends_index < nr_of_tracks - 1:
                new_index = self._matrix.control_handler.selected_sends_index + 1
            else:
                new_index = 3
        self._matrix.control_handler.message_current_parm()
        self._matrix.control_handler.selected_sends_index = new_index
        self._matrix.control_handler.reassign_mix_parm()
        self._matrix.eval_matrix()
        if fire:
            self.set_value()

    def _select_knob_assign(self, value):
        self._matrix._control._master_knob.switch_to_matrix_mode()
        ip = self._matrix.control_handler.index_parm_id(self.index)
        track = self._matrix._control._mixer._channel_strips[ip]._track
        if self._matrix.control_handler.assign_mix_parm(track, ip):
            self._matrix.eval_matrix()
            self._matrix.control_handler.message_current_parm()

    def _select_knob_assign_device(self, value):
        self._matrix._control._master_knob.switch_to_matrix_mode()
        ip = self._matrix.control_handler.index_parm_id(self.index)
        if self._matrix.control_handler.assign_device_parm(ip):
            self._matrix.eval_matrix()

    def _select_dev_mode(self, value):
        self._matrix._control._master_knob.switch_to_matrix_mode()
        mode_index = self._matrix.control_handler.index_mode_id(self.index)
        if mode_index == CONTROL_DEVICE:
            device = self._matrix._control._device._device
            if device != None:
                self._matrix.control_handler.mode = mode_index
                self._matrix.control_handler.selected_device = device
                self._matrix._control.show_message('Control Device: ' + str(device.name))
                self._matrix.control_handler.reassign_device_parm()
                self._update_matrix()
        elif mode_index != self._matrix.control_handler.mode:
            self._matrix.control_handler.mode = mode_index
            self._matrix.control_handler.reassign_mix_parm()
            self._update_matrix()
            self._matrix.control_handler.message_current_parm()

    def _update_matrix(self):
        self._matrix.eval_matrix()
        self._matrix.fire_values()

    def _inaktion(self, value):
        pass

    def _eval_scene_states(self):
        prevstate = self.active
        self._pressAction = self._launch_scene
        if self._scene == None:
            self.active = False
            self.blinking = False
            self.disable_color()
        else:
            clip_slots = self._scene.clip_slots
            count = 0
            playcount = 0
            if self._scene.is_triggered:
                self.blinking = True
            else:
                self.blinking = False
            for cs_index in range(len(clip_slots)):
                clip_slot = clip_slots[cs_index]
                if clip_slot.has_clip:
                    count = count + 1
                    if clip_slot.clip.is_playing:
                        playcount = playcount + 1

            if playcount > 0:
                self.active = True
                self.assign_color(PColor.SCENE_PLAYING)
            elif count > 0:
                self.active = False
                self.assign_color(PColor.SCENE_HASCLIPS)
            else:
                self.active = False
                self.assign_color(PColor.SCENE_NO_CLIPS)
        if prevstate != self.active:
            self.set_value()

    def unbind(self):
        if self._launch_button != None and self._track != None:
            if self._track.can_be_armed:
                self._track.remove_arm_listener(self._got_arm)
            self._track.remove_mute_listener(self._got_mute)
            self._track.remove_solo_listener(self._got_solo)
            self._track.remove_playing_slot_index_listener(self._got_playing)
            self._track.mixer_device.remove_crossfade_assign_listener(self._got_xfade)
            self._track.remove_fired_slot_index_listener(self._got_slot_fired)
        self._launch_button = None
        self._scene = None

    def disconnect(self):
        if self._launch_button != None and self._launch_button.value_has_listener(self._launch_value):
            self._launch_button.remove_value_listener(self._launch_value)
        self._matrix = None
        self._launch_button = None
        self.index = None
        self._scene = None
        self.active = None
        self.blinking = None
        self._track = None
        self._pressAction = None
        self.oncolor = None
        self.offcolor = None
        self.eval = None

    def _launch_value(self, value):
        if not self._launch_button != None:
            raise AssertionError
            raise self._pressAction != None or AssertionError
            raise value in range(128) or AssertionError
            value > 0 and self._pressAction(value)

    def _launch_scene(self, value):
        if not value in range(128):
            raise AssertionError
            if value == 0:
                return
            if self._scene != None:
                pass
            self._launch_button.is_momentary() and self._scene.set_fire_button_state(value != 0)
        elif value != 0:
            self._scene.fire()

    def _mute_track(self, value):
        if self._track != None and value > 0:
            if self._track.mute:
                self._track.mute = False
                self.active = True
                self._launch_button.send_value(100)
            else:
                self._track.mute = True
                self.active = False
                self._launch_button.send_value(0)

    def _arm_track(self, value):
        if self._track != None and self._track.can_be_armed and value > 0:
            if self._track.arm:
                self._track.arm = False
                self.active = False
                self._launch_button.send_value(0)
            else:
                self._track.arm = True
                self.active = True
                self._launch_button.send_value(100)
            self._matrix.do_arm(self.index)

    def _stop_track(self, value):
        if self._track != None and value > 0:
            self._track.stop_all_clips()

    def _solo_track(self, value):
        if self._track != None and value > 0:
            if self._track.solo:
                self._track.solo = False
                self.active = False
                self._launch_button.send_value(0)
            else:
                self._track.solo = True
                self.active = True
                self._launch_button.send_value(100)
            self._matrix.do_solo(self.index)

    def _select_track(self, value):
        if self._track != None and value > 0:
            self._matrix.setSelectedTrack(self._track)