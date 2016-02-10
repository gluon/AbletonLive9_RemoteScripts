#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/TargetTrackComponent.py
from _Framework.SubjectSlot import Subject, subject_slot, subject_slot_group
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class TargetTrackComponent(ControlSurfaceComponent, Subject):
    """
    TargetTrackComponent handles determining the track to target for
    note mode-related functionality and notifying listeners.
    """
    __subject_events__ = ('target_track',)
    _target_track = None
    _armed_track_stack = []

    def __init__(self, *a, **k):
        super(TargetTrackComponent, self).__init__(*a, **k)
        self._on_tracks_changed.subject = self.song()
        self._on_tracks_changed()

    @property
    def target_track(self):
        return self._target_track

    def on_selected_track_changed(self):
        if not self._armed_track_stack:
            self._set_target_track()

    @subject_slot('tracks')
    def _on_tracks_changed(self):
        tracks = filter(lambda t: t.can_be_armed and t.has_midi_input, self.song().tracks)
        self._on_arm_changed.replace_subjects(tracks)
        self._on_frozen_state_changed.replace_subjects(tracks)
        self._refresh_armed_track_stack(tracks)

    @subject_slot_group('arm')
    def _on_arm_changed(self, track):
        if track in self._armed_track_stack:
            self._armed_track_stack.remove(track)
        if track.arm:
            self._armed_track_stack.append(track)
            self._set_target_track(track)
        else:
            self._set_target_track()

    @subject_slot_group('is_frozen')
    def _on_frozen_state_changed(self, track):
        if track in self._armed_track_stack:
            self._armed_track_stack.remove(track)
        if track == self._target_track:
            self._set_target_track()

    def _set_target_track(self, target = None):
        new_target = self._target_track
        if target is None:
            if self._armed_track_stack:
                new_target = self._armed_track_stack[-1]
            else:
                new_target = self.song().view.selected_track
        else:
            new_target = target
        if self._target_track != new_target:
            self._target_track = new_target
        self.notify_target_track()

    def _refresh_armed_track_stack(self, all_tracks):
        for track in self._armed_track_stack:
            if track not in all_tracks:
                self._armed_track_stack.remove(track)

        for track in all_tracks:
            if track.arm and track not in self._armed_track_stack:
                self._armed_track_stack.append(track)

        self._set_target_track()