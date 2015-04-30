#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\AudioClipEditComponent.py
"""
Created on 22.10.2013

@author: Eric
"""
import Live
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if, clamp
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import *
from MIDI_Map import *
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement

def gain_to_midi(gain):
    return gain * 127


def midi_to_gain(midi):
    return midi / 127.0


def midi_to_pitchc(midi):
    return int(midi / 127.0 * 96 - 48)


def midi_to_pitchf(midi):
    return int(midi / 127.0 * 100 - 50)


def pitchc_to_midi(pitch):
    return int((pitch + 48.0) / 96.0 * 127)


def pitchf_to_midi(pitch):
    return int((pitch + 50.0) / 100.0 * 127)


def bars_to_measure(beats, denom, num):
    brs = int(beats / denom)
    bts = int(beats) % num
    msr = int((beats - brs * denom - bts) / 0.25)
    return str(brs + 1) + ':' + str(bts + 1) + ':' + str(msr + 1)


def loop_str(clip):
    sgnd = clip.signature_denominator
    sgnum = clip.signature_numerator
    return 'Loop : [' + bars_to_measure(clip.loop_start, sgnd, sgnum) + ' - ' + bars_to_measure(clip.loop_end, sgnd, sgnum) + ']'


INC_STEPS = (0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
INC_DISP = ('1/16 Beat', '1/8 Beat', '1/4 Beat', '1/2 Beat', '1 Beat', '2 Beats', '1 Bar', '2 Bar')

class AudioClipEditComponent(CompoundComponent):
    """
    classdocs
    """

    def __init__(self, *a, **k):
        super(AudioClipEditComponent, self).__init__(*a, **k)
        self._loop_start_slider = SliderElement(MIDI_CC_TYPE, 2, 60)
        self._action_loop_start.subject = self._loop_start_slider
        self._loop_end_slider = SliderElement(MIDI_CC_TYPE, 2, 61)
        self._action_loop_end.subject = self._loop_end_slider
        self._mark_start_slider = SliderElement(MIDI_CC_TYPE, 2, 62)
        self._action_mark_start.subject = self._mark_start_slider
        self._mark_end_slider = SliderElement(MIDI_CC_TYPE, 2, 63)
        self._action_mark_end.subject = self._mark_end_slider
        self._pitch_c_slider = SliderElement(MIDI_CC_TYPE, 2, 64)
        self._pitch_f_slider = SliderElement(MIDI_CC_TYPE, 2, 65)
        self._gain_slider = SliderElement(MIDI_CC_TYPE, 2, 66)
        self._action_pitch_c.subject = self._pitch_c_slider
        self._action_pitch_f.subject = self._pitch_f_slider
        self._action_gain.subject = self._gain_slider
        self._loop_inc_slider = SliderElement(MIDI_CC_TYPE, 2, 67)
        self._action_loop_inc.subject = self._loop_inc_slider
        self._loop_move_button = ButtonElement(False, MIDI_CC_TYPE, 2, 74)
        self._action_mv_loop.subject = self._loop_move_button
        self._loop_set_button = ButtonElement(False, MIDI_CC_TYPE, 2, 70)
        self._action_loop_toggle.subject = self._loop_set_button
        self._warp_set_button = ButtonElement(False, MIDI_CC_TYPE, 2, 71)
        self._action_warp_toggle.subject = self._warp_set_button
        self._zoom_scroll_button = ButtonElement(False, MIDI_CC_TYPE, 2, 73)
        self._action_scroll_mode.subject = self._zoom_scroll_button
        self.selected_clip_slot = None
        self.inc_index = 4
        self.loop_inc = INC_STEPS[self.inc_index]
        self.start_inc = INC_STEPS[self.inc_index]
        self.mv_loop = False
        self._on_pitch_c_changed.subject = None
        self._on_pitch_f_changed.subject = None
        self._on_gain_changed.subject = None
        self._scroll_mode = False
        self.update_selected_clip()

    @subject_slot('value')
    def _action_scroll_mode(self, value):
        if value > 0:
            self._scroll_mode = True
        else:
            self._scroll_mode = False

    @subject_slot('value')
    def _action_warp_toggle(self, value):
        if value > 0:
            if self.selected_clip_slot and self.selected_clip_slot.has_clip:
                clip = self.selected_clip_slot.clip
                if clip.is_audio_clip:
                    clip.warping = not clip.warping
                    self._warp_set_button.send_value(clip.warping and 127 or 0, True)

    @subject_slot('value')
    def _action_loop_toggle(self, value):
        if value > 0:
            if self.selected_clip_slot and self.selected_clip_slot.has_clip:
                clip = self.selected_clip_slot.clip
                clip.looping = not clip.looping
                self._loop_set_button.send_value(clip.looping and 127 or 0, True)

    @subject_slot('value')
    def _action_loop_inc(self, value):
        if not (value == 1 and 1):
            inc = -1
            val = self.inc_index + inc
            self.inc_index = val >= 0 and val < len(INC_STEPS) and val
            self.loop_inc = INC_STEPS[val]
            self.start_inc = INC_STEPS[val]
            self.canonical_parent.timed_message(2, 'Loop Adjust: ' + INC_DISP[val])
            self.canonical_parent.show_message('Loop Adjust: ' + INC_DISP[val])

    @subject_slot('value')
    def _action_mv_loop(self, value):
        if value > 0:
            if self.mv_loop:
                self._loop_move_button.send_value(0, True)
                self.mv_loop = False
            else:
                self._loop_move_button.send_value(127, True)
                self.mv_loop = True

    @subject_slot('value')
    def _action_mark_start(self, value):
        if self._scroll_mode:
            scroll = value == 1 and 3 or 2
            self.application().view.scroll_view(scroll, 'Detail/Clip', False)
        elif not (value == 1 and 1):
            inc = -1
            clip = self.selected_clip_slot and self.selected_clip_slot.has_clip and self.selected_clip_slot.clip
            ls = clip.start_marker
            le = clip.end_marker
            ls = max(0, min(le - self.start_inc, ls + inc * self.start_inc))
            clip.start_marker = ls
            bars_to_measure(ls, clip.signature_denominator, clip.signature_numerator)
            self.canonical_parent.timed_message(2, 'Clip Start: ' + bars_to_measure(ls, clip.signature_denominator, clip.signature_numerator))

    @subject_slot('value')
    def _action_mark_end(self, value):
        if self._scroll_mode:
            scroll = value == 1 and 3 or 2
            self.application().view.zoom_view(scroll, 'Detail/Clip', False)
        elif not (value == 1 and 1):
            inc = -1
            clip = self.selected_clip_slot and self.selected_clip_slot.has_clip and self.selected_clip_slot.clip
            ls = clip.start_marker
            le = clip.end_marker
            le = max(ls + self.start_inc, le + inc * self.start_inc)
            clip.end_marker = le
            self.canonical_parent.timed_message(2, 'Clip End: ' + bars_to_measure(le, clip.signature_denominator, clip.signature_numerator))

    @subject_slot('value')
    def _action_loop_start(self, value):
        if not (value == 1 and 1):
            inc = -1
            if self.selected_clip_slot and self.selected_clip_slot.has_clip:
                clip = self.selected_clip_slot.clip
                ls = clip.loop_start
                le = clip.loop_end
                if self.mv_loop:
                    diff = le - ls
                    ls = max(0, ls + inc * self.loop_inc)
                    clip.loop_end = inc > 0 and ls + diff
                    clip.end_marker = ls + diff
                    clip.loop_start = ls
                    clip.start_marker = ls
                else:
                    clip.loop_start = ls
                    clip.start_marker = ls
                    clip.loop_end = ls + diff
                    clip.end_marker = ls + diff
                self.canonical_parent.timed_message(2, loop_str(clip))
            else:
                ls = max(0, min(le - self.loop_inc, ls + inc * self.loop_inc))
                clip.loop_start = ls
                self.canonical_parent.timed_message(2, loop_str(clip))

    @subject_slot('value')
    def _action_loop_end(self, value):
        if not (value == 1 and 1):
            inc = -1
            if self.selected_clip_slot and self.selected_clip_slot.has_clip:
                clip = self.selected_clip_slot.clip
                ls = clip.loop_start
                le = clip.loop_end
                le = max(ls + self.loop_inc, le + inc * self.loop_inc)
                clip.loop_end = le
                clip.end_marker = self.mv_loop and le
            self.canonical_parent.timed_message(2, loop_str(clip))

    def update(self):
        pass

    @subject_slot('value')
    def _action_pitch_c(self, value):
        cs = self.selected_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            cs.clip.pitch_coarse = midi_to_pitchc(value)

    @subject_slot('value')
    def _action_pitch_f(self, value):
        cs = self.selected_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            cs.clip.pitch_fine = midi_to_pitchf(value)

    @subject_slot('value')
    def _action_gain(self, value):
        cs = self.selected_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            cs.clip.gain = midi_to_gain(value)

    def _update_clip_name(self):
        cs = self.song().view.highlighted_clip_slot
        if not cs:
            track = self.song().view.selected_track
            self.canonical_parent.send_to_display('Rt Trck: ' + track.name, 3)
        elif cs.has_clip:
            self.canonical_parent.send_to_display(cs.clip.is_audio_clip and 'A' or 'M' + ':' + cs.clip.name, 3)
        else:
            track = cs.canonical_parent
            index = list(track.clip_slots).index(cs)
            scene = self.song().scenes[index]
            self.canonical_parent.send_to_display('E<' + str(scene.name) + '> T:' + track.name, 3)

    @subject_slot('has_clip')
    def _on_has_clip_changed(self):
        self._update_clip_name()

    @subject_slot('name')
    def _on_name_changed(self):
        self._update_clip_name()

    def update_selected_clip(self):
        cs = self.song().view.highlighted_clip_slot
        if cs != self.selected_clip_slot:
            self.selected_clip_slot = cs
            self._update_clip_name()
            if cs and cs.has_clip and cs.clip.is_audio_clip:
                self._on_pitch_c_changed.subject = cs.clip
                self._on_pitch_f_changed.subject = cs.clip
                self._on_gain_changed.subject = cs.clip
                self._on_warp_changed.subject = cs.clip
                self._gain_slider.send_value(gain_to_midi(cs.clip.gain))
                self._pitch_c_slider.send_value(pitchc_to_midi(cs.clip.pitch_coarse))
                self._pitch_f_slider.send_value(pitchf_to_midi(cs.clip.pitch_fine))
                self._warp_set_button.send_value(cs.clip.warping and 127 or 0, True)
            else:
                self._on_pitch_c_changed.subject = None
                self._on_pitch_f_changed.subject = None
                self._on_gain_changed.subject = None
                self._on_warp_changed.subject = None
                self._on_loop_changed.subject = None
            if cs and cs.has_clip:
                self._on_loop_changed.subject = cs.clip
                self._on_name_changed.subject = cs.clip
                self._loop_set_button.send_value(cs.clip.looping and 127 or 0, True)
            else:
                self._on_name_changed.subject = None
                self._on_loop_changed.subject = None
            self._on_has_clip_changed.subject = cs

    def on_selected_track_changed(self):
        self.update_selected_clip()

    def on_selected_scene_changed(self):
        self.update_selected_clip()

    @subject_slot('looping')
    def _on_loop_changed(self):
        cs = self.song().view.highlighted_clip_slot
        if cs and cs.has_clip:
            self._loop_set_button.send_value(cs.clip.looping and 127 or 0, True)

    @subject_slot('warping')
    def _on_warp_changed(self):
        cs = self.song().view.highlighted_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            self._warp_set_button.send_value(cs.clip.warping and 127 or 0, True)

    @subject_slot('pitch_coarse')
    def _on_pitch_c_changed(self):
        cs = self.song().view.highlighted_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            self._pitch_c_slider.send_value(pitchc_to_midi(cs.clip.pitch_coarse))

    @subject_slot('pitch_fine')
    def _on_pitch_f_changed(self):
        cs = self.song().view.highlighted_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            self._pitch_f_slider.send_value(pitchf_to_midi(cs.clip.pitch_fine))

    @subject_slot('gain')
    def _on_gain_changed(self):
        cs = self.song().view.highlighted_clip_slot
        if cs and cs.has_clip and cs.clip.is_audio_clip:
            self._gain_slider.send_value(gain_to_midi(cs.clip.gain))