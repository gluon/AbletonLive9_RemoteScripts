#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Serato/SpecialMixerComponent.py
import Live
from _Framework.MixerComponent import MixerComponent
from SpecialChanStripComponent import SpecialChanStripComponent

class SpecialMixerComponent(MixerComponent):

    def __init__(self, num_tracks):
        self._tracks_to_use_callback = None
        self._serato_interface = None
        MixerComponent.__init__(self, num_tracks)
        for index in range(num_tracks):
            self._channel_strips[index].set_index(index)

    def disconnect(self):
        MixerComponent.disconnect(self)
        self._serato_interface = None
        self._tracks_to_use_callback = None

    def set_tracks_to_use_callback(self, callback):
        self._tracks_to_use_callback = callback

    def set_serato_interface(self, serato_interface):
        raise serato_interface != None or AssertionError
        self._serato_interface = serato_interface
        self.on_selected_track_changed()

    def tracks_to_use(self):
        tracks = tuple()
        if self._tracks_to_use_callback != None:
            tracks = self._tracks_to_use_callback()
        else:
            tracks = MixerComponent.tracks_to_use(self)
        return tracks

    def on_selected_track_changed(self):
        MixerComponent.on_selected_track_changed(self)
        if self._serato_interface != None:
            self._serato_interface.PySCA_SetSelectedTrack(self._selected_strip_index())

    def _selected_strip_index(self):
        result = -1
        if self._master_strip.is_track_selected():
            result = 0
        else:
            for index in range(len(self._channel_strips)):
                if self._channel_strips[index].is_track_selected():
                    result = index + 1
                    break

        return result

    def _create_strip(self):
        return SpecialChanStripComponent()

    def _reassign_tracks(self):
        MixerComponent._reassign_tracks(self)
        self.on_selected_track_changed()