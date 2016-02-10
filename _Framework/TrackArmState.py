#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/TrackArmState.py
from __future__ import absolute_import
from .SubjectSlot import Subject, subject_slot, SlotManager

class TrackArmState(Subject, SlotManager):
    __subject_events__ = ('arm',)

    def __init__(self, track = None, *a, **k):
        super(TrackArmState, self).__init__(*a, **k)
        self.set_track(track)

    def set_track(self, track):
        self._track = track
        self._arm = track and track.can_be_armed and (track.arm or track.implicit_arm)
        subject = track if track and track.can_be_armed else None
        self._on_explicit_arm_changed.subject = subject
        self._on_implicit_arm_changed.subject = subject

    @subject_slot('arm')
    def _on_explicit_arm_changed(self):
        self._on_arm_changed()

    @subject_slot('implicit_arm')
    def _on_implicit_arm_changed(self):
        self._on_arm_changed()

    def _on_arm_changed(self):
        new_state = self._track.arm or self._track.implicit_arm
        if self._arm != new_state:
            self._arm = new_state
            self.notify_arm()

    def _get_arm(self):
        if self._track.can_be_armed:
            return self._arm
        return False

    def _set_arm(self, new_state):
        if self._track.can_be_armed:
            self._track.arm = new_state
            if not new_state:
                self._track.implicit_arm = False
        self._arm = new_state

    arm = property(_get_arm, _set_arm)