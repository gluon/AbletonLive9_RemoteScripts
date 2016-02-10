#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Arturia/MixerComponent.py
from _Framework.MixerComponent import MixerComponent as MixerComponentBase
from .ScrollComponent import ScrollComponent

class MixerComponent(MixerComponentBase):

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)
        self._track_selection = self.register_component(ScrollComponent())
        self._track_selection.can_scroll_up = self._can_select_prev_track
        self._track_selection.can_scroll_down = self._can_select_next_track
        self._track_selection.scroll_up = self._select_prev_track
        self._track_selection.scroll_down = self._select_next_track

    def set_selected_track_volume_control(self, control):
        self.selected_strip().set_volume_control(control)

    def set_selected_track_pan_control(self, control):
        self.selected_strip().set_pan_control(control)

    def set_selected_track_send_controls(self, controls):
        self.selected_strip().set_send_controls(controls)

    def set_return_volume_controls(self, controls):
        for strip, control in map(None, self._return_strips, controls or []):
            strip.set_volume_control(control)

    def set_track_select_encoder(self, encoder):
        self._track_selection.set_scroll_encoder(encoder)

    def all_tracks(self):
        return self.tracks_to_use() + (self.song().master_track,)

    def tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    def _can_select_prev_track(self):
        return self.song().view.selected_track != self.song().tracks[0]

    def _can_select_next_track(self):
        return self.song().view.selected_track != self.song().master_track

    def _select_prev_track(self):
        selected_track = self.song().view.selected_track
        all_tracks = self.all_tracks()
        raise selected_track in all_tracks or AssertionError
        index = list(all_tracks).index(selected_track)
        self.song().view.selected_track = all_tracks[index - 1]

    def _select_next_track(self):
        selected_track = self.song().view.selected_track
        all_tracks = self.all_tracks()
        raise selected_track in all_tracks or AssertionError
        index = list(all_tracks).index(selected_track)
        self.song().view.selected_track = all_tracks[index + 1]