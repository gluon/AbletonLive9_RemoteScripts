# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/selected_track_parameter_provider.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from ableton.v2.base import depends, listens
from .parameter_provider import ParameterProvider
TRACK_PARAMETER_NAMES = ('Volume', 'Pan', 'Send A', 'Send B', 'Send C', 'Send D', 'Send E',
                         'Send F', 'Send G', 'Send H', 'Send I', 'Send J', 'Send K',
                         'Send L')

def toggle_arm(track_to_arm, song, exclusive=False):
    if track_to_arm.can_be_armed:
        track_to_arm.arm = not track_to_arm.arm
        if exclusive and (track_to_arm.implicit_arm or track_to_arm.arm):
            for track in song.tracks:
                if track.can_be_armed and track != track_to_arm:
                    track.arm = False


class SelectedTrackParameterProvider(ParameterProvider):

    @depends(song=None)
    def __init__(self, song=None, *a, **k):
        super(SelectedTrackParameterProvider, self).__init__(*a, **k)
        self._track = None
        self._on_selected_track.subject = song.view
        self._on_visible_tracks.subject = song
        self._on_selected_track()
        return

    @property
    def parameters(self):
        if self._track:
            params = [
             self._track.mixer_device.volume,
             self._track.mixer_device.panning] + list(self._track.mixer_device.sends)
            return [ self._create_parameter_info(p, n) for n, p in zip(TRACK_PARAMETER_NAMES, params)
                   ]
        return []

    def _create_parameter_info(self, parameter, name):
        raise NotImplementedError()

    @listens('visible_tracks')
    def _on_visible_tracks(self):
        self.notify_parameters()

    @listens('selected_track')
    def _on_selected_track(self):
        self._track = self._on_selected_track.subject.selected_track
        self.notify_parameters()