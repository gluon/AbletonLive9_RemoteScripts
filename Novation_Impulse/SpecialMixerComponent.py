#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Novation_Impulse/SpecialMixerComponent.py
from _Framework.MixerComponent import MixerComponent
from _Framework.ButtonElement import ButtonElement

class SpecialMixerComponent(MixerComponent):
    """ Special mixer class that reassigns buttons to mute or solo based on a toggle """

    def __init__(self, num_tracks):
        self._shift_button = None
        self._selected_mute_solo_button = None
        self._strip_mute_solo_buttons = None
        self._mute_solo_flip_button = None
        MixerComponent.__init__(self, num_tracks)
        self._selected_tracks = []
        self._register_timer_callback(self._on_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        self._selected_tracks = None
        MixerComponent.disconnect(self)
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None
        if self._mute_solo_flip_button != None:
            self._mute_solo_flip_button.remove_value_listener(self._mute_solo_flip_value)
            self._mute_solo_flip_button = None
        self._selected_mute_solo_button = None
        self._strip_mute_solo_buttons = None

    def set_shift_button(self, shift_button):
        if not (shift_button == None or shift_button.is_momentary()):
            raise AssertionError
            if self._shift_button != None:
                self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = shift_button
            self._shift_button != None and self._shift_button.add_value_listener(self._shift_value)

    def set_selected_mute_solo_button(self, button):
        raise isinstance(button, (type(None), ButtonElement)) or AssertionError
        self._selected_mute_solo_button = button
        self.selected_strip().set_mute_button(self._selected_mute_solo_button)
        self.selected_strip().set_solo_button(None)

    def set_strip_mute_solo_buttons(self, buttons, flip_button):
        if not (buttons is None or isinstance(buttons, tuple) and len(buttons) == len(self._channel_strips)):
            raise AssertionError
            if not isinstance(flip_button, (type(None), ButtonElement)):
                raise AssertionError
                self._mute_solo_flip_button != None and self._mute_solo_flip_button.remove_value_listener(self._mute_solo_flip_value)
            self._mute_solo_flip_button = flip_button
            self._mute_solo_flip_button != None and self._mute_solo_flip_button.add_value_listener(self._mute_solo_flip_value)
        self._strip_mute_solo_buttons = buttons
        for index in range(len(self._channel_strips)):
            strip = self.channel_strip(index)
            button = None
            if self._strip_mute_solo_buttons != None:
                button = self._strip_mute_solo_buttons[index]
            strip.set_mute_button(button)
            strip.set_solo_button(None)

    def tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    def _shift_value(self, value):
        if not self._shift_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            value > 0 and self.selected_strip().set_mute_button(None)
            self.selected_strip().set_solo_button(self._selected_mute_solo_button)
        else:
            self.selected_strip().set_solo_button(None)
            self.selected_strip().set_mute_button(self._selected_mute_solo_button)

    def _mute_solo_flip_value(self, value):
        raise self._mute_solo_flip_button != None or AssertionError
        raise value in range(128) or AssertionError
        if self._strip_mute_solo_buttons != None:
            for index in range(len(self._strip_mute_solo_buttons)):
                strip = self.channel_strip(index)
                if value == 0:
                    strip.set_mute_button(None)
                    strip.set_solo_button(self._strip_mute_solo_buttons[index])
                else:
                    strip.set_solo_button(None)
                    strip.set_mute_button(self._strip_mute_solo_buttons[index])

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