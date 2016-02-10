#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/instrument_component.py
from __future__ import absolute_import, print_function
from ableton.v2.base import Subject, index_if, listenable_property, listens, liveobj_valid, find_if
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.control import control_matrix
from ableton.v2.control_surface.components import PlayableComponent, Slideable, SlideComponent
from . import consts
from .melodic_pattern import SCALES, MelodicPattern, pitch_index_to_string
from .message_box_component import Messenger
from .pad_control import PadControl
from .slideable_touch_strip_component import SlideableTouchStripComponent
DEFAULT_SCALE = SCALES[0]

class NoteLayout(Subject):
    is_horizontal = listenable_property.managed(True)
    interval = listenable_property.managed(3)

    def __init__(self, song = None, preferences = dict(), *a, **k):
        raise liveobj_valid(song) or AssertionError
        super(NoteLayout, self).__init__(*a, **k)
        self._song = song
        self._scale = self._get_scale_from_name(self._song.scale_name)
        self._preferences = preferences
        self._is_in_key = self._preferences.setdefault('is_in_key', True)
        self._is_fixed = self._preferences.setdefault('is_fixed', False)

    @property
    def notes(self):
        return self.scale.to_root_note(self.root_note).notes

    @listenable_property
    def root_note(self):
        return self._song.root_note

    @root_note.setter
    def root_note(self, root_note):
        self._song.root_note = root_note
        self.notify_root_note(root_note)

    @listenable_property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self._song.scale_name = scale.name
        self.notify_scale(self._scale)

    @listenable_property
    def is_in_key(self):
        return self._is_in_key

    @is_in_key.setter
    def is_in_key(self, is_in_key):
        self._is_in_key = is_in_key
        self._preferences['is_in_key'] = self._is_in_key
        self.notify_is_in_key(self._is_in_key)

    @listenable_property
    def is_fixed(self):
        return self._is_fixed

    @is_fixed.setter
    def is_fixed(self, is_fixed):
        self._is_fixed = is_fixed
        self._preferences['is_fixed'] = self._is_fixed
        self.notify_is_fixed(self._is_fixed)

    def _get_scale_from_name(self, name):
        return find_if(lambda scale: scale.name == name, SCALES) or DEFAULT_SCALE


