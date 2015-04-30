#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\MonoNavSection.py
"""
Created on 13.11.2013

@author: Eric
"""
import Live
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot
from _Generic.Devices import *
from MIDI_Map import debug_out
from KnobSection import *
from _Framework.DeviceBankRegistry import DeviceBankRegistry
MODE_ADJUST = 0
MODE_NAV = 1

class MonoNavSection(CompoundComponent):

    def __init__(self, mode_selector, *a, **k):
        super(MonoNavSection, self).__init__(*a, **k)
        is_momentary = True
        self._modesel = mode_selector
        self._device_bank_registry = DeviceBankRegistry()
        self.volume_knob = SliderElement(MIDI_CC_TYPE, 0, 40)
        self.tempo_knob = SliderElement(MIDI_CC_TYPE, 0, 41)
        self.swing_knob = SliderElement(MIDI_CC_TYPE, 0, 42)
        self.mode_button = ButtonElement(True, MIDI_CC_TYPE, 2, 86)
        self.alt_button = ButtonElement(True, MIDI_CC_TYPE, 2, 81)
        self._do_left_knob.subject = self.volume_knob
        self._do_center_knob.subject = self.tempo_knob
        self._do_right_knob.subject = self.swing_knob
        self._do_mode_button.subject = self.mode_button
        self._do_alt_button.subject = self.alt_button
        self._mode = MODE_ADJUST
        self._alt_down = False

    def do_message(self, msg, statusbarmsg = None):
        if statusbarmsg == None:
            self.canonical_parent.show_message(msg)
        else:
            self.canonical_parent.show_message(statusbarmsg)
        self.canonical_parent.timed_message(2, msg)

    @subject_slot('value')
    def _do_left_knob(self, value):
        if not (value == 0 and -1):
            diff = 1
            if self._mode == MODE_ADJUST:
                self.canonical_parent.isShiftDown() and self.chg_cue(diff)
            else:
                self.chg_volume(diff)
        else:
            self._do_channel_selection(diff)

    @subject_slot('value')
    def _do_center_knob(self, value):
        if not (value == 0 and -1):
            diff = 1
            if self._mode == MODE_ADJUST:
                self.canonical_parent.isShiftDown() and self.chg_tempo(diff * 0.1)
            else:
                self.chg_tempo(diff)
        else:
            self._modesel.navigate(diff, False, self.canonical_parent.isShiftDown())

    def chg_tempo(self, diff):
        self.song().tempo = max(20, min(999, self.song().tempo + diff))
        self.canonical_parent.timed_message(2, 'Tempo: ' + str(round(self.song().tempo, 2)))

    def chg_volume(self, diff):
        if self._alt_down:
            self.song().master_track.mixer_device.volume.value = calc_new_parm(self.song().master_track.mixer_device.volume, diff)
        else:
            repeat(self.song().master_track.mixer_device.volume, diff)

    def chg_cue(self, diff):
        if self._alt_down:
            self.song().master_track.mixer_device.cue_volume.value = calc_new_parm(self.song().master_track.mixer_device.cue_volume, diff)
        else:
            repeat(self.song().master_track.mixer_device.cue_volume, diff)

    def _do_channel_selection(self, dir):
        song = self.song()
        if self._alt_down:
            if self.canonical_parent.isShiftDown():
                if dir == 1:
                    self.canonical_parent._device._bank_up_value(1)
                else:
                    self.canonical_parent._device._bank_down_value(1)
            else:
                ndir = dir == -1 and Live.Application.Application.View.NavDirection.left or Live.Application.Application.View.NavDirection.right
                self.application().view.scroll_view(ndir, 'Detail/DeviceChain', True)
        elif self.canonical_parent.isShiftDown():
            scenes = song.scenes
            scene = song.view.selected_scene
            sindex = list(scenes).index(scene)
            sel_scene = sindex + dir
            if sel_scene >= 0 and sel_scene < len(scenes):
                song.view.selected_scene = scenes[sel_scene]
        elif not (dir == -1 and Live.Application.Application.View.NavDirection.left):
            direction = Live.Application.Application.View.NavDirection.right
            self.application().view.scroll_view(direction, 'Session', True)
            self.canonical_parent.arm_selected_track and arm_exclusive(song)

    @subject_slot('value')
    def _do_right_knob(self, value):
        diff = value == 0 and -1 or 1
        if self._mode == MODE_ADJUST:
            song = self.song()
            if self.canonical_parent.isShiftDown():
                quant = song.clip_trigger_quantization
                song.clip_trigger_quantization = max(0, min(13, quant + diff))
                self.do_message('Clip Quantize ' + CLIQ_DESCR[song.clip_trigger_quantization])
            else:
                rec_quant = song.midi_recording_quantization
                index = QUANT_CONST.index(rec_quant) + diff
                if index >= 0 and index < len(QUANT_CONST):
                    song.midi_recording_quantization = QUANT_CONST[index]
                    self.do_message(QUANT_DESCR[index])
        else:
            self._modesel.navigate(diff, True, self.canonical_parent.isShiftDown())

    @subject_slot('value')
    def _do_mode_button(self, value):
        if value != 0:
            if self.canonical_parent.isShiftDown():
                self.canonical_parent.toggle_nav_mode()
            elif self._alt_down:
                self.canonical_parent._do_focus_navigate(1)
            elif self._mode == MODE_ADJUST:
                self._mode = MODE_NAV
                self.do_message('Master Knobs control navigation')
                self.mode_button.send_value(1, True)
            elif self._mode == MODE_NAV:
                self._mode = MODE_ADJUST
                self.do_message('Master Knobs control Volume | Tempo | Quantization')
                self.mode_button.send_value(0, True)

    @subject_slot('value')
    def _do_alt_button(self, value):
        self._alt_down = value > 0

    def refresh(self):
        pass

    def update(self):
        pass

    def disconnect(self):
        super(MonoNavSection, self).disconnect()