#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\Mk2KnobControl.py
import Live
import time
from MIDI_Map import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import *
from VarButtonElement import ColorButton
from StateButton import StateButton
KN2_MODE_VOLUME = 1
KN2_MODE_CUE = 2
KN2_MODE_QUANT = 3
KN2_MODE_TEMPO_COARSE = 4
KN2_MODE_TEMPO_FINE = 5
KN2_MODE_CLIP_QUANT = 6
KN2_MODE_CLIPN_HOR = 7
KN2_MODE_CLIPN_VER = 8
KN2_MODE_XFADE = 9
KN2_MODE_GENERAL = 10
KN2_P_SCALES = 11
LEFT_DOWN = 1
RIGHT_DOWN = 2
PARM_RANGE = 127
QUANT_DESCR = (' No Rec Quantize', ' 1/4 Rec Quantize', ' 1/8 Rec Quantize', ' 1/8 Rec Triplet Quantize', '1/8 & 1/8 Triplet Quantize', ' 1/16 Rec Quantize', ' 1/16 Triplet Rec Quantize', ' 1/16 & 1/16 Triplet Rec Quantize', '1/32 Rec Quantize')
QUANT_CONST = (Live.Song.RecordingQuantization.rec_q_no_q,
 Live.Song.RecordingQuantization.rec_q_quarter,
 Live.Song.RecordingQuantization.rec_q_eight,
 Live.Song.RecordingQuantization.rec_q_eight_triplet,
 Live.Song.RecordingQuantization.rec_q_eight_eight_triplet,
 Live.Song.RecordingQuantization.rec_q_sixtenth,
 Live.Song.RecordingQuantization.rec_q_sixtenth_triplet,
 Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
 8)
CLIQ_DESCR = ('None', '8 Bars', '4 Bars', '2 Bars', '1 Bar', '1/2', '1/2T', '1/4', '1/4T', '1/8', '1/8T', '1/16', '1/16T', '1/32')
LR_CONTROL_CLIP = 0
LR_CONTROL_SEL = 1
LR_CONTROL_DEV = 2
LR_CONTROL_LOOP = 3
LR_MODE_HUES = (6, 14, 39, 90)
L_MODE_FUNCTION = ('Clip Horizontal', 'Track Selection', 'Track Selection', 'Loop Start')
R_MODE_FUNCTION = ('Clip Vertical', 'Scene Selection', 'Device Selection', 'Loop Length')
LOOP_KNOB_DIVISION = (4.0, 1.0, 0.5)
PAD_KNOB_OCTAVE = 1
PAD_KNOB_SCALE = 2
PAD_KNOB_BASEN = 4

