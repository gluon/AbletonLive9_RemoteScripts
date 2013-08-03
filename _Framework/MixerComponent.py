#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/MixerComponent.py
from CompoundComponent import CompoundComponent
from ChannelStripComponent import ChannelStripComponent
from TrackEQComponent import TrackEQComponent
from TrackFilterComponent import TrackFilterComponent
from ButtonElement import ButtonElement
from EncoderElement import EncoderElement

class MixerComponent(CompoundComponent):
    """ Class encompassing several channel strips to form a mixer """

    def __init__(self, num_tracks, num_returns = 0, with_eqs = False, with_filters = False):
        raise num_tracks >= 0 or AssertionError
        raise num_returns >= 0 or AssertionError
        CompoundComponent.__init__(self)
        self._track_offset = -1
        self._bank_up_button = None
        self._bank_down_button = None
        self._next_track_button = None
        self._prev_track_button = None
        self._prehear_volume_control = None
        self._crossfader_control = None
        self._channel_strips = []
        self._return_strips = []
        self._track_eqs = []
        self._track_filters = []
        self._offset_can_start_after_tracks = False
        for index in range(num_tracks):
            self._channel_strips.append(self._create_strip())
            self.register_components(self._channel_strips[index])
            if with_eqs:
                self._track_eqs.append(TrackEQComponent())
                self.register_components(self._track_eqs[index])
            if with_filters:
                self._track_filters.append(TrackFilterComponent())
                self.register_components(self._track_filters[index])

        for index in range(num_returns):
            self._return_strips.append(self._create_strip())
            self.register_components(self._return_strips[index])

        self._master_strip = self._create_strip()
        self.register_components(self._master_strip)
        self._master_strip.set_track(self.song().master_track)
        self._selected_strip = self._create_strip()
        self.register_components(self._selected_strip)
        self.on_selected_track_changed()
        self.set_track_offset(0)

    def disconnect(self):
        CompoundComponent.disconnect(self)
        if self._bank_up_button != None:
            self._bank_up_button.remove_value_listener(self._bank_up_value)
            self._bank_up_button = None
        if self._bank_down_button != None:
            self._bank_down_button.remove_value_listener(self._bank_down_value)
            self._bank_down_button = None
        if self._next_track_button != None:
            self._next_track_button.remove_value_listener(self._next_track_value)
            self._next_track_button = None
        if self._prev_track_button != None:
            self._prev_track_button.remove_value_listener(self._prev_track_value)
            self._prev_track_button = None
        if self._prehear_volume_control != None:
            self._prehear_volume_control.release_parameter()
            self._prehear_volume_control = None
        if self._crossfader_control != None:
            self._crossfader_control.release_parameter()
            self._crossfader_control = None

    def channel_strip(self, index):
        raise index in range(len(self._channel_strips)) or AssertionError
        return self._channel_strips[index]

    def return_strip(self, index):
        raise index in range(len(self._return_strips)) or AssertionError
        return self._return_strips[index]

    def track_eq(self, index):
        raise index in range(len(self._track_eqs)) or AssertionError
        return self._track_eqs[index]

    def track_filter(self, index):
        raise index in range(len(self._track_filters)) or AssertionError
        return self._track_filters[index]

    def master_strip(self):
        return self._master_strip

    def selected_strip(self):
        return self._selected_strip

    def set_prehear_volume_control(self, control):
        if not (control == None or isinstance(control, EncoderElement)):
            raise AssertionError
            self._prehear_volume_control != None and self._prehear_volume_control.release_parameter()
        self._prehear_volume_control = control
        self.update()

    def set_crossfader_control(self, control):
        if not (control == None or isinstance(control, EncoderElement)):
            raise AssertionError
            self._crossfader_control != None and self._crossfader_control.release_parameter()
        self._crossfader_control = control
        self.update()

    def set_bank_buttons(self, up_button, down_button):
        if not (up_button == None or isinstance(up_button, ButtonElement)):
            raise AssertionError
            if not (down_button == None or isinstance(down_button, ButtonElement)):
                raise AssertionError
                do_update = False
                if up_button is not self._bank_up_button:
                    do_update = True
                    if self._bank_up_button != None:
                        self._bank_up_button.remove_value_listener(self._bank_up_value)
                    self._bank_up_button = up_button
                    if self._bank_up_button != None:
                        self._bank_up_button.add_value_listener(self._bank_up_value)
                if down_button is not self._bank_down_button:
                    do_update = True
                    if self._bank_down_button != None:
                        self._bank_down_button.remove_value_listener(self._bank_down_value)
                    self._bank_down_button = down_button
                    self._bank_down_button != None and self._bank_down_button.add_value_listener(self._bank_down_value)
            do_update and self.on_track_list_changed()

    def set_select_buttons(self, next_button, prev_button):
        if not (next_button == None or isinstance(next_button, ButtonElement)):
            raise AssertionError
            if not (prev_button == None or isinstance(prev_button, ButtonElement)):
                raise AssertionError
                do_update = False
                if next_button is not self._next_track_button:
                    do_update = True
                    if self._next_track_button != None:
                        self._next_track_button.remove_value_listener(self._next_track_value)
                    self._next_track_button = next_button
                    if self._next_track_button != None:
                        self._next_track_button.add_value_listener(self._next_track_value)
                if prev_button is not self._prev_track_button:
                    do_update = True
                    if self._prev_track_button != None:
                        self._prev_track_button.remove_value_listener(self._prev_track_value)
                    self._prev_track_button = prev_button
                    self._prev_track_button != None and self._prev_track_button.add_value_listener(self._prev_track_value)
            do_update and self.on_selected_track_changed()

    def set_track_offset(self, new_offset):
        if not isinstance(new_offset, int):
            raise AssertionError
            raise new_offset >= 0 or AssertionError
            new_offset != self._track_offset and self._offset_can_start_after_tracks |= new_offset > len(self.tracks_to_use()) - 1
            self._track_offset = new_offset
            self._reassign_tracks()

    def on_enabled_changed(self):
        self.update()

    def on_track_list_changed(self):
        if not self._offset_can_start_after_tracks:
            self._track_offset = min(self._track_offset, len(self.tracks_to_use()) - 1)
        self._reassign_tracks()

    def on_selected_track_changed(self):
        selected_track = self.song().view.selected_track
        if self._selected_strip != None:
            self._selected_strip.set_track(selected_track)
        if self.is_enabled():
            if self._next_track_button != None:
                if selected_track != self.song().master_track:
                    self._next_track_button.turn_on()
                else:
                    self._next_track_button.turn_off()
            if self._prev_track_button != None:
                if selected_track != self.song().visible_tracks[0]:
                    self._prev_track_button.turn_on()
                else:
                    self._prev_track_button.turn_off()

    def tracks_to_use(self):
        return self.song().visible_tracks

    def update(self):
        if self._allow_updates:
            master_track = self.song().master_track
            if self.is_enabled():
                if self._prehear_volume_control != None:
                    self._prehear_volume_control.connect_to(master_track.mixer_device.cue_volume)
                if self._crossfader_control != None:
                    self._crossfader_control.connect_to(master_track.mixer_device.crossfader)
            else:
                if self._prehear_volume_control != None:
                    self._prehear_volume_control.release_parameter()
                if self._crossfader_control != None:
                    self._crossfader_control.release_parameter()
                if self._bank_up_button != None:
                    self._bank_up_button.turn_off()
                if self._bank_down_button != None:
                    self._bank_down_button.turn_off()
                if self._next_track_button != None:
                    self._next_track_button.turn_off()
                if self._prev_track_button != None:
                    self._prev_track_button.turn_off()
        else:
            self._update_requests += 1

    def _reassign_tracks(self):
        tracks = self.tracks_to_use()
        returns = self.song().return_tracks
        for index in range(len(self._channel_strips)):
            track_index = self._track_offset + index
            track = None
            if len(tracks) > track_index:
                track = tracks[track_index]
            self._channel_strips[index].set_track(track)
            if len(self._track_eqs) > index:
                self._track_eqs[index].set_track(track)
            if len(self._track_filters) > index:
                self._track_filters[index].set_track(track)

        for index in range(len(self._return_strips)):
            if len(returns) > index:
                self._return_strips[index].set_track(returns[index])
            else:
                self._return_strips[index].set_track(None)

        if self._bank_down_button != None:
            if self._track_offset > 0:
                self._bank_down_button.turn_on()
            else:
                self._bank_down_button.turn_off()
        if self._bank_up_button != None:
            if len(tracks) > self._track_offset + len(self._channel_strips):
                self._bank_up_button.turn_on()
            else:
                self._bank_up_button.turn_off()

    def _create_strip(self):
        return ChannelStripComponent()

    def _bank_up_value(self, value):
        if not isinstance(value, int):
            raise AssertionError
            if not self._bank_up_button != None:
                raise AssertionError
                if self.is_enabled():
                    new_offset = (value is not 0 or not self._bank_up_button.is_momentary()) and self._track_offset + len(self._channel_strips)
                    len(self.tracks_to_use()) > new_offset and self.set_track_offset(new_offset)

    def _bank_down_value(self, value):
        if not isinstance(value, int):
            raise AssertionError
            if not self._bank_down_button != None:
                raise AssertionError
                self.is_enabled() and (value is not 0 or not self._bank_down_button.is_momentary()) and self.set_track_offset(max(0, self._track_offset - len(self._channel_strips)))

    def _next_track_value(self, value):
        if not self._next_track_button != None:
            raise AssertionError
            raise value != None or AssertionError
            raise isinstance(value, int) or AssertionError
            selected_track = self.is_enabled() and (value is not 0 or not self._next_track_button.is_momentary()) and self.song().view.selected_track
            all_tracks = tuple(self.song().visible_tracks) + tuple(self.song().return_tracks) + (self.song().master_track,)
            if not selected_track in all_tracks:
                raise AssertionError
                if selected_track != all_tracks[-1]:
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[index + 1]

    def _prev_track_value(self, value):
        if not self._prev_track_button != None:
            raise AssertionError
            raise value != None or AssertionError
            raise isinstance(value, int) or AssertionError
            selected_track = self.is_enabled() and (value is not 0 or not self._prev_track_button.is_momentary()) and self.song().view.selected_track
            all_tracks = tuple(self.song().visible_tracks) + tuple(self.song().return_tracks) + (self.song().master_track,)
            if not selected_track in all_tracks:
                raise AssertionError
                if selected_track != all_tracks[0]:
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[index - 1]