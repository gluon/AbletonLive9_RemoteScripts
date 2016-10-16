#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/simpler_slice_nudging.py
from __future__ import absolute_import, with_statement
from contextlib import contextmanager
import Live
from ableton.v2.base import SlotManager, find_if, liveobj_valid, clamp, listens
from .simpler_zoom import is_simpler
CENTERED_NUDGE_VALUE = 0.5
MINIMUM_SLICE_DISTANCE = 2

class SimplerSliceNudging(SlotManager):
    _simpler = None
    _nudge_parameter = None

    def set_device(self, device):
        self._simpler = device if is_simpler(device) else None
        self.__on_selected_slice_changed.subject = self._simpler
        with self._updating_nudge_parameter():
            self._nudge_parameter = find_if(lambda p: p.name == 'Nudge', self._simpler.parameters if liveobj_valid(self._simpler) else [])

    @contextmanager
    def _updating_nudge_parameter(self):
        if self._nudge_parameter:
            self._nudge_parameter.set_display_value_conversion(None)
        yield
        if self._nudge_parameter:
            self._nudge_parameter.set_display_value_conversion(self._display_value_conversion)
        self.__on_nudge_delta.subject = self._nudge_parameter

    def _can_access_slicing_properties(self):
        return liveobj_valid(self._simpler) and self._simpler.current_playback_mode == str(Live.SimplerDevice.PlaybackMode.slicing) and self._simpler.sample_length > 0

    @listens('view.selected_slice')
    def __on_selected_slice_changed(self):
        if self._nudge_parameter:
            self._nudge_parameter.notify_value()

    @listens('delta')
    def __on_nudge_delta(self, delta):
        if self._can_access_slicing_properties():
            old_slice_time = self._simpler.view.selected_slice
            if old_slice_time >= 0:
                if self._is_first_slice_at_time(old_slice_time):
                    new_start = self._new_start_marker_time(old_slice_time, delta)
                    self._simpler.start_marker = new_start
                    return
                new_slice_time = self._new_slice_time(old_slice_time, delta)
                if old_slice_time != new_slice_time:
                    original_slices = self._simpler.slices
                    self._simpler.insert_slice(new_slice_time)
                    self._simpler.remove_slice(old_slice_time)
                    try:
                        self._simpler.view.selected_slice = new_slice_time
                    except RuntimeError:
                        self._simpler.view.selected_slice = self._simpler.slices[list(original_slices).index(old_slice_time)]

    def _is_first_slice_at_time(self, slice_time):
        start_sample = self._simpler.start_marker
        return abs(slice_time - start_sample) < MINIMUM_SLICE_DISTANCE

    def _new_start_marker_time(self, old_slice_time, delta):
        change_in_samples = self._sample_change_from_delta(delta)
        new_start_marker_time = old_slice_time + change_in_samples
        return clamp(new_start_marker_time, 0, self._simpler.sample_length - MINIMUM_SLICE_DISTANCE)

    def _sample_change_from_delta(self, delta):
        sample_length = self._simpler.sample_length
        change_in_samples = round(delta * sample_length / 10)
        return int(change_in_samples)

    def _get_surrounding_slices(self, slice_time):
        slices = list(self._simpler.slices)
        index = slices.index(slice_time)
        sample_length = self._simpler.sample_length
        previous_slice = slices[index - 1] + MINIMUM_SLICE_DISTANCE if index > 0 else 0
        next_slice = slices[index + 1] if index < len(slices) - 1 else sample_length
        return (previous_slice, next_slice)

    def _display_value_conversion(self, _value):
        selected_slice = self._simpler.view.selected_slice if self._can_access_slicing_properties() else -1
        return str(selected_slice) if selected_slice >= 0 else '-'

    def _get_min_first_slice_length(self):
        return Live.SimplerDevice.get_min_first_slice_length_in_samples(self._simpler.proxied_object)

    def _new_slice_time(self, old_slice_time, delta):
        previous_slice, next_slice = self._get_surrounding_slices(old_slice_time)
        change_in_samples = self._sample_change_from_delta(delta)
        min_second_slice_start = self._simpler.start_marker + self._get_min_first_slice_length()
        lower_bound = max(0, min_second_slice_start, previous_slice)
        upper_bound = min(next_slice, self._simpler.end_marker, self._simpler.sample_length) - MINIMUM_SLICE_DISTANCE
        return clamp(old_slice_time + change_in_samples, lower_bound, upper_bound)