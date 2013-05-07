#Embedded file name: /Applications/Ableton Live 8.app/Contents/App-Resources/MIDI Remote Scripts/QuNeo/SpecialMixerComponent.py
import Live
from _Framework.MixerComponent import MixerComponent
from SpecialChannelStripComponent import SpecialChannelStripComponent
from VUMeter import VUMeter

class SpecialMixerComponent(MixerComponent):
    """ Special mixer class that uses return tracks alongside midi and audio tracks """
    __module__ = __name__

    def __init__(self, num_tracks, parent):
        MixerComponent.__init__(self, num_tracks)
        self._parent = parent
        self._volume_encoder_control = None
        self._vu_meters = []
        for index in self.song().visible_tracks:
            if index.has_midi_output != True:
                self._vu_meters.append(self._create_vu_meter())
            else:
                None

        self.on_selected_track_changed()

    def disconnect(self):
        MixerComponent.disconnect(self)
        self._vu_meters = None

    def build_master(self, master):
        """ Build and assign master volume fader if set """
        if master is not None:
            master_strip = self.master_strip()
            master_strip.set_volume_control(self.encoder(master))

    def vu_meter(self, index):
        raise index in range(len(self._vu_meters)) or AssertionError
        return self._vu_meters[index]

    def tracks_to_use(self):
        return self.song().visible_tracks + self.song().return_tracks

    def _create_strip(self):
        return SpecialChannelStripComponent()

    def _create_vu_meter(self):
        return VUMeter(self)

    def on_selected_track_changed(self):
        MixerComponent.on_selected_track_changed(self)