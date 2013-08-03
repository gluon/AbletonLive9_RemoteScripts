#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_0/LC2SessionSnapshot.py
from LC2Sysex import LC2Sysex

class LC2SessionBank:

    def set_song(song):
        LC2SessionBank.song = song

    set_song = staticmethod(set_song)

    def set_timer_callback(func):
        LC2SessionBank.timer_callback = func

    set_timer_callback = staticmethod(set_timer_callback)

    def release_attributes():
        LC2SessionBank.song = None
        LC2SessionBank.timer_callback = None

    release_attributes = staticmethod(release_attributes)

    def __init__(self):
        self._snapshots = {}
        self._send_states()

    def add(self, id):
        self._snapshots[id] = LC2SessionSnapshot()
        self._send_states()

    def _send_states(self):
        sysex = LC2Sysex('SNAPSHOT_STATES')
        val = 0
        for t in self.get_states():
            sysex.byte(t)

        sysex.send()

    def load(self, id):
        if id in self._snapshots:
            self._snapshots[id].load()

    def get_states(self):
        states = []
        for i in range(16):
            states.append(i in self._snapshots and 1 or 0)

        return states

    def playing_slot_changed(self, name, slot_id):
        for id in self._snapshots:
            self._snapshots[id].playing_slot_changed(name, slot_id)


class LC2SessionSnapshot:

    def __init__(self):
        self._waiting_for_load = 0
        self._trigger_slot = -1
        self._trigger_name = None
        self._tracks = []
        self._tempo = LC2SessionBank.song().tempo
        for track in LC2SessionBank.song().tracks:
            self._tracks.append(LC2TrackSnapshot(track))
            if self._tracks[-1]._has_playing_clip() and self._trigger_slot == -1:
                self._trigger_slot = self._tracks[-1]._playing_slot_id()
                self._trigger_name = self._tracks[-1]._get_track_name()

    def load(self):
        self._waiting_for_load = 1
        if self._trigger_slot == -1:
            self._load_snapshot()
            self._waiting_for_load = 0
        for tr in self._tracks:
            tr._launch(LC2SessionBank.song().tracks)

    def playing_slot_changed(self, track_name, slot_id):
        if self._waiting_for_load and track_name == self._trigger_name and slot_id == self._trigger_slot:
            LC2SessionBank.timer_callback(1, self._load_snapshot)

    def _load_snapshot(self):
        for tr in self._tracks:
            tr._load(LC2SessionBank.song().tracks)

        LC2SessionBank.song().tempo = self._tempo
        self._waiting_for_load = 0


class LC2TrackSnapshot:

    def __init__(self, track):
        self._track_name = track.name
        self._playing_slot = track.playing_slot_index
        self._solo = track.solo
        self._mute = track.mute
        self._vol = track.mixer_device.volume.value
        self._pan = track.mixer_device.panning.value
        self._sends = []
        for send in track.mixer_device.sends:
            self._sends.append(send.value)

    def _has_playing_clip(self):
        return self._playing_slot > -1

    def _playing_slot_id(self):
        return self._playing_slot

    def _get_track_name(self):
        return self._track_name

    def _load(self, tracks):
        return
        track = self.find_track(tracks)
        if track is not None:
            track.solo = self._solo
            track.mute = self._mute
            track.mixer_device.volume.value = self._vol
            track.mixer_device.panning.value = self._pan
            for id, send in enumerate(track.mixer_device.sends):
                if id < len(self._sends):
                    send.value = self._sends[id]

    def _launch(self, tracks):
        track = self.find_track(tracks)
        if track is not None:
            if hasattr(track, 'clip_slots'):
                if self._playing_slot > -1:
                    if self._playing_slot < len(track.clip_slots):
                        if track.clip_slots[self._playing_slot].has_clip:
                            track.clip_slots[self._playing_slot].clip.fire()
                        else:
                            track.stop_all_clips()
                else:
                    track.stop_all_clips()

    def find_track(self, tracks):
        track = None
        for tr in tracks:
            if tr.name == self._track_name:
                track = tr
                break

        return track