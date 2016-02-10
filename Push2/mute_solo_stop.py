#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/mute_solo_stop.py
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.base import listenable_property, listens, listens_group, liveobj_valid, MultiSlot, SlotManager, Subject
from ableton.v2.control_surface import Component, CompoundComponent, Layer
from ableton.v2.control_surface.control import ButtonControl
from pushbase.message_box_component import Messenger
from .track_list import toggle_mixable_mute, toggle_mixable_solo
GLOBAL_ACTION_LOCK_MODE_DELAY = 0.6

def stop_clip_in_selected_track(song):
    selected_track = song.view.selected_track
    if selected_track != song.master_track and selected_track not in song.return_tracks:
        selected_track.stop_all_clips()


class TrackStateColorIndicator(Subject, SlotManager):
    color = listenable_property.managed('DefaultButton.On')

    def __init__(self, item_provider = None, track_property = None, property_active_color = None, song = None, *a, **k):
        super(TrackStateColorIndicator, self).__init__(*a, **k)
        self._provider = item_provider
        self._active_color = property_active_color
        self._property = track_property
        self._song = song
        self.__on_items_changed.subject = item_provider
        self.register_slot(MultiSlot(listener=self.__on_property_changed, event=('selected_item', track_property), subject=item_provider))
        self._update_color()

    @listens('items')
    def __on_items_changed(self):
        self._update_color()

    def __on_property_changed(self):
        self._update_color()

    def _update_color(self):
        selected_mixable = self._provider.selected_item
        use_active_color = liveobj_valid(selected_mixable) and selected_mixable != self._song.master_track and getattr(selected_mixable, self._property)
        self.color = self._active_color if use_active_color else 'DefaultButton.On'


class GlobalMixerActionComponent(Component):
    action_button = ButtonControl(delay_time=GLOBAL_ACTION_LOCK_MODE_DELAY)

    def __init__(self, track_list_component = None, mode = None, immediate_action = None, default_color_indicator = None, mode_locked_color = None, mode_active_color = None, *a, **k):
        if not track_list_component is not None:
            raise AssertionError
            raise mode is not None or AssertionError
            raise mode in track_list_component.modes or AssertionError
            super(GlobalMixerActionComponent, self).__init__(*a, **k)
            self._mode = mode
            self._immediate_action = immediate_action
            self._mode_locked = False
            self._default_color_indicator = None
            self._locked_color = mode_locked_color
            self._active_color = mode_active_color if mode_active_color is not None else 'DefaultButton.On'
            self._allow_released_immediately_action = True
            self._track_list_component = track_list_component
            self._default_color_indicator = default_color_indicator is not None and self.register_disconnectable(default_color_indicator)
            self.__on_default_color_changed.subject = default_color_indicator
        self._update_default_color()

    @listenable_property
    def mode_locked(self):
        return self._mode_locked

    @property
    def mode(self):
        return self._mode

    def cancel_release_action(self):
        self._allow_released_immediately_action = False

    def cancel_locked_mode(self):
        self._track_list_component.pop_mode(self._mode)
        self._mode_locked = False
        self._update_default_color()

    @listens('color')
    def __on_default_color_changed(self, _):
        self._update_default_color()

    @action_button.released_immediately
    def action_button(self, button):
        if self._allow_released_immediately_action:
            self._immediate_action()

    @action_button.pressed
    def action_button(self, button):
        if self._mode_locked:
            self._allow_released_immediately_action = False
            self._unlock_mode()
        else:
            self._allow_released_immediately_action = True
            self._track_list_component.push_mode(self._mode)
            self.action_button.color = self._active_color

    @action_button.pressed_delayed
    def action_button(self, button):
        if self._allow_released_immediately_action:
            self._lock_mode()

    @action_button.released
    def action_button(self, button):
        if not self._mode_locked:
            self._track_list_component.pop_mode(self._mode)
            self._update_default_color()

    def _lock_mode(self):
        self._mode_locked = True
        self.action_button.color = self._locked_color
        self.notify_mode_locked(self._mode_locked)

    def _unlock_mode(self):
        self.cancel_locked_mode()
        self.notify_mode_locked(self._mode_locked)

    def _update_default_color(self):
        if self._mode not in self._track_list_component.active_modes:
            self.action_button.color = self._default_color_indicator.color if self._default_color_indicator else 'DefaultButton.On'


