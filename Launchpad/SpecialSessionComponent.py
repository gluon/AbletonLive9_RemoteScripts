#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Launchpad/SpecialSessionComponent.py
import Live
from _Framework.SessionComponent import SessionComponent
from _Framework.ButtonElement import ButtonElement
from ConfigurableButtonElement import ConfigurableButtonElement

class SpecialSessionComponent(SessionComponent):
    """ Special session subclass that handles ConfigurableButtons """

    def __init__(self, num_tracks, num_scenes):
        self._tracks_and_listeners = []
        SessionComponent.__init__(self, num_tracks, num_scenes)

    def disconnect(self):
        for index in range(len(self._tracks_and_listeners)):
            track = self._tracks_and_listeners[index][0]
            fire_listener = self._tracks_and_listeners[index][1]
            playing_listener = self._tracks_and_listeners[index][2]
            if track != None:
                if track.fired_slot_index_has_listener(fire_listener):
                    track.remove_fired_slot_index_listener(fire_listener)
                if track.playing_slot_index_has_listener(playing_listener):
                    track.remove_playing_slot_index_listener(playing_listener)

        SessionComponent.disconnect(self)

    def _reassign_tracks(self):
        for index in range(len(self._tracks_and_listeners)):
            track = self._tracks_and_listeners[index][0]
            fire_listener = self._tracks_and_listeners[index][1]
            playing_listener = self._tracks_and_listeners[index][2]
            if track != None:
                if track.fired_slot_index_has_listener(fire_listener):
                    track.remove_fired_slot_index_listener(fire_listener)
                if track.playing_slot_index_has_listener(playing_listener):
                    track.remove_playing_slot_index_listener(playing_listener)

        self._tracks_and_listeners = []
        tracks_to_use = self.tracks_to_use()
        for index in range(self._num_tracks):
            fire_listener = lambda index = index: self._on_fired_slot_index_changed(index)
            playing_listener = lambda index = index: self._on_playing_slot_index_changed(index)
            track = None
            if self._track_offset + index < len(tracks_to_use):
                track = tracks_to_use[self._track_offset + index]
            if track != None:
                self._tracks_and_listeners.append((track, fire_listener, playing_listener))
                track.add_fired_slot_index_listener(fire_listener)
                track.add_playing_slot_index_listener(playing_listener)
            self._update_stop_clips_led(index)

    def _on_fired_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _on_playing_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _update_stop_clips_led(self, index):
        if self.is_enabled() and self._stop_track_clip_buttons != None:
            button = self._stop_track_clip_buttons[index]
            if index in range(len(self._tracks_and_listeners)):
                track = self._tracks_and_listeners[index][0]
                if track.fired_slot_index == -2:
                    button.send_value(self._stop_track_clip_value)
                elif track.playing_slot_index >= 0:
                    button.send_value(21)
                else:
                    button.turn_off()
            else:
                button.send_value(4)