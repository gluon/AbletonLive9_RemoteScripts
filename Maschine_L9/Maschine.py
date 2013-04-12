#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk1\Maschine.py
from __future__ import with_statement
import Live
import MidiRemoteScript
import time
from VarButtonElement import VarButtonElement, TwinButton
from StateButton import StateButton, ToggleButton
from MaschineSessionComponent import MaschineSessionComponent
from MaschineDeviceComponent import MaschineDeviceComponent
from PadScale import *
from SceneMatrix import SceneMatrix
from MainKnobControl import MainKnobControl
from MIDI_Map import *
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent

class Maschine(ControlSurface):
    __module__ = __name__
    __doc__ = 'Control Script for Maschine and Maschine Mikro'

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance, False)
        with self.component_guard():
            self._c_ref = c_instance
            register_sender(self)
            self._set_suppress_rebuild_requests(True)
            self._active = True
            self._midi_pause_count = 0
            self._suggested_input_port = str('Maschine Controller In')
            self._suggested_output_port = str('Maschine Controller Out')
            self.value_encoder_tempo = None
            self.enc_tempo_mode = None
            self.nav_index = 0
            self.blink_state = 1
            self._scenematrix = SceneMatrix(self)
            self._master_knob = MainKnobControl(self)
            self.md_select_pressed = False
            self.md_solo_pressed = False
            self._rec_quant = Live.Song.RecordingQuantization.rec_q_no_q
            self.adjust_time = None
            self.modelegacy = False
            self.test_value = 1
            self._mode = CLIP_MODE
            self._modifier_down = False
            self.time_callback = None
            self._device_nav_button_left = None
            self._device_nav_button_right = None
            self._return_mode = 0
            self._returntopad = False
            self._pad_mode = PM_OFF
            self._device = self._set_up_device_control()
            self._base_note = 0
            self._octave = 0.55
            self._scale_select_mode = MODE_PRESS_NONE
            self.show_message(str(''))
            self.request_rebuild_midi_map()
            self.send_sliders = []
            for track in range(8):
                self.send_sliders.append(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, SEND_CC_OFF + track))

            self.send_slider_index = 0
            self.send_slider_toggle_button = StateButton(False, MIDI_CC_TYPE, 0, 90)
            self.send_slider_toggle_button.add_value_listener(self._do_toggle_send)
            self._set_up_controls()
            self._setup_transport()
            self._set_up_session()
            self._set_up_mixer()
            self._set_up_machine_knobs()
            self.current_scale_index = 0
            self.assign_transpose(SCALES[self.current_scale_index])
            self.set_highlighting_session_component(self._session)
            self._set_mode()
            self._set_suppress_rebuild_requests(False)
            self.timer_repeat = 0
            self.time_callback = None
            self.schedule_message(3, self._start_display)
            self.song().view.add_detail_clip_listener(self.clip_handle)
            self.song().add_visible_tracks_listener(self.clip_handle)
            self.song().add_scenes_listener(self.clip_handle)
            self.application().view.add_view_focus_changed_listener(self.focus_changed)
            self.log_message('##### LIVE 9 Maschine & Machine Mikro Controller - Version: 1.00')

    def _start_display(self):
        self._set_mode()
        self._master_knob.update()
        self.clip_mode_button.send_value(127, True)
        if self._scenematrix.soloexclusive:
            self._armsolomode_button.send_value(127, True)
        else:
            self._armsolomode_button.send_value(0, True)
        self._master_knob.start_up()
        self.current_scale_to_display()

    def _set_up_controls(self):
        is_momentary = True
        self.scene_mode_button = None
        self._set_scene_mode_button(StateButton(False, MIDI_CC_TYPE, 0, 112))
        self.clip_mode_button = None
        self._set_clip_mode_button(StateButton(False, MIDI_CC_TYPE, 0, 113))
        self.pad_mode_button = None
        self._set_pad_mode_button(StateButton(False, MIDI_CC_TYPE, 0, 114))
        self.control_mode_button = None
        self._set_control_mode_button(StateButton(False, MIDI_CC_TYPE, 0, 115))
        self.xfade_assign_button = None
        self._set_xfade_assign_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 116))
        self._undo_button = None
        self._set_undo_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 85))
        self._redo_button = None
        self._set_redo_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 87))
        self._armsolomode_button = None
        self._set_armsolomode_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 89))
        self._pad_scale_up = None
        self._pad_scale_down = None
        self._set_scale_up_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 83))
        self._set_scale_down_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 94))
        self._mode_octave_button = None
        self._mode_base_button = None
        self._fire_button = None
        self._set_mode_select_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 117))
        self._set_mode_solo_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 118))
        self._set_fire_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 119))
        self._pad_solo_button = None
        self._mute_button = None
        self._pad_select_button = None
        self._group_d_button = None
        self._group_h_button = None
        self._fire_dedictated_button = None
        self._set_mikro_select_button(StateButton(False, MIDI_CC_TYPE, 1, 117))
        self._set_mikro_solo_button(StateButton(False, MIDI_CC_TYPE, 1, 118))
        self._set_mute_button(StateButton(is_momentary, MIDI_CC_TYPE, 1, 119))
        self._set_group_d_button(StateButton(is_momentary, MIDI_CC_TYPE, 1, 120))
        self._set_group_h_button(StateButton(is_momentary, MIDI_CC_TYPE, 1, 121))
        self._set_dedictated_fire_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 9))
        self.test_button = StateButton(is_momentary, MIDI_CC_TYPE, 5, 60)
        self.note_repeat_button = StateButton(is_momentary, MIDI_CC_TYPE, 5, 61)
        self.test_button.add_value_listener(self.do_test)
        self.note_repeat_button.add_value_listener(self.do_note_repeat)
        self.track_left_button = None
        self._set_track_left_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 120))
        self.track_right_button = None
        self._set_track_right_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 121))
        self._navigate_button = None
        self._set_navigate_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 127))
        self.display_update_button = None
        self._set_display_update_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 86))

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
        device.set_bank_nav_buttons(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 4), StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 5))
        self._device_nav_button_left = StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 6)
        self._device_nav_button_right = StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF + 7)
        self._device_nav_button_left.add_value_listener(self._nav_value_left)
        self._device_nav_button_right.add_value_listener(self._nav_value_right)
        device.name = 'Device_Component'
        self.set_device_component(device)
        return device

    def _set_up_mixer(self):
        self._mixer = MixerComponent(8)
        for track in range(8):
            strip = self._mixer.channel_strip(track)
            strip.set_arm_button(StateButton(True, MIDI_CC_TYPE, BASIC_CHANNEL, ARM_CC_OFF + track))
            strip.set_solo_button(StateButton(True, MIDI_CC_TYPE, BASIC_CHANNEL, SOLO_CC_OFF + track))
            strip.set_mute_button(StateButton(True, MIDI_CC_TYPE, BASIC_CHANNEL, MUTE_CC_OFF + track))
            strip.set_volume_control(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, LEVEL_CC_OFF + track))
            strip.set_pan_control(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, PAN_CC_OFF + track))
            strip.set_select_button(StateButton(True, MIDI_CC_TYPE, BASIC_CHANNEL, SELECT_CC_OFF + track))
            st = tuple([self.send_sliders[track]])
            strip.set_send_controls(st)

        self._session.set_mixer(self._mixer)

    def update_display(self):
        with self.component_guard():
            with self._is_sending_scheduled_messages():
                self._task_group.update(0.1)
            if self._mode == CLIP_MODE and not self._modifier_down:
                self._session.notify_b(self.blink_state)
            elif self._mode == PAD_MODE:
                pass
            else:
                self._scenematrix.notify_scene_mode(self.blink_state)
            self.blink_state = (self.blink_state + 1) % 8

    def _set_mode(self, mode = None):
        selMode = self._mode
        if selMode != None:
            selMode = mode
        if selMode == SCENE_MODE:
            self.clip_mode_button.send_value(0, True)
            self.pad_mode_button.send_value(0, True)
            self.control_mode_button.send_value(0, True)
            self.scene_mode_button.send_value(127, True)
        elif selMode == CLIP_MODE:
            self.scene_mode_button.send_value(0, True)
            self.pad_mode_button.send_value(0, True)
            self.control_mode_button.send_value(0, True)
            self.clip_mode_button.send_value(100, True)
        elif selMode == PAD_MODE:
            self.scene_mode_button.send_value(0, True)
            self.clip_mode_button.send_value(0, True)
            self.control_mode_button.send_value(0, True)
            self.pad_mode_button.send_value(127, True)
        elif selMode == CONTROL_MODE:
            self.scene_mode_button.send_value(0, True)
            self.clip_mode_button.send_value(0, True)
            self.pad_mode_button.send_value(0, True)
            self.control_mode_button.send_value(127, True)

    def song(self):
        return ControlSurface.song(self)

    def _set_up_session(self):
        self._session = MaschineSessionComponent()
        self._session.add_offset_listener(self.notify_track_scroll)
        self._session.set_scene_bank_buttons(StateButton(True, MIDI_CC_TYPE, 0, 92), StateButton(True, MIDI_CC_TYPE, 0, 81))
        self._session.set_track_bank_buttons(StateButton(True, MIDI_CC_TYPE, 0, 93), StateButton(True, MIDI_CC_TYPE, 0, 91))
        self._session.set_stop_all_clips_button(StateButton(True, MIDI_CC_TYPE, 0, 111))
        track_stop_buttons = [ StateButton(True, MIDI_CC_TYPE, BASIC_CHANNEL, index + STOP_CC_OFF) for index in range(4) ]
        self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
        self._init_matrix()
        self._set_up_buttons()
        self._session._link()
        self._session.set_advance(STEP4)

    def _init_matrix(self):
        self._button_sequence = []
        self._matrix = []
        for scene_index in range(4):
            button_row = []
            for track_index in range(4):
                button = VarButtonElement(True, 0, scene_index, track_index, self)
                partner = TwinButton(True, 1, button)
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

    def ox(self, value, button):
        if not isinstance(button, TwinButton):
            raise AssertionError
            self._mode == PAD_MODE and button.fire(value)

    def _set_up_buttons(self):
        self._bmatrix = None
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

    def set_appointed_device(self, device):
        with self.component_guard():
            self._device.set_device(device)

    def _deassign_matrix(self):
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(None)

    def _setup_transport(self):
        is_momentary = True
        transport = TransportComponent()
        transport.set_play_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 108))
        transport.set_stop_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 110))
        transport.set_record_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 109))
        transport.set_overdub_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 107))
        transport.set_metronome_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 104))
        transport.set_nudge_buttons(StateButton(is_momentary, MIDI_CC_TYPE, 1, 51), StateButton(is_momentary, MIDI_CC_TYPE, 1, 50))
        transport.set_punch_buttons(ToggleButton(MIDI_CC_TYPE, 1, 52), ToggleButton(MIDI_CC_TYPE, 1, 53))
        transport.set_loop_button(StateButton(is_momentary, MIDI_CC_TYPE, 1, 54))
        transport.set_seek_buttons(StateButton(is_momentary, MIDI_CC_TYPE, 1, 59), StateButton(is_momentary, MIDI_CC_TYPE, 1, 58))
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

    def _invoke_track_edit(self, mode):
        self._deassign_matrix()
        self._scenematrix.assign()
        self._scenematrix.set_mode(mode)
        self._scenematrix.set_active(True)
        self._pad_mode = PM_ON
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)
        self._scenematrix.update()

    def _enter_control_mode(self):
        self._set_mode(CONTROL_MODE)
        if self._mode == CLIP_MODE:
            self._deassign_matrix()
        elif self._mode == PAD_MODE:
            self._register_buttons()
        self._scenematrix.assign()
        self._scenematrix.set_mode(SCENE_MODE_CONTROL)
        self._scenematrix.set_active(True)
        self._return_mode = SCENE_MODE_CONTROL
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)
        self._scenematrix.update()
        self._master_knob.switch_to_matrix_mode()
        self._mode = CONTROL_MODE

    def _enter_scene_mode(self):
        self._set_mode(SCENE_MODE)
        if self._mode == CLIP_MODE:
            self._deassign_matrix()
        elif self._mode == PAD_MODE:
            self._register_buttons()
        elif self._mode == CONTROL_MODE:
            self._master_knob.exit_matrix_mode()
        self._scenematrix.assign()
        self._scenematrix.set_mode(SCENE_MODE_NORMAL)
        self._scenematrix.set_active(True)
        self._return_mode = SCENE_MODE_NORMAL
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)
        self._scenematrix.update()
        self._mode = SCENE_MODE

    def _from_pad_mode(self, matrix_mode):
        self._register_buttons()
        self._scenematrix.assign()
        self._scenematrix.set_mode(matrix_mode)
        self._scenematrix.set_active(True)
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)
        self._scenematrix.update()
        self._mode = SCENE_MODE

    def _enter_pad_mode(self):
        self._set_mode(PAD_MODE)
        if self._mode == CLIP_MODE:
            self._deassign_matrix()
        elif self._mode == SCENE_MODE:
            self._scenematrix.deassign()
        elif self._mode == CONTROL_MODE:
            self._scenematrix.deassign()
            self._master_knob.exit_matrix_mode()
        self._scenematrix.set_active(False)
        self._mode = PAD_MODE
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.send_value(0, True)
                button.set_to_notemode(True)
                self._forwarding_registry[MIDI_NOTE_ON_STATUS, button.get_identifier()] = button
                self._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button

        self._mode = PAD_MODE

    def _register_buttons(self):
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.set_to_notemode(False)
                button.send_value(0)
                fwkey = [MIDI_NOTE_ON_STATUS]
                fwkey.append(button.get_identifier())
                self._forwarding_registry[tuple(fwkey)] = button
                self._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button

    def _back_to_clip_mode(self):
        self._pad_mode = PM_OFF
        self._scenematrix.set_mode(SCENE_MODE_NORMAL)
        self._scenematrix.deassign()
        self._scenematrix.set_active(False)
        self._set_up_clip_matrix()

    def _enter_clip_mode(self):
        self._set_mode(CLIP_MODE)
        if self._mode == SCENE_MODE:
            self._scenematrix.deassign()
            self._scenematrix.set_active(False)
        elif self._mode == CONTROL_MODE:
            self._master_knob.exit_matrix_mode()
            self._scenematrix.set_active(False)
        self._set_up_clip_matrix()
        self._mode = CLIP_MODE

    def _set_up_clip_matrix(self):
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.set_to_notemode(False)

        self.request_rebuild_midi_map()
        self._reset_matrix()
        self.update_button_matrix()

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

    def _set_up_machine_knobs(self):
        master_track = self.song().master_track
        self.recordQuantSlider = SliderElement(MIDI_CC_TYPE, 0, 42)
        self.recordQuantSlider.add_value_listener(self._on_rec_quant, True)
        self.master_volume = SliderElement(MIDI_CC_TYPE, 0, 40)
        self.prehear = SliderElement(MIDI_CC_TYPE, 0, 41)
        self.master_volume.connect_to(master_track.mixer_device.volume)
        self.prehear.connect_to(master_track.mixer_device.cue_volume)

    def _on_rec_quant(self, value, encoder):
        if not value in range(128):
            raise AssertionError
            raise isinstance(encoder, EncoderElement) or AssertionError
            self._scale_select_mode == MODE_PRESS_NONE and self.set_quant(value)
            self.value_encoder_tempo = value
            self.enc_tempo = self.song().tempo
        elif self._scale_select_mode == MODE_PRESS_SELECT or self._scale_select_mode == MODE_PRESS_SOLO:
            if self.value_encoder_tempo == None:
                self.value_encoder_tempo = value
                self.enc_tempo = self.song().tempo
                self.enc_tempo_mode = self._scale_select_mode
            else:
                if self.enc_tempo_mode != self._scale_select_mode:
                    self.value_encoder_tempo = value
                diff = value - self.value_encoder_tempo
                if self._scale_select_mode == MODE_PRESS_SOLO:
                    diff *= 0.01
                self.song().tempo = max(20, min(999, self.enc_tempo + diff))
                self.enc_tempo_mode = self._scale_select_mode
            if value == 127 or value == 0:
                encoder.send_value(63, True)
                self.value_encoder_tempo = 63
                self.enc_tempo = self.song().tempo

    def set_quant(self, value):
        req_q = None
        msg = None
        if value < 15:
            msg = ' No Rec Quant '
            self._rec_quant = self.song().midi_recording_quantization
            req_q = Live.Song.RecordingQuantization.rec_q_no_q
        elif value < 30:
            msg = ' 1/4 Rec Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_quarter
        elif value < 45:
            msg = ' 1/8 Rec Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_eight
        elif value < 60:
            msg = ' 1/8 Triplet Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_eight_triplet
        elif value < 75:
            msg = ' 1/8 & 1/8 Triplet Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_eight_eight_triplet
        elif value < 90:
            msg = ' 1/16 Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_sixtenth
        elif value < 105:
            msg = ' 1/16 Triplet Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_sixtenth_triplet
        else:
            msg = ' 1/16 & 1/16 Triplet Quant'
            req_q = Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet
        if req_q != self._rec_quant:
            self.song().midi_recording_quantization = req_q
            self._rec_quant = req_q
            self.show_message(str(msg))

    def _set_undo_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._undo_button != None:
                self._undo_button.remove_value_listener(self._do_undo)
            self._undo_button = button
            self._undo_button != None and self._undo_button.add_value_listener(self._do_undo)

    def _do_undo(self, value):
        if not self._undo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                (value != 0 or not self._undo_button.is_momentary()) and self.song().can_undo == 1 and self.song().undo()
                self.show_message(str('UNDO'))

    def _set_redo_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._redo_button != None:
                self._redo_button.remove_value_listener(self._do_redo)
            self._redo_button = button
            self._redo_button != None and self._redo_button.add_value_listener(self._do_redo)

    def _do_redo(self, value):
        if not self._redo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                (value != 0 or not self._redo_button.is_momentary()) and self.song().can_redo == 1 and self.song().redo()
                self.show_message(str('Redo'))

    def _set_armsolomode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._armsolomode_button != None:
                self._armsolomode_button.remove_value_listener(self._do_armsolo_mode)
            self._armsolomode_button = button
            self._armsolomode_button != None and self._armsolomode_button.add_value_listener(self._do_armsolo_mode)

    def _do_armsolo_mode(self, value):
        if not self._armsolomode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self._scenematrix.set_armsolo_exclusive(self._armsolomode_button)

    def _set_navigate_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._navigate_button != None:
                self._navigate_button.remove_value_listener(self._do_navigate)
            self._navigate_button = button
            self._navigate_button != None and self._navigate_button.add_value_listener(self._do_navigate)

    def _do_navigate(self, value):
        if not self._navigate_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.nav_index = value != 0 and (self.nav_index + 1) % len(VIEWS_ALL)
            self.application().view.focus_view(VIEWS_ALL[self.nav_index])
            self.show_message('Focus on : ' + str(VIEWS_ALL[self.nav_index]))

    def _set_fire_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._fire_button != None:
                self._fire_button.remove_value_listener(self._do_mute_fire_button)
            self._fire_button = button
            self._fire_button != None and self._fire_button.add_value_listener(self._do_mute_fire_button)

    def _do_mute_fire_button(self, value):
        raise self._fire_button != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_mute(value, True)

    def _set_mute_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._mute_button != None:
                self._mute_button.remove_value_listener(self._do_mute_button)
            self._mute_button = button
            self._mute_button != None and self._mute_button.add_value_listener(self._do_mute_button)

    def _do_mute_button(self, value):
        raise self._mute_button != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_mute(value, self.modelegacy)

    def _handle_mute(self, value, legacymode = False):
        self._modifier_down = value != 0
        if legacymode and self._mode == PAD_MODE:
            if value != 0 or not self._mute_button.is_momentary():
                clip_slot = self.song().view.highlighted_clip_slot
                if clip_slot:
                    clip_slot.fire()
        if not legacymode and (self._mode == PAD_MODE or self._returntopad):
            if value != 0:
                self._from_pad_mode(SCENE_MODE_MUTE)
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

    def _set_dedictated_fire_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._fire_dedictated_button != None:
                self._fire_dedictated_button.remove_value_listener(self._do_dedictated_fire_button)
            self._fire_dedictated_button = button
            self._fire_dedictated_button != None and self._fire_dedictated_button.add_value_listener(self._do_dedictated_fire_button)

    def _do_dedictated_fire_button(self, value):
        if not self._fire_dedictated_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                clip_slot = (value != 0 or not self._mute_button.is_momentary()) and self.song().view.highlighted_clip_slot
                clip_slot and clip_slot.fire()

    def _set_mode_solo_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._mode_base_button != None:
                self._mode_base_button.remove_value_listener(self._do_pad_mode_base)
            self._mode_base_button = button
            self._mode_base_button != None and self._mode_base_button.add_value_listener(self._do_pad_mode_base)

    def _do_pad_mode_base(self, value):
        raise self._mode_base_button != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_solo(value, True)

    def _set_mikro_solo_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._pad_solo_button != None:
                self._pad_solo_button.remove_value_listener(self._do_pad_solo_multi)
            self._pad_solo_button = button
            self._pad_solo_button != None and self._pad_solo_button.add_value_listener(self._do_pad_solo_multi)

    def _do_pad_solo_multi(self, value):
        raise value in range(128) or AssertionError
        self._handle_solo(value, self.modelegacy)

    def _handle_solo(self, value, asmodifier = False):
        self._modifier_down = value != 0
        if asmodifier and self._mode == PAD_MODE:
            if value == 0:
                self._scale_select_mode = MODE_PRESS_NONE
            else:
                self._scale_select_mode = MODE_PRESS_SOLO
        elif not asmodifier and (self._mode == PAD_MODE or self._returntopad):
            if value != 0:
                self._from_pad_mode(SCENE_MODE_SOLO)
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

    def _set_mode_select_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._mode_octave_button != None:
                self._mode_octave_button.remove_value_listener(self._do_pad_mode_octave)
            self._mode_octave_button = button
            self._mode_octave_button != None and self._mode_octave_button.add_value_listener(self._do_pad_mode_octave)

    def _do_pad_mode_octave(self, value):
        raise self._mode_octave_button != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_select(value, True)

    def _set_mikro_select_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._pad_select_button != None:
                self._pad_select_button.remove_value_listener(self._do_pad_select_multi)
            self._pad_select_button = button
            self._pad_select_button != None and self._pad_select_button.add_value_listener(self._do_pad_select_multi)

    def _do_pad_select_multi(self, value):
        raise value in range(128) or AssertionError
        self._handle_select(value, self.modelegacy)

    def _handle_select(self, value, asmodifer = False):
        self._modifier_down = value != 0
        if asmodifer and self._mode == PAD_MODE:
            if value == 0:
                self._scale_select_mode = MODE_PRESS_NONE
            else:
                self._scale_select_mode = MODE_PRESS_SELECT
        elif not asmodifer and (self._mode == PAD_MODE or self._returntopad):
            if value != 0:
                self._from_pad_mode(SCENE_MODE_SELECT)
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

    def _set_scale_up_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._pad_scale_up != None:
                self._pad_scale_up.remove_value_listener(self._do_pad_note_up)
            self._pad_scale_up = button
            self._pad_scale_up != None and self._pad_scale_up.add_value_listener(self._do_pad_note_up)

    def _do_pad_note_up(self, value):
        raise self._pad_scale_up != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_groupd_up(value, True)

    def _set_group_d_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._group_d_button != None:
                self._group_d_button.remove_value_listener(self._do_arm)
            self._group_d_button = button
            self._group_d_button != None and self._group_d_button.add_value_listener(self._do_arm)

    def _do_arm(self, value):
        raise self._pad_scale_up != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_groupd_up(value, self.modelegacy)

    def _handle_groupd_up(self, value, legacymode = False):
        self._modifier_down = value != 0
        if legacymode and self._mode == PAD_MODE:
            if value != 0:
                if self._scale_select_mode == MODE_PRESS_SELECT:
                    self.inc_scale(1)
                elif self._scale_select_mode == MODE_PRESS_SOLO:
                    self.inc_base_note(1)
                else:
                    self.inc_octave(1)
        elif not legacymode and (self._mode == PAD_MODE or self._returntopad):
            if value != 0:
                self._from_pad_mode(SCENE_MODE_ARM)
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

    def _set_scale_down_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._pad_scale_down != None:
                self._pad_scale_down.remove_value_listener(self._do_pad_note_down)
            self._pad_scale_down = button
            self._pad_scale_down != None and self._pad_scale_down.add_value_listener(self._do_pad_note_down)

    def _do_pad_note_down(self, value):
        raise self._pad_scale_down != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_grouph_down(value, True)

    def _set_group_h_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._group_h_button != None:
                self._group_h_button.remove_value_listener(self._do_stop)
            self._group_h_button = button
            self._group_h_button != None and self._group_h_button.add_value_listener(self._do_stop)

    def _do_stop(self, value):
        raise self._group_h_button != None or AssertionError
        raise value in range(128) or AssertionError
        self._handle_grouph_down(value)

    def _handle_grouph_down(self, value, legacymode = False):
        self._modifier_down = value != 0
        if legacymode and self._mode == PAD_MODE:
            if value != 0:
                if self._scale_select_mode == MODE_PRESS_SELECT:
                    self.inc_scale(-1)
                elif self._scale_select_mode == MODE_PRESS_SOLO:
                    self.inc_base_note(-1)
                else:
                    self.inc_octave(-1)
        elif not legacymode and (self._mode == PAD_MODE or self._returntopad):
            if value != 0:
                self._from_pad_mode(SCENE_MODE_STOP)
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

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        if self._midi_pause_count == 2:
            time.sleep(0.002)
            self._midi_pause_count = 0
        else:
            self._midi_pause_count = self._midi_pause_count + 1
        return True

    def do_test(self, value):
        if value == 0:
            return
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                if self.test_value == 0:
                    button.send_value(0, True)
                else:
                    button.send_value(120, True)

        self.scene_mode_button.send_value(self.test_value, True)
        self.clip_mode_button.send_value(self.test_value, True)
        self.pad_mode_button.send_value(self.test_value, True)
        self.control_mode_button.send_value(self.test_value, True)
        if self.test_value == 1:
            self.test_value = 0
        else:
            self.test_value = 1

    def do_note_repeat(self, value):
        nrvalue = 0
        if value != 0:
            nrvalue = 1
        debug_out(' REPEAT HOLD ' + str(nrvalue))

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
        self.assign_transpose(scale)
        self.show_message(' OCTAVE ' + BASE_NOTE[self._base_note] + str(newoctave - 2) + ' to ' + scale.name)
        self.current_scale_to_display()

    def inc_base_note(self, inc):
        newbase = self._base_note + inc
        if newbase < 0:
            self._base_note = 11
        elif newbase > 11:
            self._base_note = 0
        else:
            self._base_note = newbase
        scale = SCALES[self.current_scale_index]
        self.assign_transpose(scale)
        self.show_message(' Base Note ' + BASE_NOTE[self._base_note] + ' to ' + scale.name)
        self.current_scale_to_display()

    def inc_scale(self, inc):
        nr_of_scales = len(SCALES)
        newindex = self.current_scale_index + inc
        if newindex >= 0 and newindex < nr_of_scales:
            self.current_scale_index += inc
        elif newindex < 0:
            self.current_scale_index = nr_of_scales - 1
        else:
            self.current_scale_index = 0
        newscale = SCALES[self.current_scale_index]
        self.assign_transpose(newscale)
        self.show_message(' PAD Scale ' + newscale.name + ' ' + BASE_NOTE[self._base_note] + str(newscale.to_octave(self._octave) - 2))
        self.current_scale_to_display()

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
            button.send_value(0)

        self.update_transpose()

    def set_device_nav_button_left(self, button):
        if self._device_nav_button_left != None:
            self._device_nav_button_left.remove_value_listener(self._nav_value_left)
        self._device_nav_button_left = button
        if self._device_nav_button_left != None:
            self._device_nav_button_left.add_value_listener(self._nav_value_left)

    def set_device_nav_button_right(self, button):
        if self._device_nav_button_right != None:
            self._device_nav_button_right.remove_value_listener(self._nav_value_right)
        self._device_nav_button_right = button
        if self._device_nav_button_right != None:
            self._device_nav_button_right.add_value_listener(self._nav_value_right)

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

    def _set_xfade_assign_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.xfade_assign_button != None:
                self.xfade_assign_button.remove_value_listener(self._do_xfade_assign)
            self.xfade_assign_button = button
            self.xfade_assign_button != None and self.xfade_assign_button.add_value_listener(self._do_xfade_assign)

    def _do_xfade_assign(self, value):
        if not self.xfade_assign_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self._modifier_down = value != 0
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

    def _set_track_left_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.track_left_button != None:
                self.track_left_button.remove_value_listener(self._a_trk_left)
            self.track_left_button = button
            self.track_left_button != None and self.track_left_button.add_value_listener(self._a_trk_left)

    def _set_track_right_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.track_right_button != None:
                self.track_right_button.remove_value_listener(self._a_trk_right)
            self.track_right_button = button
            self.track_right_button != None and self.track_right_button.add_value_listener(self._a_trk_right)

    def _set_display_update_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.display_update_button != None:
                self.display_update_button.remove_value_listener(self._a_display_update)
            self.display_update_button = button
            self.display_update_button != None and self.display_update_button.add_value_listener(self._a_display_update)

    def _set_scene_mode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.scene_mode_button != None:
                self.scene_mode_button.remove_value_listener(self._a_mode_scene)
            self.scene_mode_button = button
            self.scene_mode_button != None and self.scene_mode_button.add_value_listener(self._a_mode_scene)

    def _set_clip_mode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.clip_mode_button != None:
                self.clip_mode_button.remove_value_listener(self._a_mode_clip)
            self.clip_mode_button = button
            self.clip_mode_button != None and self.clip_mode_button.add_value_listener(self._a_mode_clip)

    def _set_pad_mode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.pad_mode_button != None:
                self.pad_mode_button.remove_value_listener(self._a_mode_pad)
            self.pad_mode_button = button
            self.pad_mode_button != None and self.pad_mode_button.add_value_listener(self._a_mode_pad)

    def _set_control_mode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.control_mode_button != None:
                self.control_mode_button.remove_value_listener(self._a_mode_control)
            self.control_mode_button = button
            self.control_mode_button != None and self.control_mode_button.add_value_listener(self._a_mode_control)

    def _a_mode_control(self, value):
        if not self.control_mode_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.show_message('CONTROL MODE')
            self._set_mode(CONTROL_MODE)
            self._enter_control_mode()

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
            self._set_mode(PAD_MODE)
            self._enter_pad_mode()

    def clip_handle(self):
        if self._mode == SCENE_MODE or self._mode == CONTROL_MODE or self._modifier_down:
            self._scenematrix.update()

    def focus_changed(self):
        pass

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

    def _a_trk_left(self, value):
        if not self.track_left_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                direction = value != 0 and self.application().view.is_view_visible('Session') and Live.Application.Application.View.NavDirection.left
                self.application().view.scroll_view(direction, 'Session', True)

    def _a_trk_right(self, value):
        if not self.track_left_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                direction = value != 0 and self.application().view.is_view_visible('Session') and Live.Application.Application.View.NavDirection.right
                self.application().view.scroll_view(direction, 'Session', True)

    def update_transpose(self):
        self._set_suppress_rebuild_requests(True)
        self.request_rebuild_midi_map()
        self._set_suppress_rebuild_requests(False)

    def _a_display_update(self, value):
        if not self.display_update_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if value != 0 or not self.display_update_button.is_momentary():
                    self.show_message(' Maschine Display Updated ')
                    self._master_knob.update()
                    self._set_mode()
                    self._mode == PAD_MODE and self.assign_transpose(SCALES[self.current_scale_index])
                elif self._mode == SCENE_MODE:
                    self._enter_scene_mode()
                elif self._mode == CONTROL_MODE:
                    self._enter_control_mode()
                self._master_knob.start_up()
                self.current_scale_to_display()
                self._scenematrix.soloexclusive and self._armsolomode_button.send_value(127, True)
            else:
                self._armsolomode_button.send_value(0, True)
            self._session.update()
            self.refresh_state()
            self.update_display()

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

    def handle_sysex(self, midi_bytes):
        pass

    def turn_off_matrix(self):
        for row in range(4):
            for column in range(4):
                button = self._matrix[row][column]
                button.set_to_notemode(False)
                button.send_value(0, True)
                button.send_value(0, True)

    def _handle_device_changed(self, device):
        self._scenematrix.update_on_device(device)

    def _hande_device_parm_changed(self):
        self._scenematrix.update_on_device_parm_changed()

    def remove_listener(self, control, callback):
        if control != None and control.value_has_listener(callback):
            control.remove_value_listener(callback)
        control.disconnect()

    def current_scale_to_display(self):
        scale = SCALES[self.current_scale_index]
        text = scale.name + ' ' + BASE_NOTE[self._base_note] + str(scale.to_octave(self._octave))
        self.send_to_display(text)

    def send_to_display(self, text, grid = 0):
        if not USE_DISPLAY:
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

    def disconnect(self):
        self.turn_off_matrix()
        self._active = False
        self.send_to_display('', 0)
        self.send_to_display('', 1)
        self.send_to_display('', 2)
        self.send_to_display('', 3)
        self._set_suppress_rebuild_requests(True)
        self._master_knob.disconnect()
        self.xfadeKnob.disconnect()
        self.remove_listener(self.tap_button, self._do_tap_tempo)
        self.remove_listener(self.cue_add_delete_button, self._do_toggle_cue)
        self.remove_listener(self.cue_prev_button, self._do_toggle_prev_cue)
        self.remove_listener(self.cue_next_button, self._do_toggle_next_cue)
        self.remove_listener(self.send_slider_toggle_button, self._do_toggle_send)
        self.remove_listener(self.recordQuantSlider, self._on_rec_quant)
        self.remove_listener(self._undo_button, self._do_undo)
        self.remove_listener(self._redo_button, self._do_redo)
        self.remove_listener(self._armsolomode_button, self._do_armsolo_mode)
        self.remove_listener(self._navigate_button, self._do_navigate)
        self.remove_listener(self._fire_button, self._do_mute_fire_button)
        self.remove_listener(self._mode_base_button, self._do_pad_mode_base)
        self.remove_listener(self._mode_octave_button, self._do_pad_mode_octave)
        self.remove_listener(self._pad_scale_up, self._do_pad_note_up)
        self.remove_listener(self._pad_scale_down, self._do_pad_note_down)
        self.remove_listener(self._device_nav_button_left, self._nav_value_left)
        self.remove_listener(self._device_nav_button_right, self._nav_value_right)
        self.remove_listener(self.xfade_assign_button, self._do_xfade_assign)
        self.remove_listener(self.track_left_button, self._a_trk_left)
        self.remove_listener(self.track_right_button, self._a_trk_right)
        self.remove_listener(self.display_update_button, self._a_display_update)
        self.remove_listener(self.scene_mode_button, self._a_mode_scene)
        self.remove_listener(self.clip_mode_button, self._a_mode_clip)
        self.remove_listener(self.pad_mode_button, self._a_mode_pad)
        self.remove_listener(self.control_mode_button, self._a_mode_control)
        self.remove_listener(self._pad_solo_button, self._do_pad_solo_multi)
        self.remove_listener(self._mute_button, self._do_mute_button)
        self.remove_listener(self._pad_select_button, self._do_pad_select_multi)
        self.remove_listener(self._group_d_button, self._do_arm)
        self.remove_listener(self._group_h_button, self._do_stop)
        self.remove_listener(self._fire_dedictated_button, self._do_dedictated_fire_button)
        self.xfadeKnob.disconnect()
        self.master_volume.disconnect()
        self.prehear.disconnect()
        self._mixer.disconnect()
        self.song().view.remove_detail_clip_listener(self.clip_handle)
        self.song().remove_visible_tracks_listener(self.clip_handle)
        self.song().remove_scenes_listener(self.clip_handle)
        self.application().view.remove_view_focus_changed_listener(self.focus_changed)
        self._button_sequence = None
        self._matrix = None
        self._bmatrix = None
        self.time_callback = None
        self._device_nav_button_left = None
        self._device_nav_button_right = None
        self.send_sliders = None
        self.send_slider_toggle_button = None
        self.timer_repeat = None
        ControlSurface.disconnect(self)
        self._scenematrix.disconnect()
        self._scenematrix = None
        self._device = None