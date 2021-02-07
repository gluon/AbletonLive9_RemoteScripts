# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/auto_arm_component.py
# Compiled at: 2016-09-29 19:13:24
"""
Component that automatically arms the selected track.
"""
from __future__ import absolute_import, print_function
from functools import partial
from itertools import ifilter
from ableton.v2.base import mixin, nop, listens, listens_group
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.mode import LatchingBehaviour
from .message_box_component import Messenger

class AutoArmRestoreBehaviour(LatchingBehaviour):
    """
    Mode button behaviour that auto-arm is enabled when the mode is
    activated. If it is not, then it will make the button blink and
    restore it in the second press.
    
    Note that this interface is passive, you have to manually call
    update() to make sure the light is update when the auto-arm
    condition changes.
    """

    def __init__(self, auto_arm=None, *a, **k):
        super(AutoArmRestoreBehaviour, self).__init__(*a, **k)
        self._auto_arm = auto_arm
        self._last_update_params = None
        self._skip_super = False
        return

    def press_immediate(self, component, mode):
        called_super = False
        if component.selected_mode != mode:
            called_super = True
            super(AutoArmRestoreBehaviour, self).press_immediate(component, mode)
        if self._auto_arm.needs_restore_auto_arm:
            self._auto_arm.restore_auto_arm()
        elif not called_super:
            called_super = True
            super(AutoArmRestoreBehaviour, self).press_immediate(component, mode)
        self._skip_super = not called_super

    def press_delayed(self, component, mode):
        if not self._skip_super:
            super(AutoArmRestoreBehaviour, self).press_delayed(component, mode)

    def release_immediate(self, component, mode):
        if not self._skip_super:
            super(AutoArmRestoreBehaviour, self).release_immediate(component, mode)

    def release_delayed(self, component, mode):
        if not self._skip_super:
            super(AutoArmRestoreBehaviour, self).release_delayed(component, mode)

    def update_button(self, component, mode, selected_mode):
        self._last_update_params = (component, mode, selected_mode)
        button = component.get_mode_button(mode)
        button.mode_selected_color = 'DefaultButton.Alert' if self._auto_arm.needs_restore_auto_arm else 'DefaultButton.On'

    def update(self):
        if self._last_update_params:
            self.update_button(*self._last_update_params)


class AutoArmComponent(Component, Messenger):
    """
    Component that implictly arms tracks to keep the selected track
    always armed while there is no compatible red-armed track.
    """

    def __init__(self, *a, **k):
        super(AutoArmComponent, self).__init__(*a, **k)
        self._auto_arm_restore_behaviour = None
        self._on_tracks_changed.subject = self.song
        self._on_exclusive_arm_changed.subject = self.song
        self._on_tracks_changed()
        self._notification_reference = partial(nop, None)
        self._on_selected_track_changed.subject = self.song.view
        return

    def auto_arm_restore_behaviour(self, *extra_classes, **extra_params):
        if not self._auto_arm_restore_behaviour:
            self._auto_arm_restore_behaviour = mixin(AutoArmRestoreBehaviour, *extra_classes)(auto_arm=self, **extra_params)
        else:
            assert not extra_params and not extra_classes
        return self._auto_arm_restore_behaviour

    def track_can_be_armed(self, track):
        return track.can_be_armed and track.has_midi_input

    def can_auto_arm_track(self, track):
        return self.track_can_be_armed(track)

    @listens('selected_track')
    def _on_selected_track_changed(self):
        self.update()

    def _update_notification(self):
        if self.needs_restore_auto_arm:
            self._notification_reference = self.show_notification('  Press [Note] to arm the track:    ' + self.song.view.selected_track.name, blink_text='  Press        to arm the track:    ' + self.song.view.selected_track.name, notification_time=10.0)
        else:
            self._hide_notification()

    def _hide_notification(self):
        if self._notification_reference() is not None:
            self._notification_reference().hide()
        return

    def update(self):
        super(AutoArmComponent, self).update()
        song = self.song
        enabled = self.is_enabled() and not self.needs_restore_auto_arm
        selected_track = song.view.selected_track
        for track in song.tracks:
            if self.track_can_be_armed(track):
                track.implicit_arm = enabled and selected_track == track and self.can_auto_arm_track(track)

        if self._auto_arm_restore_behaviour:
            self._auto_arm_restore_behaviour.update()
        self._update_notification()

    def restore_auto_arm(self):
        song = self.song
        exclusive_arm = song.exclusive_arm
        for track in song.tracks:
            if exclusive_arm or self.can_auto_arm_track(track):
                if track.can_be_armed:
                    track.arm = False

    @property
    def needs_restore_auto_arm(self):
        song = self.song
        exclusive_arm = song.exclusive_arm
        return self.is_enabled() and self.can_auto_arm_track(song.view.selected_track) and not song.view.selected_track.arm and any(ifilter(lambda track: (exclusive_arm or self.can_auto_arm_track(track)) and track.can_be_armed and track.arm, song.tracks))

    @listens('tracks')
    def _on_tracks_changed(self):
        tracks = filter(lambda t: t.can_be_armed, self.song.tracks)
        self._on_arm_changed.replace_subjects(tracks)
        self._on_input_routing_type_changed.replace_subjects(tracks)
        self._on_frozen_state_changed.replace_subjects(tracks)

    @listens('exclusive_arm')
    def _on_exclusive_arm_changed(self):
        self.update()

    @listens_group('arm')
    def _on_arm_changed(self, track):
        self.update()

    @listens_group('input_routing_type')
    def _on_input_routing_type_changed(self, track):
        self.update()

    @listens_group('is_frozen')
    def _on_frozen_state_changed(self, track):
        self.update()