class Mk2KnobControl:
    __module__ = __name__
    __doc__ = 'Mk2 Module for Controlling Parameters with Master Knob'

    def __init__(self, parent):
        self._parent = parent
        self.master_track = parent.song().master_track
        self.volume_button = None
        self._set_volume_button(StateButton(True, MIDI_CC_TYPE, 3, 110))
        self.the_slider = SliderElement(MIDI_CC_TYPE, 1, 86)
        self.the_slider.add_value_listener(self._do_main_slider, True)
        self.xfade_button = None
        self._set_xfade_button(StateButton(True, MIDI_CC_TYPE, 3, 116))
        self.swing_button = None
        self._set_swing_button(StateButton(True, MIDI_CC_TYPE, 3, 111))
        self.mode = KN2_MODE_VOLUME
        self.previous_mode = -1
        self.tempo_button = None
        self._set_tempo_button(StateButton(True, MIDI_CC_TYPE, 3, 112))
        self.push_button = None
        self._set_push_button(StateButton(True, MIDI_CC_TYPE, 1, 87))
        self.clipn_v_button = None
        self.clipn_h_button = None
        self._set_clipn_h_button(StateButton(True, MIDI_CC_TYPE, 3, 114))
        self._set_clipn_v_button(StateButton(True, MIDI_CC_TYPE, 3, 115))
        self.toggle_buttons = [self.volume_button,
         self.xfade_button,
         self.swing_button,
         self.tempo_button,
         self.clipn_h_button,
         self.clipn_v_button]
        self.shift_button = None
        self._set_shift_button(StateButton(True, MIDI_CC_TYPE, 3, 113))
        self.shift_on = False
        self.scroll_mod_left_button = None
        self.scroll_mod_right_button = None
        self._set_scroll_mod_left_button(StateButton(True, MIDI_CC_TYPE, 0, 105))
        self._set_scroll_mod_right_button(StateButton(True, MIDI_CC_TYPE, 0, 106))
        self._prev_mode = KN2_MODE_VOLUME
        self.lrmode = LR_CONTROL_CLIP
        self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
        self.loop_div_index = 0
        self.loop_incdex = 4.0
        self.arrow_mode_button = ColorButton(True, MIDI_CC_TYPE, 30)
        self.arrow_mode_button.add_value_listener(self.toggle_arrow_mode)
        self.arrow_mode_button.send_color(LR_MODE_HUES[self.lrmode])
        self.arrow_mode_button.send_value(127, True)
        self.navflags = 0
        self.octave_mod_button = StateButton(True, MIDI_CC_TYPE, 1, 70)
        self.octave_mod_button.add_value_listener(self._action_octave)
        self.scale_mod_button = StateButton(True, MIDI_CC_TYPE, 1, 71)
        self.scale_mod_button.add_value_listener(self._action_scale)
        self.basenote_mod_button = StateButton(True, MIDI_CC_TYPE, 1, 72)
        self.basenote_mod_button.add_value_listener(self._action_base_note)
        self.keycolor_mod_button = StateButton(True, MIDI_CC_TYPE, 1, 73)
        self.keycolor_mod_button.add_value_listener(self._action_key_color)
        self.pad_to_mainknob_mode = 0
        self._measure_left_click = 0
        self._measure_right_click = 0
        self.mode_assign_map = {KN2_MODE_VOLUME: (self.chg_volume,
                           0,
                           'Master Knob controls MASTER Volume',
                           KN2_MODE_CUE),
         KN2_MODE_CUE: (self.chg_cue,
                        0,
                        'Master Knob controls Cue Level',
                        KN2_MODE_VOLUME),
         KN2_MODE_TEMPO_COARSE: (self.chg_tempo,
                                 3,
                                 'Master Knob controls TEMPO Coarse',
                                 KN2_MODE_TEMPO_FINE),
         KN2_MODE_TEMPO_FINE: (self.chg_tempo_fine,
                               3,
                               'Master Knob controls TEMPO Fine',
                               KN2_MODE_TEMPO_COARSE),
         KN2_MODE_XFADE: (self.chg_xfade,
                          1,
                          'Master Knob controls Crossfader',
                          -1),
         KN2_MODE_QUANT: (self.chg_quant,
                          2,
                          'Master Knob controls Recording Quantize',
                          KN2_MODE_CLIP_QUANT),
         KN2_MODE_CLIP_QUANT: (self.chg_clip_q,
                               2,
                               'Master Knob controls Clip Start Quantize',
                               KN2_MODE_QUANT),
         KN2_MODE_CLIPN_HOR: (self.nav_c_hor,
                              4,
                              'Master Knob Clip View horizontally',
                              -1),
         KN2_MODE_CLIPN_VER: (self.nav_c_ver,
                              5,
                              'Master Knob Clip View vertically',
                              -1),
         KN2_MODE_GENERAL: (self.chg_general,
                            -1,
                            None,
                            -1),
         KN2_P_SCALES: (self.modify_pad_scaling,
                        -1,
                        None,
                        -1)}

    def start_up(self):
        self._set_mode(KN2_MODE_VOLUME)
        self.arrow_mode_button.send_value(127, True)

    def toggle_arrow_mode(self, value):
        if value > 0:
            self.lrmode = (self.lrmode + 1) % 4
            self.arrow_mode_button.send_hue(LR_MODE_HUES[self.lrmode])
            self._parent.show_message('Left/Right Buttons Control:    ' + L_MODE_FUNCTION[self.lrmode] + ' / ' + R_MODE_FUNCTION[self.lrmode])

    def switch_to_matrix_mode(self):
        if self.mode != KN2_MODE_GENERAL:
            self.previous_mode = self.mode
            self._set_mode(KN2_MODE_GENERAL)

    def exit_matrix_mode(self):
        if self.mode == KN2_MODE_GENERAL:
            self._set_mode(self.previous_mode)
            self.previous_mode = -1

    def update_shift(self):
        if self.shift_on:
            self.shift_button.send_value(127, True)
        else:
            self.shift_button.send_value(0, True)

    def _set_mode(self, mode):
        if not mode in range(11):
            raise AssertionError
            self.update_shift()
            if mode == self.mode:
                return
            self._prev_mode = mode
            self.mode = mode
            self.switch_radio_buttons(self.mode_assign_map[self.mode][1])
            message = self.mode_assign_map[self.mode][2]
            message != None and self._parent.show_message(message)

    def switch_radio_buttons(self, which):
        for index in range(len(self.toggle_buttons)):
            if index == which:
                self.toggle_buttons[index].send_value(127, True)
            else:
                self.toggle_buttons[index].send_value(0, True)

    def update(self):
        self.switch_radio_buttons(self.mode_assign_map[self.mode][1])
        self.arrow_mode_button.send_color(LR_MODE_HUES[self.lrmode])
        self.arrow_mode_button.send_value(127, True)

    def _do_main_slider(self, value, encoder):
        if not value in range(128):
            raise AssertionError
            if not isinstance(encoder, EncoderElement):
                raise AssertionError
                if value == 1:
                    delta = 1
                else:
                    delta = -1
                if self.pad_to_mainknob_mode != 0:
                    self.mode_assign_map[KN2_P_SCALES][0](delta)
                elif self.navflags == 0:
                    self.mode_assign_map[self.mode][0](delta)
                if self.lrmode == LR_CONTROL_CLIP:
                    self.navflags & LEFT_DOWN != 0 and self.nav_c_hor(delta)
                self.navflags & RIGHT_DOWN != 0 and self.nav_c_ver(delta)
        elif self.lrmode == LR_CONTROL_SEL:
            if self.navflags & LEFT_DOWN != 0:
                self.nav_track(delta)
            if self.navflags & RIGHT_DOWN != 0:
                self._parent.scroll_scene(delta)
        elif self.lrmode == LR_CONTROL_DEV:
            if self.navflags & LEFT_DOWN != 0:
                self.nav_track(delta)
            if self.navflags & RIGHT_DOWN != 0:
                self._parent.scroll_device(delta)
        elif self.lrmode == LR_CONTROL_LOOP:
            if self.navflags & LEFT_DOWN != 0:
                self.adjust_loop_start(delta)
            if self.navflags & RIGHT_DOWN != 0:
                self.adjust_loop_length(delta)

    def modify_pad_scaling(self, delta):
        if self.pad_to_mainknob_mode & PAD_KNOB_OCTAVE != 0:
            self._parent.inc_octave(delta)
        if self.pad_to_mainknob_mode & PAD_KNOB_SCALE != 0:
            self._parent.inc_scale(delta)
        if self.pad_to_mainknob_mode & PAD_KNOB_BASEN != 0:
            self._parent.inc_base_note(delta)
        self._parent.update_transpose()

    def adjust_loop_start(self, delta):
        loopval = self._parent.song().loop_start
        loopval += self.loop_incdex * delta
        if loopval < 0:
            loopval = 0
        elif loopval > 999:
            loopval = 999
        self._parent.song().loop_start = loopval

    def adjust_loop_length(self, delta):
        loopval = self._parent.song().loop_length
        loopval += self.loop_incdex * delta
        if loopval < self.loop_incdex:
            loopval = self.loop_incdex
        elif loopval > 999:
            loopval = 999
        self._parent.song().loop_length = loopval

    def chg_general(self, delta):
        self._parent._scenematrix.control_handler.mod_value(delta, self.shift_on)

    def nav_track(self, direction):
        if direction == 1:
            self._parent._a_trk_right(1)
        else:
            self._parent._a_trk_left(1)

    def nav_c_hor(self, direction):
        self._parent.move_view_horizontal(direction)

    def nav_c_ver(self, direction):
        if direction == 1:
            self._parent._session.bank_up()
        else:
            self._parent._session.bank_down()

    def chg_volume(self, diff):
        if self.shift_on:
            self.repeat(self.master_track.mixer_device.volume, diff)
        else:
            self.master_track.mixer_device.volume.value = self.calc_new_parm(self.master_track.mixer_device.volume, diff)

    def chg_xfade(self, diff):
        if self.shift_on:
            self.repeat(self.master_track.mixer_device.crossfader, diff)
        else:
            self.master_track.mixer_device.crossfader.value = self.calc_new_parm(self.master_track.mixer_device.crossfader, diff)

    def chg_cue(self, diff):
        if self.shift_on:
            self.repeat(self.master_track.mixer_device.cue_volume, diff)
        else:
            self.master_track.mixer_device.cue_volume.value = self.calc_new_parm(self.master_track.mixer_device.cue_volume, diff)

    def repeat(self, parm, delta):
        count = 0
        while count < SHIFT_INC:
            parm.value = self.calc_new_parm(parm, delta)
            count += 1

    def calc_new_parm(self, parm, delta):
        parm_range = parm.max - parm.min
        int_val = int((parm.value - parm.min) / parm_range * PARM_RANGE + 0.1)
        inc_val = min(PARM_RANGE, max(0, int_val + delta))
        return float(inc_val) / float(PARM_RANGE) * parm_range + parm.min

    def chg_quant(self, diff):
        rec_quant = self._parent.song().midi_recording_quantization
        index = self.get_quant_index(rec_quant)
        new_index = index + diff
        if new_index >= 0 and new_index < len(QUANT_CONST):
            self._parent.song().midi_recording_quantization = QUANT_CONST[new_index]
            self._parent.show_message(QUANT_DESCR[new_index])

    def chg_clip_q(self, diff):
        quant = self._parent.song().clip_trigger_quantization
        self._parent.song().clip_trigger_quantization = max(0, min(13, quant + diff))
        self._parent.show_message('Clip Quantize ' + CLIQ_DESCR[self._parent.song().clip_trigger_quantization])

    def chg_tempo_fine(self, diff):
        if diff < 0:
            amount = -0.01
        else:
            amount = 0.01
        self.chg_tempo(amount)

    def chg_tempo(self, diff):
        self._parent.song().tempo = max(20, min(999, self._parent.song().tempo + diff))

    def get_quant_index(self, const):
        for index in range(len(QUANT_CONST)):
            if const == QUANT_CONST[index]:
                return index

        return -1

    def _action_octave(self, value):
        if value != 0:
            self.pad_to_mainknob_mode |= PAD_KNOB_OCTAVE
        else:
            self.pad_to_mainknob_mode &= ~PAD_KNOB_OCTAVE

    def _action_scale(self, value):
        if value != 0:
            self.pad_to_mainknob_mode |= PAD_KNOB_SCALE
        else:
            self.pad_to_mainknob_mode &= ~PAD_KNOB_SCALE

    def _action_base_note(self, value):
        if value != 0:
            self.pad_to_mainknob_mode |= PAD_KNOB_BASEN
        else:
            self.pad_to_mainknob_mode &= ~PAD_KNOB_BASEN

    def _action_key_color(self, value):
        if value != 0:
            self._parent.step_key_color_mode()

    def _set_volume_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.volume_button != None:
                self.volume_button.remove_value_listener(self._action_volume)
            self.volume_button = button
            self.volume_button != None and self.volume_button.add_value_listener(self._action_volume)

    def _action_volume(self, value):
        if not self.volume_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.mode != KN2_MODE_VOLUME and self._set_mode(KN2_MODE_VOLUME)

    def _set_xfade_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.xfade_button != None:
                self.xfade_button.remove_value_listener(self._action_xfade)
            self.xfade_button = button
            self.xfade_button != None and self.xfade_button.add_value_listener(self._action_xfade)

    def _action_xfade(self, value):
        if not self.xfade_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.mode != KN2_MODE_XFADE and self._set_mode(KN2_MODE_XFADE)

    def _set_swing_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.swing_button != None:
                self.swing_button.remove_value_listener(self._action_swing)
            self.swing_button = button
            self.swing_button != None and self.swing_button.add_value_listener(self._action_swing)

    def _action_swing(self, value):
        if not self.swing_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.mode != KN2_MODE_QUANT and self._set_mode(KN2_MODE_QUANT)

    def _set_tempo_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.tempo_button != None:
                self.tempo_button.remove_value_listener(self._action_tempo)
            self.tempo_button = button
            self.tempo_button != None and self.tempo_button.add_value_listener(self._action_tempo)

    def _action_tempo(self, value):
        if not self.tempo_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.mode != KN2_MODE_TEMPO_COARSE and self._set_mode(KN2_MODE_TEMPO_COARSE)

    def _set_clipn_h_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.clipn_h_button != None:
                self.clipn_h_button.remove_value_listener(self._action_clipnh)
            self.clipn_h_button = button
            self.clipn_h_button != None and self.clipn_h_button.add_value_listener(self._action_clipnh)

    def _action_clipnh(self, value):
        if not self.clipn_h_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.mode != KN2_MODE_CLIPN_HOR and self._set_mode(KN2_MODE_CLIPN_HOR)

    def _set_clipn_v_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.clipn_v_button != None:
                self.clipn_v_button.remove_value_listener(self._action_clipnv)
            self.clipn_v_button = button
            self.clipn_v_button != None and self.clipn_v_button.add_value_listener(self._action_clipnv)

    def _action_clipnv(self, value):
        if not self.clipn_v_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.mode != KN2_MODE_CLIPN_VER and self._set_mode(KN2_MODE_CLIPN_VER)

    def _set_shift_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.shift_button != None:
                self.shift_button.remove_value_listener(self._action_shift)
            self.shift_button = button
            self.shift_button != None and self.shift_button.add_value_listener(self._action_shift)

    def _action_shift(self, value):
        if not self.shift_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.shift_on = value != 0 and not self.shift_on
            self.update_shift()

    def _set_scroll_mod_left_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.scroll_mod_left_button != None:
                self.scroll_mod_left_button.remove_value_listener(self._action_scroll_left)
            self.scroll_mod_left_button = button
            self.scroll_mod_left_button != None and self.scroll_mod_left_button.add_value_listener(self._action_scroll_left)

    def _set_scroll_mod_right_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.scroll_mod_right_button != None:
                self.scroll_mod_right_button.remove_value_listener(self._action_scroll_right)
            self.scroll_mod_right_button = button
            self.scroll_mod_right_button != None and self.scroll_mod_right_button.add_value_listener(self._action_scroll_right)

    def _action_scroll_left(self, value):
        if not self.scroll_mod_left_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.scroll_mod_left_button.send_value(127, True)
            self.navflags |= LEFT_DOWN
            self._measure_left_click = int(round(time.time() * 1000))
        else:
            self.scroll_mod_left_button.send_value(0, True)
            self.navflags &= ~LEFT_DOWN
            clicktime = int(round(time.time() * 1000)) - self._measure_left_click
            if clicktime < CLICK_TIME:
                if self._parent._modifier_down:
                    self._parent.modify_track_offset(-1)
                elif self._parent._mode == PAD_MODE:
                    self._do_lr_as_scale_mode(-1)
                elif self._parent._mode == SCENE_MODE:
                    self._parent.modify_scene_offset(-1)
                elif self._parent._mode == CLIP_MODE:
                    self._parent.move_view_horizontal(-1)
                elif self._parent._mode == CONTROL_MODE:
                    self._parent.move_view_horizontal(-1)

    def _action_scroll_right(self, value):
        if not self.scroll_mod_right_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value != 0 and self.scroll_mod_right_button.send_value(127, True)
            self.navflags |= RIGHT_DOWN
            self._measure_right_click = int(round(time.time() * 1000))
        else:
            self.scroll_mod_right_button.send_value(0, True)
            self.navflags &= ~RIGHT_DOWN
            clicktime = int(round(time.time() * 1000)) - self._measure_right_click
            if clicktime < CLICK_TIME:
                if self._parent._modifier_down:
                    self._parent.modify_track_offset(1)
                elif self._parent._mode == PAD_MODE:
                    self._do_lr_as_scale_mode(1)
                elif self._parent._mode == SCENE_MODE:
                    self._parent.modify_scene_offset(1)
                elif self._parent._mode == CLIP_MODE:
                    self._parent.move_view_horizontal(1)
                elif self._parent._mode == CONTROL_MODE:
                    self._parent.move_view_horizontal(1)

    def _do_lr_as_scale_mode(self, delta):
        if self.pad_to_mainknob_mode == PAD_KNOB_SCALE:
            self._parent.inc_scale(delta)
        elif self.pad_to_mainknob_mode == PAD_KNOB_BASEN:
            self._parent.inc_base_note(delta)
        else:
            self._parent.inc_octave(delta)
        self._parent.update_transpose()

    def _set_push_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.push_button != None:
                self.push_button.remove_value_listener(self._action_push)
            self.push_button = button
            self.push_button != None and self.push_button.add_value_listener(self._action_push)

    def _action_push(self, value):
        if not self.push_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                next_mode = self.mode_assign_map[self.mode][3]
                next_mode != -1 and self._set_mode(next_mode)
            self.loop_div_index = self.lrmode == LR_CONTROL_LOOP and self.navflags != 0 and (self.loop_div_index + 1) % len(LOOP_KNOB_DIVISION)
            self._parent.show_message('Loop Selection Granularity : ' + str(LOOP_KNOB_DIVISION[self.loop_div_index]) + ' beats ')
            self.loop_incdex = LOOP_KNOB_DIVISION[self.loop_div_index]

    def remove_listener(self, control, callback):
        if control != None and control.value_has_listener(callback):
            control.remove_value_listener(callback)
        control.disconnect()

    def disconnect(self):
        self.remove_listener(self.the_slider, self._do_main_slider)
        self.remove_listener(self.arrow_mode_button, self.toggle_arrow_mode)
        self.remove_listener(self.volume_button, self._action_volume)
        self.remove_listener(self.xfade_button, self._action_xfade)
        self.remove_listener(self.swing_button, self._action_swing)
        self.remove_listener(self.clipn_h_button, self._action_clipnh)
        self.remove_listener(self.clipn_v_button, self._action_clipnv)
        self.remove_listener(self.shift_button, self._action_shift)
        self.remove_listener(self.scroll_mod_left_button, self._action_scroll_left)
        self.remove_listener(self.scroll_mod_right_button, self._action_scroll_right)
        self.remove_listener(self.push_button, self._action_push)
        self.remove_listener(self.octave_mod_button, self._action_octave)
        self.remove_listener(self.scale_mod_button, self._action_scale)
        self.remove_listener(self.basenote_mod_button, self._action_base_note)
        self.remove_listener(self.keycolor_mod_button, self._action_key_color)
        self._parent = None
        self.master_track = None
        self.the_slider = None
        self.mode_assign_map = None