#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl_Classic/ChannelStrip.py
from MackieControlComponent import *
from itertools import chain

class ChannelStrip(MackieControlComponent):
    """Represets a Channel Strip of the Mackie Control, which consists out of the"""

    def __init__(self, main_script, strip_index):
        MackieControlComponent.__init__(self, main_script)
        self.__channel_strip_controller = None
        self.__is_touched = False
        self.__strip_index = strip_index
        self.__stack_offset = 0
        self.__bank_and_channel_offset = 0
        self.__assigned_track = None
        self.__v_pot_parameter = None
        self.__v_pot_display_mode = VPOT_DISPLAY_SINGLE_DOT
        self.__fader_parameter = None
        self.__meters_enabled = False
        self.__last_meter_value = -1
        self.__send_meter_mode()
        self.__within_track_added_or_deleted = False
        self.__within_destroy = False
        self.set_bank_and_channel_offset(offset=0, show_return_tracks=False, within_track_added_or_deleted=False)

    def destroy(self):
        self.__within_destroy = True
        if self.__assigned_track:
            self.__remove_listeners()
        self.__assigned_track = None
        self.send_midi((208, 0 + (self.__strip_index << 4)))
        self.__meters_enabled = False
        self.__send_meter_mode()
        self.refresh_state()
        MackieControlComponent.destroy(self)
        self.__within_destroy = False

    def set_channel_strip_controller(self, channel_strip_controller):
        self.__channel_strip_controller = channel_strip_controller

    def strip_index(self):
        return self.__strip_index

    def assigned_track(self):
        return self.__assigned_track

    def is_touched(self):
        return self.__is_touched

    def set_is_touched(self, touched):
        self.__is_touched = touched

    def stack_offset(self):
        return self.__stack_offset

    def set_stack_offset(self, offset):
        """This is the offset that one gets by 'stacking' several MackieControl XTs:
           the first is at index 0, the second at 8, etc ...
        """
        self.__stack_offset = offset

    def set_bank_and_channel_offset(self, offset, show_return_tracks, within_track_added_or_deleted):
        final_track_index = self.__strip_index + self.__stack_offset + offset
        self.__within_track_added_or_deleted = within_track_added_or_deleted
        if show_return_tracks:
            tracks = self.song().return_tracks
        else:
            tracks = self.song().visible_tracks
        if final_track_index < len(tracks):
            new_track = tracks[final_track_index]
        else:
            new_track = None
        if new_track != self.__assigned_track:
            if self.__assigned_track:
                self.__remove_listeners()
            self.__assigned_track = new_track
            if self.__assigned_track:
                self.__add_listeners()
        self.refresh_state()
        self.__within_track_added_or_deleted = False

    def v_pot_parameter(self):
        return self.__v_pot_parameter

    def set_v_pot_parameter(self, parameter, display_mode = VPOT_DISPLAY_SINGLE_DOT):
        self.__v_pot_display_mode = display_mode
        self.__v_pot_parameter = parameter
        if not parameter:
            self.unlight_vpot_leds()

    def fader_parameter(self):
        return self.__fader_parameter

    def set_fader_parameter(self, parameter):
        self.__fader_parameter = parameter
        if not parameter:
            self.reset_fader()

    def enable_meter_mode(self, Enabled, needs_to_send_meter_mode = True):
        self.__meters_enabled = Enabled
        if needs_to_send_meter_mode or Enabled:
            self.__send_meter_mode()

    def reset_fader(self):
        self.send_midi((PB_STATUS + self.__strip_index, 0, 0))

    def unlight_vpot_leds(self):
        self.send_midi((CC_STATUS + 0, 48 + self.__strip_index, 32))

    def show_full_enlighted_poti(self):
        self.send_midi((CC_STATUS + 0, 48 + self.__strip_index, VPOT_DISPLAY_WRAP * 16 + 11))

    def handle_channel_strip_switch_ids(self, sw_id, value):
        if sw_id in range(SID_RECORD_ARM_BASE, SID_RECORD_ARM_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_RECORD_ARM_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    if self.song().exclusive_arm:
                        exclusive = not self.control_is_pressed()
                    else:
                        exclusive = self.control_is_pressed()
                    self.__toggle_arm_track(exclusive)
        elif sw_id in range(SID_SOLO_BASE, SID_SOLO_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_SOLO_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    if self.song().exclusive_solo:
                        exclusive = not self.control_is_pressed()
                    else:
                        exclusive = self.control_is_pressed()
                    self.__toggle_solo_track(exclusive)
        elif sw_id in range(SID_MUTE_BASE, SID_MUTE_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_MUTE_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    self.__toggle_mute_track()
        elif sw_id in range(SID_SELECT_BASE, SID_SELECT_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_SELECT_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    self.__select_track()
        elif sw_id in range(SID_VPOD_PUSH_BASE, SID_VPOD_PUSH_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_VPOD_PUSH_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    self.__channel_strip_controller.handle_pressed_v_pot(self.__strip_index, self.__stack_offset)
        elif sw_id in fader_touch_switch_ids:
            if sw_id - SID_FADER_TOUCH_SENSE_BASE is self.__strip_index:
                if value == BUTTON_PRESSED or value == BUTTON_RELEASED:
                    touched = value == BUTTON_PRESSED
                    self.set_is_touched(touched)
                    self.__channel_strip_controller.handle_fader_touch(self.__strip_index, self.__stack_offset, touched)

    def handle_vpot_rotation(self, strip_index, cc_value):
        if strip_index is self.__strip_index:
            self.__channel_strip_controller.handle_vpot_rotation(self.__strip_index, self.__stack_offset, cc_value)

    def refresh_state(self):
        if not self.__within_track_added_or_deleted:
            self.__update_track_is_selected_led()
        self.__update_solo_led()
        self.__update_mute_led()
        self.__update_arm_led()
        if not self.__within_destroy and self.__assigned_track != None:
            self.__send_meter_mode()
            self.__last_meter_value = -1
        if not self.__assigned_track:
            self.reset_fader()
            self.unlight_vpot_leds()

    def on_update_display_timer(self):
        if not self.main_script().is_pro_version or self.__meters_enabled and self.__channel_strip_controller.assignment_mode() == CSM_VOLPAN:
            if self.__assigned_track:
                if self.__assigned_track.can_be_armed and self.__assigned_track.arm:
                    meter_value = self.__assigned_track.input_meter_level
                else:
                    meter_value = self.__assigned_track.output_meter_level
            else:
                meter_value = 0.0
            meter_byte = int(meter_value * 12.0) + (self.__strip_index << 4)
            if self.__last_meter_value != meter_value or meter_value != 0.0:
                self.__last_meter_value = meter_value
                self.send_midi((208, meter_byte))

    def build_midi_map(self, midi_map_handle):
        needs_takeover = False
        if self.__fader_parameter:
            feeback_rule = Live.MidiMap.PitchBendFeedbackRule()
            feeback_rule.channel = self.__strip_index
            feeback_rule.value_pair_map = tuple()
            feeback_rule.delay_in_ms = 200.0
            Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, self.__fader_parameter, self.__strip_index, feeback_rule, not needs_takeover)
            Live.MidiMap.send_feedback_for_parameter(midi_map_handle, self.__fader_parameter)
        else:
            channel = self.__strip_index
            Live.MidiMap.forward_midi_pitchbend(self.script_handle(), midi_map_handle, channel)
        if self.__v_pot_parameter:
            if self.__v_pot_display_mode == VPOT_DISPLAY_SPREAD:
                range_end = 7
            else:
                range_end = 12
            feeback_rule = Live.MidiMap.CCFeedbackRule()
            feeback_rule.channel = 0
            feeback_rule.cc_no = 48 + self.__strip_index
            feeback_rule.cc_value_map = tuple([ self.__v_pot_display_mode * 16 + x for x in range(1, range_end) ])
            feeback_rule.delay_in_ms = -1.0
            Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self.__v_pot_parameter, 0, FID_PANNING_BASE + self.__strip_index, Live.MidiMap.MapMode.relative_signed_bit, feeback_rule, needs_takeover)
            Live.MidiMap.send_feedback_for_parameter(midi_map_handle, self.__v_pot_parameter)
        else:
            channel = 0
            cc_no = FID_PANNING_BASE + self.__strip_index
            Live.MidiMap.forward_midi_cc(self.script_handle(), midi_map_handle, channel, cc_no)

    def __assigned_track_index(self):
        index = 0
        for t in chain(self.song().visible_tracks, self.song().return_tracks):
            if t == self.__assigned_track:
                return index
            index += 1

        if not (self.__assigned_track and 0):
            raise AssertionError

    def __add_listeners(self):
        if self.__assigned_track.can_be_armed:
            self.__assigned_track.add_arm_listener(self.__update_arm_led)
        self.__assigned_track.add_mute_listener(self.__update_mute_led)
        self.__assigned_track.add_solo_listener(self.__update_solo_led)
        if not self.song().view.selected_track_has_listener(self.__update_track_is_selected_led):
            self.song().view.add_selected_track_listener(self.__update_track_is_selected_led)

    def __remove_listeners(self):
        if self.__assigned_track.can_be_armed:
            self.__assigned_track.remove_arm_listener(self.__update_arm_led)
        self.__assigned_track.remove_mute_listener(self.__update_mute_led)
        self.__assigned_track.remove_solo_listener(self.__update_solo_led)
        self.song().view.remove_selected_track_listener(self.__update_track_is_selected_led)

    def __send_meter_mode(self):
        on_mode = 1
        off_mode = 0
        if self.__meters_enabled:
            on_mode = on_mode | 2
        if self.__assigned_track:
            mode = on_mode
        else:
            mode = off_mode
        if self.main_script().is_extension():
            device_type = SYSEX_DEVICE_TYPE_XT
        else:
            device_type = SYSEX_DEVICE_TYPE
        self.send_midi((240,
         0,
         0,
         102,
         device_type,
         32,
         self.__strip_index,
         mode,
         247))

    def __toggle_arm_track(self, exclusive):
        if self.__assigned_track and self.__assigned_track.can_be_armed:
            self.__assigned_track.arm = not self.__assigned_track.arm
            if exclusive:
                for t in self.song().tracks:
                    if t != self.__assigned_track:
                        t.arm = False

    def __toggle_mute_track(self):
        if self.__assigned_track:
            self.__assigned_track.mute = not self.__assigned_track.mute

    def __toggle_solo_track(self, exclusive):
        if self.__assigned_track:
            self.__assigned_track.solo = not self.__assigned_track.solo
            if exclusive:
                for t in chain(self.song().tracks, self.song().return_tracks):
                    if t != self.__assigned_track:
                        t.solo = False

    def __select_track(self):
        if self.__assigned_track:
            all_tracks = tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
            if self.song().view.selected_track != all_tracks[self.__assigned_track_index()]:
                self.song().view.selected_track = all_tracks[self.__assigned_track_index()]
            elif self.application().view.is_view_visible('Arranger'):
                if self.__assigned_track:
                    self.__assigned_track.view.is_collapsed = not self.__assigned_track.view.is_collapsed

    def __update_arm_led(self):
        track = self.__assigned_track
        if track and track.can_be_armed and track.arm:
            self.send_midi((NOTE_ON_STATUS, SID_RECORD_ARM_BASE + self.__strip_index, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_RECORD_ARM_BASE + self.__strip_index, BUTTON_STATE_OFF))

    def __update_mute_led(self):
        if self.__assigned_track and self.__assigned_track.mute:
            self.send_midi((NOTE_ON_STATUS, SID_MUTE_BASE + self.__strip_index, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MUTE_BASE + self.__strip_index, BUTTON_STATE_OFF))

    def __update_solo_led(self):
        if self.__assigned_track and self.__assigned_track.solo:
            self.send_midi((NOTE_ON_STATUS, SID_SOLO_BASE + self.__strip_index, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_SOLO_BASE + self.__strip_index, BUTTON_STATE_OFF))

    def __update_track_is_selected_led(self):
        if self.song().view.selected_track == self.__assigned_track:
            self.send_midi((NOTE_ON_STATUS, SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_OFF))


class MasterChannelStrip(MackieControlComponent):

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__strip_index = MASTER_CHANNEL_STRIP_INDEX
        self.__assigned_track = self.song().master_track

    def destroy(self):
        self.reset_fader()
        MackieControlComponent.destroy(self)

    def set_channel_strip_controller(self, channel_strip_controller):
        pass

    def handle_channel_strip_switch_ids(self, sw_id, value):
        pass

    def refresh_state(self):
        pass

    def on_update_display_timer(self):
        pass

    def enable_meter_mode(self, Enabled):
        pass

    def reset_fader(self):
        self.send_midi((PB_STATUS + self.__strip_index, 0, 0))

    def build_midi_map(self, midi_map_handle):
        needs_takeover = False
        if self.__assigned_track:
            volume = self.__assigned_track.mixer_device.volume
            feeback_rule = Live.MidiMap.PitchBendFeedbackRule()
            feeback_rule.channel = self.__strip_index
            feeback_rule.value_pair_map = tuple()
            feeback_rule.delay_in_ms = 200.0
            Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, volume, self.__strip_index, feeback_rule, not needs_takeover)
            Live.MidiMap.send_feedback_for_parameter(midi_map_handle, volume)