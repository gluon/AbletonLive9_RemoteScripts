#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/ChannelStripComponent.py
import Live
from itertools import chain
from ControlSurfaceComponent import ControlSurfaceComponent
from ButtonElement import ButtonElement
from EncoderElement import EncoderElement
from DisplayDataSource import DisplayDataSource
from _Framework.Util import nop

class ChannelStripComponent(ControlSurfaceComponent):
    """ Class attaching to the mixer of a given track """
    _active_instances = []

    def number_of_arms_pressed():
        result = 0
        for strip in ChannelStripComponent._active_instances:
            if not isinstance(strip, ChannelStripComponent):
                raise AssertionError
                strip.arm_button_pressed() and result += 1

        return result

    number_of_arms_pressed = staticmethod(number_of_arms_pressed)

    def number_of_solos_pressed():
        result = 0
        for strip in ChannelStripComponent._active_instances:
            if not isinstance(strip, ChannelStripComponent):
                raise AssertionError
                strip.solo_button_pressed() and result += 1

        return result

    number_of_solos_pressed = staticmethod(number_of_solos_pressed)
    empty_color = None

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        ChannelStripComponent._active_instances.append(self)
        self._track = None
        self._send_controls = []
        self._pan_control = None
        self._volume_control = None
        self._select_button = None
        self._mute_button = None
        self._solo_button = None
        self._arm_button = None
        self._shift_button = None
        self._crossfade_toggle = None
        self._track_name_data_source = None
        self._shift_pressed = False
        self._solo_pressed = False
        self._arm_pressed = False
        self._invert_mute_feedback = False
        self._empty_control_slots = self.register_slot_manager()

    def disconnect(self):
        """ releasing references and removing listeners"""
        ChannelStripComponent._active_instances.remove(self)
        if self._select_button != None:
            self._select_button.remove_value_listener(self._select_value)
            self._select_button.reset()
            self._select_button = None
        if self._mute_button != None:
            self._mute_button.remove_value_listener(self._mute_value)
            self._mute_button.reset()
            self._mute_button = None
        if self._solo_button != None:
            self._solo_button.remove_value_listener(self._solo_value)
            self._solo_button.reset()
            self._solo_button = None
        if self._arm_button != None:
            self._arm_button.remove_value_listener(self._arm_value)
            self._arm_button.reset()
            self._arm_button = None
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button.reset()
            self._shift_button = None
        if self._crossfade_toggle != None:
            self._crossfade_toggle.remove_value_listener(self._crossfade_toggle_value)
            self._crossfade_toggle.reset()
            self._crossfade_toggle = None
        if self._track_name_data_source != None:
            self._track_name_data_source.set_display_string('')
            self._track_name_data_source = None
        if self._track != None:
            if self._track != self.song().master_track:
                if self._track.mixer_device.sends_has_listener(self._on_sends_changed):
                    self._track.mixer_device.remove_sends_listener(self._on_sends_changed)
                if self._track.mute_has_listener(self._on_mute_changed):
                    self._track.remove_mute_listener(self._on_mute_changed)
                if self._track.name_has_listener(self._on_track_name_changed):
                    self._track.remove_name_listener(self._on_track_name_changed)
                if self._track.solo_has_listener(self._on_solo_changed):
                    self._track.remove_solo_listener(self._on_solo_changed)
                if self._track.mixer_device.crossfade_assign_has_listener(self._on_cf_assign_changed):
                    self._track.mixer_device.remove_crossfade_assign_listener(self._on_cf_assign_changed)
                if self._track not in self.song().return_tracks:
                    if self._track.can_be_armed and self._track.arm_has_listener(self._on_arm_changed):
                        self._track.remove_arm_listener(self._on_arm_changed)
                    if self._track.current_input_routing_has_listener(self._on_input_routing_changed):
                        self._track.remove_current_input_routing_listener(self._on_input_routing_changed)
            if self._pan_control != None:
                self._pan_control.release_parameter()
                self._pan_control = None
            if self._volume_control != None:
                self._volume_control.release_parameter()
                self._volume_control = None
            if self._send_controls != None:
                for send_control in self._send_controls:
                    if send_control != None:
                        send_control.release_parameter()

                self._send_controls = None
            self._track = None
        super(ChannelStripComponent, self).disconnect()

    def set_track(self, track):
        if not isinstance(track, (type(None), Live.Track.Track)):
            raise AssertionError
            if self._track != None:
                if self._track != self.song().master_track:
                    if self._track.mixer_device.sends_has_listener(self._on_sends_changed):
                        self._track.mixer_device.remove_sends_listener(self._on_sends_changed)
                    if self._track.mute_has_listener(self._on_mute_changed):
                        self._track.remove_mute_listener(self._on_mute_changed)
                    if self._track.name_has_listener(self._on_track_name_changed):
                        self._track.remove_name_listener(self._on_track_name_changed)
                    if self._track.solo_has_listener(self._on_solo_changed):
                        self._track.remove_solo_listener(self._on_solo_changed)
                    if self._track.mixer_device.crossfade_assign_has_listener(self._on_cf_assign_changed):
                        self._track.mixer_device.remove_crossfade_assign_listener(self._on_cf_assign_changed)
                    if self._track not in self.song().return_tracks:
                        if self._track.can_be_armed and self._track.arm_has_listener(self._on_arm_changed):
                            self._track.remove_arm_listener(self._on_arm_changed)
                        if self._track.current_input_routing_has_listener(self._on_input_routing_changed):
                            self._track.remove_current_input_routing_listener(self._on_input_routing_changed)
            if self._pan_control != None:
                self._pan_control.release_parameter()
            if self._volume_control != None:
                self._volume_control.release_parameter()
            if self._send_controls != None:
                for send_control in self._send_controls:
                    if send_control != None:
                        send_control.release_parameter()

            self._track = track
            raise self._track != None and (isinstance(self._track, Live.Track.Track) or AssertionError)
            if not self._track in tuple(self.song().tracks) + tuple(self.song().return_tracks) + (self.song().master_track,):
                raise AssertionError
                if self._track != self.song().master_track:
                    self._track.add_solo_listener(self._on_solo_changed)
                    self._track.mixer_device.add_sends_listener(self._on_sends_changed)
                    self._track.add_mute_listener(self._on_mute_changed)
                    self._track.add_name_listener(self._on_track_name_changed)
                    self._track.mixer_device.add_crossfade_assign_listener(self._on_cf_assign_changed)
                    if self._track not in self.song().return_tracks:
                        self._track.can_be_armed and self._track.add_arm_listener(self._on_arm_changed)
                    self._track.add_current_input_routing_listener(self._on_input_routing_changed)
            for button in (self._select_button,
             self._mute_button,
             self._solo_button,
             self._arm_button,
             self._crossfade_toggle):
                if button != None:
                    button.turn_off()

        self._update_track_name_data_source()
        self.update()

    def _update_track_name_data_source(self):
        if self._track_name_data_source != None:
            if self._track != None:
                self._track_name_data_source.set_display_string(self._track.name)
            else:
                self._track_name_data_source.set_display_string(' - ')

    def set_send_controls(self, controls):
        if self._send_controls != None:
            for send_control in self._send_controls:
                if send_control != None:
                    send_control.release_parameter()

        self._send_controls = controls
        self.update()

    def set_pan_control(self, control):
        if not isinstance(control, (type(None), EncoderElement)):
            raise AssertionError
            if control != self._pan_control:
                self._pan_control != None and self._pan_control.release_parameter()
            self._pan_control = control
            self.update()

    def set_volume_control(self, control):
        if not isinstance(control, (type(None), EncoderElement)):
            raise AssertionError
            if control != self._volume_control:
                self._volume_control != None and self._volume_control.release_parameter()
            self._volume_control = control
            self.update()

    def set_select_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if button != self._select_button:
                if self._select_button != None:
                    self._select_button.remove_value_listener(self._select_value)
                    self._select_button.reset()
                self._select_button = button
                self._select_button != None and self._select_button.add_value_listener(self._select_value)
            self.update()

    def set_mute_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if button != self._mute_button:
                if self._mute_button != None:
                    self._mute_button.remove_value_listener(self._mute_value)
                    self._mute_button.reset()
                self._mute_button = button
                self._mute_button != None and self._mute_button.add_value_listener(self._mute_value)
            self.update()

    def set_solo_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if button != self._solo_button:
                if self._solo_button != None:
                    self._solo_button.remove_value_listener(self._solo_value)
                    self._solo_button.reset()
                self._solo_pressed = False
                self._solo_button = button
                self._solo_button != None and self._solo_button.add_value_listener(self._solo_value)
            self.update()

    def set_arm_button(self, button):
        if not self._track != self.song().master_track:
            raise AssertionError
            if not (button == None or isinstance(button, ButtonElement)):
                raise AssertionError
                if button != self._arm_button:
                    self._arm_button != None and self._arm_button.remove_value_listener(self._arm_value)
                    self._arm_button.reset()
                self._arm_pressed = False
                self._arm_button = button
                self._arm_button != None and self._arm_button.add_value_listener(self._arm_value)
            self.update()

    def set_shift_button(self, button):
        if not self._track != self.song().master_track:
            raise AssertionError
            if not (button == None or isinstance(button, ButtonElement) and button.is_momentary()):
                raise AssertionError
                if button != self._shift_button:
                    self._shift_button != None and self._shift_button.remove_value_listener(self._shift_value)
                    self._shift_button.reset()
                self._shift_button = button
                self._shift_button != None and self._shift_button.add_value_listener(self._shift_value)
            self.update()

    def set_crossfade_toggle(self, button):
        if not self._track != self.song().master_track:
            raise AssertionError
            if not (button == None or isinstance(button, ButtonElement)):
                raise AssertionError
                if button != self._crossfade_toggle:
                    self._crossfade_toggle != None and self._crossfade_toggle.remove_value_listener(self._crossfade_toggle_value)
                    self._crossfade_toggle.reset()
                self._crossfade_toggle = button
                self._crossfade_toggle != None and self._crossfade_toggle.add_value_listener(self._crossfade_toggle_value)
            self.update()

    def set_invert_mute_feedback(self, invert_feedback):
        if not isinstance(invert_feedback, type(False)):
            raise AssertionError
            self._invert_mute_feedback = invert_feedback != self._invert_mute_feedback and invert_feedback
            self.update()

    def on_enabled_changed(self):
        self.update()

    def on_selected_track_changed(self):
        if self.is_enabled() and self._select_button != None:
            if self._track != None or self.empty_color == None:
                if self.song().view.selected_track == self._track:
                    self._select_button.turn_on()
                else:
                    self._select_button.turn_off()
            else:
                self._select_button.set_light(self.empty_color)

    def solo_button_pressed(self):
        return self._solo_pressed

    def arm_button_pressed(self):
        return self._arm_pressed

    def track_name_data_source(self):
        if self._track_name_data_source == None:
            self._track_name_data_source = DisplayDataSource()
            self._update_track_name_data_source()
        return self._track_name_data_source

    def _connect_parameters(self):
        if self._pan_control != None:
            self._pan_control.connect_to(self._track.mixer_device.panning)
        if self._volume_control != None:
            self._volume_control.connect_to(self._track.mixer_device.volume)
        if self._send_controls != None:
            index = 0
            for send_control in self._send_controls:
                if send_control != None:
                    if index < len(self._track.mixer_device.sends):
                        send_control.connect_to(self._track.mixer_device.sends[index])
                    else:
                        send_control.release_parameter()
                        self._empty_control_slots.register_slot(send_control, nop, 'value')
                index += 1

    def _disconnect_parameters(self):
        if self._pan_control != None:
            self._pan_control.release_parameter()
            self._empty_control_slots.register_slot(self._pan_control, nop, 'value')
        if self._volume_control != None:
            self._volume_control.release_parameter()
            self._empty_control_slots.register_slot(self._volume_control, nop, 'value')
        if self._send_controls != None:
            for send_control in self._send_controls:
                if send_control != None:
                    send_control.release_parameter()
                    self._empty_control_slots.register_slot(send_control, nop, 'value')

    def update(self):
        if self._allow_updates:
            if self.is_enabled():
                self._empty_control_slots.disconnect()
                if self._track != None:
                    self._connect_parameters()
                else:
                    self._disconnect_parameters()
                self.on_selected_track_changed()
                self._on_mute_changed()
                self._on_solo_changed()
                self._on_arm_changed()
                self._on_cf_assign_changed()
            else:
                self._disconnect_parameters()
        else:
            self._update_requests += 1

    def _select_value(self, value):
        if not self._select_button != None:
            raise AssertionError
            if not isinstance(value, int):
                raise AssertionError
                if self.is_enabled():
                    if self._track != None:
                        self.song().view.selected_track = (value != 0 or not self._select_button.is_momentary()) and self.song().view.selected_track != self._track and self._track

    def _mute_value(self, value):
        if not self._mute_button != None:
            raise AssertionError
            if not isinstance(value, int):
                raise AssertionError
                if self.is_enabled():
                    self._track.mute = self._track != None and self._track != self.song().master_track and (not self._mute_button.is_momentary() or value != 0) and not self._track.mute

    def update_solo_state(self, solo_exclusive, new_value, respect_multi_selection, track):
        if track == self._track or respect_multi_selection and track.is_part_of_selection:
            track.solo = new_value
        elif solo_exclusive and track.solo:
            track.solo = False

    def _solo_value(self, value):
        if not self._solo_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled():
                    if self._track != None and self._track != self.song().master_track:
                        self._solo_pressed = value != 0 and self._solo_button.is_momentary()
                        expected_solos_pressed = (value != 0 or not self._solo_button.is_momentary()) and 0
                        expected_solos_pressed = self._solo_pressed and 1
                    solo_exclusive = self.song().exclusive_solo != self._shift_pressed and (not self._solo_button.is_momentary() or ChannelStripComponent.number_of_solos_pressed() == expected_solos_pressed)
                    new_value = not self._track.solo
                    respect_multi_selection = self._track.is_part_of_selection
                    for track in self.song().tracks:
                        self.update_solo_state(solo_exclusive, new_value, respect_multi_selection, track)

                    for track in self.song().return_tracks:
                        self.update_solo_state(solo_exclusive, new_value, respect_multi_selection, track)

    def _arm_value(self, value):
        if not self._arm_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled():
                    if self._track != None and self._track.can_be_armed:
                        self._arm_pressed = value != 0 and self._arm_button.is_momentary()
                        expected_arms_pressed = (not self._arm_button.is_momentary() or value != 0) and 0
                        expected_arms_pressed = self._arm_pressed and 1
                    arm_exclusive = self.song().exclusive_arm != self._shift_pressed and (not self._arm_button.is_momentary() or ChannelStripComponent.number_of_arms_pressed() == expected_arms_pressed)
                    new_value = not self._track.arm
                    respect_multi_selection = self._track.is_part_of_selection
                    for track in self.song().tracks:
                        if track.can_be_armed:
                            if track == self._track or respect_multi_selection and track.is_part_of_selection:
                                track.arm = new_value
                            elif arm_exclusive and track.arm:
                                track.arm = False

    def _shift_value(self, value):
        raise self._shift_button != None or AssertionError
        self._shift_pressed = value != 0

    def _crossfade_toggle_value(self, value):
        if not self._crossfade_toggle != None:
            raise AssertionError
            if not isinstance(value, int):
                raise AssertionError
                if self.is_enabled():
                    self._track.mixer_device.crossfade_assign = self._track != None and (value != 0 or not self._crossfade_toggle.is_momentary()) and (self._track.mixer_device.crossfade_assign - 1) % len(self._track.mixer_device.crossfade_assignments.values)

    def _on_sends_changed(self):
        if self.is_enabled():
            self.update()

    def _on_mute_changed(self):
        if self.is_enabled() and self._mute_button != None:
            if self._track != None or self.empty_color == None:
                if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.mute != self._invert_mute_feedback:
                    self._mute_button.turn_on()
                else:
                    self._mute_button.turn_off()
            else:
                self._mute_button.set_light(self.empty_color)

    def _on_solo_changed(self):
        if self.is_enabled() and self._solo_button != None:
            if self._track != None or self.empty_color == None:
                if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.solo:
                    self._solo_button.turn_on()
                else:
                    self._solo_button.turn_off()
            else:
                self._solo_button.set_light(self.empty_color)

    def _on_arm_changed(self):
        if self.is_enabled() and self._arm_button != None:
            if self._track != None and self._track in self.song().tracks and self._track.can_be_armed and self._track.arm:
                self._arm_button.turn_on()
            else:
                self._arm_button.turn_off()

    def _on_track_name_changed(self):
        if self._track != None:
            self._update_track_name_data_source()

    def _on_cf_assign_changed(self):
        if self.is_enabled() and self._crossfade_toggle != None:
            if self._track != None and self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.mixer_device.crossfade_assign != 1:
                self._crossfade_toggle.turn_on()
            else:
                self._crossfade_toggle.turn_off()

    def _on_input_routing_changed(self):
        if not self._track != None:
            raise AssertionError
            if self.is_enabled():
                self._track.can_be_armed and not self._track.arm_has_listener(self._on_arm_changed) and self._track.add_arm_listener(self._on_arm_changed)
            self._on_arm_changed()