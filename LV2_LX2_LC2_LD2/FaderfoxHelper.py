#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/LV2_LX2_LC2_LD2/FaderfoxHelper.py
import Live
from ParamMap import Callable
from Devices import *
from Params import *

class FaderfoxHelper:
    __module__ = __name__
    __doc__ = 'General Live helper'

    def __init__(self, parent):
        self.parent = parent

    def song(self):
        return self.parent.song()

    def selected_scene_idx(self):

        def tuple_idx(tuple, obj):
            for i in xrange(0, len(tuple)):
                if tuple[i] == obj:
                    return i

        return tuple_idx(self.song().scenes, self.song().view.selected_scene)

    def toggle_clip_playing(self, track_idx):
        scene = self.song().view.selected_scene
        max_track_idx = len(scene.clip_slots)
        if max_track_idx > track_idx and scene.clip_slots[track_idx].has_clip:
            clip = scene.clip_slots[track_idx].clip
            if clip.is_playing:
                clip.stop()
            else:
                clip.fire()

    def trigger_track_clip(self, track_idx, clip_idx):
        if track_idx < len(self.song().tracks):
            track = self.song().tracks[track_idx]
            if clip_idx < len(track.clip_slots):
                slot = track.clip_slots[clip_idx]
                if slot.has_clip:
                    clip = slot.clip
                    if not (clip.is_playing or clip.is_triggered):
                        clip.fire()
                        return 1
                    clip.stop()
                    return 0
                    self.song().view.selected_scene = self.song().scenes[clip_idx]
                else:
                    self.stop_track(track_idx)
                    return 0

    def stop_track(self, track_idx):
        if track_idx < len(self.song().tracks):
            track = self.song().tracks[track_idx]
            clip_idx = self.track_playing_slot_idx(track)
            if clip_idx >= 0:
                track.clip_slots[clip_idx].clip.stop()
                return (track_idx, clip_idx)
            else:
                return (None, None)
        return (None, None)

    def is_track_playing(self, track):
        for slot in track.clip_slots:
            if slot.has_clip and slot.clip.is_playing:
                return 1

        return 0

    def track_playing_slot_idx(self, track):
        idx = 0
        for slot in track.clip_slots:
            if slot.has_clip and slot.clip.is_playing:
                return idx
            idx += 1

        return -1

    def switch_monitor_track(self, track):
        if hasattr(track, 'current_monitoring_state'):
            track.current_monitoring_state = (track.current_monitoring_state + 1) % len(track.monitoring_states.values)

    def switch_crossfader_ab(self, track):
        if hasattr(track.mixer_device, 'crossfade_assign'):
            track.mixer_device.crossfade_assign = (track.mixer_device.crossfade_assign - 1) % len(track.mixer_device.crossfade_assignments.values)

    def toggle_track_attribute(self, track, attr):
        track.__setattr__(attr, not track.__getattribute__(attr))

    def solo_track(self, track):
        tracks = tuple(self.song().tracks) + tuple(self.song().return_tracks)
        if track.solo:
            for track2 in tracks:
                track2.solo = 0

        else:
            for track2 in tracks:
                if track2 != track:
                    track2.solo = 0

            track.solo = 1

    def arm_track(self, track):
        tracks = tuple(self.song().tracks) + tuple(self.song().return_tracks)
        if track.arm or not track.can_be_armed:
            for track2 in tracks:
                if track2.can_be_armed:
                    track2.arm = 0

        else:
            for track2 in tracks:
                if track2 != track and track2.can_be_armed:
                    track2.arm = 0

            track.arm = 1

    def is_master_track_selected(self):
        return not cmp(self.song().view.selected_track, self.song().master_track)

    def get_track(self, idx):
        real_idx = idx
        tracks = tuple(self.song().tracks) + tuple(self.song().return_tracks)
        if idx < len(tracks):
            return tracks[idx]
        elif self.is_master_track_selected():
            new_idx = min(15, len(tracks) - 1)
            return self.get_track(new_idx)
        else:
            return self.song().master_track

    def selected_track_idx(self):

        def tuple_idx(tuple, obj):
            for i in xrange(0, len(tuple)):
                if not cmp(tuple[i], obj):
                    return i

        return tuple_idx(tuple(self.song().tracks) + tuple(self.song().return_tracks), self.song().view.selected_track)

    def device_name(self, device):
        if hasattr(device, 'class_name'):
            return device.class_name
        elif FIVETOSIX_DICT.has_key(device.name):
            return FIVETOSIX_DICT[device.name]
        else:
            return device.name

    def track_find_last_eq(self, track):

        def is_eq(device):
            return self.device_name(device) == 'Eq8' or self.device_name(device) == 'FilterEQ3'

        result = None
        for device in track.devices:
            if is_eq(device):
                result = device

        return result

    def eq_params(self, eq):
        if self.device_name(eq) == 'Eq8':
            return [ self.get_parameter_by_name(eq, name) for name in ['3 Gain A',
             '4 Gain A',
             '5 Gain A',
             '6 Gain A'] ]
        elif self.device_name(eq) == 'FilterEQ3':
            return [ self.get_parameter_by_name(eq, name) for name in ['GainLo',
             'GainMid',
             'GainHi',
             ''] ]
        else:
            return [None,
             None,
             None,
             None]

    def device_is_plugin(self, device):
        return self.device_name(device) in ('AuPluginDevice', 'PluginDevice')

    def current_q_step(self):
        q_map = {Live.Song.Quantization.q_no_q: 0.03125,
         Live.Song.Quantization.q_8_bars: 32.0,
         Live.Song.Quantization.q_4_bars: 16.0,
         Live.Song.Quantization.q_2_bars: 8.0,
         Live.Song.Quantization.q_bar: 4.0,
         Live.Song.Quantization.q_half: 2.0,
         Live.Song.Quantization.q_half_triplet: 1.0 + 1.0 / 3,
         Live.Song.Quantization.q_quarter: 1.0,
         Live.Song.Quantization.q_quarter_triplet: 2 * (1.0 / 3),
         Live.Song.Quantization.q_eight: 0.5,
         Live.Song.Quantization.q_eight_triplet: 1.0 / 3,
         Live.Song.Quantization.q_sixtenth: 0.25,
         Live.Song.Quantization.q_sixtenth_triplet: 1.0 / 6,
         Live.Song.Quantization.q_thirtytwoth: 0.125}
        return q_map[self.song().clip_trigger_quantization]

    def number_of_parameter_banks(self, device):
        result = 0
        if self.device_name(device) in DEVICE_DICT.keys():
            device_bank = DEVICE_DICT[self.device_name(device)]
            result = len(device_bank)
        else:
            param_count = len(list(device.parameters))
            result = param_count / 8
            if not param_count % 8 == 0:
                result += 1
        return result

    def get_parameter_by_name(self, device, name):
        for i in device.parameters:
            if hasattr(i, 'original_name'):
                if i.original_name == name:
                    return i
            else:
                device_name = self.device_name(device)
                if FIVETOSIX_PARAMS_DICT.has_key(device_name) and FIVETOSIX_PARAMS_DICT[device_name].has_key(name):
                    name = FIVETOSIX_PARAMS_DICT[device_name][name]
                if i.name == name:
                    return i