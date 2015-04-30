#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\EditSection.py
"""
Created on 15.10.2013

@author: Eric Ahrens
"""
import Live
from _Framework.SubjectSlot import subject_slot
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
import time
from StateButton import StateButton
from MIDI_Map import *
from _Framework.SliderElement import SliderElement
ES_NONE = 0
ES_DUPLICATE = 1
ES_NEW = 2
ES_DOUBLE = 3
ES_CLEAR = 4
ES_QUANT = 5
ES_NUDGE = 6
ES_NAVIGATE = 7
ES_KNOB = 8

def select_clip_slot(song, slot):
    if slot:
        song.view.highlighted_clip_slot = slot


def is_clicked(downtime):
    clicktime = int(round(time.time() * 1000)) - downtime
    if clicktime < 500:
        return True
    else:
        return False


class EditSection(CompoundComponent):

    def __init__(self, *a, **k):
        super(EditSection, self).__init__(*a, **k)
        is_momentary = True
        self.mikro_shift_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 2, 80)
        self._do_shift_mikro.subject = self.mikro_shift_button
        self.shift_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 80)
        self._do_shift.subject = self.shift_button
        self.alt_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 82)
        self._do_alt.subject = self.alt_button
        self.mikro_shift = False
        self.shiftdown = False
        self.altdown = False
        self.edit_state = ES_NONE
        self._down_button = None
        self._action_set_quant.subject = SliderElement(MIDI_CC_TYPE, 2, 110)
        self._action_init_loop.subject = SliderElement(MIDI_CC_TYPE, 2, 111)
        self._nav_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 115)
        self._action_navigate.subject = self._nav_button
        self._copy_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 95)
        self._action_duplicate.subject = self._copy_button
        self._quantize_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 97)
        self._action_quantize.subject = self._quantize_button
        self._paste_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 96)
        self._action_new.subject = self._paste_button
        self._note_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 101)
        self._action_note.subject = self._note_button
        self._clear_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 103)
        self._action_clear.subject = self._clear_button
        self._nudge_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 100)
        self._action_nudge_button.subject = self._nudge_button
        self.action_time = False
        self.pad_action = False
        self.pad_wheel_action = False
        self.quantize = 5
        self.quantize_amount = 1.0
        self.initial_clip_len = 4.0
        self._focused_clip = None
        self._focused_c_index = None
        self._color_edit = False
        self.nav_index = 0

    def disconnect(self):
        super(EditSection, self).disconnect()

    def init(self):
        self._color_edit_button.send_value(0, True)

    def set_color_edit(self, val):
        self._color_edit = val

    def is_color_edit(self):
        return self._color_edit

    def connect_session(self, session):
        for sindex in range(session.height()):
            scene = session.scene(sindex)
            for cindex in range(session.width()):
                clip = scene.clip_slot(cindex)
                clip.set_modifier(self)

    def set_mode_selector(self, mode_selector):
        self._mode_selector = mode_selector
        self._mode_selector.assign_edit_section(self)

    @subject_slot('value')
    def _do_shift_mikro(self, value):
        self.mikro_shift = value != 0
        self.shiftdown = value != 0
        if self._mode_selector:
            self._mode_selector.set_shift_state(self.mikro_shift)

    @subject_slot('value')
    def _do_shift(self, value):
        self.shiftdown = value != 0

    @subject_slot('value')
    def _do_alt(self, value):
        self.altdown = value != 0

    def modifiers(self):
        return self.shiftdown and 1 | (self.altdown and 1 << 1)

    def isShiftdown(self):
        return self.shiftdown

    def isAltdown(self):
        return self.altdown

    def isClipAltDown(self):
        return self.altdown or self._mode_selector.isClipDown()

    def hasModification(self, mode):
        if mode == SCENE_MODE:
            return self.edit_state != ES_NONE
        elif mode == CLIP_MODE:
            if self.edit_state != ES_NONE:
                return True
            elif self._color_edit:
                return True
        return False

    def update(self):
        pass

    def _get_current_slot(self, song):
        scene = song.view.selected_scene
        track = song.view.selected_track
        clip_slot = song.view.highlighted_clip_slot
        scenes = song.scenes
        tracks = song.tracks
        sindex = vindexof(scenes, scene)
        tindex = vindexof(tracks, track)
        return (clip_slot,
         track,
         scenes,
         tindex,
         sindex)

    def do_message(self, msg, statusbarmsg = None):
        if statusbarmsg == None:
            self.canonical_parent.show_message(msg)
        else:
            self.canonical_parent.show_message(statusbarmsg)
        self.canonical_parent.timed_message(2, msg)

    def edit_note(self, note_value):
        self.pad_action = True
        if self.edit_state == ES_CLEAR:
            cs = self.song().view.highlighted_clip_slot
            if cs and cs.has_clip and cs.clip.is_midi_clip:
                if self.shiftdown:
                    cs.clip.remove_notes(0.0, 0, cs.clip.length, 127)
                else:
                    cs.clip.remove_notes(0.0, note_value, cs.clip.length, 1)

    def edit_scene_slot(self, scene, index):
        self.pad_action = True
        if scene != None:
            song = self.song()
            if self.edit_state == ES_DUPLICATE:
                self.do_message('Duplicate Scene ' + str(scene.name))
                song.duplicate_scene(index)
            elif self.edit_state == ES_NEW:
                idx = 1
                if self.shiftdown:
                    idx = 0
                song.create_scene(index + idx)
                self.do_message('Create Scene ' + str(self.song().view.selected_scene.name))
            elif self.edit_state == ES_CLEAR:
                self.do_message('Delete Scene ' + str(scene.name))
                song.delete_scene(index)
            elif self.edit_state == ES_DOUBLE:
                song.capture_and_insert_scene()
                scene = self.song().view.selected_scene
                self.do_message('Capture to ' + scene.name)
            elif self.edit_state == ES_NUDGE:
                self.clear_auto_scene(scene, index)
                self.do_message('Clr Env in Scene ' + scene.name)
            elif self.edit_state == ES_QUANT:
                pass
            elif self.edit_state == ES_NAVIGATE:
                self.song().view.selected_scene = scene

    def duplciate_clip_slot(self, clip_slot):
        if clip_slot.has_clip:
            try:
                track = clip_slot.canonical_parent
                index = list(track.clip_slots).index(clip_slot)
                track.duplicate_clip_slot(index)
                self.do_message('Duplicate Clip ' + clip_slot.clip.name)
                select_clip_slot(self.song(), track.clip_slots[index + 1])
            except Live.Base.LimitationError:
                pass
            except RuntimeError:
                pass

    @subject_slot('value')
    def _action_set_quant(self, value):
        self.mod_quant_size(value == 0 and -1 or 1)

    @subject_slot('value')
    def _action_init_loop(self, value):
        self.mod_new_initlen(value == 0 and -1 or 1)

    def mod_new_initlen(self, diff):
        if abs(diff) == 4:
            newval = self.initial_clip_len + diff
            newval = int(newval / 4) * 4
            self.initial_clip_len = max(4.0, min(64.0, newval))
        else:
            self.initial_clip_len = max(1.0, min(64.0, self.initial_clip_len + diff))
        self.canonical_parent.timed_message(2, 'Init Clip Len: ' + str(int(self.initial_clip_len)) + ' Beats', True)
        self.canonical_parent.show_message('Initial Clip Length : ' + str(int(self.initial_clip_len)) + ' beats')

    def mod_quant_size(self, diff):
        self.quantize = max(1, min(len(QUANT_CONST) - 1, self.quantize + diff))
        self.canonical_parent.timed_message(2, 'Quantize: ' + QUANT_STRING[self.quantize], True)
        self.canonical_parent.show_message('Quantize set to : ' + QUANT_STRING[self.quantize])

    def knob_pad_action(self, activate):
        if activate:
            self.pad_wheel_action = True
            self.edit_state = ES_KNOB
            self._focused_clip = None
        else:
            self.pad_wheel_action = False
            self.edit_state = ES_NONE
            self._focused_clip = None

    def edit_colors(self, diff, jump_selection = False):
        pass

    def edit_clip_slot(self, clipslot_component, value):
        if self._color_edit:
            if value != 0:
                if clipslot_component._clip_slot != None:
                    self._focused_clip = clipslot_component
                    self._mode_selector.pick_color(clipslot_component)
            else:
                self._focused_clip = None
        else:
            self.pad_action = True
            if value != 0 and clipslot_component._clip_slot != None:
                clip_slot = clipslot_component._clip_slot
                if self.edit_state == ES_DUPLICATE:
                    if self.shiftdown:
                        self.duplicate_track_cs(clip_slot)
                    else:
                        self.duplciate_clip_slot(clip_slot)
                elif self.edit_state == ES_NEW:
                    if self.shiftdown:
                        self.create_new_midi_track(clip_slot)
                    else:
                        self.create_new_clip(clip_slot)
                elif self.edit_state == ES_CLEAR:
                    if self.altdown:
                        if clip_slot.clip != None:
                            clip = clip_slot.clip
                            if clip.is_midi_clip:
                                self.do_message('Clear all Notes in Clip')
                                clip.remove_notes(0.0, 0, clip.length, 127)
                    elif self.shiftdown:
                        self.delete_track_cs(clip_slot)
                    else:
                        if clip_slot.clip:
                            self.do_message('Delete Clip ' + clip_slot.clip.name)
                        clipslot_component._do_delete_clip()
                elif self.edit_state == ES_DOUBLE:
                    if self.shiftdown:
                        self.create_new_audio_track(clip_slot)
                    else:
                        self.double_clipslot(clip_slot)
                elif self.edit_state == ES_NUDGE:
                    if self.shiftdown:
                        self._new_return_track()
                    else:
                        self.clear_automation(clip_slot)
                elif self.edit_state == ES_QUANT:
                    self.quantize_clisplot(clipslot_component._clip_slot)
                elif self.edit_state == ES_NAVIGATE:
                    clipslot_component._do_select_clip(clipslot_component._clip_slot)
                    if self.canonical_parent.arm_selected_track:
                        arm_exclusive(self.song())

    def _new_return_track(self):
        song = self.song()
        song.create_return_track()
        self.do_message('New Return Track')

    def _new_scene(self):
        song = self.song()
        scene = song.view.selected_scene
        sindex = vindexof(song.scenes, scene)
        sindex = sindex >= 0 and sindex or 0
        song.create_scene(sindex + 1)
        new_scene = song.view.selected_scene
        self.do_message('New Scene ' + new_scene.name)

    def _new_audio_track(self):
        song = self.song()
        track = song.view.selected_track
        tindex = 0
        if not track.can_be_armed:
            tindex = len(song.tracks) - 1
        else:
            tindex = vindexof(song.tracks, track)
        tindex = tindex >= 0 and tindex or 0
        song.create_audio_track(tindex + 1)
        track = song.view.selected_track
        self.do_message('New Audio Track ' + track.name)

    def _new_midi_track(self):
        song = self.song()
        track = song.view.selected_track
        tindex = 0
        if not track.can_be_armed:
            tindex = len(song.tracks) - 1
        else:
            tindex = vindexof(song.tracks, track)
        tindex = tindex >= 0 and tindex or 0
        song.create_midi_track(tindex + 1)
        track = song.view.selected_track
        self.do_message('New MIDI Track ' + track.name)

    def _new_midi_clip(self):
        song = self.song()
        if song.view.selected_track.has_midi_input:
            clip_slot = song.view.highlighted_clip_slot
            if clip_slot != None and not clip_slot.has_clip:
                clip_slot.create_clip(self.initial_clip_len)
                song.view.detail_clip = clip_slot.clip
                self.do_message('New MIDI Clip ' + clip_slot.clip.name)
                self.application().view.show_view('Detail')

    def quantize_scene(self, scene, index, fiftyPerc):
        tracks = self.song().tracks
        for track in tracks:
            clipslots = track.clip_slots
            if len(clipslots) >= index and clipslots[index].clip != None:
                clipslots[index].clip.quantize(QUANT_CONST[self.quantize], self.shiftdown and 0.5 or 1.0)

    def clear_auto_scene(self, scene, index):
        tracks = self.song().tracks
        for track in tracks:
            clipslots = track.clip_slots
            if len(clipslots) >= index and clipslots[index].clip != None:
                clipslots[index].clip.clear_all_envelopes()

    def _capture_new_scene(self):
        self.song().capture_and_insert_scene()
        scene = self.song().view.selected_scene
        self.do_message('Capture to ' + scene.name)

    def _duplicate_selected_scene(self):
        song = self.song()
        scene = song.view.selected_scene
        sindex = vindexof(song.scenes, scene)
        if scene and sindex >= 0:
            self.do_message('Duplicate Scene ' + scene.name)
            song.duplicate_scene(sindex)

    def _duplicate_selected_track(self):
        song = self.song()
        track = song.view.selected_track
        t_index = track_index(song, track)
        if track and t_index and t_index[1] == TYPE_TRACK_SESSION:
            tindex = t_index[0]
            self.do_message('Dupl. Track ' + track.name, 'Duplicate Track ' + track.name)
            song.duplicate_track(tindex)

    def _duplicate_selected_clip(self):
        song = self.song()
        clip_slot, track, scenes, tindex, sindex = self._get_current_slot(song)
        if clip_slot != None and clip_slot.clip != None:
            self.do_message('Duplicate ' + clip_slot.clip.name, 'Duplicate Clip ' + clip_slot.clip.name)
            track.duplicate_clip_slot(sindex)
            index = sindex + 1
            if index >= 0 and index < len(scenes):
                song.view.selected_scene = scenes[index]

    def duplicate_track_cs(self, clip_slot):
        if clip_slot != None:
            song = self.song()
            track = clip_slot.canonical_parent
            t_index = track_index(song, track)
            if track and t_index and t_index[1] == TYPE_TRACK_SESSION:
                tindex = t_index[0]
                self.do_message('Duplicate Track ' + track.name)
                song.duplicate_track(tindex)

    def clear_automation(self, clip_slot):
        song = self.song()
        if clip_slot != None and clip_slot.clip != None:
            self.do_message('Clr.Env. ' + clip_slot.clip.name, 'Clear Envelopes ' + clip_slot.clip.name)
            clip_slot.clip.clear_all_envelopes()

    def quantize_clisplot(self, clip_slot):
        if clip_slot.clip != None:
            self.do_message('Quantize Clip: ' + clip_slot.clip.name + (self.shiftdown and ' 50%' or ''))
            clip_slot.clip.quantize(QUANT_CONST[self.quantize], self.shiftdown and 0.5 or 1.0)
            self.song().view.detail_clip = clip_slot.clip
            self.canonical_parent.focus_clip_detail()

    def double_clipslot(self, clip_slot):
        song = self.song()
        track = clip_slot.canonical_parent
        if clip_slot.clip != None and track.has_midi_input:
            clip = clip_slot.clip
            if clip.length <= 2048.0:
                clip.duplicate_loop()
                self.do_message('Dupl. Lp: ' + str(int(clip.length / 4)) + ' Bars')
                song.view.detail_clip = clip
                self.canonical_parent.focus_clip_detail()
            else:
                self.do_message('Clip is to long to Duplicate')

    def create_new_clip(self, clip_slot):
        song = self.song()
        track = clip_slot.canonical_parent
        if clip_slot.clip == None and track.has_midi_input:
            clip_slot.create_clip(self.initial_clip_len)
            song.view.detail_clip = clip_slot.clip
            select_clip_slot(song, clip_slot)
            self.canonical_parent.focus_clip_detail()
            self.do_message('New Midi Clip ' + song.view.highlighted_clip_slot.clip.name)

    def create_new_midi_track(self, clip_slot):
        if clip_slot != None:
            song = self.song()
            track = clip_slot.canonical_parent
            tindex = vindexof(song.tracks, track)
            tindex = tindex >= 0 and tindex or 0
            song.create_midi_track(tindex + 1)
            track = song.view.selected_track
            self.do_message('New Midi Track ' + track.name)

    def create_new_audio_track(self, clip_slot):
        if clip_slot != None:
            song = self.song()
            track = clip_slot.canonical_parent
            tindex = vindexof(song.tracks, track)
            tindex = tindex >= 0 and tindex or 0
            song.create_audio_track(tindex + 1)
            track = song.view.selected_track
            self.do_message('New Audio Track ' + track.name)

    def delete_track_cs(self, clip_slot):
        if clip_slot != None:
            song = self.song()
            track = clip_slot.canonical_parent
            t_index = track_index(song, track)
            if track and len(song.tracks) > 1 and t_index and t_index[1] == TYPE_TRACK_SESSION:
                self.do_message('Delete Track ' + track.name)
                song.delete_track(t_index[0])

    def _double_selected_clip(self):
        song = self.song()
        clip_slot = song.view.highlighted_clip_slot
        if clip_slot != None and clip_slot.clip != None and song.view.selected_track.has_midi_input:
            clip = clip_slot.clip
            if clip.length <= 2048.0:
                clip_slot.clip.duplicate_loop()
                self.do_message('Dupl. Lp ' + str(int(clip_slot.clip.length / 4)) + ' Bars')
                song.view.detail_clip = clip_slot.clip
                self.canonical_parent.focus_clip_detail()
            else:
                self.do_message('Clip is to long to Duplicate')

    def _clear_events(self):
        song = self.song()
        clip_slot = song.view.highlighted_clip_slot
        if clip_slot != None and clip_slot.clip != None:
            self.do_message('Clr.Env. ' + clip_slot.clip.name, 'Clear Envelopes ' + clip_slot.clip.name)
            clip_slot.clip.clear_all_envelopes()

    def _delete_current_clip(self):
        song = self.song()
        clip_slot = song.view.highlighted_clip_slot
        if clip_slot != None and clip_slot.clip != None:
            self.do_message('Delete Clip ' + clip_slot.clip.name)
            clip_slot.delete_clip()

    def _delete_selected_track(self):
        song = self.song()
        track = song.view.selected_track
        t_index = track_index(song, track)
        if track and len(song.tracks) > 1 and t_index and t_index[1] == TYPE_TRACK_SESSION:
            self.do_message('Delete Track ' + track.name)
            song.delete_track(t_index[0])

    def _delete_selected_scene(self):
        song = self.song()
        scene = song.view.selected_scene
        sindex = vindexof(song.scenes, scene)
        if scene and len(song.scenes) > 1 and sindex >= 0:
            self.do_message('Delete Scene ' + scene.name)
            song.delete_scene(sindex)

    def _click_duplicate(self):
        modifiers = self.modifiers()
        if modifiers == 0:
            self._duplicate_selected_clip()
        elif modifiers == 1:
            self._duplicate_selected_track()
        elif modifiers == 2:
            self._duplicate_selected_scene()

    def _click_new(self):
        modifiers = self.modifiers()
        if modifiers == 0:
            self._new_midi_clip()
        elif modifiers == 1:
            self._new_midi_track()
        elif modifiers == 2:
            self._new_scene()

    def _click_double(self):
        modifiers = self.modifiers()
        if modifiers == 0:
            self._double_selected_clip()
        elif modifiers == 1:
            self._new_audio_track()
        elif modifiers == 2:
            self._capture_new_scene()

    def _click_clear(self):
        modifiers = self.modifiers()
        if modifiers == 0:
            self._delete_current_clip()
        elif modifiers == 1:
            self._delete_selected_track()
        elif modifiers == 2:
            self._delete_selected_scene()

    def _click_quantize(self):
        song = self.song()
        clip_slot = song.view.highlighted_clip_slot
        if clip_slot != None:
            self.quantize_clisplot(clip_slot)

    def _click_nudge(self):
        modifiers = self.modifiers()
        if modifiers == 0:
            self._clear_events()
        elif modifiers == 1:
            self._new_return_track()
        elif modifiers == 2:
            pass

    def _select(self, button):
        if self._down_button:
            self._down_button.turn_off()
        button.turn_on()
        self._down_button = button
        self.action_time = int(round(time.time() * 1000))

    def _deselect(self, button):
        if button == self._clear_button:
            self._mode_selector.exit_clear_state()
        if self._down_button == button:
            self._down_button.turn_off()
            self._down_button = None
            prev_state = self.edit_state
            self.edit_state = ES_NONE
            modeid = self._mode_selector.mode().get_mode_id()
            if self.pad_action:
                self.pad_action = False
                return False
            if modeid == CLIP_MODE or modeid == SCENE_MODE:
                return False
            if (modeid == PAD_MODE or modeid == CONTROL_MODE) and prev_state == ES_CLEAR:
                return False
            else:
                return True
        self.pad_action = False
        return False

    @subject_slot('value')
    def _action_navigate(self, value):
        if self.isShiftdown() and value != 0:
            self.nav_index = (self.nav_index + 1) % len(VIEWS_ALL)
            self.application().view.focus_view(VIEWS_ALL[self.nav_index])
            self.canonical_parent.show_message('Focus on : ' + str(VIEWS_ALL[self.nav_index]))
        elif value != 0:
            self._select(self._nav_button)
            self.edit_state = ES_NAVIGATE
        else:
            self._deselect(self._nav_button)

    @subject_slot('value')
    def _action_duplicate(self, value):
        if value != 0:
            self._select(self._copy_button)
            self.edit_state = ES_DUPLICATE
        elif self._deselect(self._copy_button):
            self._click_duplicate()

    @subject_slot('value')
    def _action_new(self, value):
        if value != 0:
            self._select(self._paste_button)
            self.edit_state = ES_NEW
        elif self._deselect(self._paste_button):
            self._click_new()

    @subject_slot('value')
    def _action_note(self, value):
        if value != 0:
            self._select(self._note_button)
            self.edit_state = ES_DOUBLE
        elif self._deselect(self._note_button):
            self._click_double()

    @subject_slot('value')
    def _action_clear(self, value):
        self.canonical_parent._hold_clear_action(value)
        if value != 0:
            self._mode_selector.enter_clear_state()
            self._select(self._clear_button)
            self.edit_state = ES_CLEAR
        elif self._deselect(self._clear_button):
            self._click_clear()

    @subject_slot('value')
    def _action_nudge_button(self, value):
        if value != 0:
            self._select(self._nudge_button)
            self.edit_state = ES_NUDGE
        elif self._deselect(self._nudge_button):
            self._click_nudge()

    @subject_slot('value')
    def _action_quantize(self, value):
        if value != 0:
            self._select(self._quantize_button)
            self.edit_state = ES_QUANT
        elif self._deselect(self._quantize_button):
            self._click_quantize()

    @subject_slot('value')
    def _toggle_color_mode(self, value):
        if value != 0:
            session = self.canonical_parent._session
            if session.is_color_mode():
                self._color_mode_button.switch_off()
                session._change_color_mode(1)
            else:
                self._color_mode_button.send_color(1)
                session._change_color_mode(1)