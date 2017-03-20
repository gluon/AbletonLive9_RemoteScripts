# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/special_session_component.py
# Compiled at: 2016-06-08 13:13:04
from __future__ import absolute_import, print_function
import Live
from ableton.v2.base import const, depends, forward_property, inject, listens, liveobj_valid
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.components import ClipSlotComponent, SceneComponent, SessionComponent
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.mode import EnablingModesComponent
from pushbase.touch_strip_element import TouchStripStates, TouchStripModes
from .actions import clip_name_from_clip_slot
from .message_box_component import Messenger
from .consts import MessageBoxText

class ClipSlotCopyHandler(Messenger):

    def __init__(self, *a, **k):
        super(ClipSlotCopyHandler, self).__init__(*a, **k)
        self._is_copying = False
        self._source_clip_slot = None
        self._last_shown_notification_ref = const(None)
        return

    @property
    def is_copying(self):
        return self._is_copying

    def duplicate(self, clip_slot):
        if self._is_copying:
            self._finish_copying(clip_slot)
        else:
            self._start_copying(clip_slot)

    def stop_copying(self):
        self._reset_copying_state()
        notification_ref = self._last_shown_notification_ref()
        if notification_ref is not None:
            notification_ref.hide()
        return

    def _show_notification(self, notification):
        self._last_shown_notification_ref = self.show_notification(notification)

    def _start_copying(self, source_clip_slot):
        if not source_clip_slot.is_group_slot:
            if liveobj_valid(source_clip_slot.clip):
                if not source_clip_slot.clip.is_recording:
                    self._is_copying = True
                    self._source_clip_slot = source_clip_slot
                    clip_name = clip_name_from_clip_slot(source_clip_slot)
                    self._show_notification((MessageBoxText.COPIED_CLIP, clip_name))
                else:
                    self._show_notification(MessageBoxText.CANNOT_COPY_RECORDING_CLIP)
            else:
                self._show_notification(MessageBoxText.CANNOT_COPY_EMPTY_CLIP)
        else:
            self._show_notification(MessageBoxText.CANNOT_COPY_GROUP_SLOT)

    def _finish_copying(self, target_clip_slot):
        if not target_clip_slot.is_group_slot:
            source_is_audio = self._source_clip_slot.clip.is_audio_clip
            target_track = target_clip_slot.canonical_parent
            if source_is_audio:
                if target_track.has_audio_input:
                    self._perform_copy(target_clip_slot)
                else:
                    self._show_notification(MessageBoxText.CANNOT_COPY_AUDIO_CLIP_TO_MIDI_TRACK)
            elif not target_track.has_audio_input:
                self._perform_copy(target_clip_slot)
            else:
                self._show_notification(MessageBoxText.CANNOT_COPY_MIDI_CLIP_TO_AUDIO_TRACK)
        else:
            self._show_notification(MessageBoxText.CANNOT_PASTE_INTO_GROUP_SLOT)

    def _perform_copy(self, target_clip_slot):
        self._source_clip_slot.duplicate_clip_to(target_clip_slot)
        self._on_duplicated(self._source_clip_slot, target_clip_slot)
        self._reset_copying_state()

    def _reset_copying_state(self):
        self._source_clip_slot = None
        self._is_copying = False
        return

    def _on_duplicated(self, source_clip_slot, target_clip_slot):
        clip_name = clip_name_from_clip_slot(source_clip_slot)
        track_name = target_clip_slot.canonical_parent.name
        self._show_notification((
         MessageBoxText.PASTED_CLIP, clip_name, track_name))


class DuplicateSceneComponent(Component, Messenger):

    def __init__(self, session_ring=None, *a, **k):
        super(DuplicateSceneComponent, self).__init__(*a, **k)
        assert session_ring is not None
        self._session_ring = session_ring
        self._scene_buttons = None
        return

    def set_scene_buttons(self, buttons):
        self._scene_buttons = buttons
        self._on_scene_value.subject = buttons

    @listens('value')
    def _on_scene_value(self, value, index, _, is_momentary):
        if self.is_enabled() and (value or not is_momentary):
            try:
                self.song.duplicate_scene(self._session_ring.scene_offset + index)
                self.show_notification(MessageBoxText.DUPLICATE_SCENE % self.song.view.selected_scene.name)
            except Live.Base.LimitationError:
                self.expect_dialog(MessageBoxText.SCENE_LIMIT_REACHED)
            except RuntimeError:
                self.expect_dialog(MessageBoxText.SCENE_DUPLICATION_FAILED)
            except IndexError:
                pass


