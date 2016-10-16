#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Novation_Impulse/Novation_Impulse.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SessionComponent import SessionComponent
from _Framework.DeviceComponent import DeviceComponent
from TransportViewModeSelector import TransportViewModeSelector
from SpecialMixerComponent import SpecialMixerComponent
from ShiftableTransportComponent import ShiftableTransportComponent
from PeekableEncoderElement import PeekableEncoderElement
from EncoderModeSelector import EncoderModeSelector
INITIAL_DISPLAY_DELAY = 30
STANDARD_DISPLAY_DELAY = 20
IS_MOMENTARY = True
SYSEX_START = (240, 0, 32, 41, 103)
PAD_TRANSLATIONS = ((0, 3, 60, 0),
 (1, 3, 62, 0),
 (2, 3, 64, 0),
 (3, 3, 65, 0),
 (0, 2, 67, 0),
 (1, 2, 69, 0),
 (2, 2, 71, 0),
 (3, 2, 72, 0))
LED_OFF = 4
RED_FULL = 7
RED_BLINK = 11
GREEN_FULL = 52
GREEN_BLINK = 56
AMBER_FULL = RED_FULL + GREEN_FULL - 4
AMBER_BLINK = AMBER_FULL - 4 + 8

class Novation_Impulse(ControlSurface):
    """ Script for Novation's Impulse keyboards """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._device_selection_follows_track_selection = True
            self._suggested_input_port = 'Impulse'
            self._suggested_output_port = 'Impulse'
            self._has_sliders = True
            self._current_midi_map = None
            self._display_reset_delay = -1
            self._shift_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 39)
            self._preview_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 41)
            self._master_slider = SliderElement(MIDI_CC_TYPE, 0, 8)
            self._shift_button.name = 'Shift_Button'
            self._master_slider.name = 'Master_Volume_Control'
            self._master_slider.add_value_listener(self._slider_value, identify_sender=True)
            self._preview_button.add_value_listener(self._preview_value)
            self._setup_mixer()
            self._setup_session()
            self._setup_transport()
            self._setup_device()
            self._setup_name_display()
            device_button = ButtonElement(not IS_MOMENTARY, MIDI_CC_TYPE, 1, 10)
            mixer_button = ButtonElement(not IS_MOMENTARY, MIDI_CC_TYPE, 1, 9)
            device_button.name = 'Encoder_Device_Mode'
            mixer_button.name = 'Encoder_Mixer_Mode'
            self._encoder_modes = EncoderModeSelector(self._device_component, self._mixer, self._next_bank_button, self._prev_bank_button, self._encoders)
            self._encoder_modes.set_device_mixer_buttons(device_button, mixer_button)
            self._string_to_display = None
            for component in self.components:
                component.set_enabled(False)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self.schedule_message(3, self._send_midi, SYSEX_START + (6, 1, 1, 1, 247))

    def handle_sysex(self, midi_bytes):
        if midi_bytes[0:-2] == SYSEX_START + (7,) and midi_bytes[-2] != 0:
            self._has_sliders = midi_bytes[-2] != 25
            self.schedule_message(1, self._show_startup_message)
            for control in self.controls:
                if isinstance(control, InputControlElement):
                    control.clear_send_cache()

            for component in self.components:
                component.set_enabled(True)

            if self._has_sliders:
                self._mixer.master_strip().set_volume_control(self._master_slider)
                self._mixer.update()
            else:
                self._mixer.master_strip().set_volume_control(None)
                self._mixer.selected_strip().set_volume_control(self._master_slider)
                for index in range(len(self._sliders)):
                    self._mixer.channel_strip(index).set_volume_control(None)
                    slider = self._sliders[index]
                    slider.release_parameter()
                    if slider.value_has_listener(self._slider_value):
                        slider.remove_value_listener(self._slider_value)

            self._encoder_modes.set_provide_volume_mode(not self._has_sliders)
            self.request_rebuild_midi_map()

    def disconnect(self):
        self._name_display_data_source.set_display_string('  ')
        for encoder in self._encoders:
            encoder.remove_value_listener(self._encoder_value)

        self._master_slider.remove_value_listener(self._slider_value)
        if self._has_sliders:
            for slider in tuple(self._sliders):
                slider.remove_value_listener(self._slider_value)

        for button in self._strip_buttons:
            button.remove_value_listener(self._mixer_button_value)

        self._preview_button.remove_value_listener(self._preview_value)
        ControlSurface.disconnect(self)
        self._encoders = None
        self._sliders = None
        self._strip_buttons = None
        self._master_slider = None
        self._current_midi_map = None
        self._shift_button = None
        self._name_display = None
        self._prev_bank_button = None
        self._next_bank_button = None
        self._encoder_modes = None
        self._transport_view_modes = None
        self._send_midi(SYSEX_START + (6, 0, 0, 0, 247))

    def build_midi_map(self, midi_map_handle):
        self._current_midi_map = midi_map_handle
        ControlSurface.build_midi_map(self, midi_map_handle)

    def update_display(self):
        ControlSurface.update_display(self)
        if self._string_to_display != None:
            self._name_display_data_source.set_display_string(self._string_to_display)
            self._string_to_display = None
        if self._display_reset_delay >= 0:
            self._display_reset_delay -= 1
            if self._display_reset_delay == -1:
                self._show_current_track_name()

    def _setup_mixer(self):
        mute_solo_flip_button = ButtonElement(not IS_MOMENTARY, MIDI_CC_TYPE, 0, 34)
        self._next_nav_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 37)
        self._prev_nav_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 38)
        self._strip_buttons = []
        mute_solo_flip_button.name = 'Mute_Solo_Flip_Button'
        self._next_nav_button.name = 'Next_Track_Button'
        self._prev_nav_button.name = 'Prev_Track_Button'
        self._mixer = SpecialMixerComponent(8)
        self._mixer.name = 'Mixer'
        self._mixer.set_select_buttons(self._next_nav_button, self._prev_nav_button)
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.master_strip().set_volume_control(self._master_slider)
        self._sliders = []
        for index in range(8):
            strip = self._mixer.channel_strip(index)
            strip.name = 'Channel_Strip_' + str(index)
            strip.set_invert_mute_feedback(True)
            self._sliders.append(SliderElement(MIDI_CC_TYPE, 0, index))
            self._sliders[-1].name = str(index) + '_Volume_Control'
            self._sliders[-1].set_feedback_delay(-1)
            self._sliders[-1].add_value_listener(self._slider_value, identify_sender=True)
            strip.set_volume_control(self._sliders[-1])
            self._strip_buttons.append(ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 9 + index))
            self._strip_buttons[-1].name = str(index) + '_Mute_Button'
            self._strip_buttons[-1].add_value_listener(self._mixer_button_value, identify_sender=True)

        self._mixer.master_strip().set_mute_button(ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 1, 17))
        self._mixer.set_strip_mute_solo_buttons(tuple(self._strip_buttons), mute_solo_flip_button)

    def _setup_session(self):
        num_pads = len(PAD_TRANSLATIONS)
        self._track_left_button = ButtonElement(not IS_MOMENTARY, MIDI_CC_TYPE, 0, 36)
        self._track_right_button = ButtonElement(not IS_MOMENTARY, MIDI_CC_TYPE, 0, 35)
        self._session = SessionComponent(8, 0)
        self._session.name = 'Session_Control'
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.set_mixer(self._mixer)
        self._session.set_page_left_button(self._track_left_button)
        self._session.set_page_right_button(self._track_right_button)
        pads = []
        for index in range(num_pads):
            pads.append(ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 60 + index))
            pads[-1].name = 'Pad_' + str(index)
            clip_slot = self._session.selected_scene().clip_slot(index)
            clip_slot.set_triggered_to_play_value(GREEN_BLINK)
            clip_slot.set_triggered_to_record_value(RED_BLINK)
            clip_slot.set_stopped_value(AMBER_FULL)
            clip_slot.set_started_value(GREEN_FULL)
            clip_slot.set_recording_value(RED_FULL)
            clip_slot.set_launch_button(pads[-1])
            clip_slot.name = str(index) + '_Selected_Clip_Slot'

    def _setup_transport(self):
        rwd_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 27)
        ffwd_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 28)
        stop_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 29)
        play_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 30)
        loop_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 31)
        rec_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, 32)
        ffwd_button.name = 'FFwd_Button'
        rwd_button.name = 'Rwd_Button'
        loop_button.name = 'Loop_Button'
        play_button.name = 'Play_Button'
        stop_button.name = 'Stop_Button'
        rec_button.name = 'Record_Button'
        transport = ShiftableTransportComponent()
        transport.name = 'Transport'
        transport.set_stop_button(stop_button)
        transport.set_play_button(play_button)
        transport.set_record_button(rec_button)
        transport.set_shift_button(self._shift_button)
        self._transport_view_modes = TransportViewModeSelector(transport, self._session, ffwd_button, rwd_button, loop_button)
        self._transport_view_modes.name = 'Transport_View_Modes'

    def _setup_device(self):
        encoders = []
        for index in range(8):
            encoders.append(PeekableEncoderElement(MIDI_CC_TYPE, 1, index, Live.MidiMap.MapMode.relative_binary_offset))
            encoders[-1].set_feedback_delay(-1)
            encoders[-1].add_value_listener(self._encoder_value, identify_sender=True)
            encoders[-1].name = 'Device_Control_' + str(index)

        self._encoders = tuple(encoders)
        self._prev_bank_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 1, 12)
        self._next_bank_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 1, 11)
        self._prev_bank_button.name = 'Device_Bank_Down_Button'
        self._next_bank_button.name = 'Device_Bank_Up_Button'
        device = DeviceComponent()
        device.name = 'Device_Component'
        self.set_device_component(device)
        device.set_parameter_controls(self._encoders)
        device.set_bank_nav_buttons(self._prev_bank_button, self._next_bank_button)

    def _setup_name_display(self):
        self._name_display = PhysicalDisplayElement(16, 1)
        self._name_display.name = 'Display'
        self._name_display.set_message_parts(SYSEX_START + (8,), (247,))
        self._name_display_data_source = DisplayDataSource()
        self._name_display.segment(0).set_data_source(self._name_display_data_source)

    def _encoder_value(self, value, sender):
        if not sender in self._encoders:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                display_string = self._device_component.is_enabled() and ' - '
                display_string = sender.mapped_parameter() != None and sender.mapped_parameter().name
            self._set_string_to_display(display_string)

    def _slider_value(self, value, sender):
        if not sender in tuple(self._sliders) + (self._master_slider,):
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self._mixer.is_enabled():
                    display_string = ' - '
                    if sender.mapped_parameter() != None:
                        master = self.song().master_track
                        tracks = self.song().tracks
                        returns = self.song().return_tracks
                        track = None
                        if sender == self._master_slider:
                            track = self._has_sliders and master
                        else:
                            track = self.song().view.selected_track
                    else:
                        track = self._mixer.channel_strip(self._sliders.index(sender))._track
                    display_string = track == master and 'Master'
                elif track in tracks:
                    display_string = str(list(tracks).index(track) + 1)
                elif track in returns:
                    display_string = str(chr(ord('A') + list(returns).index(track)))
                else:
                    raise False or AssertionError
                display_string += ' Volume'
            self._set_string_to_display(display_string)

    def _mixer_button_value(self, value, sender):
        if not value in range(128):
            raise AssertionError
            if self._mixer.is_enabled() and value > 0:
                strip = self._mixer.channel_strip(self._strip_buttons.index(sender))
                self._string_to_display = strip != None and None
                self._name_display.segment(0).set_data_source(strip.track_name_data_source())
                self._name_display.update()
                self._display_reset_delay = STANDARD_DISPLAY_DELAY
            else:
                self._set_string_to_display(' - ')

    def _preview_value(self, value):
        raise value in range(128) or AssertionError
        for encoder in self._encoders:
            encoder.set_peek_mode(value > 0)

    def _show_current_track_name(self):
        if self._name_display != None and self._mixer != None:
            self._string_to_display = None
            self._name_display.segment(0).set_data_source(self._mixer.selected_strip().track_name_data_source())
            self._name_display.update()

    def _show_startup_message(self):
        self._name_display.display_message('LIVE')
        self._display_reset_delay = INITIAL_DISPLAY_DELAY

    def _set_string_to_display(self, string_to_display):
        raise isinstance(string_to_display, (str, unicode)) or AssertionError
        self._name_display.segment(0).set_data_source(self._name_display_data_source)
        self._string_to_display = string_to_display
        self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        self._show_current_track_name()
        all_tracks = self._has_sliders or self._session.tracks_to_use()
        selected_track = self.song().view.selected_track
        num_strips = self._session.width()
        if selected_track in all_tracks:
            track_index = list(all_tracks).index(selected_track)
            new_offset = track_index - track_index % num_strips
            if not new_offset / num_strips == int(new_offset / num_strips):
                raise AssertionError
                self._session.set_offsets(new_offset, self._session.scene_offset())