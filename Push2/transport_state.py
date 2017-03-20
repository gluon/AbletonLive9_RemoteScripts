# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/transport_state.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base import listenable_property, listens
from ableton.v2.control_surface import CompoundComponent
from .real_time_channel import RealTimeDataComponent
COUNT_IN_DURATION_IN_BARS = (0, 1, 2, 4)

class TransportState(CompoundComponent):
    count_in_duration = listenable_property.managed(0)

    def __init__(self, song=None, *a, **kw):
        super(TransportState, self).__init__(*a, **kw)
        self._song = song
        self.__on_is_playing_changed.subject = song
        self._count_in_time_real_time_data = self.register_component(RealTimeDataComponent(channel_type='count-in'))
        self.__on_count_in_duration_changed.subject = song
        self.__on_is_counting_in_changed.subject = song
        self.__on_signature_numerator_changed.subject = song
        self.__on_signature_denominator_changed.subject = song
        self.__on_count_in_channel_changed.subject = self._count_in_time_real_time_data
        self._update_count_in_duration()

    @listenable_property
    def count_in_real_time_channel_id(self):
        return self._count_in_time_real_time_data.channel_id

    @listenable_property
    def is_counting_in(self):
        return self._song.is_counting_in

    @listenable_property
    def signature_numerator(self):
        return self._song.signature_numerator

    @listenable_property
    def signature_denominator(self):
        return self._song.signature_denominator

    def _update_count_in_duration(self):
        self.count_in_duration = COUNT_IN_DURATION_IN_BARS[self._song.count_in_duration]

    @listens('count_in_duration')
    def __on_count_in_duration_changed(self):
        if not self.is_counting_in:
            self._update_count_in_duration()

    @listens('is_counting_in')
    def __on_is_counting_in_changed(self):
        self._count_in_time_real_time_data.set_data(self._song if self.is_counting_in else None)
        self.notify_is_counting_in()
        self._update_count_in_duration()
        return

    @listens('signature_numerator')
    def __on_signature_numerator_changed(self):
        self.notify_signature_numerator()

    @listens('signature_denominator')
    def __on_signature_denominator_changed(self):
        self.notify_signature_denominator()

    @listenable_property
    def is_playing(self):
        return self._song.is_playing

    @listens('is_playing')
    def __on_is_playing_changed(self):
        self.notify_is_playing()

    @listens('channel_id')
    def __on_count_in_channel_changed(self):
        self.notify_count_in_real_time_channel_id()