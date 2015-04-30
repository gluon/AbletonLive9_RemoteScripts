#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_Serato/SpecialClipSlotComponent.py
import Live
import libInterprocessCommsAPIPython
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot
from PySCAClipControl import *

class SpecialClipSlotComponent(ClipSlotComponent):

    def __init__(self):
        ClipSlotComponent.__init__(self)
        self._scene_index = -1
        self._track_index = -1
        self._serato_interface = None

    def disconnect(self):
        if self._clip_slot != None and self.has_clip():
            self._clip_slot.clip.remove_name_listener(self._on_name_changed)
            self._clip_slot.clip.remove_color_listener(self._on_color_changed)
        ClipSlotComponent.disconnect(self)
        self._on_load_state_changed()
        self._on_name_changed()
        self._on_color_changed()
        self._serato_interface = None

    def set_serato_interface(self, serato_interface):
        if not serato_interface != None:
            raise AssertionError
            self._serato_interface = serato_interface
            self._clip_slot != None and self.update()
        self._on_load_state_changed()
        self._on_name_changed()
        self._on_color_changed()
        self.update()

    def set_clip_slot(self, clip_slot):
        if self._clip_slot != None and self.has_clip():
            self._clip_slot.clip.remove_name_listener(self._on_name_changed)
            self._clip_slot.clip.remove_color_listener(self._on_color_changed)
        ClipSlotComponent.set_clip_slot(self, clip_slot)
        if self._clip_slot != None and self.has_clip():
            self._clip_slot.clip.add_name_listener(self._on_name_changed)
            self._clip_slot.clip.add_color_listener(self._on_color_changed)
        self._on_load_state_changed()
        self._on_name_changed()
        self._on_color_changed()
        self.update()

    def set_indexes(self, scene_index, track_index):
        raise scene_index >= 0 or AssertionError
        raise track_index >= 0 or AssertionError
        self._scene_index = scene_index
        self._track_index = track_index
        self._on_load_state_changed()
        self._on_name_changed()
        self._on_color_changed()
        self.update()

    def update(self):
        self._has_fired_slot = False
        if self._allow_updates:
            if self.is_enabled() and self._serato_interface != None:
                value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsStopped
                if self._clip_slot != None:
                    object_to_check = self._clip_slot
                    if self.has_clip():
                        object_to_check = self._clip_slot.clip
                    if object_to_check.is_triggered:
                        value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsQueued
                        if object_to_check.will_record_on_start:
                            value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsRecordingQueued
                    elif object_to_check.is_playing:
                        value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsPlaying
                        if object_to_check.is_recording:
                            value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsRecording
                if self._track_index > -1 and self._scene_index > -1:
                    self._serato_interface.PySCA_SetClipPlayState(self._track_index + 1, self._scene_index + 1, value_to_send)
        else:
            self._update_requests += 1

    @subject_slot('has_clip')
    def _on_clip_state_changed(self):
        if not self._clip_slot != None:
            raise AssertionError
            if self.has_clip():
                if not self._clip_slot.clip.name_has_listener(self._on_name_changed):
                    self._clip_slot.clip.add_name_listener(self._on_name_changed)
                if not self._clip_slot.clip.color_has_listener(self._on_color_changed):
                    self._clip_slot.clip.add_color_listener(self._on_color_changed)
                if not self._clip_slot.clip.playing_status_has_listener(self._on_playing_state_changed):
                    self._clip_slot.clip.add_playing_status_listener(self._on_playing_state_changed)
                self._clip_slot.clip.is_recording_has_listener(self._on_recording_state_changed) or self._clip_slot.clip.add_is_recording_listener(self._on_recording_state_changed)
        self._on_load_state_changed()
        self._on_color_changed()
        self._on_name_changed()
        self.update()

    def _on_name_changed(self):
        if self._serato_interface != None and -1 not in (self._track_index, self._scene_index):
            name = ''
            if self._clip_slot != None and self.has_clip():
                name = self._clip_slot.clip.name
            self._serato_interface.PySCA_SetClipLabel(self._track_index + 1, self._scene_index + 1, name)

    def _on_color_changed(self):
        if self._serato_interface != None and -1 not in (self._track_index, self._scene_index):
            if self._clip_slot != None and self.has_clip():
                self._serato_interface.PySCA_SetClipColor(self._track_index + 1, self._scene_index + 1, self._clip_slot.clip.color)

    def _on_load_state_changed(self):
        if self._serato_interface != None and -1 not in (self._track_index, self._scene_index):
            value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsEmpty
            if self._clip_slot != None and self.has_clip():
                value_to_send = libInterprocessCommsAPIPython.kAbletonClipIsLoaded
            self._serato_interface.PySCA_SetClipLoadState(self._track_index + 1, self._scene_index + 1, value_to_send)