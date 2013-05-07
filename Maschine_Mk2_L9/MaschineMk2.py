#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\MaschineMk2.py
from __future__ import with_statement
import Live
import MidiRemoteScript
import time
from functools import partial
from _Framework.Task import Task
from _Framework.SubjectSlot import subject_slot
from PadScale import *
from MIDI_Map import *
from MaschineSessionComponent import MaschineSessionComponent
from MaschineDeviceComponent import MaschineDeviceComponent
from VarButtonElement import VarButtonElement
from VarButtonElement import GatedColorButton
from VarButtonElement import TwinButton
from ControlHandler import ControlHandler
from SceneMatrix import SceneMatrix
from Mk2KnobControl import Mk2KnobControl
from StateButton import StateButton, ToggleButton
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.DeviceComponent import DeviceComponent

class MaschineMk2(ControlSurface):
    __module__ = __name__
    __doc__ = 'Control Script for Maschine Mk2 and Maschine Mikro Mk2'

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance, False)
        with self.component_guard():
            self._suppress_send_midi = True
            self.togglecolor = (10, 30, 50, 70, 90)
            self.toggleindex = 0
            self._c_ref = c_instance
            self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
            self._c_inst = c_instance
            is_momentary = True
            self._active = True
            self._modifier_down = False
            self._return_mode = 0
            self._returntopad = False
            self._mode = CLIP_MODE
            self.init_slot = 0
            self.init_done = False
            self._midi_pause_count = 0
            self.nav_index = 0
            self._base_note = 0
            self._octave = 0.55
            self._scale_select_mode = MODE_PRESS_NONE
            self.send_slider_index = 0
            self._pad_mode = PM_OFF
            self._note_display_mode = ND_KEYBOARD1
            self._set_suppress_rebuild_requests(True)
            self._scenematrix = SceneMatrix(self)
            self._master_knob = Mk2KnobControl(self)
            self._device = self._set_up_device_control()
            self.show_message(str(''))
            self.request_rebuild_midi_map()
            self._set_global_buttons()
            self._set_mode_buttons()
            self._setup_transport()
            self._set_modecontrol()
            self._set_up_session()
            self._set_up_mixer()
            self._set_up_timer()
            self._set_up_machine_knobs()
            self.current_scale_index = 0
            self.assign_transpose(SCALES[self.current_scale_index])
            self.set_highlighting_session_component(self._session)
            self._navigate_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 127)
            self._navigate_button.add_value_listener(self._do_focus_navigate)
            self.display_update_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 86)
            self.display_update_button.add_value_listener(self._a_display_update)
            self._set_suppress_rebuild_requests(False)
            self.song().view.add_detail_clip_listener(self.clip_handle)
            self.song().add_visible_tracks_listener(self.clip_handle)
            self.song().add_scenes_listener(self.clip_handle)
            self.application().view.add_view_focus_changed_listener(self.focus_changed)
            self.log_message('########## LIVE 9 MASCHINE MK2 V 1.02 #############')
            self._suppress_send_midi = False

    def _set_up_mixer(self):
        is_momentary = True
        self._mixer = MixerComponent(8)
        self.send_sliders = []
        for track in range(8):
            self.send_sliders.append(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, SEND_CC_OFF + track))

        for track in range(8):
            strip = self._mixer.channel_strip(track)
            strip.set_arm_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, ARM_CC_OFF + track))
            strip.set_solo_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, SOLO_CC_OFF + track))
            strip.set_mute_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, MUTE_CC_OFF + track))
            strip.set_volume_control(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, LEVEL_CC_OFF + track))
            strip.set_pan_control(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, PAN_CC_OFF + track))
            strip.set_select_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, SELECT_CC_OFF + track))
            st = tuple([self.send_sliders[track]])
            strip.set_send_controls(st)

        self.send_slider_toggle_button = StateButton(False, MIDI_CC_TYPE, 0, 90)
        self.send_slider_toggle_button.add_value_listener(self._do_toggle_send)
        self._session.set_mixer(self._mixer)

    def _set_global_buttons(self):
        is_momentary = True
        self._undo_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 85)
        self._undo_button.add_value_listener(self._do_undo)
        self._redo_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 87)
        self._redo_button.add_value_listener(self._do_redo)
        self._armsolomode_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 89)
        self._armsolomode_button.add_value_listener(self._do_armsolo_mode)
        self._fire_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 9)
        self._fire_button.add_value_listener(self._do_fire_button)
        self.track_left_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 120)
        self.track_right_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 121)
        self.track_left_button.add_value_listener(self._a_trk_left)
        self.track_right_button.add_value_listener(self._a_trk_right)
        self.test_button = StateButton(True, MIDI_CC_TYPE, 5, 60)
        self.note_repeat_button = StateButton(True, MIDI_CC_TYPE, 5, 61)
        self.test_button.add_value_listener(self.do_test)
        self.note_repeat_button.add_value_listener(self.do_note_repeat)
        self.reset_test_button = StateButton(True, MIDI_CC_TYPE, 5, 62)
        self.reset_test_button.add_value_listener(self.do_reset)

    def _set_mode_buttons(self):
        self.xfade_assign_button = StateButton(True, MIDI_CC_TYPE, 0, 116)
        self._pad_select_button = StateButton(False, MIDI_CC_TYPE, 0, 117)
        self._pad_solo_button = StateButton(False, MIDI_CC_TYPE, 0, 118)
        self._mute_button = StateButton(False, MIDI_CC_TYPE, 0, 119)
        self._pad_scale_up = GatedColorButton(True, MIDI_CC_TYPE, 83, 0)
        self._pad_scale_down = GatedColorButton(True, MIDI_CC_TYPE, 94, 16)
        self._pad_select_button.add_value_listener(self._do_pad_select_multi)
        self._mute_button.add_value_listener(self._do_mute_button)
        self._pad_solo_button.add_value_listener(self._do_pad_solo_multi)
        self.xfade_assign_button.add_value_listener(self._do_xfade_assign)
        self._pad_scale_up.add_value_listener(self._do_pad_note_up)
        self._pad_scale_down.add_value_listener(self._do_pad_note_down)

    def set_appointed_device(self, device):
        with self.component_guard():
            self._device_component.set_device(device)

    def _set_up_device_control(self):
        is_momentary = True
        device = MaschineDeviceComponent(self)
        device.set_device_changed_listener(self._handle_device_changed)
        device.set_device_parm_listener(self._hande_device_parm_changed)
        param_controls = []
        for index in range(8):
            param_controls.append(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_CC_OFF + index))

        device.set_parameter_controls(tuple(param_controls))
        device.set_on_off_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF))
        device.set_bank_nav_buttons(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 4), ButtonElement(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 5))
        self._device_nav_button_left = StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 6)
        self._device_nav_button_right = StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 7)
        self._device_nav_button_left.add_value_listener(self._nav_value_left)
        self._device_nav_button_right.add_value_listener(self._nav_value_right)
        device.name = 'Device_Component'
        self.set_device_component(device)
        return device

    def _setup_transport(self):
        is_momentary = True
        transport = TransportComponent()
        playButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 108)
        stopButton = StateButton(not is_momentary, MIDI_CC_TYPE, 0, 110)
        recordButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 109)
        overdubButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 107)
        metrononmeButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 104)
        playButton.name = 'Play'
        stopButton.name = 'Stop'
        recordButton.name = 'Record'
        overdubButton.name = 'Overdub'
        metrononmeButton.name = 'Metronome'
        transport.set_play_button(playButton)
        transport.set_stop_button(stopButton)
        transport.set_record_button(recordButton)
        transport.set_overdub_button(overdubButton)
        transport.set_metronome_button(metrononmeButton)
        transport.set_nudge_buttons(StateButton(is_momentary, MIDI_CC_TYPE, 1, 51), StateButton(is_momentary, MIDI_CC_TYPE, 1, 50))
        punchinbutton = ToggleButton(MIDI_CC_TYPE, 1, 52)
        punchoutbutton = ToggleButton(MIDI_CC_TYPE, 1, 53)
        punchinbutton.name = 'Punch In'
        punchoutbutton.name = 'Punch Out'
        transport.set_punch_buttons(punchinbutton, punchoutbutton)
        transport.set_loop_button(StateButton(is_momentary, MIDI_CC_TYPE, 1, 54))
        self.transp_ff_button = ButtonElement(True, MIDI_CC_TYPE, 1, 59)
        self.transp_rw_button = ButtonElement(True, MIDI_CC_TYPE, 1, 58)
        transport.set_seek_buttons(self.transp_ff_button, self.transp_rw_button)
        self.xfadeKnob = SliderElement(MIDI_CC_TYPE, 1, 100)
        self.xfadeKnob.connect_to(self.song().master_track.mixer_device.crossfader)
        self.tap_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 88)
        self.tap_button.add_value_listener(self._do_tap_tempo)
        self.cue_add_delete_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 55)
        self.cue_prev_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 56)
        self.cue_next_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 57)
        self.cue_add_delete_button.add_value_listener(self._do_toggle_cue)
        self.cue_prev_button.add_value_listener(self._do_toggle_prev_cue)
        self.cue_next_button.add_value_listener(self._do_toggle_next_cue)

    def _set_up_machine_knobs(self):
        master_track = self.song().master_track
        self.master_volume = SliderElement(MIDI_CC_TYPE, 0, 40)
        self.prehear = SliderElement(MIDI_CC_TYPE, 0, 41)
        self.master_volume.connect_to(master_track.mixer_device.volume)
        self.prehear.connect_to(master_track.mixer_device.cue_volume)

    def _set_up_session(self):
        is_momentary = True
        self._session = MaschineSessionComponent()
        self._session.add_offset_listener(self.notify_track_scroll)
        nhue = COLOR_HUE_NAV
        self.nav_buttons = (GatedColorButton(True, MIDI_CC_TYPE, 92, nhue),
         GatedColorButton(True, MIDI_CC_TYPE, 81, nhue),
         GatedColorButton(True, MIDI_CC_TYPE, 93, nhue),
         GatedColorButton(True, MIDI_CC_TYPE, 91, nhue))
        self._session.set_scene_bank_buttons(self.nav_buttons[0], self.nav_buttons[1])
        self._session.set_track_bank_buttons(self.nav_buttons[2], self.nav_buttons[3])
        self._session.set_stop_all_clips_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 111))
        track_stop_buttons = [ StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, index + STOP_CC_OFF) for index in range(4) ]
        self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
        self._init_matrix()
        self._set_up_buttons()
        self._session._link()
        self._session.set_advance(STEP4)

    def _set_up_buttons(self):
        self._bmatrix = ButtonMatrixElement()
        for scene_index in range(4):
            button_row = []
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                button = self._matrix[scene_index][track_index]
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(button)
                clip_slot.set_triggered_to_play_value(1)
                clip_slot.set_triggered_to_record_value(1)
                clip_slot.set_started_value(1)
                clip_slot.set_recording_value(1)
                clip_slot.set_stopped_value(1)

            self._bmatrix.add_row(tuple(button_row))

    def _init_matrix(self):
        is_momentary = True
        self._button_sequence = []
        self._matrix = []
        for scene_index in range(4):
            button_row = []
            for track_index in range(4):
                button = VarButtonElement(is_momentary, 0, scene_index, track_index, self)
                partner = TwinButton(is_momentary, 1, button)
                partner.add_value_listener(self.ox, True)
                button_row.append(button)

            self._matrix.append(tuple(button_row))

        for scene_index in [3,
         2,
         1,
         0]:
            for track_index in range(4):
                self._button_sequence.append(self._matrix[scene_index][track_index])

        self._session.set_matrix(self._matrix)

    def set_pad_translations(self, pad_translations):
        ControlSurface.set_pad_translations(pad_translations)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self._update_hardware()

    def ox(self, value, button):
        if not isinstance(button, TwinButton):
            raise AssertionError
            self._mode == PAD_MODE and button.fire(value)

    def _update_hardware(self):
        self._session.update()
        self._set_suppress_rebuild_requests(True)
        self._set_mode()
        self._master_knob.update()
        if self._scenematrix.soloexclusive:
            self._armsolomode_button.send_value(1, True)
        else:
            self._armsolomode_button.send_value(0, True)
        self._master_knob.start_up()
        self._pad_scale_up.activate()
        self._pad_scale_down.activate()
        self.current_scale_to_display()
        self.send_to_display(KEY_COLOR_MODES_STRINGS[self._note_display_mode], 1)
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                button = self._matrix[scene_index][track_index]
                button.refresh()

        self._set_suppress_rebuild_requests(False)

    def get_color(self, value, track_index, scene_index):
        if not self._active:
            return
        if self._mode == SCENE_MODE or self._mode == CONTROL_MODE or self._pad_mode == PM_ON:
            element = self._scenematrix.get_element(scene_index, track_index)
            return element.get_color(value)
        elif self._mode == CLIP_MODE:
            scene = self._session.scene(scene_index)
            clip_slot = scene.clip_slot(track_index)._clip_slot
            cindex = 0
            if value == 0:
                cindex = 1
            if clip_slot != None:
                if clip_slot.has_clip:
                    if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                        return PColor.CLIP_RECORD[cindex]
                    if clip_slot.clip.is_playing:
                        return PColor.CLIP_PLAY[cindex]
                    elif clip_slot.clip.is_triggered:
                        return PColor.CLIP_PLAY[cindex]
                    else:
                        return PColor.CLIP_STOPPED[cindex]
                elif clip_slot.will_record_on_start:
                    return PColor.CLIP_RECORD[cindex]
                elif clip_slot.is_playing:
                    return PColor.CLIP_GROUP_PLAY[cindex]
                elif clip_slot.controls_other_clips:
                    return PColor.CLIP_GROUP_CONTROL[cindex]
                elif clip_slot.is_triggered:
                    return PColor.CLIP_GROUP_TRIGGER[cindex]
        elif self._mode == PAD_MODE:
            button = self._matrix[scene_index][track_index]
            return self.get_color_by_note_mode(button.get_identifier(), value > 0)

    def step_key_color_mode(self):
        self._note_display_mode = (self._note_display_mode + 1) % len(KEY_COLOR_MODES_STRINGS)
        self.show_message('Pad Mode Key Color = ' + KEY_COLOR_MODES_STRINGS[self._note_display_mode])
        self.send_to_display('Colors: ' + KEY_COLOR_MODES_STRINGS[self._note_display_mode], 1)
        if self._mode == PAD_MODE:
            for note_index in range(16):
                button = self._button_sequence[note_index]
                button.send_color_direct(self.get_color_by_note_mode(button.get_identifier(), False))

    def get_color_by_note_mode(self, midi_note, on):
        if self._note_display_mode == ND_BASE_OTHER:
            interval = (midi_note + 12 - self._base_note) % 12
            if on:
                return INTERVAL_COLOR_MAP[interval][0]
            else:
                return INTERVAL_COLOR_MAP[interval][1]
        elif on:
            return KEY_COLOR_MAP[midi_note % 12][0]
        else:
            return KEY_COLOR_MAP[midi_note % 12][1]

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        if self._midi_pause_count == 2:
            time.sleep(0.002)
            self._midi_pause_count = 0
        else:
            self._midi_pause_count = self._midi_pause_count + 1
        return True

    def clip_handle(self):
        if self._mode == SCENE_MODE or self._mode == CONTROL_MODE or self._modifier_down:
            self._scenematrix.update()

    def _a_display_update(self, value):
        if not self.display_update_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            (value != 0 or not self.display_update_button.is_momentary()) and self._update_hardware()
            self.show_message('Maschine Display Updated')

    def _set_up_timer(self):
        self.blink_state = 1

    def update_display(self):
        with self.component_guard():
            with self._is_sending_scheduled_messages():
                self._task_group.update(0.1)
            if self._mode == CLIP_MODE and not self._modifier_down:
                if self.blink_state == 0:
                    self._session.notify(1, 0)
                elif self.blink_state == 1:
                    self._session.notify(1, 1)
                elif self.blink_state == 3:
                    self._session.notify(2, 0)
                elif self.blink_state == 4:
                    self._session.notify(2, 1)
            elif self._mode == PAD_MODE:
                pass
            elif self.blink_state == 0:
                self._scenematrix.notify_scene_mode(1)
            elif self.blink_state == 2:
                self._scenematrix.notify_scene_mode(0)
            self.blink_state = (self.blink_state + 1) % 4
            self.init_slot += 1

    def _invoke_track_edit(self, mode):
        self._deassign_matrix()
        self._scenematrix.assign()
        self._scenematrix.set_mode(mode)
        self._pad_mode = PM_ON
        self.request_rebuild_midi_map()
        self._scenematrix.update()

    def _set_modecontrol(self):
        is_momentary = True
        self.scene_mode_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 112)
        self.clip_mode_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 113)
        self.pad_mode_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 114)
        self.control_mode_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 115)
        self.xfade_assign_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 116)
        self.scene_mode_button.add_value_listener(self._a_mode_scene)
        self.clip_mode_button.add_value_listener(self._a_mode_clip)
        self.pad_mode_button.add_value_listener(self._a_mode_pad)
        self.control_mode_button.add_value_listener(self._a_mode_control)

    def _set_mode(self, mode = None):
        if mode == None:
            mode = self._mode
        if mode == SCENE_MODE:
            self.clip_mode_button.send_value(OFF_VALUE, True)
            self.pad_mode_button.send_value(OFF_VALUE, True)
            self.control_mode_button.send_value(OFF_VALUE, True)
            self.scene_mode_button.send_value(ON_VALUE, True)
        elif mode == CLIP_MODE:
            self.scene_mode_button.send_value(OFF_VALUE, True)
            self.pad_mode_button.send_value(OFF_VALUE, True)
            self.control_mode_button.send_value(OFF_VALUE, True)
            self.clip_mode_button.send_value(ON_VALUE, True)
        elif mode == PAD_MODE:
            self.scene_mode_button.send_value(OFF_VALUE, True)
            self.clip_mode_button.send_value(OFF_VALUE, True)
            self.control_mode_button.send_value(OFF_VALUE, True)
            self.pad_mode_button.send_value(ON_VALUE, True)
        elif mode == CONTROL_MODE:
            self.scene_mode_button.send_value(OFF_VALUE, True)
            self.clip_mode_button.send_value(OFF_VALUE, True)
            self.pad_mode_button.send_value(OFF_VALUE, True)
            self.control_mode_button.send_value(ON_VALUE, True)

    def _reset_matrix(self):
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                button = self._matrix[scene_index][track_index]
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(button)

    def update_button_matrix(self):
        self._session.update()
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                button = self._matrix[scene_index][track_index]
                clip_slot = scene.clip_slot(track_index)
                if clip_slot._clip_slot != None and clip_slot._clip_slot.clip != None:
                    button.send_value(1, True)
                else:
                    button.send_value(0, True)

    def _deassign_matrix(self):
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(None)

    def _from_pad_mode(self, matrix_mode):
        self._mode = SCENE_MODE
        self._register_buttons()
        self._scenematrix.assign()
        self._scenematrix.set_mode(matrix_mode)
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._scenematrix.update()
        self._set_suppress_rebuild_requests(False)

    def _enter_pad_mode(self):
        self._set_mode(PAD_MODE)
        if self._mode == CLIP_MODE:
            self._deassign_matrix()
        elif self._mode == SCENE_MODE:
            self._scenematrix.deassign()
        elif self._mode == CONTROL_MODE:
            self._scenematrix.deassign()
            self._master_knob.exit_matrix_mode()
        self._mode = PAD_MODE
        self._set_suppress_rebuild_requests(True)
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.send_value(0, True)
                button.set_to_notemode(True)
                self._forwarding_registry[MIDI_NOTE_ON_STATUS, button.get_identifier()] = button
                self._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button

        self._set_suppress_rebuild_requests(False)

    def _register_buttons(self, update = False):
        self._set_suppress_rebuild_requests(True)
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.set_to_notemode(False)
                if update:
                    button.send_value(127, True)
                fwkey = [MIDI_NOTE_ON_STATUS]
                fwkey.append(button.get_identifier())
                self._forwarding_registry[tuple(fwkey)] = button
                self._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button

        self._set_suppress_rebuild_requests(False)

    def _back_to_clip_mode(self):
        self._pad_mode = PM_OFF
        self._scenematrix.set_mode(SCENE_MODE_NORMAL)
        self._scenematrix.deassign()
        self._set_up_clip_matrix()

    def _set_up_clip_matrix(self):
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.set_to_notemode(False)

        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._reset_matrix()
        self.update_button_matrix()
        self._set_suppress_rebuild_requests(False)

    def _enter_scene_mode(self):
        self._set_mode(SCENE_MODE)
        if self._mode == CLIP_MODE:
            self._deassign_matrix()
        elif self._mode == CONTROL_MODE:
            self._master_knob.exit_matrix_mode()
        elif self._mode == PAD_MODE:
            self._register_buttons()
        self._mode = SCENE_MODE
        self._scenematrix.assign()
        self._scenematrix.set_mode(SCENE_MODE_NORMAL)
        self._return_mode = SCENE_MODE_NORMAL
        self.request_rebuild_midi_map()

    def _enter_clip_mode(self):
        self._set_suppress_rebuild_requests(True)
        self._set_mode(CLIP_MODE)
        if self._mode == SCENE_MODE:
            self._scenematrix.deassign()
        elif self._mode == CONTROL_MODE:
            self._master_knob.exit_matrix_mode()
        self._mode = CLIP_MODE
        self._set_up_clip_matrix()
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)

    def _enter_control_mode(self):
        self._set_mode(CONTROL_MODE)
        if self._mode == CLIP_MODE:
            self._deassign_matrix()
        elif self._mode == PAD_MODE:
            self._mode = CONTROL_MODE
            self._register_buttons()
        self._mode = CONTROL_MODE
        self._set_suppress_rebuild_requests(True)
        self._scenematrix.set_mode(SCENE_MODE_CONTROL)
        self._return_mode = SCENE_MODE_CONTROL
        self._scenematrix.assign()
        self._master_knob.switch_to_matrix_mode()
        self._set_suppress_rebuild_requests(False)
        self.request_rebuild_midi_map()
        self._scenematrix.update()

    def _a_mode_scene(self, value):
        if not self.scene_mode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.show_message('SCENE MODE')
            self._enter_scene_mode()

    def _a_mode_clip(self, value):
        if not self.clip_mode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.show_message('CLIP MODE')
            self._enter_clip_mode()

    def _a_mode_pad(self, value):
        if not self.pad_mode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.show_message('PAD MODE')
            self._enter_pad_mode()

    def _a_mode_control(self, value):
        if not self.control_mode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.show_message('CONTROL MODE')
            self._enter_control_mode()

    def _do_pad_select_multi(self, value):
        if not value in range(128):
            raise AssertionError
            self._modifier_down = value != 0
            if self._mode == PAD_MODE or self._returntopad:
                value != 0 and self._from_pad_mode(SCENE_MODE_SELECT)
                self._returntopad = True
            else:
                self._returntopad = False
                self._enter_pad_mode()
        elif self._mode == CLIP_MODE:
            if value != 0:
                self._invoke_track_edit(SCENE_MODE_SELECT)
            else:
                self._back_to_clip_mode()
        elif self._mode != PAD_MODE:
            if value == 0:
                self._scenematrix.set_mode(self._return_mode)
            else:
                if self._scenematrix.in_main_mode():
                    self._return_mode = self._scenematrix.mode
                self._scenematrix.set_mode(SCENE_MODE_SELECT)

    def _do_mute_button(self, value):
        if not self._mute_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self._modifier_down = value != 0
                (self._mode == PAD_MODE or self._returntopad) and value != 0 and self._from_pad_mode(SCENE_MODE_MUTE)
                self._returntopad = True
            else:
                self._returntopad = False
                self._enter_pad_mode()
        elif self._mode == SCENE_MODE or self._mode == CONTROL_MODE:
            if value == 0:
                self._scenematrix.set_mode(self._return_mode)
                self._pad_mode = PM_OFF
            else:
                if self._scenematrix.in_main_mode():
                    self._return_mode = self._scenematrix.mode
                self._scenematrix.set_mode(SCENE_MODE_MUTE)
                self._pad_mode = PM_ON
        elif self._mode == CLIP_MODE:
            if value > 0:
                self._invoke_track_edit(SCENE_MODE_MUTE)
            else:
                self._back_to_clip_mode()
                self._pad_mode = PM_OFF

    def _do_pad_solo_multi(self, value):
        if not value in range(128):
            raise AssertionError
            self._modifier_down = value != 0
            if self._mode == PAD_MODE or self._returntopad:
                value != 0 and self._from_pad_mode(SCENE_MODE_SOLO)
                self._returntopad = True
            else:
                self._returntopad = False
                self._enter_pad_mode()
        elif self._mode == CLIP_MODE:
            if value != 0:
                self._invoke_track_edit(SCENE_MODE_SOLO)
            else:
                self._back_to_clip_mode()
        elif self._mode != PAD_MODE:
            if value == 0:
                self._scenematrix.set_mode(self._return_mode)
            else:
                if self._scenematrix.in_main_mode():
                    self._return_mode = self._scenematrix.mode
                self._scenematrix.set_mode(SCENE_MODE_SOLO)

    def _do_xfade_assign(self, value):
        if not self.xfade_assign_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                (self._mode == PAD_MODE or self._returntopad) and value != 0 and self._from_pad_mode(SCENE_MODE_XFADE)
                self._returntopad = True
            else:
                self._returntopad = False
                self._enter_pad_mode()
        elif self._mode == CLIP_MODE:
            if value != 0:
                self._invoke_track_edit(SCENE_MODE_XFADE)
            else:
                self._back_to_clip_mode()
        elif self._mode == SCENE_MODE or self._mode == CONTROL_MODE:
            if value == 0:
                self._scenematrix.set_mode(self._return_mode)
            else:
                if self._scenematrix.in_main_mode():
                    self._return_mode = self._scenematrix.mode
                self._scenematrix.set_mode(SCENE_MODE_XFADE)

    def _do_pad_note_up(self, value):
        if not self._pad_scale_up != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self._pad_scale_up.send_value(value, True)
                self._modifier_down = value != 0
                (self._mode == PAD_MODE or self._returntopad) and value != 0 and self._from_pad_mode(SCENE_MODE_ARM)
                self._returntopad = True
            else:
                self._returntopad = False
                self._enter_pad_mode()
        elif self._mode == CLIP_MODE:
            self.show_message('Arm tracks with pads')
            if value != 0:
                self._invoke_track_edit(SCENE_MODE_ARM)
            else:
                self._back_to_clip_mode()
        elif self._mode == SCENE_MODE or self._mode == CONTROL_MODE:
            self.show_message('Arm tracks with pads')
            if value == 0:
                self._scenematrix.set_mode(self._return_mode)
            else:
                if self._scenematrix.in_main_mode():
                    self._return_mode = self._scenematrix.mode
                self._scenematrix.set_mode(SCENE_MODE_ARM)

    def _do_pad_note_down(self, value):
        if not self._pad_scale_down != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self._pad_scale_down.send_value(value, True)
                self._modifier_down = value != 0
                (self._mode == PAD_MODE or self._returntopad) and value != 0 and self._from_pad_mode(SCENE_MODE_STOP)
                self._returntopad = True
            else:
                self._returntopad = False
                self._enter_pad_mode()
        elif self._mode == CLIP_MODE:
            self.show_message('Stop tracks with pads')
            if value != 0:
                self._invoke_track_edit(SCENE_MODE_STOP)
            else:
                self._back_to_clip_mode()
        elif self._mode == SCENE_MODE or self._mode == CONTROL_MODE:
            self.show_message('Stop tracks with pads')
            if value == 0:
                self._scenematrix.set_mode(self._return_mode)
            else:
                if self._scenematrix.in_main_mode():
                    self._return_mode = self._scenematrix.mode
                self._scenematrix.set_mode(SCENE_MODE_STOP)

    def modify_track_offset(self, delta):
        self._scenematrix.mod_track_offset(delta)

    def modify_scene_offset(self, delta):
        self._scenematrix.mod_scene_offset(delta)

    def move_view_horizontal(self, delta):
        if delta == 1:
            self._session.bank_right()
        else:
            self._session.bank_left()
        if self._mode == CONTROL_MODE:
            self._scenematrix.update()

    def inc_octave(self, inc):
        scale = SCALES[self.current_scale_index]
        octave = scale.to_octave(self._octave)
        newoctave = octave + inc
        if newoctave < 0:
            newoctave = 0
        elif newoctave > scale.octave_range:
            newoctave = scale.octave_range
        self._octave = scale.to_relative(newoctave, self._octave)
        scale = SCALES[self.current_scale_index]
        self.show_message(' OCTAVE ' + BASE_NOTE[self._base_note] + str(newoctave - 2) + ' to ' + scale.name)
        self.current_scale_to_display()

    def inc_base_note(self, inc):
        newbase = self._base_note + inc
        if newbase < 0:
            self._base_note = 0
        elif newbase > 11:
            self._base_note = 11
        else:
            self._base_note = newbase
        scale = SCALES[self.current_scale_index]
        self.show_message(' Base Note ' + BASE_NOTE[self._base_note] + ' to ' + scale.name)
        self.current_scale_to_display()

    def current_scale_to_display(self):
        scale = SCALES[self.current_scale_index]
        text = scale.name + ' ' + BASE_NOTE[self._base_note] + str(scale.to_octave(self._octave))
        self.send_to_display(text)

    def inc_scale(self, inc):
        nr_of_scales = len(SCALES)
        newindex = self.current_scale_index + inc
        if newindex < 0:
            newindex = 0
        elif newindex >= nr_of_scales:
            newindex = nr_of_scales - 1
        else:
            self.current_scale_index += inc
        newscale = SCALES[self.current_scale_index]
        self.show_message(' PAD Scale ' + newscale.name + ' ' + BASE_NOTE[self._base_note] + str(newscale.to_octave(self._octave) - 2))
        self.current_scale_to_display()

    def update_transpose(self):
        self.assign_transpose(SCALES[self.current_scale_index])
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)

    def set_scale(self, scale):
        raise isinstance(scale, PadScale) or AssertionError
        scale_len = len(scale.notevalues)
        octave = scale.to_octave(self._octave)

    def assign_transpose(self, scale):
        raise isinstance(scale, PadScale) or AssertionError
        scale_len = len(scale.notevalues)
        octave = scale.to_octave(self._octave)
        last_note_val = None
        for note_index in range(16):
            button = self._button_sequence[note_index]
            scale_index = note_index % scale_len
            octave_offset = note_index / scale_len
            note_value = scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
            if note_value < 128:
                last_note_val = note_value
            elif last_note_val != None:
                note_value = last_note_val
            button.set_send_note(note_value)
            if self._mode == PAD_MODE:
                button.send_color_direct(self.get_color_by_note_mode(note_value, False))

    def do_reset(self, value):
        if value == 0:
            return
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                data_byte1 = button._original_identifier
                button.send_midi((MIDI_CC_STATUS + 2, data_byte1, 0))

    def do_test(self, value):
        color = self.togglecolor[self.toggleindex]
        self.toggleindex = (self.toggleindex + 1) % len(self.togglecolor)
        if value == 0:
            return
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                self.schedule_message(1, self.dosend, (color,
                 127,
                 127,
                 row,
                 column))

    def dosend(self, parm = None):
        button = self._matrix[parm[3]][parm[4]]
        data_byte1 = button._original_identifier
        button.send_midi((MIDI_CC_STATUS + 0, data_byte1, parm[0]))
        button.send_midi((MIDI_CC_STATUS + 1, data_byte1, parm[1]))
        button.send_midi((MIDI_CC_STATUS + 2, data_byte1, parm[2]))

    def do_note_repeat(self, value):
        nrvalue = 0
        if value != 0:
            nrvalue = 1
        self._c_ref.set_note_repeat_state(nrvalue)

    def _do_toggle_send(self, value):
        nr_of_tracks = len(self.song().return_tracks)
        if value == 0 or nr_of_tracks < 1:
            return
        prev = self.send_slider_index
        self.send_slider_index += 1
        if self.send_slider_index >= nr_of_tracks:
            self.send_slider_index = 0
        self.show_message(' Set Send ' + str(SENDS[self.send_slider_index]))
        if prev != self.send_slider_index:
            for track in range(8):
                strip = self._mixer.channel_strip(track)
                slider_list = []
                for index in range(self.send_slider_index + 1):
                    if index < self.send_slider_index - 1:
                        slider_list.append(None)
                    else:
                        slider_list.append(self.send_sliders[track])
                    strip.set_send_controls(tuple(slider_list))

    def _do_armsolo_mode(self, value):
        if not self._armsolomode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self._scenematrix.set_armsolo_exclusive(self._armsolomode_button)

    def _do_fire_button(self, value):
        if not self._fire_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                clip_slot = (value != 0 or not self._mute_button.is_momentary()) and self.song().view.highlighted_clip_slot
                clip_slot and clip_slot.fire()

    def _do_undo(self, value):
        if not self._undo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                (value != 0 or not self._undo_button.is_momentary()) and self.song().can_undo == 1 and self.song().undo()
                self.show_message(str('UNDO'))

    def _do_redo(self, value):
        if not self._redo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                (value != 0 or not self._redo_button.is_momentary()) and self.song().can_redo == 1 and self.song().redo()
                self.show_message(str('REDO'))

    def _a_trk_left(self, value):
        if not value in range(128):
            raise AssertionError
            if value != 0:
                direction = self.application().view.is_view_visible('Session') and Live.Application.Application.View.NavDirection.left
                self.application().view.scroll_view(direction, 'Session', True)

    def _a_trk_right(self, value):
        if not value in range(128):
            raise AssertionError
            if value != 0:
                direction = self.application().view.is_view_visible('Session') and Live.Application.Application.View.NavDirection.right
                self.application().view.scroll_view(direction, 'Session', True)

    def _nav_value_left(self, value):
        if not self._device_nav_button_left != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                modifier_pressed = True
                value > 0 and (not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain')) and self.application().view.show_view('Detail')
                self.application().view.show_view('Detail/DeviceChain')
            else:
                direction = Live.Application.Application.View.NavDirection.left
                self.application().view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)

    def _nav_value_right(self, value):
        if not self._device_nav_button_right != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                modifier_pressed = value > 0 and True
                (not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain')) and self.application().view.show_view('Detail')
                self.application().view.show_view('Detail/DeviceChain')
            else:
                direction = Live.Application.Application.View.NavDirection.right
                self.application().view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)

    def _do_tap_tempo(self, value):
        if not value in range(128):
            raise AssertionError
            value > 0 and self.song().tap_tempo()

    def _do_toggle_cue(self, value):
        if not value in range(128):
            raise AssertionError
            value > 0 and self.song().set_or_delete_cue()

    def _do_toggle_prev_cue(self, value):
        if not value in range(128):
            raise AssertionError
            value > 0 and self.song().jump_to_prev_cue()

    def _do_toggle_next_cue(self, value):
        if not value in range(128):
            raise AssertionError
            value > 0 and self.song().jump_to_next_cue()

    def focus_changed(self):
        pass

    def _handle_device_changed(self, device):
        pass

    def _hande_device_parm_changed(self):
        pass

    def _do_focus_navigate(self, value):
        if not self._navigate_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.nav_index = value != 0 and (self.nav_index + 1) % len(VIEWS_ALL)
            self.application().view.focus_view(VIEWS_ALL[self.nav_index])
            self.show_message('Focus on : ' + str(VIEWS_ALL[self.nav_index]))

    def scroll_focus(self, delta):
        if delta == 1:
            self.nav_index = (self.nav_index + 1) % len(VIEWS_ALL)
        elif self.nav_index == 0:
            self.nav_index = len(VIEWS_ALL) - 1
        else:
            self.nav_index -= 1
        self.show_message('Focus on : ' + str(VIEWS_ALL[self.nav_index]))
        self.application().view.focus_view(VIEWS_ALL[self.nav_index])

    def scroll_device(self, delta):
        if not (delta == 1 or delta == -1):
            raise AssertionError
            direction = delta == 1 and Live.Application.Application.View.NavDirection.right
        else:
            direction = Live.Application.Application.View.NavDirection.left
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', True)

    def scroll_scene(self, delta):
        if not self.track_left_button != None:
            raise AssertionError
            raise delta == 1 or delta == -1 or AssertionError
            direction = delta == 1 and Live.Application.Application.View.NavDirection.down
        else:
            direction = Live.Application.Application.View.NavDirection.up
        self.application().view.scroll_view(direction, 'Session', True)

    def index_in_strip(self, track):
        for ind in range(len(self._mixer._channel_strips)):
            strack = self._mixer._channel_strips[ind]._track
            if strack == track:
                return ind

        return -1

    def notify_track_scroll(self):
        self._scenematrix.update_control_selection()
        if self._mode == CONTROL_MODE:
            self._scenematrix.eval_matrix()
            self._scenematrix.fire_values()

    def send_to_display(self, text, grid = 0):
        if USE_DISPLAY == False:
            return
        if len(text) > 28:
            text = text[:27]
        msgsysex = [240,
         0,
         0,
         102,
         23,
         18,
         min(grid, 3) * 28]
        filled = text.ljust(28)
        for c in filled:
            msgsysex.append(ord(c))

        msgsysex.append(247)
        self._send_midi(tuple(msgsysex))

    def send_color(self, button, hue, sat, bright):
        raise isinstance(button, ButtonElement) or AssertionError
        raise hue in range(128) or AssertionError
        raise sat in range(128) or AssertionError
        raise bright in range(128) or AssertionError
        data_byte1 = button._original_identifier
        button.send_midi((MIDI_CC_STATUS + 2, data_byte1, bright))
        button.send_midi((MIDI_CC_STATUS + 1, data_byte1, sat))
        button.send_midi((MIDI_CC_STATUS + 0, data_byte1, hue))

    def turn_off_matrix(self):
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                self.send_color(button, 2, 0, 0)
                button.set_to_notemode(False)

    def remove_listener(self, control, callback):
        if control != None and control.value_has_listener(callback):
            control.remove_value_listener(callback)
        control.disconnect()

    def disconnect(self):
        self.turn_off_matrix()
        self.scene_mode_button.send_value(0, True)
        self.clip_mode_button.send_value(0, True)
        self.pad_mode_button.send_value(0, True)
        self.control_mode_button.send_value(0, True)
        time.sleep(0.2)
        self._active = False
        self._suppress_send_midi = True
        self.remove_listener(self.scene_mode_button, self._a_mode_scene)
        self.remove_listener(self.clip_mode_button, self._a_mode_clip)
        self.remove_listener(self.pad_mode_button, self._a_mode_pad)
        self.remove_listener(self.control_mode_button, self._a_mode_control)
        self.remove_listener(self._undo_button, self._do_undo)
        self.remove_listener(self._redo_button, self._do_redo)
        self.remove_listener(self._armsolomode_button, self._do_armsolo_mode)
        self.remove_listener(self.xfade_assign_button, self._do_xfade_assign)
        self.remove_listener(self._fire_button, self._do_fire_button)
        self._session.remove_offset_listener(self.notify_track_scroll)
        self._mixer.disconnect()
        ControlSurface.disconnect(self)