class SpecialClipSlotComponent(ClipSlotComponent, Messenger):

    @depends(copy_handler=const(None), fixed_length_recording=const(None))
    def __init__(self, copy_handler=None, fixed_length_recording=None, *a, **k):
        assert copy_handler is not None
        assert fixed_length_recording is not None
        super(SpecialClipSlotComponent, self).__init__(*a, **k)
        self._copy_handler = copy_handler
        self._fixed_length_recording = fixed_length_recording
        return

    def _do_delete_clip(self):
        if self._clip_slot and self._clip_slot.has_clip:
            clip_name = self._clip_slot.clip.name
            self._clip_slot.delete_clip()
            self.show_notification(MessageBoxText.DELETE_CLIP % clip_name)

    def _do_select_clip(self, clip_slot):
        if liveobj_valid(self._clip_slot):
            if self.song.view.highlighted_clip_slot != self._clip_slot:
                self.song.view.highlighted_clip_slot = self._clip_slot

    def _do_duplicate_clip(self):
        self._copy_handler.duplicate(self._clip_slot)

    def _on_clip_duplicated(self, source_clip, destination_clip):
        slot_name = source_clip.name
        self.show_notification(MessageBoxText.DUPLICATE_CLIP % slot_name)

    def _clip_is_recording(self):
        return self.has_clip() and self._clip_slot.clip.is_recording

    def _do_launch_clip(self, fire_state):
        should_start_fixed_length_recording = self._fixed_length_recording.should_start_fixed_length_recording(self._clip_slot)
        clip_is_recording = self._clip_is_recording()
        if fire_state and not should_start_fixed_length_recording and not clip_is_recording or not fire_state:
            super(SpecialClipSlotComponent, self)._do_launch_clip(fire_state)
        elif should_start_fixed_length_recording:
            track = self._clip_slot.canonical_parent
            self._fixed_length_recording.start_recording_in_slot(track, list(track.clip_slots).index(self._clip_slot))
        elif clip_is_recording:
            self._fixed_length_recording.stop_recording(self._clip_slot.clip)


class SpecialSceneComponent(SceneComponent, Messenger):
    clip_slot_component_type = SpecialClipSlotComponent

    def _do_delete_scene(self, scene):
        try:
            if self._scene:
                song = self.song
                name = self._scene.name
                song.delete_scene(list(song.scenes).index(self._scene))
                self.show_notification(MessageBoxText.DELETE_SCENE % name)
        except RuntimeError:
            pass


class SpecialSessionComponent(SessionComponent):
    """
    Special session subclass that handles ConfigurableButtons
    and has a button to fire the selected clip slot.
    """
    _session_component_ends_initialisation = False
    scene_component_type = SpecialSceneComponent
    duplicate_button = ButtonControl()

    def __init__(self, clip_slot_copy_handler=None, fixed_length_recording=None, *a, **k):
        self._clip_copy_handler = clip_slot_copy_handler or ClipSlotCopyHandler()
        self._fixed_length_recording = fixed_length_recording
        with inject(copy_handler=const(self._clip_copy_handler), fixed_length_recording=const(self._fixed_length_recording)).everywhere():
            super(SpecialSessionComponent, self).__init__(*a, **k)
        self._slot_launch_button = None
        self._duplicate_button = None
        self._duplicate = self.register_component(DuplicateSceneComponent(self._session_ring))
        self._duplicate_enabler = self.register_component(EnablingModesComponent(component=self._duplicate))
        self._end_initialisation()
        return

    duplicate_layer = forward_property('_duplicate')('layer')

    @duplicate_button.pressed
    def duplicate_button(self, button):
        self._duplicate_enabler.selected_mode = 'enabled'

    @duplicate_button.released
    def duplicate_button(self, button):
        self._duplicate_enabler.selected_mode = 'disabled'
        self._clip_copy_handler.stop_copying()

    def set_slot_launch_button(self, button):
        self._slot_launch_button = button
        self._on_slot_launch_value.subject = button

    def set_clip_launch_buttons(self, buttons):
        if buttons:
            buttons.reset()
        super(SpecialSessionComponent, self).set_clip_launch_buttons(buttons)

    def set_touch_strip(self, touch_strip):
        if touch_strip:
            touch_strip.set_mode(TouchStripModes.CUSTOM_FREE)
            touch_strip.send_state([ TouchStripStates.STATE_OFF for _ in xrange(touch_strip.state_count)
                                   ])
        self._on_touch_strip_value.subject = touch_strip

    @listens('value')
    def _on_touch_strip_value(self, value):
        pass

    @listens('value')
    def _on_slot_launch_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._slot_launch_button.is_momentary():
                if liveobj_valid(self.song.view.highlighted_clip_slot):
                    self.song.view.highlighted_clip_slot.fire()
                self._slot_launch_button.turn_on()
            else:
                self._slot_launch_button.turn_off()