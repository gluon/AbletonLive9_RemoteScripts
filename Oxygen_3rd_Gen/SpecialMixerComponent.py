#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Oxygen_3rd_Gen/SpecialMixerComponent.py
from _Framework.MixerComponent import MixerComponent

class SpecialMixerComponent(MixerComponent):
    """ Special mixer class that uses return tracks alongside midi and audio tracks """

    def __init__(self, num_tracks):
        MixerComponent.__init__(self, num_tracks)
        self._selected_tracks = []
        self._register_timer_callback(self._on_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        self._selected_tracks = None
        MixerComponent.disconnect(self)

    def tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    def _on_timer(self):
        sel_track = None
        while len(self._selected_tracks) > 0:
            track = self._selected_tracks[-1]
            if track != None and track.has_midi_input and track.can_be_armed and not track.arm:
                sel_track = track
                break
            del self._selected_tracks[-1]

        if sel_track != None:
            found_recording_clip = False
            song = self.song()
            tracks = song.tracks
            check_arrangement = song.is_playing and song.record_mode
            for track in tracks:
                if track.can_be_armed and track.arm:
                    if check_arrangement:
                        found_recording_clip = True
                        break
                    else:
                        playing_slot_index = track.playing_slot_index
                        if playing_slot_index in range(len(track.clip_slots)):
                            slot = track.clip_slots[playing_slot_index]
                            if slot.has_clip and slot.clip.is_recording:
                                found_recording_clip = True
                                break

            if not found_recording_clip:
                if song.exclusive_arm:
                    for track in tracks:
                        if track.can_be_armed and track.arm and track != sel_track:
                            track.arm = False

                sel_track.arm = True
                sel_track.view.select_instrument()
        self._selected_tracks = []

    def _next_track_value(self, value):
        MixerComponent._next_track_value(self, value)
        self._selected_tracks.append(self.song().view.selected_track)

    def _prev_track_value(self, value):
        MixerComponent._prev_track_value(self, value)
        self._selected_tracks.append(self.song().view.selected_track)