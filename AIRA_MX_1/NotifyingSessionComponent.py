#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AIRA_MX_1/NotifyingSessionComponent.py
from itertools import count, izip_longest
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.SessionComponent import SessionComponent, SceneComponent

class SpecialSceneComponent(SceneComponent):
    """
    Special scene class that indicates whether any clips are
    playing/triggered on the scene.
    """

    def __init__(self, *a, **k):
        super(SpecialSceneComponent, self).__init__(*a, **k)
        self._playing_value = 127
        self._scene_index = 0

    def scene_name(self):
        if self._scene and self._scene.name:
            return self._scene.name

    def set_playing_value(self, value):
        self._playing_value = value

    def set_scene(self, scene):
        if scene != self._scene or type(self._scene) != type(scene):
            self._scene = scene
            self._on_is_triggered_changed.subject = scene
            self._on_scene_color_changed.subject = scene
            if self._scene:
                self._scene_index = list(self.song().scenes).index(self._scene)
            self.update()

    def update_light(self):
        self._update_launch_button()

    def _update_launch_button(self):
        if self.is_enabled() and self._launch_button is not None:
            value_to_send = self._no_scene_value
            if self._scene:
                if self._has_fired_slots():
                    value_to_send = self._triggered_value
                elif self._has_playing_slots():
                    value_to_send = self._playing_value
                else:
                    value_to_send = self._scene_value
            if value_to_send is None:
                self._launch_button.turn_off()
            else:
                self._launch_button.set_light(value_to_send)

    def _has_fired_slots(self):
        for track in self.song().tracks:
            if track.fired_slot_index == self._scene_index:
                return True

        return False

    def _has_playing_slots(self):
        for track in self.song().tracks:
            if track.playing_slot_index == self._scene_index:
                return True

        return False


class NotifyingSessionComponent(SessionComponent):
    """
    Special session class that uses the status bar to display
    the scene name or number being controlled.
    """
    scene_component_type = SpecialSceneComponent

    def __init__(self, *a, **k):
        super(NotifyingSessionComponent, self).__init__(*a, **k)
        self._last_scene_offset = self._scene_offset
        self._on_offset_changed.subject = self

    def set_clip_launch_buttons(self, buttons):
        first_scene = self.scene(0)
        for track_index, button in izip_longest(xrange(self._num_tracks), buttons or []):
            slot = first_scene.clip_slot(track_index)
            slot.set_launch_button(button)

    def _enable_skinning(self):
        super(NotifyingSessionComponent, self)._enable_skinning()
        for scene_index in xrange(self._num_scenes):
            scene = self.scene(scene_index)
            scene.set_playing_value('Session.ScenePlaying')

    def _reassign_tracks(self):
        tracks_to_use = self.song().tracks
        self._on_fired_slot_index_changed.replace_subjects(tracks_to_use, count())
        self._on_playing_slot_index_changed.replace_subjects(tracks_to_use, count())
        self._update_stop_track_clip_buttons()
        self._update_scene_launch_buttons()

    @subject_slot_group('fired_slot_index')
    def _on_fired_slot_index_changed(self, track_index):
        super(NotifyingSessionComponent, self)._on_fired_slot_index_changed(track_index)
        self._update_scene_launch_buttons()

    @subject_slot_group('playing_slot_index')
    def _on_playing_slot_index_changed(self, track_index):
        super(NotifyingSessionComponent, self)._on_playing_slot_index_changed(track_index)
        self._update_scene_launch_buttons()

    def _update_scene_launch_buttons(self):
        for scene in self._scenes:
            scene.update_light()

    @subject_slot('offset')
    def _on_offset_changed(self):
        if self._last_scene_offset != self._scene_offset:
            name = self._scenes[0].scene_name()
            if not name:
                name = self._scene_offset + 1
            self._show_msg_callback('Controlling Scene %s' % name)
            self._last_scene_offset = self._scene_offset