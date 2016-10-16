#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/mixer.py
from __future__ import absolute_import, print_function
from itertools import izip, izip_longest
from ...base import clamp, listens, liveobj_valid
from ..compound_component import CompoundComponent
from .channel_strip import ChannelStripComponent, release_control

def simple_track_assigner(song, tracks_provider):
    tracks = list(tracks_provider.controlled_tracks())
    if len(tracks) < tracks_provider.num_tracks:
        num_empty_track_slots = tracks_provider.num_tracks - len(tracks)
        tracks += [None] * num_empty_track_slots
    return tracks


def right_align_return_tracks_track_assigner(song, tracks_provider):
    """
    Track assigner which aligns return tracks to the right, leaving a gap
    between regular and return tracks (if applicable).
    """
    offset = tracks_provider.track_offset
    tracks = tracks_provider.tracks_to_use()
    return_tracks = list(song.return_tracks)
    size = tracks_provider.num_tracks
    num_empty_tracks = max(0, size + offset - len(tracks))
    track_list = size * [None]
    for i in xrange(size):
        track_index = i + offset
        if len(tracks) > track_index:
            track = tracks[track_index]
            empty_offset = 0 if tracks[track_index] not in return_tracks else num_empty_tracks
            track_list[i + empty_offset] = track

    return track_list


class MixerComponent(CompoundComponent):
    """ Class encompassing several channel strips to form a mixer """

    def __init__(self, tracks_provider = None, track_assigner = right_align_return_tracks_track_assigner, auto_name = False, invert_mute_feedback = False, *a, **k):
        if not tracks_provider is not None:
            raise AssertionError
            raise callable(track_assigner) or AssertionError
            super(MixerComponent, self).__init__(*a, **k)
            self._track_assigner = track_assigner
            self._provider = tracks_provider
            self.__on_offset_changed.subject = tracks_provider
            self._send_index = 0
            self._prehear_volume_control = None
            self._crossfader_control = None
            self._send_controls = None
            self._channel_strips = []
            self._offset_can_start_after_tracks = False
            for index in range(self._provider.num_tracks):
                strip = self._create_strip()
                self._channel_strips.append(strip)
                self.register_components(self._channel_strips[index])
                if invert_mute_feedback:
                    strip.set_invert_mute_feedback(True)

            self._master_strip = self._create_master_strip()
            self.register_components(self._master_strip)
            self._master_strip.set_track(self.song.master_track)
            self._selected_strip = self._create_strip()
            self.register_components(self._selected_strip)
            self.__on_selected_track_changed.subject = self.song.view
            self.__on_selected_track_changed()
            self._reassign_tracks()
            auto_name and self._auto_name()
        self.__on_track_list_changed.subject = self.song
        self.__on_return_tracks_changed.subject = self.song
        self.__on_return_tracks_changed()

    def disconnect(self):
        super(MixerComponent, self).disconnect()
        release_control(self._prehear_volume_control)
        release_control(self._crossfader_control)
        self._prehear_volume_control = None
        self._crossfader_control = None

    @property
    def send_index(self):
        return self._send_index

    @send_index.setter
    def send_index(self, index):
        if 0 <= index < self.num_sends or index is None:
            if self._send_index != index:
                self._send_index = index
                self.set_send_controls(self._send_controls)
                self.on_send_index_changed()
        else:
            raise IndexError

    def on_send_index_changed(self):
        pass

    @property
    def num_sends(self):
        return len(self.song.return_tracks)

    def channel_strip(self, index):
        raise index in range(len(self._channel_strips)) or AssertionError
        return self._channel_strips[index]

    def master_strip(self):
        return self._master_strip

    def selected_strip(self):
        return self._selected_strip

    def set_prehear_volume_control(self, control):
        release_control(self._prehear_volume_control)
        self._prehear_volume_control = control
        self.update()

    def set_crossfader_control(self, control):
        release_control(self._crossfader_control)
        self._crossfader_control = control
        self.update()

    def set_volume_controls(self, controls):
        for strip, control in izip_longest(self._channel_strips, controls or []):
            strip.set_volume_control(control)

    def set_pan_controls(self, controls):
        for strip, control in izip_longest(self._channel_strips, controls or []):
            strip.set_pan_control(control)

    def set_send_controls(self, controls):
        self._send_controls = controls
        for strip, control in izip_longest(self._channel_strips, controls or []):
            if self._send_index is None:
                strip.set_send_controls(None)
            else:
                strip.set_send_controls((None,) * self._send_index + (control,))

    def set_arm_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            strip.set_arm_button(button)

    def set_solo_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            strip.set_mute_button(button)

    def set_track_select_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            strip.set_select_button(button)

    def set_shift_button(self, button):
        for strip in self._channel_strips or []:
            strip.set_shift_button(button)

    @listens('offset')
    def __on_offset_changed(self, *a):
        self._reassign_tracks()

    def on_enabled_changed(self):
        self.update()

    @listens('visible_tracks')
    def __on_track_list_changed(self):
        self._reassign_tracks()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        self._update_selected_strip()

    def _update_selected_strip(self):
        selected_track = self.song.view.selected_track
        if liveobj_valid(self._selected_strip):
            if selected_track != self.song.master_track:
                self._selected_strip.set_track(selected_track)
            else:
                self._selected_strip.set_track(None)

    @listens('return_tracks')
    def __on_return_tracks_changed(self):
        self._update_send_index()

    def _update_send_index(self):
        num_sends = self.num_sends
        if self._send_index is not None:
            self.send_index = clamp(self._send_index, 0, num_sends - 1) if num_sends > 0 else None
        else:
            self.send_index = 0 if num_sends > 0 else None
        self.on_num_sends_changed()

    def on_num_sends_changed(self):
        pass

    def update(self):
        super(MixerComponent, self).update()
        if self._allow_updates:
            master_track = self.song.master_track
            if self.is_enabled():
                if self._prehear_volume_control != None:
                    self._prehear_volume_control.connect_to(master_track.mixer_device.cue_volume)
                if self._crossfader_control != None:
                    self._crossfader_control.connect_to(master_track.mixer_device.crossfader)
            else:
                release_control(self._prehear_volume_control)
                release_control(self._crossfader_control)
        else:
            self._update_requests += 1

    def _reassign_tracks(self):
        tracks = self._track_assigner(self.song, self._provider)
        for track, channel_strip in izip(tracks, self._channel_strips):
            channel_strip.set_track(track)

    def _create_strip(self):
        return ChannelStripComponent()

    def _create_master_strip(self):
        return self._create_strip()

    def _auto_name(self):
        self.name = 'Mixer'
        self.master_strip().name = 'Master_Channel_Strip'
        self.selected_strip().name = 'Selected_Channel_Strip'
        for index, strip in enumerate(self._channel_strips):
            strip.name = 'Channel_Strip_%d' % index