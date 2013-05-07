#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/StepSeqComponent.py
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import forward_property
from DrumGroupComponent import DrumGroupComponent
from NoteEditorComponent import NoteEditorComponent
from LoopSelectorComponent import LoopSelectorComponent

class StepSeqComponent(CompoundComponent):
    """ Step Sequencer Component """

    def __init__(self, clip_creator = None, playhead = None, skin = None, *a, **k):
        super(StepSeqComponent, self).__init__(*a, **k)
        raise clip_creator or AssertionError
        raise playhead or AssertionError
        raise skin or AssertionError
        self._skin = skin
        self._playhead = playhead
        self._note_editor, self._loop_selector, self._big_loop_selector, self._drum_group = self.register_components(NoteEditorComponent(clip_creator=clip_creator, playhead=playhead), LoopSelectorComponent(clip_creator=clip_creator), LoopSelectorComponent(clip_creator=clip_creator, measure_length=2.0), DrumGroupComponent())
        self._big_loop_selector.set_enabled(False)
        self._big_loop_selector.set_paginator(self._note_editor)
        self._loop_selector.set_paginator(self._note_editor)
        self._shift_button = None
        self._delete_button = None
        self._mute_button = None
        self._solo_button = None
        self._note_editor_matrix = None
        self._on_pressed_pads_changed.subject = self._drum_group
        self._on_detail_clip_changed.subject = self.song().view
        self._on_detail_clip_changed()

    @forward_property('_note_editor')
    def note_settings_layer(self):
        pass

    def set_drum_group_device(self, drum_group_device):
        raise not drum_group_device or drum_group_device.can_have_drum_pads or AssertionError
        self._drum_group.set_drum_group_device(drum_group_device)
        self._on_selected_drum_pad_changed.subject = drum_group_device.view if drum_group_device else None
        self._on_selected_drum_pad_changed()

    def set_touch_strip(self, touch_strip):
        self._drum_group.set_touch_strip(touch_strip)

    def set_quantize_button(self, button):
        self._drum_group.set_quantize_button(button)

    def set_select_button(self, button):
        self._drum_group.set_select_button(button)
        self._loop_selector.set_select_button(button)

    def set_mute_button(self, button):
        self._drum_group.set_mute_button(button)
        self._note_editor.set_mute_button(button)
        self._mute_button = button

    def set_solo_button(self, button):
        self._drum_group.set_solo_button(button)
        self._solo_button = button

    def set_shift_button(self, button):
        self._big_loop_selector.set_select_button(button)
        self._drum_group.set_shift_button(button)
        self._shift_button = button
        self._on_shift_value.subject = button

    def set_delete_button(self, button):
        self._delete_button = button

    def set_loop_selector_matrix(self, matrix):
        self._loop_selector.set_loop_selector_matrix(matrix)

    def set_follow_button(self, button):
        self._loop_selector.set_follow_button(button)
        self._big_loop_selector.set_follow_button(button)

    def set_drum_matrix(self, matrix):
        self._drum_group.set_drum_matrix(matrix)

    def set_drum_bank_up_button(self, button):
        self._drum_group.set_scroll_up_button(button)

    def set_drum_bank_down_button(self, button):
        self._drum_group.set_scroll_down_button(button)

    def set_button_matrix(self, matrix):
        self._note_editor_matrix = matrix
        self._update_note_editor_matrix()

    def set_quantization_buttons(self, buttons):
        self._note_editor.set_quantization_buttons(buttons)

    def set_velocity_control(self, control):
        self._note_editor.set_velocity_control(control)

    def set_length_control(self, control):
        self._note_editor.set_length_control(control)

    def set_nudge_control(self, control):
        self._note_editor.set_nudge_control(control)

    def set_full_velocity(self, active):
        self._note_editor.set_full_velocity(active)

    def update(self):
        if self.is_enabled():
            self._playhead.velocity = int(self._skin['NoteEditor.Playhead'])

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        clip = self.song().view.detail_clip
        clip = clip if clip and clip.is_midi_clip else None
        self._note_editor.set_detail_clip(clip)
        self._loop_selector.set_detail_clip(clip)
        self._big_loop_selector.set_detail_clip(clip)

    @subject_slot('value')
    def _on_shift_value(self, value):
        if self.is_enabled():
            self._update_note_editor_matrix(enable_big_loop_selector=value and not self._loop_selector.is_following)

    @subject_slot('selected_drum_pad')
    def _on_selected_drum_pad_changed(self):
        drum_group_view = self._on_selected_drum_pad_changed.subject
        if drum_group_view:
            selected_drum_pad = drum_group_view.selected_drum_pad
            if selected_drum_pad:
                self._note_editor.set_editing_note(selected_drum_pad.note)

    @subject_slot('pressed_pads')
    def _on_pressed_pads_changed(self):
        self._note_editor.modify_all_notes_enabled = bool(self._drum_group.pressed_pads)

    def _update_note_editor_matrix(self, enable_big_loop_selector = False):
        if enable_big_loop_selector:
            self._note_editor.set_enabled(False)
            self._note_editor.set_button_matrix(None)
            self._big_loop_selector.set_enabled(True)
            self._big_loop_selector.set_loop_selector_matrix(self._note_editor_matrix)
        else:
            self._big_loop_selector.set_enabled(False)
            self._big_loop_selector.set_loop_selector_matrix(None)
            self._note_editor.set_enabled(True)
            self._note_editor.set_button_matrix(self._note_editor_matrix)