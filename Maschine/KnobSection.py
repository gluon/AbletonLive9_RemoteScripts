#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\KnobSection.py
"""
Created on 03.11.2013

@author: Eric
"""
import Live
from _Framework.CompoundComponent import CompoundComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from MIDI_Map import *
from Maschine import arm_exclusive
from _Framework.SubjectSlot import subject_slot
PARM_RANGE = 127
KSM_VOLUME = 1
KSM_SWING = 2
KSM_TEMPO = 3
KSM_XFADE = 4
KSM_EDIT = 5
KSM_SCROLL = 6
KSM_SELECT = 7
KSM_TRANSPORT = 8
KSM_TOGGLE = (KSM_SCROLL, KSM_SELECT, KSM_TRANSPORT)
KSM_HUES = (40, 16, 106)
TRANSPORT_STEPS = (0.25, 0.5, 4.0, 1.0)
QUANT_DESCR = (' No Rec Quantize', ' 1/4 Rec Quantize', ' 1/8 Rec Quantize', ' 1/8 Rec Triplet Quantize', '1/8 & 1/8 Triplet Quantize', ' 1/16 Rec Quantize', ' 1/16 Triplet Rec Quantize', ' 1/16 & 1/16 Triplet Rec Quantize', '1/32 Rec Quantize')
QUANTIZATION_NAMES = ('1/4', '1/8', '1/8t', '1/8+t', '1/16', '1/16t', '1/16+t', '1/32')
CLIQ_DESCR = ('None', '8 Bars', '4 Bars', '2 Bars', '1 Bar', '1/2', '1/2T', '1/4', '1/4T', '1/8', '1/8T', '1/16', '1/16T', '1/32')

def record_quantization_to_float(quantize):
    return float(list(QUANT_CONST).index(quantize) - 1) / float(len(QUANT_CONST) - 2)


def float_to_record_quantization(quantize):
    return QUANT_CONST[int(quantize * (len(QUANT_CONST) - 1)) + 1]


def calc_new_parm(parm, delta):
    parm_range = parm.max - parm.min
    int_val = int((parm.value - parm.min) / parm_range * PARM_RANGE + 0.1)
    inc_val = min(PARM_RANGE, max(0, int_val + delta))
    return float(inc_val) / float(PARM_RANGE) * parm_range + parm.min


def repeat(parm, delta):
    count = 0
    while count < SHIFT_INC:
        parm.value = calc_new_parm(parm, delta)
        count += 1


