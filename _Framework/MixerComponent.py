#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/MixerComponent.py
from __future__ import absolute_import
from itertools import izip_longest
from .ChannelStripComponent import ChannelStripComponent, release_control
from .CompoundComponent import CompoundComponent
from .SubjectSlot import subject_slot
from .Util import clamp

def turn_button_on_off(button, on = True):
    if button != None:
        if on:
            button.turn_on()
        else:
            button.turn_off()


class MixerComponent(CompoundComponent):
    """ Class encompassing several channel strips to form a mixer """

    def __init__(self, num_tracks = 0, num_returns = 0, auto_name = False, invert_mute_feedback = False, *a, **k):
        if not num_tracks >= 0:
            raise AssertionError
            raise num_returns >= 0 or AssertionError
            super(MixerComponent, self).__init__(*a, **k)
            self._track_offset = -1
            self._send_index = 0
            self._bank_up_button = None
            self._bank_down_button = None
            self._next_track_button = None
            self._prev_track_button = None
            self._prehear_volume_control = None
            self._crossfader_control = None
            self._send_controls = None
            self._channel_strips = []
            self._return_strips = []
            self._offset_can_start_after_tracks = False
            for index in range(num_tracks):
                strip = self._create_strip()
                self._channel_strips.append(strip)
                self.register_components(self._channel_strips[index])
                if invert_mute_feedback:
                    strip.set_invert_mute_feedback(True)

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
            auto_name and self._auto_name()
        self._on_return_tracks_changed.subject = self.song()
        self._on_return_tracks_changed()

        def make_button_slot(name):
            return self.register_slot(None, getattr(self, '_%s_value' % name), 'value')

        self._bank_up_button_slot = make_button_slot('bank_up')
        self._bank_down_button_slot = make_button_slot('bank_down')
        self._next_track_button_slot = make_button_slot('next_track')
        self._prev_track_button_slot = make_button_slot('prev_track')

    def disconnect(self):
        super(MixerComponent, self).disconnect()
        release_control(self._prehear_volume_control)
        release_control(self._crossfader_control)
        self._bank_up_button = None
        self._bank_down_button = None
        self._next_track_button = None
        self._prev_track_button = None
        self._prehear_volume_control = None
        self._crossfader_control = None

    def _get_send_index(self):
        return self._send_index

    def _set_send_index(self, index):
        if 0 <= index < self.num_sends or index is None:
            if self._send_index != index:
                self._send_index = index
                self.set_send_controls(self._send_controls)
                self.on_send_index_changed()
        else:
            raise IndexError

    send_index = property(_get_send_index, _set_send_index)

    def on_send_index_changed(self):
        pass

    @property
    def num_sends(self):
        return len(self.song().return_tracks)

    def channel_strip(self, index):
        raise index in range(len(self._channel_strips)) or AssertionError
        return self._channel_strips[index]

    def return_strip(self, index):
        raise index in range(len(self._return_strips)) or AssertionError
        return self._return_strips[index]

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

    def set_bank_buttons(self, up_button, down_button):
        do_update = False
        if up_button is not self._bank_up_button:
            do_update = True
            self._bank_up_button = up_button
            self._bank_up_button_slot.subject = up_button
        if down_button is not self._bank_down_button:
            do_update = True
            self._bank_down_button = down_button
            self._bank_down_button_slot.subject = down_button
        if do_update:
            self.on_track_list_changed()

    def set_select_buttons(self, next_button, prev_button):
        do_update = False
        if next_button is not self._next_track_button:
            do_update = True
            self._next_track_button = next_button
            self._next_track_button_slot.subject = next_button
        if prev_button is not self._prev_track_button:
            do_update = True
            self._prev_track_button = prev_button
            self._prev_track_button_slot.subject = prev_button
        if do_update:
            self.on_selected_track_changed()

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
            turn_button_on_off(self._next_track_button, on=selected_track != self.song().master_track)
            turn_button_on_off(self._prev_track_button, on=selected_track != self.song().visible_tracks[0])

    @subject_slot('return_tracks')
    def _on_return_tracks_changed(self):
        num_sends = self.num_sends
        if self._send_index is not None:
            self.send_index = clamp(self._send_index, 0, num_sends - 1) if num_sends > 0 else None
        else:
            self.send_index = 0 if num_sends > 0 else None
        self.on_num_sends_changed()

    def on_num_sends_changed(self):
        pass

    def tracks_to_use(self):
        return self.song().visible_tracks

    def update(self):
        super(MixerComponent, self).update()
        if self._allow_updates:
            master_track = self.song().master_track
            if self.is_enabled():
                if self._prehear_volume_control != None:
                    self._prehear_volume_control.connect_to(master_track.mixer_device.cue_volume)
                if self._crossfader_control != None:
                    self._crossfader_control.connect_to(master_track.mixer_device.crossfader)
            else:
                release_control(self._prehear_volume_control)
                release_control(self._crossfader_control)
                map(lambda x: turn_button_on_off(x, on=False), [self._bank_up_button,
                 self._bank_down_button,
                 self._next_track_button,
                 self._prev_track_button])
        else:
            self._update_requests += 1

    def _reassign_tracks(self):
        tracks = self.tracks_to_use()
        returns = self.song().return_tracks
        num_strips = len(self._channel_strips)
        for index in range(num_strips):
            track_index = self._track_offset + index
            track = tracks[track_index] if len(tracks) > track_index else None
            self._channel_strips[index].set_track(track)

        for index in range(len(self._return_strips)):
            if len(returns) > index:
                self._return_strips[index].set_track(returns[index])
            else:
                self._return_strips[index].set_track(None)

        turn_button_on_off(self._bank_down_button, on=self._track_offset > 0)
        turn_button_on_off(self._bank_up_button, on=len(tracks) > self._track_offset + num_strips)

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

    def _auto_name(self):
        self.name = 'Mixer'
        self.master_strip().name = 'Master_Channel_Strip'
        self.selected_strip().name = 'Selected_Channel_Strip'
        for index, strip in enumerate(self._channel_strips):
            strip.name = 'Channel_Strip_%d' % index