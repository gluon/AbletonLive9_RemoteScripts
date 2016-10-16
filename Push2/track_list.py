#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/track_list.py
from __future__ import absolute_import, print_function
from functools import partial
from itertools import chain, izip
import Live
from ableton.v2.base import nop, listenable_property, listens, listens_group, liveobj_valid
from ableton.v2.control_surface.control import ButtonControl, control_list
from ableton.v2.control_surface.mode import ModeButtonBehaviour, ModesComponent
from pushbase.actions import is_clip_stop_pending
from pushbase.consts import MessageBoxText
from pushbase.message_box_component import Messenger
from pushbase.special_chan_strip_component import toggle_arm
from .colors import make_blinking_track_color, make_pulsing_track_color, translate_color_index
from .mixable_utilities import can_play_clips, is_chain
from .skin_default import RECORDING_COLOR, UNLIT_COLOR
from .track_selection import get_all_mixer_tracks, SelectedMixerTrackProvider
DeviceType = Live.Device.DeviceType

def track_color_with_pending_stop(track):
    return make_blinking_track_color(track, UNLIT_COLOR)


def mixable_button_color(mixer_track, song, selected_track = None):
    color = 'Mixer.NoTrack'
    if mixer_track:
        if can_play_clips(mixer_track) and is_clip_stop_pending(mixer_track):
            color = track_color_with_pending_stop(mixer_track)
        elif mixer_track.solo:
            color = 'Mixer.SoloOn'
        elif mixer_track == selected_track and not mixer_track.mute:
            color = 'Mixer.TrackSelected'
        elif mixer_track.mute or mixer_track.muted_via_solo:
            color = 'Mixer.MutedTrack'
        else:
            color = translate_color_index(mixer_track.color_index)
    return color


def stop_clip_button_color(track, song, _):
    if liveobj_valid(track) and not is_chain(track) and bool(track.clip_slots):
        if is_clip_stop_pending(track):
            return track_color_with_pending_stop(track)
        elif track.playing_slot_index >= 0:
            if track.solo:
                return 'StopClips.SoloedTrack'
            if track.mute:
                return 'StopClips.MutedTrack'
            if track.clip_slots[track.playing_slot_index].is_recording:
                pulse_to = RECORDING_COLOR
            else:
                pulse_to = UNLIT_COLOR
            return make_pulsing_track_color(track, pulse_to)
        else:
            return 'Session.StoppedClip'
    else:
        return 'Mixer.NoTrack'


def toggle_mixable_mute(mixable, song):
    if mixable != song.master_track:
        mixable.mute = not mixable.mute


def toggle_mixable_solo(mixable, song):
    if mixable != song.master_track:
        tracks = get_all_mixer_tracks(song)
        other_solos = any([ track.solo for track in tracks ])
        if other_solos and song.exclusive_solo and not mixable.solo:
            for track in tracks:
                track.solo = False

        mixable.solo = not mixable.solo


class TrackListBehaviour(ModeButtonBehaviour):

    def press_immediate(self, component, mode):
        component.push_mode(mode)

    def release_delayed(self, component, mode):
        self.release_immediate(component, mode)

    def release_immediate(self, component, mode):
        component.pop_mode(mode)


