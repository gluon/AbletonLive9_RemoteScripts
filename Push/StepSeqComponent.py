#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/StepSeqComponent.py
from __future__ import with_statement
import Live
from itertools import imap, chain, starmap
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot, Subject, subject_slot_group
from _Framework.Util import forward_property, find_if
from DrumGroupComponent import DrumGroupComponent
from NoteEditorComponent import NoteEditorComponent
from LoopSelectorComponent import LoopSelectorComponent
from PlayheadComponent import PlayheadComponent
from NoteEditorPaginator import NoteEditorPaginator

class DrumGroupFinderComponent(ControlSurfaceComponent, Subject):
    """
    Looks in the hierarchy of devices of the selected track, looking
    for the first available drum-rack (deep-first), updating as the
    device list changes.
    """
    __subject_events__ = ('drum_group',)
    _drum_group = None

    @property
    def drum_group(self):
        """
        The latest found drum rack.
        """
        return self._drum_group

    @property
    def root(self):
        """
        The currently observed track.
        """
        return self.song().view.selected_track

    @subject_slot_group('devices')
    def _on_devices_changed(self, chain):
        self.update()

    @subject_slot_group('chains')
    def _on_chains_changed(self, chain):
        self.update()

    def on_selected_track_changed(self):
        self.update()

    def update(self):
        super(DrumGroupFinderComponent, self).update()
        if self.is_enabled():
            self._update_listeners()
            self._update_drum_group()

    def _update_listeners(self):
        root = self.root
        devices = list(find_instrument_devices(root))
        chains = list(chain([root], *[ d.chains for d in devices ]))
        self._on_chains_changed.replace_subjects(devices)
        self._on_devices_changed.replace_subjects(chains)

    def _update_drum_group(self):
        drum_group = find_drum_group_device(self.root)
        if type(drum_group) != type(self._drum_group) or drum_group != self._drum_group:
            self._drum_group = drum_group
            self.notify_drum_group()


def find_instrument_devices(track_or_chain):
    """
    Returns a list with all instrument rack descendants from a track
    or chain.
    """
    instrument = find_if(lambda d: d.type == Live.Device.DeviceType.instrument, track_or_chain.devices)
    if instrument and not instrument.can_have_drum_pads:
        if instrument.can_have_chains:
            return chain([instrument], *imap(find_instrument_devices, instrument.chains))
    return []


def find_drum_group_device(track_or_chain):
    """
    Looks up recursively for a drum_group device in the track.
    """
    instrument = find_if(lambda d: d.type == Live.Device.DeviceType.instrument, track_or_chain.devices)
    if instrument:
        if instrument.can_have_drum_pads:
            return instrument
        elif instrument.can_have_chains:
            return find_if(bool, imap(find_drum_group_device, instrument.chains))


class StepSeqComponent(CompoundComponent):
    """ Step Sequencer Component """

    def __init__(self, clip_creator = None, skin = None, grid_resolution = None, note_editor_settings = None, *a, **k):
        super(StepSeqComponent, self).__init__(*a, **k)
        raise clip_creator or AssertionError
        if not skin:
            raise AssertionError
            self._grid_resolution = grid_resolution
            note_editor_settings and self.register_component(note_editor_settings)
        self._note_editor, self._loop_selector, self._big_loop_selector, self._drum_group = self.register_components(NoteEditorComponent(settings_mode=note_editor_settings, clip_creator=clip_creator, grid_resolution=self._grid_resolution), LoopSelectorComponent(clip_creator=clip_creator), LoopSelectorComponent(clip_creator=clip_creator, measure_length=2.0), DrumGroupComponent())
        self._paginator = NoteEditorPaginator([self._note_editor])
        self._big_loop_selector.set_enabled(False)
        self._big_loop_selector.set_paginator(self._paginator)
        self._loop_selector.set_paginator(self._paginator)
        self._shift_button = None
        self._delete_button = None
        self._mute_button = None
        self._solo_button = None
        self._note_editor_matrix = None
        self._on_pressed_pads_changed.subject = self._drum_group
        self._on_detail_clip_changed.subject = self.song().view
        self._detail_clip = None
        self._playhead = None
        self._playhead_component = self.register_component(PlayheadComponent(grid_resolution=grid_resolution, paginator=self._paginator, follower=self._loop_selector, notes=chain(*starmap(range, ((92, 100),
         (84, 92),
         (76, 84),
         (68, 76)))), triplet_notes=chain(*starmap(range, ((92, 98),
         (84, 90),
         (76, 82),
         (68, 74))))))
        self._skin = skin
        self._playhead_color = 'NoteEditor.Playhead'

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
            self._playhead.velocity = int(self._skin[self._playhead_color])

    def set_drum_group_device(self, drum_group_device):
        raise not drum_group_device or drum_group_device.can_have_drum_pads or AssertionError
        self._drum_group.set_drum_group_device(drum_group_device)
        self._on_selected_drum_pad_changed.subject = drum_group_device.view if drum_group_device else None
        self._on_selected_drum_pad_changed()

    def set_touch_strip(self, touch_strip):
        self._drum_group.set_page_strip(touch_strip)

    def set_detail_touch_strip(self, touch_strip):
        self._drum_group.set_scroll_strip(touch_strip)

    def set_quantize_button(self, button):
        self._drum_group.set_quantize_button(button)

    def set_full_velocity_button(self, button):
        self._note_editor.set_full_velocity_button(button)

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
        self._shift_button = button
        self._on_shift_value.subject = button

    def set_delete_button(self, button):
        self._delete_button = button
        self._drum_group.set_delete_button(button)

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
        self._big_loop_selector.set_follow_button(button)

    def set_drum_matrix(self, matrix):
        self._drum_group.set_drum_matrix(matrix)

    def set_drum_bank_up_button(self, button):
        self._drum_group.set_scroll_page_up_button(button)

    def set_drum_bank_down_button(self, button):
        self._drum_group.set_scroll_page_down_button(button)

    def set_drum_bank_detail_up_button(self, button):
        self._drum_group.set_scroll_up_button(button)

    def set_drum_bank_detail_down_button(self, button):
        self._drum_group.set_scroll_down_button(button)

    def set_button_matrix(self, matrix):
        self._note_editor_matrix = matrix
        self._update_note_editor_matrix()

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

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        clip = self.song().view.detail_clip
        clip = clip if self.is_enabled() and clip and clip.is_midi_clip else None
        self._detail_clip = clip
        self._note_editor.set_detail_clip(clip)
        self._loop_selector.set_detail_clip(clip)
        self._big_loop_selector.set_detail_clip(clip)
        self._playhead_component.set_clip(self._detail_clip)

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
                self._note_editor.editing_note = selected_drum_pad.note

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