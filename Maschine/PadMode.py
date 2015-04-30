#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\PadMode.py
import Live
from MIDI_Map import *
from PadScale import *
from MaschineMode import MaschineMode, find_drum_device
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot
from _Framework.SliderElement import SliderElement

class PadMode(MaschineMode):

    def __init__(self, button_index, monochrome = False, *a, **k):
        super(PadMode, self).__init__(button_index, *a, **k)
        self._note_display_mode = ND_KEYBOARD1
        self.current_scale_index = 0
        self._scale = None
        self._base_note = 0
        self._octave = 0.55
        self.current_scale_index = 0
        self._in_edit_mode = False
        self._editmode = None
        self._is_monochrome = monochrome
        self._color_edit_assign = monochrome and self.assign_edit_mono or self.assign_edit_color
        self.assign_transpose(SCALES[self.current_scale_index])
        is_momentary = True
        self.octave_down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 120)
        self.octave_up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 121)
        self.base_down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 124)
        self.base_up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 125)
        self.scale_down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 118)
        self.scale_up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 119)
        self._adjust_scale.subject = SliderElement(MIDI_CC_TYPE, 2, 116)
        self._adjust_octav.subject = SliderElement(MIDI_CC_TYPE, 2, 115)
        self._adjust_basem.subject = SliderElement(MIDI_CC_TYPE, 2, 117)
        self._do_oct_down.subject = self.octave_down_button
        self._do_oct_up.subject = self.octave_up_button
        self._do_base_down.subject = self.base_down_button
        self._do_base_up.subject = self.base_up_button
        self._do_scale_down.subject = self.scale_down_button
        self._do_scale_up.subject = self.scale_up_button
        self._seg_display = None

    def set_edit_mode(self, editmode):
        self._editmode = editmode

    def set_segment_display(self, displayer):
        self._seg_display = displayer

    def get_color(self, value, column, row):
        button = self.canonical_parent._bmatrix.get_button(column, row)
        if button != None:
            midi_note = button.get_identifier()
            on = value != 0
            return self.get_color_by_note_mode(midi_note, on)

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

    def step_key_color_mode(self):
        self._note_display_mode = (self._note_display_mode + 1) % len(KEY_COLOR_MODES_STRINGS)
        self.canonical_parent.show_message('Note Mode Key Color: ' + KEY_COLOR_MODES_STRINGS[self._note_display_mode])
        self.canonical_parent.timed_message(2, 'Note Col: ' + KEY_COLOR_MODES_STRINGS[self._note_display_mode])
        if self._active:
            self.assign_transpose(SCALES[self.current_scale_index])

    def update_text_display(self):
        self.text_current_scale()

    def navigate(self, dir, modifier, alt_modifier = False):
        if modifier:
            self.inc_scale(dir)
        elif alt_modifier:
            self.inc_base_note(dir)
        else:
            self.inc_octave(dir)

    @subject_slot('value')
    def _adjust_scale(self, value):
        self.inc_scale(value == 0 and -1 or 1)

    @subject_slot('value')
    def _adjust_octav(self, value):
        self.inc_octave(value == 0 and -1 or 1)

    @subject_slot('value')
    def _adjust_basem(self, value):
        self.inc_base_note(value == 0 and -1 or 1)

    @subject_slot('value')
    def _do_oct_up(self, value):
        if value != 0:
            self.inc_octave(1)

    @subject_slot('value')
    def _do_oct_down(self, value):
        if value != 0:
            self.inc_octave(-1)

    @subject_slot('value')
    def _do_base_up(self, value):
        if value != 0:
            self.inc_base_note(1)

    @subject_slot('value')
    def _do_base_down(self, value):
        if value != 0:
            self.inc_base_note(-1)

    @subject_slot('value')
    def _do_scale_up(self, value):
        if value != 0:
            self.inc_scale(1)

    @subject_slot('value')
    def _do_scale_down(self, value):
        if value != 0:
            self.inc_scale(-1)

    def get_mode_id(self):
        return PAD_MODE

    def text_current_scale(self):
        scale = SCALES[self.current_scale_index]
        text = scale.name + ' ' + BASE_NOTE[self._base_note] + str(scale.to_octave(self._octave) - 2)
        self.canonical_parent.send_to_display(text)

    def inc_base_note(self, inc):
        prev_value = self._base_note
        self._base_note = min(11, max(0, self._base_note + inc))
        if prev_value != self._base_note:
            scale = SCALES[self.current_scale_index]
            self.canonical_parent.show_message(' Base Note ' + BASE_NOTE[self._base_note] + ' to ' + scale.name)
            self.text_current_scale()
            self.update_transpose()
            if self._seg_display:
                self._seg_display.timed_segment(self._base_note)

    def inc_scale(self, inc):
        nr_of_scales = len(SCALES) - 1
        prev_value = self.current_scale_index
        self.current_scale_index = min(nr_of_scales, max(0, self.current_scale_index + inc))
        if prev_value != self.current_scale_index:
            newscale = SCALES[self.current_scale_index]
            self.canonical_parent.show_message(' PAD Scale ' + newscale.name + ' ' + BASE_NOTE[self._base_note] + str(newscale.to_octave(self._octave) - 2))
            self.text_current_scale()
            self.update_transpose()
            if self._seg_display:
                self._seg_display.timed_segment(self.current_scale_index)

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
        self.canonical_parent.show_message(' OCTAVE ' + BASE_NOTE[self._base_note] + str(newoctave - 2) + ' to ' + scale.name)
        self.text_current_scale()
        self.update_transpose()
        if self._seg_display:
            val = newoctave - 2
            if val < 0:
                val = 100 + abs(val)
            self._seg_display.timed_segment(val)

    def get_octave(self):
        return SCALES[self.current_scale_index].to_octave(self._octave)

    def update_transpose(self):
        if self._active:
            self.assign_transpose(SCALES[self.current_scale_index])
            self.canonical_parent._set_suppress_rebuild_requests(True)
            self.canonical_parent.request_rebuild_midi_map()
            self.canonical_parent._set_suppress_rebuild_requests(False)

    def fitting_mode(self, track):
        if not track:
            return self
        drum_device = find_drum_device(track)
        if drum_device != None and self._alternate_mode != None:
            return self._alternate_mode
        return self

    def refresh(self):
        if self._active:
            scale_len = len(self._scale.notevalues)
            octave = self._scale.to_octave(self._octave)
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    note_index = (3 - row) * 4 + column
                    scale_index = note_index % scale_len
                    octave_offset = note_index / scale_len
                    note_value = self._scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
                    button.reset()
                    button.send_color_direct(self.get_color_by_note_mode(note_value, False))

    def assign_edit_color(self, in_notes, button, note_value):
        if in_notes:
            if note_value in in_notes:
                button.send_color_direct(self.get_color_by_note_mode(note_value, True))
            else:
                button.send_color_direct(self.get_color_by_note_mode(note_value, False))
        else:
            button.send_color_direct(self.get_color_by_note_mode(note_value, False))

    def assign_edit_mono(self, in_notes, button, note_value):
        if in_notes:
            if note_value in in_notes:
                button.send_value(127, True)
            else:
                button.send_value(0, True)
        else:
            button.send_value(0, True)

    def get_in_notes(self):
        cs = self.song().view.highlighted_clip_slot
        if cs.has_clip and cs.clip.is_midi_clip:
            in_notes = set()
            notes = cs.clip.get_notes(0.0, 0, cs.clip.length, 127)
            for note in notes:
                in_notes.add(note[0])

            return in_notes

    def assign_transpose(self, scale):
        if not isinstance(scale, PadScale):
            raise AssertionError
            self._scale = scale
            scale_len = len(scale.notevalues)
            octave = scale.to_octave(self._octave)
            last_note_val = None
            in_notes = self._active and (self._in_edit_mode and self.get_in_notes() or None)
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    note_index = (3 - row) * 4 + column
                    scale_index = note_index % scale_len
                    octave_offset = note_index / scale_len
                    note_value = scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
                    if note_value < 128:
                        last_note_val = note_value
                    elif last_note_val != None:
                        note_value = last_note_val
                    button.set_send_note(note_value)
                    if self._in_edit_mode:
                        self._color_edit_assign(in_notes, button, note_value)
                    else:
                        button.send_color_direct(self.get_color_by_note_mode(note_value, False))

    def auto_select(self):
        return True

    @subject_slot('notes')
    def _on_notes_changed(self):
        if self._in_edit_mode:
            in_notes = self.get_in_notes()
            if in_notes:
                for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                    if button:
                        if button._msg_identifier in in_notes:
                            button.send_value(127, True)
                        else:
                            button.send_value(0, True)

            else:
                for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                    button.send_value(0, True)

    def enter_clear_state(self):
        self._in_edit_mode = True
        cs = self.song().view.highlighted_clip_slot
        in_notes = set()
        if cs != None and cs.has_clip and cs.clip.is_midi_clip:
            clip = cs.clip
            notes = clip.get_notes(0.0, 0, clip.length, 127)
            self._on_notes_changed.subject = clip
            for note in notes:
                in_notes.add(note[0])

        else:
            self._on_notes_changed.subject = None
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                if button._msg_identifier in in_notes:
                    button.send_value(127, True)
                else:
                    button.send_value(0, True)
                button.set_to_notemode(False)
                button.add_value_listener(self._action_clear, True)

    def exit_clear_state(self):
        self._in_edit_mode = False
        self._on_notes_changed.subject = None
        scale_len = len(self._scale.notevalues)
        octave = self._scale.to_octave(self._octave)
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                note_index = (3 - row) * 4 + column
                scale_index = note_index % scale_len
                octave_offset = note_index / scale_len
                button.send_value(0, True)
                note_value = self._scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
                button.send_color_direct(self.get_color_by_note_mode(note_value, False))
                button.set_to_notemode(True)
                button.remove_value_listener(self._action_clear)

    def _action_clear(self, value, button):
        if value != 0:
            self._editmode.edit_note(button._msg_identifier)

    def enter(self):
        self._active = True
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                button.send_value(0, True)
                button.set_to_notemode(True)
                self.canonical_parent._forwarding_registry[MIDI_NOTE_ON_STATUS, button.get_identifier()] = button
                self.canonical_parent._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button

        self.update_transpose()

    def exit(self):
        self._active = False