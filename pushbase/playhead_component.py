# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/playhead_component.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base import listens, liveobj_valid
from ableton.v2.control_surface import Component

class PlayheadComponent(Component):
    """
    Updates the contents of the Live playhead object.
    """

    def __init__(self, paginator=None, grid_resolution=None, follower=None, notes=range(8), triplet_notes=range(6), feedback_channels=[], *a, **k):
        super(PlayheadComponent, self).__init__(*a, **k)
        self._playhead = None
        self._clip = None
        self._paginator = paginator
        self._grid_resolution = grid_resolution
        self._follower = follower
        self._notes = tuple(notes)
        self._triplet_notes = tuple(triplet_notes)
        self._feedback_channels = feedback_channels
        self._on_page_changed.subject = self._paginator
        self._on_grid_resolution_changed.subject = self._grid_resolution
        self._on_follower_is_following_changed.subject = self._follower
        return

    def set_playhead(self, playhead):
        self._playhead = playhead
        self.update()

    def set_clip(self, clip):
        self._clip = clip
        self._on_playing_status_changed.subject = clip
        self._on_song_is_playing_changed.subject = self.song if clip else None
        self.update()
        return

    @listens('page')
    def _on_page_changed(self):
        self.update()

    @listens('playing_status')
    def _on_playing_status_changed(self):
        self.update()

    @listens('is_playing')
    def _on_song_is_playing_changed(self):
        self.update()

    @listens('index')
    def _on_grid_resolution_changed(self):
        self.update()

    @listens('is_following')
    def _on_follower_is_following_changed(self, value):
        self.update()

    def update(self):
        super(PlayheadComponent, self).update()
        if self._playhead:
            clip = None
            if self.is_enabled() and self.song.is_playing and liveobj_valid(self._clip):
                if self._clip.is_arrangement_clip or self._clip.is_playing:
                    clip = self._clip
            self._playhead.clip = clip
            self._playhead.set_feedback_channels(self._feedback_channels)
            if clip:
                is_triplet = self._grid_resolution.clip_grid[1]
                notes = self._triplet_notes if is_triplet else self._notes
                self._playhead.notes = list(notes)
                self._playhead.wrap_around = self._follower.is_following and self._paginator.can_change_page
                self._playhead.start_time = self._paginator.page_length * self._paginator.page_index
                self._playhead.step_length = self._paginator.page_length / len(notes)
        return