class InstrumentComponent(PlayableComponent, CompoundComponent, Slideable, Messenger):
    """
    Class that sets up the button matrix as a piano, using different
    selectable layouts for the notes.
    """
    __events__ = ('pattern',)
    matrix = control_matrix(PadControl, pressed_color='Instrument.NoteAction')

    def __init__(self, note_layout = None, *a, **k):
        raise note_layout is not None or AssertionError
        super(InstrumentComponent, self).__init__(*a, **k)
        self._note_layout = note_layout
        self._delete_button = None
        self._first_note = self.page_length * 3 + self.page_offset
        self._last_page_length = self.page_length
        self._delete_button = None
        self._last_page_offset = self.page_offset
        self._detail_clip = None
        self._has_notes = [False] * 128
        self._has_notes_pattern = self._get_pattern(0)
        self._aftertouch_control = None
        self._slider = self.register_component(SlideComponent(self))
        self._touch_slider = self.register_component(SlideableTouchStripComponent(self))
        for event in ('scale', 'root_note', 'is_in_key', 'is_fixed', 'is_horizontal', 'interval'):
            self.register_slot(self._note_layout, self._on_note_layout_changed, event)

        self._update_pattern()

    def set_detail_clip(self, clip):
        if clip != self._detail_clip:
            self._detail_clip = clip
            self._on_clip_notes_changed.subject = clip
            self._on_loop_start_changed.subject = clip
            self._on_loop_end_changed.subject = clip
            self._on_clip_notes_changed()

    @listens('notes')
    def _on_clip_notes_changed(self):
        if self._detail_clip:
            self._has_notes = [False] * 128
            loop_start = self._detail_clip.loop_start
            loop_length = self._detail_clip.loop_end - loop_start
            notes = self._detail_clip.get_notes(loop_start, 0, loop_length, 128)
            for note in notes:
                self._has_notes[note[0]] = True

        self.notify_contents()

    @listens('loop_start')
    def _on_loop_start_changed(self):
        self._on_loop_selection_changed()

    @listens('loop_end')
    def _on_loop_end_changed(self):
        self._on_loop_selection_changed()

    def _on_loop_selection_changed(self):
        self._on_clip_notes_changed()

    def contents(self, index):
        if self._detail_clip:
            note = self._has_notes_pattern[index].index
            if note is not None:
                return self._has_notes[note]
            return False
        return False

    @property
    def page_length(self):
        if self._note_layout.is_in_key:
            return len(self._note_layout.notes)
        return 12

    @property
    def position_count(self):
        if not self._note_layout.is_in_key:
            return 139
        else:
            offset = self.page_offset
            octaves = 11 if self._note_layout.notes[0] < 8 else 10
            return offset + len(self._note_layout.notes) * octaves

    def _first_scale_note_offset(self):
        if not self._note_layout.is_in_key:
            return self._note_layout.notes[0]
        elif self._note_layout.notes[0] == 0:
            return 0
        else:
            return len(self._note_layout.notes) - index_if(lambda n: n >= 12, self._note_layout.notes)

    @property
    def page_offset(self):
        if self._note_layout.is_fixed:
            return 0
        return self._first_scale_note_offset()

    def _get_position(self):
        return self._first_note

    def _set_position(self, note):
        self._first_note = note
        self._update_pattern()
        self._update_matrix()
        self.notify_position()

    position = property(_get_position, _set_position)

    @property
    def pattern(self):
        return self._pattern

    @matrix.pressed
    def matrix(self, button):
        self._on_matrix_pressed(button)

    def _on_matrix_pressed(self, button):
        if self._delete_button and self._delete_button.is_pressed():
            pitch = self._get_note_info_for_coordinate(button.coordinate).index
            if pitch and self._detail_clip:
                self._do_delete_pitch(pitch)

    def _do_delete_pitch(self, pitch):
        clip = self._detail_clip
        if clip:
            note_name = pitch_index_to_string(pitch)
            loop_length = clip.loop_end - clip.loop_start
            clip.remove_notes(clip.loop_start, pitch, loop_length, 1)
            self.show_notification(consts.MessageBoxText.DELETE_NOTES % note_name)

    @listens('value')
    def _on_delete_value(self, value):
        self._set_control_pads_from_script(bool(value))

    def set_note_strip(self, strip):
        self._touch_slider.set_scroll_strip(strip)

    def set_octave_strip(self, strip):
        self._touch_slider.set_page_strip(strip)

    def set_octave_up_button(self, button):
        self._slider.set_scroll_page_up_button(button)

    def set_octave_down_button(self, button):
        self._slider.set_scroll_page_down_button(button)

    def set_scale_up_button(self, button):
        self._slider.set_scroll_up_button(button)

    def set_scale_down_button(self, button):
        self._slider.set_scroll_down_button(button)

    def set_aftertouch_control(self, control):
        self._aftertouch_control = control
        self._update_aftertouch()

    def set_delete_button(self, button):
        self._delete_button = button
        self._on_delete_value.subject = button
        self._set_control_pads_from_script(button and button.is_pressed())

    def _align_first_note(self):
        self._first_note = self.page_offset + (self._first_note - self._last_page_offset) * float(self.page_length) / float(self._last_page_length)
        if self._first_note >= self.position_count:
            self._first_note -= self.page_length
        self._last_page_length = self.page_length
        self._last_page_offset = self.page_offset

    def _on_note_layout_changed(self, _):
        self._update_scale()

    def _update_scale(self):
        self._align_first_note()
        self._update_pattern()
        self._update_matrix()
        self.notify_position_count()
        self.notify_position()
        self.notify_contents()

    def update(self):
        super(InstrumentComponent, self).update()
        if self.is_enabled():
            self._update_matrix()
            self._update_aftertouch()

    def _update_pattern(self):
        self._pattern = self._get_pattern()
        self._has_notes_pattern = self._get_pattern(0)
        self.notify_pattern()

    def _invert_and_swap_coordinates(self, coordinates):
        return (coordinates[1], self.width - 1 - coordinates[0])

    def _get_note_info_for_coordinate(self, coordinate):
        x, y = self._invert_and_swap_coordinates(coordinate)
        return self.pattern.note(x, y)

    def _update_button_color(self, button):
        note_info = self._get_note_info_for_coordinate(button.coordinate)
        button.color = 'Instrument.' + note_info.color

    def _button_should_be_enabled(self, button):
        return self._get_note_info_for_coordinate(button.coordinate).index != None

    def _note_translation_for_button(self, button):
        note_info = self._get_note_info_for_coordinate(button.coordinate)
        return (note_info.index, note_info.channel)

    def _set_button_control_properties(self, button):
        super(InstrumentComponent, self)._set_button_control_properties(button)
        button.sensitivity_profile = 'default' if self._takeover_pads else 'instrument'

    def _update_matrix(self):
        self._update_control_from_script()
        self._update_led_feedback()
        self._update_note_translations()

    def _get_pattern(self, first_note = None):
        if first_note is None:
            first_note = int(round(self._first_note))
        interval = self._note_layout.interval
        notes = self._note_layout.notes
        octave = first_note / self.page_length
        offset = first_note % self.page_length - self._first_scale_note_offset()
        if interval == None:
            interval = 8
        elif not self._note_layout.is_in_key:
            interval = [0,
             2,
             4,
             5,
             7,
             9,
             10,
             11][interval]
        if self._note_layout.is_horizontal:
            steps = [1, interval]
            origin = [offset, 0]
        else:
            steps = [interval, 1]
            origin = [0, offset]
        return MelodicPattern(steps=steps, scale=notes, origin=origin, root_note=octave * 12, chromatic_mode=not self._note_layout.is_in_key)

    def _update_aftertouch(self):
        if self.is_enabled() and self._aftertouch_control != None:
            self._aftertouch_control.send_value('mono')