#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/selected_track_parameter_provider.py
from __future__ import absolute_import, print_function
from ableton.v2.base import depends, listens, SlotManager
from .special_chan_strip_component import TRACK_PARAMETER_NAMES
from .parameter_provider import ParameterProvider, generate_info

class SelectedTrackParameterProvider(ParameterProvider, SlotManager):

    @depends(song=None)
    def __init__(self, song = None, *a, **k):
        super(SelectedTrackParameterProvider, self).__init__(*a, **k)
        self._track = None
        self._on_selected_track.subject = song.view
        self._on_visible_tracks.subject = song
        self._on_selected_track()

    @property
    def parameters(self):
        if self._track:
            params = [self._track.mixer_device.volume, self._track.mixer_device.panning] + list(self._track.mixer_device.sends)
            return [ generate_info(p, name=n) for n, p in zip(TRACK_PARAMETER_NAMES, params) ]
        return []

    @listens('visible_tracks')
    def _on_visible_tracks(self):
        self.notify_parameters()

    @listens('selected_track')
    def _on_selected_track(self):
        self._track = self._on_selected_track.subject.selected_track
        self.notify_parameters()