class KnobSection(CompoundComponent):
    _wheel_overide = None
    _mode = KSM_SCROLL
    _push_down = False
    scrub_mode = True
    alt_mode = False

    def __init__(self, modeselector, editsection, *a, **k):
        super(KnobSection, self).__init__(*a, **k)
        self._modesel = modeselector
        self._editsection = editsection
        self._modesel.connect_main_knob(self)
        is_momentary = True
        self.main_knob = SliderElement(MIDI_CC_TYPE, 1, 85)
        self.push_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 87)
        self.volume_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 110)
        self.swing_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 111)
        self.tempo_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 112)
        self.xfade_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 116)
        self._mode_button = self.canonical_parent.create_gated_button(80, KSM_HUES[0])
        self._color_edit_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 113)
        self._set_inicliplen_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 122)
        self._set_quantize_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 126)
        self.do_main.subject = self.main_knob
        self.do_main_push.subject = self.push_button
        self._do_volume.subject = self.volume_button
        self._do_swing.subject = self.swing_button
        self._do_tempo.subject = self.tempo_button
        self._do_xfade.subject = self.xfade_button
        self._do_toggle_mode.subject = self._mode_button
        self._do_color_button.subject = self._color_edit_button
        self._do_mikr_cliplen.subject = self._set_inicliplen_button
        self._do_mikr_quantize.subject = self._set_quantize_button
        self._do_dedicated_rec_quantize.subject = SliderElement(MIDI_CC_TYPE, 2, 112)
        self._do_dedicated_clip_quantize.subject = SliderElement(MIDI_CC_TYPE, 2, 113)
        self._radio_buttons = (self.volume_button,
         self.swing_button,
         self.tempo_button,
         self.xfade_button,
         self._color_edit_button)
        self._do_button_left.subject = ButtonElement(is_momentary, MIDI_CC_TYPE, 2, 120)
        self._do_button_right.subject = ButtonElement(is_momentary, MIDI_CC_TYPE, 2, 121)
        self.volume_button.send_value(0, True)
        self._mode_button.set_color(KSM_HUES[0])
        self.knob_action = self._scroll_action
        self._prev_mode = None
        self._prev_action = None

    def do_message(self, msg, statusbarmsg = None):
        if statusbarmsg == None:
            self.canonical_parent.show_message(msg)
        else:
            self.canonical_parent.show_message(statusbarmsg)
        self.canonical_parent.timed_message(2, msg)

    def use_scrub_mode(self):
        return self.scrub_mode

    def set_scrub_mode(self, value):
        self.scrub_mode = value
        self.scrub_mode_button.send_value(value and 127 or 0)

    def set_override(self, overide_callback):
        if self._wheel_overide != overide_callback:
            self._wheel_overide = overide_callback
            self.volume_button.send_value(0, True)
            self.swing_button.send_value(0, True)
            self.tempo_button.send_value(0, True)
            self._mode_button.switch_off()
            self._mode = None

    def reset_overide(self):
        if self._wheel_overide:
            self._wheel_overide = None

    def _scroll_action(self, value):
        inc = value == 1 and 1 or -1
        self._modesel.navigate(inc, self._push_down, self._editsection.isShiftdown())

    def _do_channel_slider(self, value):
        song = self.song()
        if self._editsection.isShiftdown():
            dir = value == 127 and Live.Application.Application.View.NavDirection.left or Live.Application.Application.View.NavDirection.right
            self.application().view.scroll_view(dir, 'Detail/DeviceChain', True)
        elif self._push_down:
            if not (value == 127 and -1):
                dir = 1
                scenes = song.scenes
                scene = song.view.selected_scene
                sindex = list(scenes).index(scene)
                sel_scene = sindex + dir
                song.view.selected_scene = sel_scene >= 0 and sel_scene < len(scenes) and scenes[sel_scene]
        elif not (value == 127 and Live.Application.Application.View.NavDirection.left):
            direction = Live.Application.Application.View.NavDirection.right
            self.application().view.scroll_view(direction, 'Session', True)
            self.canonical_parent.arm_selected_track and arm_exclusive(song)

    def _do_transport(self, value):
        if not (value == 127 and -1):
            diff = 1
            jump = 4.0
            if self._push_down:
                if self._editsection.isShiftdown():
                    jump = 0.25
                else:
                    jump = 1.0
            elif self._editsection.isShiftdown():
                jump = 0.5
            self.scrub_mode and self.song().scrub_by(jump * diff)
        else:
            self.song().jump_by(jump * diff)

    @subject_slot('value')
    def do_main(self, value):
        if self._wheel_overide:
            self._wheel_overide(value == 1 and 1 or -1, self._editsection.isShiftdown(), self._push_down)
        elif self.knob_action:
            self.knob_action(value)

    def _disable_radio_button(self):
        for button in self._radio_buttons:
            button.send_value(0, True)

    def enter_toggle_mode(self, mode = None):
        self.reset_overide()
        self.switch_pad_wheel_edit(False)
        self.alt_mode = False
        if self._mode < KSM_SCROLL or mode != None:
            if mode == None:
                self.switch_pad_wheel_edit(False)
                self._mode = KSM_SCROLL
            else:
                self._mode = mode
            self._disable_radio_button()
        else:
            modeval = self._mode + 1
            if modeval > KSM_TRANSPORT:
                modeval = KSM_SCROLL
            self._mode = modeval
        if self._mode == KSM_SCROLL:
            self.knob_action = self._scroll_action
            self.do_message('Main Knob -> Navigate')
        elif self._mode == KSM_SELECT:
            self.knob_action = self._do_channel_slider
            self.do_message('Main Knob -> Select')
        elif self._mode == KSM_TRANSPORT:
            self.knob_action = self._do_transport
            self.do_message('Main Knob -> Transport')
        self._mode_button.set_color(KSM_HUES[self._mode - KSM_SCROLL])

    @subject_slot('value')
    def _do_toggle_mode(self, value):
        if value > 0:
            if self._editsection.isShiftdown():
                self.canonical_parent.toggle_nav_mode()
            else:
                self.enter_toggle_mode()

    def _scroll_xfade(self, value):
        if not (value == 127 and -1):
            diff = 1
            self._wheel_overide and self._wheel_overide(diff, self._editsection.isShiftdown(), self._push_down)
        else:
            self.chg_xfade(diff)

    def _scroll_volume(self, value):
        if not (value == 127 and -1):
            diff = 1
            self._wheel_overide and self._wheel_overide(diff, self._editsection.isShiftdown(), self._push_down)
        elif self._editsection.isShiftdown():
            self.chg_cue(diff)
        else:
            self.chg_volume(diff)

    def _scroll_tempo(self, value):
        if not (value == 127 and -1):
            diff = 1
            self._wheel_overide and self._wheel_overide(diff, self._editsection.isShiftdown(), self._push_down)
        elif self._push_down:
            self.chg_tempo(diff * 0.1)
        elif self._editsection.isShiftdown():
            self.chg_tempo(diff * 0.01)
        else:
            self.chg_tempo(diff)

    def _scroll_req_quantize(self, value):
        if not (value == 127 and -1):
            diff = 1
            self._wheel_overide and self._wheel_overide(diff, self._editsection.isShiftdown(), self._push_down)
        else:
            song = self.song()
            if self._editsection.isShiftdown():
                quant = song.clip_trigger_quantization
                song.clip_trigger_quantization = max(0, min(13, quant + diff))
                self.do_message('Clip Quantize ' + CLIQ_DESCR[song.clip_trigger_quantization])
            else:
                rec_quant = song.midi_recording_quantization
                index = QUANT_CONST.index(rec_quant) + diff
                if index >= 0 and index < len(QUANT_CONST):
                    song.midi_recording_quantization = QUANT_CONST[index]
                    self.do_message(QUANT_DESCR[index])

    @subject_slot('value')
    def do_main_push(self, value):
        if value != 0:
            self.alt_mode = not self.alt_mode
        self._push_down = value != 0
        self._modesel.handle_push(value != 0)

    def switch_pad_wheel_edit(self, activate):
        if activate:
            self._color_edit_button.send_value(1, True)
            self._editsection.set_color_edit(True)
        else:
            self._color_edit_button.send_value(0, True)
            self._editsection.set_color_edit(False)

    def invoke_color_mode(self, active):
        if active and self._mode != KSM_EDIT:
            self._prev_mode = self._mode
            self._to_mode(KSM_EDIT)
        elif not active and self._prev_mode != None:
            self.switch_pad_wheel_edit(False)
            self._to_mode(self._prev_mode)
            self._prev_mode = None

    @subject_slot('value')
    def _do_color_button(self, value, force = False):
        if value > 0:
            if self._mode != KSM_EDIT:
                self._prev_mode = self._mode
                self.reset_overide()
                self._to_mode(KSM_EDIT)
            elif self._prev_mode != None:
                self.switch_pad_wheel_edit(False)
                self._to_mode(self._prev_mode)
                self._prev_mode = None

    def _to_mode(self, mode):
        button = None
        if mode == KSM_VOLUME:
            button = self.volume_button
            self.knob_action = self._scroll_volume
            self.switch_pad_wheel_edit(False)
        elif mode == KSM_SWING:
            button = self.swing_button
            self.knob_action = self._scroll_req_quantize
            self.switch_pad_wheel_edit(False)
        elif mode == KSM_TEMPO:
            button = self.tempo_button
            self.knob_action = self._scroll_tempo
            self.switch_pad_wheel_edit(False)
        elif mode == KSM_XFADE:
            button = self.xfade_button
            self.knob_action = self._scroll_xfade
            self.switch_pad_wheel_edit(False)
        elif mode == KSM_EDIT:
            self._editsection.set_color_edit(True)
        else:
            self.enter_toggle_mode(mode)
        self._mode = mode
        for rbutton in self._radio_buttons:
            if rbutton != button:
                rbutton.send_value(0)

        if button:
            self._mode_button.switch_off()
            button.send_value(127, True)

    def _edit_color(self, value):
        if not (value == 127 and -1):
            diff = 1
            self._wheel_overide and self._wheel_overide(diff, self._editsection.isShiftdown(), self._push_down)
        else:
            self._editsection.edit_colors(diff)

    @subject_slot('value')
    def _do_button_left(self, value):
        if value != 0:
            self._modesel.navigate(-1, self._editsection.isShiftdown(), False)

    @subject_slot('value')
    def _do_button_right(self, value):
        if value != 0:
            self._modesel.navigate(1, self._editsection.isShiftdown(), False)

    @subject_slot('value')
    def _do_mikr_cliplen(self, value):
        if value == 0:
            self.knob_action = self._prev_action
        else:
            self._prev_action = self.knob_action
            self.knob_action = self._modify_init_cliplen

    @subject_slot('value')
    def _do_mikr_quantize(self, value):
        if value == 0:
            self.knob_action = self._prev_action
        else:
            self._prev_action = self.knob_action
            self.knob_action = self._modify_quant_grid

    def _modify_init_cliplen(self, value):
        if self._push_down:
            self._editsection.mod_new_initlen(value == 1 and 1 or -1)
        else:
            self._editsection.mod_new_initlen(value == 1 and 4 or -4)

    def _modify_quant_grid(self, value):
        self._editsection.mod_quant_size(value == 1 and 1 or -1)

    @subject_slot('value')
    def _do_xfade(self, value):
        if value > 0 and self._mode != KSM_XFADE:
            self.reset_overide()
            self._to_mode(KSM_XFADE)

    @subject_slot('value')
    def _do_volume(self, value):
        if value > 0 and self._mode != KSM_VOLUME:
            self.reset_overide()
            self._to_mode(KSM_VOLUME)

    @subject_slot('value')
    def _do_swing(self, value):
        if value > 0 and self._mode != KSM_SWING:
            self.reset_overide()
            self._to_mode(KSM_SWING)

    @subject_slot('value')
    def _do_tempo(self, value):
        if value > 0 and self._mode != KSM_TEMPO:
            self.reset_overide()
            self._to_mode(KSM_TEMPO)

    @subject_slot('value')
    def _do_dedicated_clip_quantize(self, value):
        diff = value == 0 and -1 or 1
        song = self.song()
        quant = song.clip_trigger_quantization
        song.clip_trigger_quantization = max(0, min(13, quant + diff))
        self.do_message('Clip Quantize ' + CLIQ_DESCR[song.clip_trigger_quantization])

    @subject_slot('value')
    def _do_dedicated_rec_quantize(self, value):
        if not (value == 0 and -1):
            diff = 1
            song = self.song()
            rec_quant = song.midi_recording_quantization
            index = QUANT_CONST.index(rec_quant) + diff
            song.midi_recording_quantization = index >= 0 and index < len(QUANT_CONST) and QUANT_CONST[index]
            self.do_message('Rec Quantize: ' + QUANT_STRING[index])

    def chg_tempo(self, diff):
        self.song().tempo = max(20, min(999, self.song().tempo + diff))
        self.canonical_parent.timed_message(2, 'Tempo: ' + str(round(self.song().tempo, 2)))

    def chg_volume(self, diff):
        if self._push_down:
            self.song().master_track.mixer_device.volume.value = calc_new_parm(self.song().master_track.mixer_device.volume, diff)
        else:
            repeat(self.song().master_track.mixer_device.volume, diff)

    def chg_xfade(self, diff):
        if self._push_down:
            self.song().master_track.mixer_device.crossfader.value = calc_new_parm(self.song().master_track.mixer_device.crossfader, diff)
        else:
            repeat(self.song().master_track.mixer_device.crossfader, diff)

    def chg_cue(self, diff):
        if self._push_down:
            self.song().master_track.mixer_device.cue_volume.value = calc_new_parm(self.song().master_track.mixer_device.cue_volume, diff)
        else:
            repeat(self.song().master_track.mixer_device.cue_volume, diff)

    def update(self):
        pass

    def refresh(self):
        pass