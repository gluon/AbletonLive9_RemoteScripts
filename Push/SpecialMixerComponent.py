#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/SpecialMixerComponent.py
from _Framework.SubjectSlot import subject_slot
from _Framework.MixerComponent import MixerComponent
from _Framework.DisplayDataSource import DisplayDataSource
from SpecialChanStripComponent import SpecialChanStripComponent

def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)


class SpecialMixerComponent(MixerComponent):
    """
    Special mixer class that uses return tracks alongside midi and
    audio tracks.  This provides also a more convenient interface to
    set controls for the different modes of Push.
    """
    num_label_segments = 4

    def __init__(self, *a, **k):
        super(SpecialMixerComponent, self).__init__(*a, **k)
        self._pan_send_index = 0
        self._pan_send_controls = None
        self._pan_send_names_display = None
        self._pan_send_values_display = None
        self._pan_send_graphics_display = None
        self._pan_send_toggle_skip = False
        self._selected_track_data_sources = map(DisplayDataSource, ('',) * self.num_label_segments)
        self._selected_track_data_sources[0].set_display_string('Track Selection:')
        self._selected_track_name_data_source = self._selected_track_data_sources[1]
        self._on_selected_track_changed.subject = self.song().view
        self._update_selected_track_name()

    def tracks_to_use(self):
        return tracks_to_use_from_song(self.song())

    def _create_strip(self):
        return SpecialChanStripComponent()

    def set_pan_send_toggle(self, toggle):
        """
        The pan_send_toggle cycles through the different pan, or send
        modes changing the bejhaviour of the pan_send display and
        controls.
        """
        self._pan_send_toggle = toggle
        self._on_pan_send_value.subject = toggle
        self._pan_send_toggle_skip = True

    def set_selected_values_display(self, display):
        if display:
            sources = [ self.selected_strip().track_parameter_data_sources(index) for index in xrange(8) ]
            display.set_data_sources(sources)

    def set_selected_graphics_display(self, display):
        if display:
            sources = [ self.selected_strip().track_parameter_graphic_sources(index) for index in xrange(8) ]
            display.set_data_sources(sources)

    def set_selected_names_display(self, display):
        if display:
            sources = [ self.selected_strip().track_parameter_name_sources(index) for index in xrange(8) ]
            display.set_data_sources(sources)

    def set_selected_track_name_display(self, display):
        if display:
            display.set_data_sources(self._selected_track_data_sources)

    def set_track_select_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Option.Selected', 'Option.Unselected')
            strip.set_select_button(button)

    def set_solo_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.SoloOn', 'Mixer.SoloOff')
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.MuteOff', 'Mixer.MuteOn')
            strip.set_mute_button(button)

    def set_track_names_display(self, display):
        if display:
            sources = [ strip.track_name_data_source() for strip in self._channel_strips ]
            display.set_data_sources(sources)

    def set_volume_names_display(self, display):
        self._set_parameter_names_display(display, 0)

    def set_volume_values_display(self, display):
        self._set_parameter_values_display(display, 0)

    def set_volume_graphics_display(self, display):
        self._set_parameter_graphics_display(display, 0)

    def set_volume_controls(self, controls):
        for strip, control in map(None, self._channel_strips, controls or []):
            strip.set_volume_control(control)

    def set_pan_send_names_display(self, display):
        self._normalize_pan_send_index()
        self._pan_send_names_display = display
        self._set_parameter_names_display(display, self._pan_send_index + 1)

    def set_pan_send_values_display(self, display):
        self._normalize_pan_send_index()
        self._pan_send_values_display = display
        self._set_parameter_values_display(display, self._pan_send_index + 1)

    def set_pan_send_graphics_display(self, display):
        self._normalize_pan_send_index()
        self._pan_send_graphics_display = display
        self._set_parameter_graphics_display(display, self._pan_send_index + 1)

    def set_pan_send_controls(self, controls):
        self.set_send_controls(None)
        self.set_pan_controls(None)
        self._pan_send_controls = controls
        self._normalize_pan_send_index()
        if self._pan_send_index == 0:
            self.set_pan_controls(controls)
        else:
            sends = self._pan_send_index - 1
            self.set_send_controls(map(lambda ctl: (None,) * sends + (ctl,), controls or []))

    def set_selected_controls(self, controls):
        strip = self.selected_strip()
        if controls:
            strip.set_volume_control(controls[0])
            strip.set_pan_control(controls[1])
            strip.set_send_controls(controls[2:])
        else:
            strip.set_volume_control(None)
            strip.set_pan_control(None)
            strip.set_send_controls(tuple())

    def on_track_list_changed(self):
        super(SpecialMixerComponent, self).on_track_list_changed()
        self._update_pan_sends()

    def set_pan_controls(self, controls):
        for strip, control in map(None, self._channel_strips, controls or []):
            strip.set_pan_control(control)

    def set_send_controls(self, controls):
        for strip, control in map(None, self._channel_strips, controls or []):
            strip.set_send_controls(control)

    def _set_parameter_names_display(self, display, parameter):
        if display:
            sources = [ strip.track_parameter_name_sources(parameter) for strip in self._channel_strips ]
            display.set_data_sources(sources)

    def _set_parameter_values_display(self, display, parameter):
        if display:
            sources = [ strip.track_parameter_data_sources(parameter) for strip in self._channel_strips ]
            display.set_data_sources(sources)

    def _set_parameter_graphics_display(self, display, parameter):
        if display:
            sources = [ strip.track_parameter_graphic_sources(parameter) for strip in self._channel_strips ]
            display.set_data_sources(sources)

    @subject_slot('value')
    def _on_pan_send_value(self, value):
        if not self._pan_send_toggle_skip and self.is_enabled() and (value or not self._pan_send_toggle.is_momentary()):
            self._pan_send_index += 1
            self._update_pan_sends()
        self._pan_send_toggle_skip = False

    def _update_pan_sends(self):
        self.set_pan_send_controls(self._pan_send_controls)
        self.set_pan_send_names_display(self._pan_send_names_display)
        self.set_pan_send_graphics_display(self._pan_send_graphics_display)

    def _normalize_pan_send_index(self):
        if len(self.song().tracks) == 0 or self._pan_send_index > len(self.song().tracks[0].mixer_device.sends):
            self._pan_send_index = 0

    def _reassign_tracks(self):
        tracks = self.tracks_to_use()
        returns = self.song().return_tracks
        num_empty_tracks = max(0, len(self._channel_strips) + self._track_offset - len(tracks))
        num_visible_tracks = max(0, len(tracks) - len(returns) - self._track_offset)
        num_visible_returns = len(self._channel_strips) - num_empty_tracks - num_visible_tracks
        for index in range(len(self._channel_strips)):
            track_index = self._track_offset + index
            if len(tracks) > track_index:
                track = tracks[track_index]
                if tracks[track_index] not in returns:
                    self._channel_strips[index].set_track(track)
                else:
                    self._channel_strips[index + num_empty_tracks].set_track(track)
            else:
                self._channel_strips[index - num_visible_returns].set_track(None)

    @subject_slot('selected_track.name')
    def _on_selected_track_changed(self):
        self._update_selected_track_name()

    def _update_selected_track_name(self):
        selected = self.song().view.selected_track
        self._selected_track_name_data_source.set_display_string(selected.name)