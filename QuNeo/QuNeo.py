#Embedded file name: /Applications/Ableton Live 8.app/Contents/App-Resources/MIDI Remote Scripts/QuNeo/QuNeo.py
import Live
import time
import math
from _Framework.ButtonElement import ButtonElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.ControlElement import ControlElement
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.InputControlElement import *
from _Framework.SceneComponent import SceneComponent
from _Framework.SliderElement import SliderElement
from ConfigurableButtonElement import ConfigurableButtonElement
from SpecialSessionComponent import SpecialSessionComponent
from SpecialTransportComponent import SpecialTransportComponent
from SpecialMixerComponent import SpecialMixerComponent
from MIDI_Map import *
from VUMeter import VUMeter

class QuNeo(ControlSurface):
    """ Script for Keith McMillen's QuNeo Multi-Touchpad Controller """
    __module__ = __name__
    _active_instances = []

    def _combine_active_instances():
        support_devices = False
        for instance in QuNeo._active_instances:
            support_devices |= instance._device_component != None

        track_offset = 0
        for instance in QuNeo._active_instances:
            instance._activate_combination_mode(track_offset, support_devices)
            track_offset += instance._session.width()

    _combine_active_instances = staticmethod(_combine_active_instances)

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.set_suppress_rebuild_requests(True)
        self._suppress_session_highlight = True
        self._suppress_send_midi = True
        self._suggested_input_port = 'QUNEO'
        self._suggested_output_port = 'QUNEO'
        self.num_tracks = 7
        self.num_scenes = 4
        self.session = None
        self.mixer = None
        self.transport = None
        self.led_value = None
        self._note_input = []
        self.shift_button = None
        self.sequencer_button = None
        self.launch_button = None
        self.seq_offset_down = None
        self.seq_offset_up = None
        self.seq_offset_left = None
        self.seq_offset_right = None
        self.stop_all_clips = None
        self.track_bank_right = None
        self.track_bank_left = None
        self.scene_bank_down = None
        self.scene_bank_up = None
        self.beat_table = []
        self.sends = []
        self.arm_buttons = None
        self.mute_buttons = None
        self.solo_buttons = None
        self.shift_buttons = []
        self.sequencer_buttons = None
        self.scene_launch_buttons = None
        self.stop_track_buttons = None
        self.clip_slot_buttons = None
        self.instrument_buttons = None
        self.volume_control = None
        self.pan_control = None
        self.current_mode = 0
        self.set_shift_button(ConfigurableButtonElement(True, MIDI_NOTE_TYPE, PAD_CHANNEL, SHIFT_BUTTON, 127))
        self._setup_transport_control()
        self._setup_mixer_control()
        self._setup_session_control()
        self.session.set_mixer(self.mixer)
        self._shift_mode(0)
        self._set_mode(0)
        app = Live.Application.get_application()
        maj = app.get_major_version()
        min = app.get_minor_version()
        bug = app.get_bugfix_version()
        self.show_message(str(maj) + '.' + str(min) + '.' + str(bug))
        self.set_suppress_rebuild_requests(False)

    def disconnect(self):
        self.mixer
        self.session
        if self.shift_button != None:
            self.shift_button.remove_value_listener(self._shift_value)
            self.shift_button = None
        if self.shift_buttons != None:
            for button in self.shift_buttons:
                button.remove_value_listener(self._shift_buttons_value)

            self.shift_buttons = None
        self._note_input = None
        ControlSurface.disconnect(self)

    def refresh_state(self):
        ControlSurface.refresh_state(self)

    def set_shift_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self.shift_button != button:
                if self.shift_button != None:
                    self.shift_button.remove_value_listener(self._shift_value)
                self.shift_button = button
                self.shift_button != None and self.shift_button.add_value_listener(self._shift_value)

    def update_mode(self, mode):
        if mode != None:
            self._set_mode(mode)
            self.current_mode = mode

    def set_shift_buttons(self, buttons):
        if buttons != None:
            if self.shift_buttons != buttons:
                self.shift_buttons.remove_value_listener(self._shift_buttons_value)
            self.shift_buttons = buttons
            if self.shift_buttons != None:
                for button in self.shift_buttons:
                    raise isinstance(button, ButtonElement) or AssertionError
                    button.add_value_listener(self._shift_buttons_value, identify_sender=True)

        else:
            if self.shift_buttons != None:
                for button in self.shift_buttons:
                    button.remove_value_listener(self._shift_buttons_value)

            self.shift_buttons = None

    def _shift_buttons_value(self, value, sender):
        raise self.shift_buttons != None or AssertionError
        raise value in range(128) or AssertionError
        mode = int(sender._note * 0.5)
        self.update_mode(mode)

    def _shift_value(self, value):
        if not value in range(128):
            raise AssertionError
            raise self.shift_button != None or AssertionError
            value != 0 and self._shift_mode(1)
            self.shift_button.turn_on()
        else:
            self._shift_mode(0)
            self.shift_button.turn_off()

    def _shift_mode(self, value):
        if value != 0:
            self.set_suppress_rebuild_requests(True)
            self._reassign_grid(0)
            self._reassign_mixer_control(1)
            self.set_suppress_rebuild_requests(False)
        else:
            None
            self._set_mode(self.current_mode)
            self._reassign_mixer_control(1)

    def _update_grid(self):
        if self.sequencer_buttons != None:
            self.session.set_sequencer_buttons(self.sequencer_buttons)
        else:
            self.session.set_sequencer_buttons(None)
        if self.seq_offset_left != None and self.seq_offset_right != None:
            self.session.set_seq_measure_offset(self.seq_offset_left, self.seq_offset_right)
        else:
            self.session.set_seq_measure_offset(None, None)
        if self.seq_offset_up != None and self.seq_offset_down != None:
            self.session.set_seq_note_offset(self.seq_offset_up, self.seq_offset_down)
        else:
            self.session.set_seq_note_offset(None, None)
        if self.launch_button != None:
            self.session.set_slot_launch_button(self.launch_button)
        else:
            self.session.set_slot_launch_button(None)
        if self.scene_launch_buttons != None:
            for index in range(len(self.scene_launch_buttons)):
                self.session.scene(index).set_launch_button(self.scene_launch_buttons[index])

        else:
            for index in range(4):
                self.session.scene(index).set_launch_button(None)

        if self.stop_track_buttons != None:
            self.session.set_stop_track_clip_buttons(tuple(self.stop_track_buttons))
        else:
            self.session.set_stop_track_clip_buttons(None)
        if self.stop_all_clips != None:
            self.session.set_stop_all_clips_button(self.stop_all_clips)
        else:
            self.session.set_stop_all_clips_button(None)
        if self.track_bank_right != None and self.track_bank_left != None:
            self.session.set_track_bank_buttons(self.track_bank_right, self.track_bank_left)
        else:
            self.session.set_track_bank_buttons(None, None)
        if self.scene_bank_up != None and self.scene_bank_down != None:
            self.session.set_scene_bank_buttons(self.scene_bank_up, self.scene_bank_down)
        else:
            self.session.set_scene_bank_buttons(None, None)
        for row in range(4):
            for col in range(7):
                self.clip = self.session.scene(row).clip_slot(col)
                if self.clip_slot_buttons != None:
                    self.clip.set_triggered_to_play_value(30)
                    self.clip.set_triggered_to_record_value(RED_HI)
                    self.clip.set_started_value(30)
                    self.clip.set_recording_value(RED_HI)
                    self.clip.set_stopped_value(80)
                    self.clip.set_triggered_to_record_value(6)
                    self.clip.set_launch_button(self.clip_slot_buttons[row][col])
                else:
                    self.clip.set_launch_button(None)

    def turn_off_all_buttons(self):
        self.arm_buttons = None
        self.mute_buttons = None
        self.solo_buttons = None
        self.scene_launch_buttons = None
        self.stop_track_buttons = None
        if self.clip_slot_buttons != None:
            for row in range(4):
                for col in range(7):
                    button = self.clip_slot_buttons[row][col]
                    button.turn_off()

        self.clip_slot_buttons = None
        if self.shift_buttons != None:
            for button in self.shift_buttons:
                button.turn_off()
                button.remove_value_listener(self._shift_buttons_value)

        if self.sequencer_buttons != None:
            for button in self.sequencer_buttons:
                button.count = 0
                button.note_on()

        self.instrument_buttons = None
        self.shift_buttons = None
        self.sequencer_buttons = None
        self.clip_slot_buttons = None
        self.launch_button = None
        self.stop_all_clips = None
        self.track_bank_left = None
        self.track_bank_right = None
        self.scene_bank_up = None
        self.scene_bank_down = None
        self.seq_offset_left = None
        self.seq_offset_right = None
        self.seq_offset_up = None
        self.seq_offset_down = None

    def _set_mode(self, mode):
        self.turn_off_all_buttons()
        if mode == 0:
            self.stop_track_buttons = []
            self.scene_launch_buttons = []
            self.track_bank_left = self.button(PAD_CHANNEL, SESSION_LEFT)
            self.track_bank_right = self.button(PAD_CHANNEL, SESSION_RIGHT)
            self.scene_bank_up = self.button(PAD_CHANNEL, SESSION_UP)
            self.scene_bank_down = self.button(PAD_CHANNEL, SESSION_DOWN)
            self.stop_all_clips = self.led_button(GRID_CHANNEL, STOP_ALL_CLIPS, 100)
            self.launch_button = self.led_button(GRID_CHANNEL, SLOT_LAUNCH, RED_HI)
            self.clip_slot_buttons = []
            for row in range(4):
                self.clip_slot_buttons.append([])
                for col in range(7):
                    self.clip_slot_buttons[row].append(self.button(GRID_CHANNEL, CLIP_NOTE_MAP[row][col]))

            self.mute_buttons = []
            self.solo_buttons = []
            self.arm_buttons = []
            for index in range(7):
                self.mute_buttons.append(self.led_button(GRID_CHANNEL, TRACK_MUTE[index], GREEN_HI))
                self.solo_buttons.append(self.led_button(GRID_CHANNEL, TRACK_SOLO[index], ORANGE_HI))
                self.arm_buttons.append(self.led_button(GRID_CHANNEL, TRACK_ARM[index], RED_HI))
                self.stop_track_buttons.append(self.led_button(GRID_CHANNEL, STOP_TRACK[index], 100))

            for scene in range(4):
                self.scene_launch_buttons.append(self.led_button(GRID_CHANNEL, SCENE_LAUNCH[scene], GREEN_LO))

            self._update_session()
            self._update_grid()
        elif mode == 1:
            self.seq_offset_left = self.button(PAD_CHANNEL, SESSION_LEFT)
            self.seq_offset_right = self.button(PAD_CHANNEL, SESSION_RIGHT)
            self.seq_offset_up = self.button(PAD_CHANNEL, SESSION_UP)
            self.seq_offset_down = self.button(PAD_CHANNEL, SESSION_DOWN)
            self.sequencer_buttons = []
            for row in range(8):
                for col in range(8):
                    self.sequencer_buttons.append(self.led_button(GRID_CHANNEL, CLIP_NOTE_MAP[row][col], GREEN_HI))

            self._update_session()
            self._update_grid()
            self.session.clear_led()
            self.session.update_notes()
            self.session.on_device_changed()
        else:
            self.track_bank_left = self.button(PAD_CHANNEL, SESSION_LEFT)
            self.track_bank_right = self.button(PAD_CHANNEL, SESSION_RIGHT)
            self.scene_bank_up = self.button(PAD_CHANNEL, SESSION_UP)
            self.scene_bank_down = self.button(PAD_CHANNEL, SESSION_DOWN)
            self._update_session()
            self._update_grid()

    def _reassign_grid(self, value):
        if value == 0:
            self.turn_off_all_buttons()
            self.shift_buttons = []
            for index in range(2):
                self.shift_buttons.append(self.led_button(GRID_CHANNEL, TRACK_ARM[index], 127))
                if index == self.current_mode:
                    self.shift_buttons[index].send_value(127, True)
                else:
                    self.shift_buttons[index].send_value(40, True)

            self._update_session()
            self._update_grid()
        else:
            None

    def button(self, channel, value):
        is_momentary = True
        if value != -1:
            return ButtonElement(is_momentary, MIDI_NOTE_TYPE, channel, value)
        else:
            return None

    def led_button(self, channel, value, vel):
        is_momentary = True
        if value != -1:
            return ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, channel, value, vel)
        else:
            return None

    def slider(self, channel, value):
        if value != -1:
            return SliderElement(MIDI_CC_TYPE, channel, value)
        else:
            return None

    def assign_encoder(self, channel, value):
        if value != -1:
            return EncoderElement(MIDI_CC_TYPE, channel, value, Live.MidiMap.MapMode.relative_two_compliment)
        else:
            return None

    def _reassign_mixer_control(self, shift_value):
        if shift_value == 1:
            for index in range(2):
                self.sends.append(self.slider(SLIDER_CHANNEL, SELECTED_SENDS[index]))

            self.volume_control = self.slider(SLIDER_CHANNEL, SELECTED_VOL)
            self.pan_control = self.slider(SLIDER_CHANNEL, SELECTED_PAN)
        if self.sends != None:
            self.mixer.selected_strip().set_send_controls(tuple(self.sends))
        else:
            self.mixer.selected_strip().set_send_controls(tuple(None))
        if self.volume_control != None:
            self.mixer.selected_strip().set_volume_control(self.volume_control)
        else:
            self.mixer.selected_strip().set_volume_control(None)
        if self.pan_control != None:
            self.mixer.selected_strip().set_pan_control(self.pan_control)
        else:
            self.mixer.selected_strip().set_pan_control(None)

    def _update_session(self):
        if self.shift_buttons != None:
            self.set_shift_buttons(self.shift_buttons)
        else:
            self.set_shift_buttons(None)
        for index in range(7):
            if self.arm_buttons != None:
                self.mixer.channel_strip(index).set_arm_button(self.arm_buttons[index])
            else:
                self.mixer.channel_strip(index).set_arm_button(None)
            if self.solo_buttons != None:
                self.mixer.channel_strip(index).set_solo_button(self.solo_buttons[index])
            else:
                self.mixer.channel_strip(index).set_solo_button(None)
            if self.mute_buttons != None:
                self.mixer.channel_strip(index).set_invert_mute_feedback(True)
                self.mixer.channel_strip(index).set_mute_button(self.mute_buttons[index])
            else:
                self.mixer.channel_strip(index).set_mute_button(None)

    def _setup_transport_control(self):
        self.transport = SpecialTransportComponent()
        self.transport.set_metronome_button(self.led_button(PAD_CHANNEL, METRONOME, 127))
        self.transport.set_play_button(self.led_button(PAD_CHANNEL, PLAY, 127))
        self.transport.set_stop_button(self.led_button(PAD_CHANNEL, STOP, 127))
        self.transport.set_record_button(self.led_button(PAD_CHANNEL, REC, 127))
        self.transport.set_overdub_button(self.led_button(PAD_CHANNEL, OVERDUB, 127))
        self.transport.set_tempo_buttons(self.led_button(PAD_CHANNEL, TEMPO_UP, 127), self.led_button(PAD_CHANNEL, TEMPO_DOWN, 127))

    def _setup_mixer_control(self):
        self.mixer = SpecialMixerComponent(self.num_tracks, self)
        self.mixer.name = 'Mixer'
        self.mixer.set_track_offset(0)
        self.mixer.set_select_buttons(self.button(PAD_CHANNEL, TRACK_RIGHT), self.button(PAD_CHANNEL, TRACK_LEFT))
        self.mixer.set_crossfader_control(self.slider(SLIDER_CHANNEL, CROSSFADER))
        for index in range(4):
            self.mixer.channel_strip(index).set_volume_control(self.slider(SLIDER_CHANNEL, TRACK_VOL[index]))

        self.num_o_tracks = self.song().visible_tracks
        if self.num_o_tracks != None:
            index_count = -1
            index_table = []
            for index in self.song().visible_tracks:
                index_count += 1
                if index.has_midi_output != True:
                    index_table.append(index_count)
                else:
                    None

            if index_table != None:
                for index in range(len(index_table)):
                    x = index_table[index]
                    if x > 3:
                        None
                    else:
                        None

    def _setup_session_control(self):
        self.session = SpecialSessionComponent(self.num_tracks, self.num_scenes, self)
        self.session.set_offsets(0, 0)
        self.session.set_select_buttons(self.button(PAD_CHANNEL, SCENE_DOWN), self.button(PAD_CHANNEL, SCENE_UP))
        self.session.set_clip_loop_start(self.slider(SLIDER_CHANNEL, 6))
        self.session.set_clip_loop_length(self.slider(SLIDER_CHANNEL, 7))

    def _on_selected_scene_changed(self):
        ControlSurface._on_selected_scene_changed(self)

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)

    def _activate_combination_mode(self, track_offset, support_devices):
        self._session.link_with_track_offset(track_offset)