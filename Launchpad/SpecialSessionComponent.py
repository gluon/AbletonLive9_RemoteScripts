#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Launchpad/SpecialSessionComponent.py
from _Framework.SessionComponent import SessionComponent

class SpecialSessionComponent(SessionComponent):
    """ Special session subclass that handles ConfigurableButtons """

    def _update_stop_clips_led(self, index):
        if self.is_enabled() and self._stop_track_clip_buttons != None:
            button = self._stop_track_clip_buttons[index]
            tracks_to_use = self.tracks_to_use()
            track_index = index + self.track_offset()
            if 0 <= track_index < len(tracks_to_use):
                track = tracks_to_use[track_index]
                if track.fired_slot_index == -2:
                    button.send_value(self._stop_clip_triggered_value)
                elif track.playing_slot_index >= 0:
                    button.send_value(self._stop_clip_value)
                else:
                    button.turn_off()
            else:
                button.send_value(4)