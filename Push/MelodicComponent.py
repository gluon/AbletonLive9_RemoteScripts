#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/MelodicComponent.py
from __future__ import with_statement
from _Framework.Util import forward_property, find_if
from _Framework.SubjectSlot import subject_slot
from _Framework.ModesComponent import ModesComponent, LayerMode
from MessageBoxComponent import Messenger
from MatrixMaps import FEEDBACK_CHANNELS, NON_FEEDBACK_CHANNEL
from InstrumentComponent import InstrumentComponent
from NoteEditorComponent import NoteEditorComponent
from PlayheadComponent import PlayheadComponent
from MelodicPattern import pitch_index_to_string
from LoopSelectorComponent import LoopSelectorComponent
from NoteEditorPaginator import NoteEditorPaginator
NUM_NOTE_EDITORS = 7

class MelodicComponent(ModesComponent, Messenger):

    def __init__(self, clip_creator = None, parameter_provider = None, grid_resolution = None, note_editor_settings = None, skin = None, instrument_play_layer = None, instrument_sequence_layer = None, layer = None, *a, **k):
        super(MelodicComponent, self).__init__(*a, **k)
        self._matrices = None
        self._grid_resolution = grid_resolution
        self._instrument = self.register_component(InstrumentComponent())
        self._note_editors = self.register_components(*[ NoteEditorComponent(settings_mode=note_editor_settings, clip_creator=clip_creator, grid_resolution=self._grid_resolution, is_enabled=False) for _ in xrange(NUM_NOTE_EDITORS) ])
        self._paginator = NoteEditorPaginator(self._note_editors)
        self._loop_selector = self.register_component(LoopSelectorComponent(clip_creator=clip_creator, paginator=self._paginator, is_enabled=False))
        self._playhead = None
        self._playhead_component = self.register_component(PlayheadComponent(grid_resolution=grid_resolution, paginator=self._paginator, follower=self._loop_selector, is_enabled=False))
        self.add_mode('play', LayerMode(self._instrument, instrument_play_layer))
        self.add_mode('sequence', [LayerMode(self._instrument, instrument_sequence_layer),
         self._loop_selector,
         note_editor_settings,
         LayerMode(self, layer),
         self._playhead_component] + self._note_editors)
        self.selected_mode = 'play'
        scales = self._instrument.scales
        self._on_detail_clip_changed.subject = self.song().view
        self._on_scales_changed.subject = scales
        self._on_scales_preset_changed.subject = scales._presets
        self._on_notes_changed.subject = self._instrument
        self._on_selected_mode_changed.subject = self
        self._on_detail_clip_changed()
        self._update_note_editors()
        self._skin = skin
        self._playhead_color = 'Melodic.Playhead'
        self._update_playhead_color()

    scales_menu = forward_property('_instrument')('scales_menu')
    scales = forward_property('_instrument')('scales')

    def set_playhead(self, playhead):
        self._playhead = playhead
        self._playhead_component.set_playhead(playhead)
        self._update_playhead_color()

    @forward_property('_loop_selector')
    def set_loop_selector_matrix(self, matrix):
        pass

    @forward_property('_loop_selector')
    def set_short_loop_selector_matrix(self, matrix):
        pass

    next_loop_page_button = forward_property('_loop_selector')('next_page_button')
    prev_loop_page_button = forward_property('_loop_selector')('prev_page_button')

    def set_note_editor_matrices(self, matrices):
        raise not matrices or len(matrices) <= NUM_NOTE_EDITORS or AssertionError
        self._matrices = matrices
        for editor, matrix in map(None, self._note_editors, matrices or []):
            if editor:
                editor.set_button_matrix(matrix)

        self._update_matrix_channels_for_playhead()

    def _get_playhead_color(self):
        self._playhead_color

    def _set_playhead_color(self, value):
        self._playhead_color = 'Melodic.' + value
        self._update_playhead_color()

    playhead_color = property(_get_playhead_color, _set_playhead_color)

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        if self.is_enabled():
            clip = self.song().view.detail_clip
            clip = clip if self.is_enabled() and clip and clip.is_midi_clip else None
            for note_editor in self._note_editors:
                note_editor.set_detail_clip(clip)

            self._loop_selector.set_detail_clip(clip)
            self._playhead_component.set_clip(clip)
            self._instrument.set_detail_clip(clip)

    def _set_full_velocity(self, enable):
        for note_editor in self._note_editors:
            note_editor.full_velocity = enable

    def _get_full_velocity(self):
        self._note_editors[0].full_velocity

    full_velocity = property(_get_full_velocity, _set_full_velocity)

    def set_quantization_buttons(self, buttons):
        self._grid_resolution.set_buttons(buttons)

    def set_mute_button(self, button):
        for e in self._note_editors:
            e.set_mute_button(button)

    @subject_slot('selected_mode')
    def _on_selected_mode_changed(self, mode):
        self._show_notes_information(mode)

    @subject_slot('position')
    def _on_notes_changed(self, *args):
        self._update_note_editors()
        self._show_notes_information()

    @subject_slot('selected_mode')
    def _on_scales_preset_changed(self, mode):
        self._update_note_editors()

    @subject_slot('scales_changed')
    def _on_scales_changed(self):
        self._update_note_editors()

    def _update_note_editors(self, *a):
        for row, note_editor in enumerate(self._note_editors):
            note_info = self._instrument.pattern[row]
            note_editor.background_color = 'NoteEditor.' + note_info.color
            note_editor.editing_note = note_info.index

        self._update_matrix_channels_for_playhead()

    def _update_matrix_channels_for_playhead(self):
        if self.is_enabled() and self._matrices != None:
            pattern = self._instrument.pattern
            for matrix, (y, _) in self._matrices.iterbuttons():
                if matrix:
                    for x, button in enumerate(matrix):
                        if button:
                            if pattern[y].index != None:
                                button.set_identifier(x)
                                button.set_channel(FEEDBACK_CHANNELS[y])
                            else:
                                button.set_identifier(button._original_identifier)
                                button.set_channel(NON_FEEDBACK_CHANNEL)

    def _update_playhead_color(self):
        if self.is_enabled() and self._skin and self._playhead:
            self._playhead.velocity = int(self._skin[self._playhead_color])

    def update(self):
        super(MelodicComponent, self).update()
        self._on_detail_clip_changed()
        self._update_playhead_color()

    def _show_notes_information(self, mode = None):
        if self.is_enabled():
            if mode is None:
                mode = self.selected_mode
            if mode == 'sequence':
                message = 'Sequence %s to %s'
                first = find_if(lambda editor: editor.editing_note != None, self._note_editors)
                last = find_if(lambda editor: editor.editing_note != None, reversed(self._note_editors))
                start_note = first.editing_note if first != None else None
                end_note = last.editing_note if last != None else None
            else:
                message = 'Play %s to %s'
                start_note = self._instrument._pattern.note(0, 0).index
                end_note = self._instrument._pattern.note(7, 7).index
            self.show_notification(message % (pitch_index_to_string(start_note), pitch_index_to_string(end_note)))