class TrackListComponent(ModesComponent, Messenger):
    """
    Notifies whenever a track action is executed, e.g. deleting or duplicating. But
    selection does *not* count as an action.
    """
    __events__ = ('mute_solo_stop_cancel_action_performed',)
    track_action_buttons = control_list(ButtonControl, control_count=8)

    def __init__(self, tracks_provider = None, trigger_recording_on_release_callback = nop, *a, **k):
        raise tracks_provider is not None or AssertionError
        super(TrackListComponent, self).__init__(*a, **k)
        self.locked_mode = None
        self._button_handler = self._select_mixable
        self._button_feedback_provider = mixable_button_color
        self._setup_action_mode('select', handler=self._select_mixable)
        self._setup_action_mode('lock_override', handler=self._select_mixable)
        self._setup_action_mode('delete', handler=self._delete_mixable)
        self._setup_action_mode('duplicate', handler=self._duplicate_mixable)
        self._setup_action_mode('arm', handler=self._arm_track)
        self._setup_action_mode('mute', handler=partial(toggle_mixable_mute, song=self.song))
        self._setup_action_mode('solo', handler=partial(toggle_mixable_solo, song=self.song))
        self._setup_action_mode('stop', handler=self._stop_track_clip, feedback_provider=stop_clip_button_color)
        self.selected_mode = 'select'
        self._can_trigger_recording_callback = trigger_recording_on_release_callback
        self._track_provider = tracks_provider
        self._selected_track = self.register_disconnectable(SelectedMixerTrackProvider())
        self.__on_items_changed.subject = self._track_provider
        self.__on_selected_item_changed.subject = self._track_provider
        self.__on_tracks_changed.subject = self.song
        self.__on_selected_track_changed.subject = self.song.view
        self._update_track_and_chain_listeners()
        self._update_button_enabled_state()
        self._update_all_button_colors()

    @listenable_property
    def tracks(self):
        return self._track_provider.items

    @listenable_property
    def selected_track(self):
        return self._track_provider.selected_item

    @listenable_property
    def absolute_selected_track_index(self):
        song = self.song
        tracks = song.tracks + song.return_tracks + (song.master_track,)
        selected_track = song.view.selected_track
        return list(tracks).index(selected_track)

    def _setup_action_mode(self, name, handler, feedback_provider = mixable_button_color):
        self.add_mode(name, partial(self._enter_action_mode, handler=handler, feedback_provider=feedback_provider), behaviour=TrackListBehaviour())
        self.get_mode_button(name).mode_selected_color = 'DefaultButton.Transparent'
        self.get_mode_button(name).mode_unselected_color = 'DefaultButton.Transparent'

    def _enter_action_mode(self, handler, feedback_provider):
        self._button_handler = handler
        if feedback_provider != self._button_feedback_provider:
            self._button_feedback_provider = feedback_provider
            self._update_all_button_colors()

    @listens('tracks')
    def __on_tracks_changed(self):
        self._update_track_and_chain_listeners()
        self._update_button_enabled_state()

    @listens_group('mute')
    def __on_track_mute_state_changed(self, track):
        self._update_all_button_colors()

    @listens_group('solo')
    def __on_track_solo_state_changed(self, track):
        self._update_all_button_colors()

    @listens_group('fired_slot_index')
    def __on_track_fired_slot_changed(self, track):
        self._update_all_button_colors()

    @listens_group('playing_slot_index')
    def __on_track_playing_slot_changed(self, _):
        self._update_all_button_colors()

    @listens('items')
    def __on_items_changed(self):
        self._update_track_and_chain_listeners()
        self._update_button_enabled_state()

    def _update_track_and_chain_listeners(self):
        self.notify_tracks()
        self.__on_track_color_index_changed.replace_subjects(self.tracks)
        tracks_without_chains = filter(can_play_clips, self.tracks)
        self.__on_track_fired_slot_changed.replace_subjects(tracks_without_chains)
        self.__on_track_playing_slot_changed.replace_subjects(tracks_without_chains)
        all_tracks = [ _ for _ in chain(self.song.tracks, self.tracks) ]
        self.__on_track_mute_state_changed.replace_subjects(all_tracks)
        self.__on_track_solo_state_changed.replace_subjects(all_tracks)
        self.__on_track_muted_via_solo_changed.replace_subjects(all_tracks)
        self._update_button_enabled_state()
        self._update_all_button_colors()

    def _update_button_enabled_state(self):
        tracks = self.tracks
        for track, control in izip(tracks, self.track_action_buttons):
            control.enabled = liveobj_valid(track)

    @listens_group('color_index')
    def __on_track_color_index_changed(self, _):
        self._update_all_button_colors()

    @listens('selected_item')
    def __on_selected_item_changed(self):
        self.notify_selected_track()
        self._update_all_button_colors()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        self.notify_absolute_selected_track_index()

    @listens_group('muted_via_solo')
    def __on_track_muted_via_solo_changed(self, mixable):
        self._update_all_button_colors()

    def _update_all_button_colors(self):
        for index, mixer_track in enumerate(self.tracks):
            color = self._button_feedback_provider(mixer_track, self.song, self.selected_track)
            self.track_action_buttons[index].color = color

    @track_action_buttons.pressed
    def track_action_buttons(self, button):
        self._button_handler(self.tracks[button.index])
        if self.selected_mode != 'select':
            self.notify_mute_solo_stop_cancel_action_performed()

    def _select_mixable(self, track):
        if track:
            if self._track_provider.selected_item != track:
                self._track_provider.selected_item = track
            else:
                if hasattr(track, 'is_foldable') and track.is_foldable:
                    track.fold_state = not track.fold_state
                if hasattr(track, 'is_showing_chains') and track.can_show_chains:
                    track.is_showing_chains = not track.is_showing_chains

    @staticmethod
    def can_duplicate_or_delete(track_or_chain, return_tracks):
        unwrapped = track_or_chain.proxied_object
        return isinstance(unwrapped, Live.Track.Track) and unwrapped not in list(return_tracks)

    def _delete_mixable(self, track_or_chain):
        if self.can_duplicate_or_delete(track_or_chain, self.song.return_tracks):
            try:
                track_index = list(self.song.tracks).index(track_or_chain)
                name = track_or_chain.name
                self.song.delete_track(track_index)
                self.show_notification(MessageBoxText.DELETE_TRACK % name)
            except RuntimeError:
                self.show_notification(MessageBoxText.TRACK_DELETE_FAILED)

    def _duplicate_mixable(self, track_or_chain):
        if self.can_duplicate_or_delete(track_or_chain, self.song.return_tracks):
            try:
                track_index = list(self.song.tracks).index(track_or_chain)
                self.song.duplicate_track(track_index)
                self.show_notification(MessageBoxText.DUPLICATE_TRACK % track_or_chain.name)
                self._update_all_button_colors()
            except Live.Base.LimitationError:
                self.show_notification(MessageBoxText.TRACK_LIMIT_REACHED)
            except RuntimeError:
                self.show_notification(MessageBoxText.TRACK_DUPLICATION_FAILED)

    def _arm_track(self, track_or_chain):
        if not is_chain(track_or_chain) and track_or_chain.can_be_armed:
            song = self.song
            toggle_arm(track_or_chain, song, exclusive=song.exclusive_arm)
        self._can_trigger_recording_callback(False)

    def _stop_track_clip(self, mixable):
        if not is_chain(mixable):
            mixable.stop_all_clips()

    def on_enabled_changed(self):
        super(TrackListComponent, self).on_enabled_changed()
        if not self.is_enabled():
            self.selected_mode = 'select'
            self.pop_unselected_modes()
        elif self.locked_mode is not None:
            self.push_mode(self.locked_mode)