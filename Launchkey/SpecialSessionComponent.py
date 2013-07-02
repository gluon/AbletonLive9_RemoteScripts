#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Launchkey/SpecialSessionComponent.py
from _Framework.SessionComponent import SessionComponent
from _Framework.Util import in_range, nop
from consts import *

class SpecialSessionComponent(SessionComponent):
    """ Special session subclass that handles ConfigurableButtons """

    def __init__(self, num_tracks, num_scenes):
        self._update_playing_slots = nop
        SessionComponent.__init__(self, num_tracks, num_scenes)
        self._playing_slots_slots = self.register_slot_manager()
        self._update_playing_slots = self._update_playing_slots_impl
        self._update_playing_slots()

    def on_enabled_changed(self):
        SessionComponent.on_enabled_changed(self)
        for index in xrange(len(self._stop_track_clip_buttons or [])):
            self._update_stop_clips_led(index)

    def _reassign_tracks(self):
        super(SpecialSessionComponent, self)._reassign_tracks()
        self._update_playing_slots()

    def _update_playing_slots_impl(self):
        self._playing_slots_slots.disconnect()
        tracks_to_use = self.tracks_to_use()
        for index in range(self._num_tracks):
            playing_listener = lambda index = index: self._on_playing_slot_index_changed(index)
            if self._track_offset + index < len(tracks_to_use):
                track = tracks_to_use[self._track_offset + index]
                if track != None and track in self.song().tracks:
                    self._playing_slots_slots.register_slot(track, playing_listener, 'playing_slot_index')
            playing_listener()
            self._update_stop_clips_led(index)

    def _on_fired_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _on_playing_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _update_stop_clips_led(self, index):
        if self.is_enabled() and self._stop_track_clip_buttons != None:
            button = self._stop_track_clip_buttons[index]
            tracks = self.tracks_to_use()
            track_index = index + self.track_offset()
            if in_range(track_index, 0, len(tracks)):
                track = tracks[track_index]
                is_player_track = track in self.song().tracks
                if is_player_track and track.fired_slot_index == -2:
                    button.send_value(self._stop_track_clip_value)
                elif is_player_track and track.playing_slot_index >= 0:
                    button.send_value(AMBER_HALF)
                else:
                    button.turn_off()
            else:
                button.send_value(LED_OFF)