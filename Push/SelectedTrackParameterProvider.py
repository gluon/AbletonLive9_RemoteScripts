#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/SelectedTrackParameterProvider.py
from _Framework.Dependency import depends
from _Framework.SubjectSlot import subject_slot, SlotManager
from DeviceParameterComponent import ParameterProvider
from SpecialChanStripComponent import TRACK_PARAMETER_NAMES

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
            return zip(TRACK_PARAMETER_NAMES, [self._track.mixer_device.volume, self._track.mixer_device.panning] + list(self._track.mixer_device.sends))
        return []

    @subject_slot('visible_tracks')
    def _on_visible_tracks(self):
        self.notify_parameters()

    @subject_slot('selected_track')
    def _on_selected_track(self):
        self._track = self._on_selected_track.subject.selected_track
        self.notify_parameters()