#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/AutoArmComponent.py
"""
Component that automatically arms the selected track.
"""
from itertools import ifilter
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ModesComponent import LatchingBehaviour
from _Framework.Util import forward_property
from MessageBoxComponent import NotificationComponent

class AutoArmRestoreBehaviour(LatchingBehaviour):
    """
    Mode button behaviour that auto-arm is enabled when the mode is
    activated. If it is not, then it will make the button blink and
    restore it in the second press.
    
    Note that this interface is passive, you have to manually call
    update() to make sure the light is update when the auto-arm
    condition changes.
    """

    def __init__(self, auto_arm = None, *a, **k):
        super(AutoArmRestoreBehaviour, self).__init__(*a, **k)
        self._auto_arm = auto_arm
        self._last_update_params = None

    def _mode_is_active(self, component, mode, selected_mode):
        groups = component.get_mode_groups(mode)
        selected_groups = component.get_mode_groups(selected_mode)
        return mode == selected_mode or bool(groups & selected_groups)

    def press_immediate(self, component, mode):
        super(AutoArmRestoreBehaviour, self).press_immediate(component, mode)
        if self._auto_arm.needs_restore_auto_arm:
            self._auto_arm.restore_auto_arm()

    def update_button(self, component, mode, selected_mode):
        self._last_update_params = (component, mode, selected_mode)
        button = component.get_mode_button(mode)
        if button:
            if self._mode_is_active(component, mode, selected_mode):
                button.set_light('DefaultButton.Alert' if self._auto_arm.needs_restore_auto_arm else True)
            else:
                button.set_light(False)

    def update(self):
        if self._last_update_params:
            self.update_button(*self._last_update_params)


class AutoArmComponent(CompoundComponent):
    """
    Component that implictly arms tracks to keep the selected track
    always armed while there is no compatible red-armed track.
    """

    def __init__(self, *a, **k):
        super(AutoArmComponent, self).__init__(*a, **k)
        self._auto_arm_restore_behaviour = AutoArmRestoreBehaviour(auto_arm=self)
        self._notification = self.register_component(NotificationComponent(notification_time=10.0))
        self._on_tracks_changed.subject = self.song()
        self._on_tracks_changed()

    notification_layer = forward_property('_notification')('message_box_layer')

    @property
    def auto_arm_restore_behaviour(self):
        return self._auto_arm_restore_behaviour

    def can_auto_arm_track(self, track):
        return track.can_be_armed and track.has_midi_input

    def on_selected_track_changed(self):
        self.update()

    def _update_notification(self):
        if self.needs_restore_auto_arm:
            self._notification.show_notification('  Press [Note] to arm the track:    ' + self.song().view.selected_track.name, blink_text='  Press        to arm the track:    ' + self.song().view.selected_track.name)
        else:
            self._notification.hide_notification()

    def update(self):
        song = self.song()
        enabled = self.is_enabled() and not self.needs_restore_auto_arm
        selected_track = song.view.selected_track
        for track in song.tracks:
            if self.can_auto_arm_track(track):
                track.implicit_arm = enabled and selected_track == track

        self._auto_arm_restore_behaviour.update()
        self._update_notification()

    def restore_auto_arm(self):
        for track in self.song().tracks:
            if self.can_auto_arm_track(track):
                track.arm = False

    @property
    def needs_restore_auto_arm(self):
        song = self.song()
        return self.is_enabled() and self.can_auto_arm_track(song.view.selected_track) and not song.view.selected_track.arm and any(ifilter(lambda track: self.can_auto_arm_track(track) and track.arm, song.tracks))

    @subject_slot('tracks')
    def _on_tracks_changed(self):
        tracks = filter(lambda t: t.can_be_armed, self.song().tracks)
        self._on_arm_changed.replace_subjects(tracks)
        self._on_current_input_routing_changed.replace_subjects(tracks)

    @subject_slot_group('arm')
    def _on_arm_changed(self, track):
        self.update()

    @subject_slot_group('current_input_routing')
    def _on_current_input_routing_changed(self, track):
        self.update()