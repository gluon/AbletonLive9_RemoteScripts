#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/mixer_component.py
from itertools import izip
from ableton.v2.base import find_if, listenable_property, listens, listens_group, liveobj_valid, Subject, task
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v2.control_surface.components import ChannelStripComponent as ChannelStripComponentBase
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.mode import AddLayerMode, ModesComponent
from .track_selection import get_all_mixer_tracks, mixable_button_color

class MixerDeviceMuteSoloComponent(Component):
    mute_button = ButtonControl()
    solo_button = ButtonControl()
    __events__ = ('mute_or_solo_pressed',)

    def __init__(self, *a, **k):
        super(MixerDeviceMuteSoloComponent, self).__init__(*a, **k)
        self.mute_button.enabled = False
        self.solo_button.enabled = False

    def set_track(self, track):
        self._track = track
        enabled_state = True if self._track is not None else False
        self.mute_button.enabled = enabled_state
        self.solo_button.enabled = enabled_state

    @property
    def track(self):
        return self._track

    @mute_button.pressed
    def mute_button(self, button):
        self.toggle_mute()
        self.notify_mute_or_solo_pressed()

    def toggle_mute(self):
        if self._track:
            self._track.mute = not self._track.mute

    @solo_button.pressed
    def solo_button(self, button):
        self.toggle_solo()
        self.notify_mute_or_solo_pressed()

    def toggle_solo(self):
        if self._track and self._track != self.song.master_track:
            song = self.song
            tracks = get_all_mixer_tracks(song)
            other_solos = any([ track.solo for track in tracks ])
            if other_solos and song.exclusive_solo and not self._track.solo:
                for track in tracks:
                    track.solo = False

            self._track.solo = not self._track.solo


class MixerButtonStateManager(Subject):
    is_pressed = listenable_property.managed(False)


class MixerComponent(MixerComponentBase, ModesComponent):
    solo_track_button = ButtonControl()
    mute_track_button = ButtonControl()
    MIXER_BUTTON_STATE_DELAY = 0.1

    def __init__(self, solo_layer = None, mute_layer = None, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)
        self._allow_released_immediately_action = True
        self.mixer_button_state = self.register_disconnectable(MixerButtonStateManager())
        self._mixer_button_state_task = self._tasks.add(task.sequence(task.wait(self.MIXER_BUTTON_STATE_DELAY), task.run(self._update_mixer_button_state))).kill()
        self.add_mode('default', None)
        self.add_mode('solo', AddLayerMode(self, solo_layer))
        self.add_mode('mute', AddLayerMode(self, mute_layer))
        self.selected_mode = 'default'
        self._on_items_changed.subject = self._provider
        self._on_selected_item_changed.subject = self._provider
        self._on_selected_item_changed()
        self._update_channel_strip_button_colors()
        self.__on_channel_strip_mute_or_solo_changed.replace_subjects(self._channel_strips)

    @listens_group('mute_or_solo_pressed')
    def __on_channel_strip_mute_or_solo_changed(self, _):
        self._allow_released_immediately_action = False

    def _create_strip(self):
        return MixerDeviceMuteSoloComponent()

    def _create_master_strip(self):
        return ChannelStripComponentBase()

    @listens('items')
    def _on_items_changed(self):
        mixer_tracks = self._provider.items
        for track, channel_strip in izip(mixer_tracks, self._channel_strips):
            channel_strip.set_track(track)

        self._on_solo_changed.replace_subjects(mixer_tracks)
        self._on_mute_changed.replace_subjects(mixer_tracks)
        self._update_button_state_colors()
        self._update_channel_strip_button_colors()

    def set_mute_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            strip.mute_button.set_control_element(button)

    def set_solo_buttons(self, buttons):
        for strip, button in map(None, self._channel_strips, buttons or []):
            strip.solo_button.set_control_element(button)

    def _reassign_tracks(self):
        self._on_items_changed()

    def _update_selected_strip(self):
        """
        We are not interested in setting the selected channel strip, which occurs in the
        base mixer component.
        """
        pass

    def _update_send_index(self):
        """
        We are not interested in the base mixer's send index, which is updated when the
        return tracks change. This also reassigns the send_controls, which we are not
        interested in doing.
        """
        pass

    def _mute_or_solo_is_pressed(self):
        return self.solo_track_button.is_pressed or self.mute_track_button.is_pressed

    def _update_mixer_button_state(self):
        self.mixer_button_state.is_pressed = self._mute_or_solo_is_pressed()

    @listens('selected_item')
    def _on_selected_item_changed(self):
        self._update_button_state_colors()
        self._update_channel_strip_button_colors()

    @listens_group('solo')
    def _on_solo_changed(self, mixable):
        self._update_button_state_colors()
        self._update_channel_strip_button_colors()

    @listens_group('mute')
    def _on_mute_changed(self, mixable):
        self._update_button_state_colors()
        self._update_channel_strip_button_colors()

    @solo_track_button.released_immediately
    def solo_track_button(self, button):
        if self._allow_released_immediately_action:
            self._toggle_channel_strip_property(lambda channel_strip: channel_strip.toggle_solo())

    @solo_track_button.pressed
    def solo_track_button(self, button):
        self._allow_released_immediately_action = True
        self.push_mode('solo')
        self._mixer_button_state_task.restart()

    @solo_track_button.released
    def solo_track_button(self, button):
        self.pop_mode('solo')
        self.mixer_button_state.is_pressed = self._mute_or_solo_is_pressed()
        self._update_button_state_colors()

    @mute_track_button.released_immediately
    def mute_track_button(self, button):
        if self._allow_released_immediately_action:
            self._toggle_channel_strip_property(lambda channel_strip: channel_strip.toggle_mute())

    @mute_track_button.pressed
    def mute_track_button(self, button):
        self._allow_released_immediately_action = True
        self.push_mode('mute')
        self._mixer_button_state_task.restart()

    @mute_track_button.released
    def mute_track_button(self, button):
        self.pop_mode('mute')
        self.mixer_button_state.is_pressed = self._mute_or_solo_is_pressed()
        self._update_button_state_colors()

    def _toggle_channel_strip_property(self, toggle_function):
        channel_strip = self._get_selected_track_channel_strip()
        if channel_strip:
            toggle_function(channel_strip)

    def _get_selected_track_channel_strip(self):
        selected_track = self._provider.selected_item
        return find_if(lambda strip: strip.track == selected_track, self._channel_strips)

    def _update_channel_strip_button_colors(self):
        song = self.song
        for strip in self._channel_strips:
            color = mixable_button_color(strip.track, song, self._provider.selected_item)
            strip.mute_button.color = color
            strip.solo_button.color = color

    def _update_button_state_colors(self):
        song = self.song
        selected_track = self._provider.selected_item
        if selected_track != song.master_track:
            self.mute_track_button.color = self._get_track_state_mode_state('mute', selected_track.mute if liveobj_valid(selected_track) else False, 'Mixer.MuteOff')
            self.solo_track_button.color = self._get_track_state_mode_state('solo', selected_track.solo if liveobj_valid(selected_track) else False, 'Mixer.SoloOn')

    def _get_track_state_mode_state(self, mode, track_state_parameter, on_color):
        return on_color if track_state_parameter or self.selected_mode == mode else 'DefaultButton.On'