class MuteSoloStopClipComponent(CompoundComponent, Messenger):
    MESSAGE_FOR_MODE = {'mute': 'Mute: %s',
     'solo': 'Solo: %s',
     'stop': 'Stop Clips: %s'}
    stop_all_clips_button = ButtonControl()

    def __init__(self, item_provider = None, solo_track_button = None, mute_track_button = None, stop_clips_button = None, track_list_component = None, cancellation_action_performers = [], *a, **k):
        super(MuteSoloStopClipComponent, self).__init__(*a, **k)
        self._currently_locked_button_handler = None
        self._track_list = track_list_component
        self._solo_button_handler = self.register_component(GlobalMixerActionComponent(track_list_component=track_list_component, mode='solo', mode_active_color='Mixer.SoloOn', mode_locked_color='Mixer.LockedSoloMode', default_color_indicator=TrackStateColorIndicator(item_provider=item_provider, track_property='solo', property_active_color='Mixer.SoloOn', song=self.song), immediate_action=lambda : toggle_mixable_solo(item_provider.selected_item, self.song)))
        self._solo_button_handler.layer = Layer(action_button=solo_track_button)
        self._mute_button_handler = self.register_component(GlobalMixerActionComponent(track_list_component=track_list_component, mode='mute', mode_active_color='Mixer.MuteOff', mode_locked_color='Mixer.LockedMuteMode', default_color_indicator=TrackStateColorIndicator(item_provider=item_provider, track_property='mute', property_active_color='Mixer.MuteOff', song=self.song), immediate_action=lambda : toggle_mixable_mute(item_provider.selected_item, self.song)))
        self._mute_button_handler.layer = Layer(action_button=mute_track_button)
        self._stop_button_handler = self.register_component(GlobalMixerActionComponent(track_list_component=track_list_component, mode='stop', immediate_action=partial(stop_clip_in_selected_track, self.song), mode_locked_color='StopClips.LockedStopMode'))
        self._stop_button_handler.layer = Layer(action_button=stop_clips_button)
        self.__on_mute_solo_stop_cancel_action_performed.replace_subjects([track_list_component] + cancellation_action_performers)
        button_handlers = (self._mute_button_handler, self._solo_button_handler, self._stop_button_handler)
        self.__on_mode_locked_changed.replace_subjects(button_handlers, button_handlers)
        self.__on_selected_item_changed.subject = item_provider

    @stop_all_clips_button.pressed
    def stop_all_clips_button(self, button):
        self.song.stop_all_clips()

    @listens_group('mute_solo_stop_cancel_action_performed')
    def __on_mute_solo_stop_cancel_action_performed(self, _):
        self.cancel_release_actions()

    @listens_group('mode_locked')
    def __on_mode_locked_changed(self, is_locked, button_handler):
        if is_locked:
            if self._currently_locked_button_handler:
                self._currently_locked_button_handler.cancel_locked_mode()
            self._currently_locked_button_handler = button_handler
        else:
            self._currently_locked_button_handler = None
        self._track_list.locked_mode = self._currently_locked_button_handler.mode if is_locked else None
        self._show_mode_lock_change_notification(is_locked, button_handler.mode)

    @listens('selected_item')
    def __on_selected_item_changed(self):
        self.cancel_release_actions()

    def _show_mode_lock_change_notification(self, is_locked, mode):
        message_template = self.MESSAGE_FOR_MODE[mode]
        message_part = 'Locked' if is_locked else 'Unlocked'
        self.show_notification(message_template % message_part)

    def cancel_release_actions(self):
        self._solo_button_handler.cancel_release_action()
        self._mute_button_handler.cancel_release_action()
        self._stop_button_handler.cancel_release_action()