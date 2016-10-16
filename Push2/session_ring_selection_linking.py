#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/session_ring_selection_linking.py
from __future__ import absolute_import, print_function
from ableton.v2.base.slot import SlotManager, listens
from ableton.v2.base.dependency import depends
from ableton.v2.base.util import index_if

class SessionRingSelectionLinking(SlotManager):

    @depends(song=None)
    def __init__(self, session_ring = None, selection_changed_notifier = None, song = None, *a, **k):
        super(SessionRingSelectionLinking, self).__init__(*a, **k)
        raise session_ring is not None or AssertionError
        raise selection_changed_notifier is not None or AssertionError
        raise song is not None or AssertionError
        self._session_ring = session_ring
        self._song = song
        self._on_selection_changed.subject = selection_changed_notifier

    @listens('selection_changed')
    def _on_selection_changed(self):
        if self._song.view.selected_track == self._song.master_track:
            return
        track_index = self._current_track_index()
        right_ring_index = self._session_ring.track_offset + self._session_ring.num_tracks - 1
        offset_left = track_index - self._session_ring.track_offset
        offset_right = track_index - right_ring_index
        adjustment = min(0, offset_left) + max(0, offset_right)
        new_track_offset = self._session_ring.track_offset + adjustment
        if new_track_offset != self._session_ring.track_offset:
            self._session_ring.set_offsets(new_track_offset, self._session_ring.scene_offset)

    def _current_track_index(self):
        current_track = self._session_ring.selected_item
        return index_if(lambda t: t == current_track, self._session_ring.tracks_to_use())