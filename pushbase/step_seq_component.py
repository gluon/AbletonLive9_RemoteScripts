# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/step_seq_component.py
# Compiled at: 2016-11-16 18:13:21
from __future__ import absolute_import, print_function
from itertools import chain, starmap
from ableton.v2.base import forward_property, listens, liveobj_valid
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.elements import to_midi_value
from .loop_selector_component import LoopSelectorComponent
from .playhead_component import PlayheadComponent
from .note_editor_paginator import NoteEditorPaginator
from .matrix_maps import PLAYHEAD_FEEDBACK_CHANNELS
from .step_duplicator import StepDuplicatorComponent

class StepSeqComponent(CompoundComponent):
    """
    This component represents one of the sequencing mechanisms for Push, which has one
    NoteEditorComponent associated with a single pitch. The component mostly manages
    distributing control elements to sub-components, which then provide the logic for
    this layout.
    """

    def __init__(self, clip_creator=None, skin=None, grid_resolution=None, note_editor_component=None, instrument_component=None, *a, **k):
        super(StepSeqComponent, self).__init__(*a, **k)
        assert clip_creator is not None
        assert skin is not None
        assert instrument_component is not None
        assert note_editor_component is not None
        self._grid_resolution = grid_resolution
        self._note_editor, self._loop_selector = self.register_components(note_editor_component, LoopSelectorComponent(clip_creator=clip_creator, default_size=16))
        self._instrument = instrument_component
        self._paginator = NoteEditorPaginator([self._note_editor])
        self._step_duplicator = self.register_component(StepDuplicatorComponent())
        self._note_editor.set_step_duplicator(self._step_duplicator)
        self._loop_selector.set_paginator(self._paginator)
        self._on_pressed_pads_changed.subject = self._instrument
        self._on_selected_note_changed.subject = self._instrument
        self._on_detail_clip_changed.subject = self.song.view
        self._detail_clip = None
        self._playhead = None
        self._playhead_component = self.register_component(PlayheadComponent(grid_resolution=grid_resolution, paginator=self._paginator, follower=self._loop_selector, notes=chain(*starmap(range, (
         (92, 100), (84, 92),
         (76, 84), (68, 76)))), triplet_notes=chain(*starmap(range, (
         (92, 98), (84, 90),
         (76, 82), (68, 74)))), feedback_channels=PLAYHEAD_FEEDBACK_CHANNELS))
        self._skin = skin
        self._playhead_color = 'NoteEditor.Playhead'
        return

    def set_playhead(self, playhead):
        self._playhead = playhead
        self._playhead_component.set_playhead(playhead)
        self._update_playhead_color()

    def _get_playhead_color(self):
        return self._playhead_color

    def _set_playhead_color(self, value):
        self._playhead_color = 'NoteEditor.' + value
        self._update_playhead_color()

    playhead_color = property(_get_playhead_color, _set_playhead_color)

    def _is_triplet_quantization(self):
        return self._grid_resolution.clip_grid[1]

    def _update_playhead_color(self):
        if self.is_enabled() and self._skin and self._playhead:
            self._playhead.velocity = to_midi_value(self._skin[self._playhead_color])

    def set_full_velocity_button(self, button):
        self._note_editor.set_full_velocity_button(button)

    def set_select_button(self, button):
        self._instrument.set_select_button(button)
        self._loop_selector.set_select_button(button)

    def set_mute_button(self, button):
        self._instrument.set_mute_button(button)
        self._note_editor.mute_button.set_control_element(button)

    def set_solo_button(self, button):
        self._instrument.set_solo_button(button)

    def set_delete_button(self, button):
        self._instrument.set_delete_button(button)

    def set_next_loop_page_button(self, button):
        self._loop_selector.next_page_button.set_control_element(button)

    def set_prev_loop_page_button(self, button):
        self._loop_selector.prev_page_button.set_control_element(button)

    def set_loop_selector_matrix(self, matrix):
        self._loop_selector.set_loop_selector_matrix(matrix)

    def set_short_loop_selector_matrix(self, matrix):
        self._loop_selector.set_short_loop_selector_matrix(matrix)

    def set_follow_button(self, button):
        self._loop_selector.set_follow_button(button)

    def set_duplicate_button(self, button):
        self._step_duplicator.button.set_control_element(button)

    def set_button_matrix(self, matrix):
        self._note_editor.set_matrix(matrix)

    def set_quantization_buttons(self, buttons):
        self._grid_resolution.set_buttons(buttons)

    def set_velocity_control(self, control):
        self._note_editor.set_velocity_control(control)

    def set_length_control(self, control):
        self._note_editor.set_length_control(control)

    def set_nudge_control(self, control):
        self._note_editor.set_nudge_control(control)

    @forward_property('_note_editor')
    def full_velocity(self):
        pass

    def update(self):
        super(StepSeqComponent, self).update()
        self._on_detail_clip_changed()
        self._update_playhead_color()

    @listens('detail_clip')
    def _on_detail_clip_changed(self):
        clip = self.song.view.detail_clip
        clip = clip if liveobj_valid(clip) and clip.is_midi_clip else None
        self._detail_clip = clip
        self._note_editor.set_detail_clip(clip)
        self._loop_selector.set_detail_clip(clip)
        self._playhead_component.set_clip(self._detail_clip)
        return

    @listens('selected_note')
    def _on_selected_note_changed(self):
        selected_note = self._instrument.selected_note
        if selected_note >= 0:
            self._note_editor.editing_note = selected_note

    @listens('pressed_pads')
    def _on_pressed_pads_changed(self):
        self._note_editor.modify_all_notes_enabled = bool(self._instrument.pressed_pads)