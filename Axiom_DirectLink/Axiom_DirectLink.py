#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_DirectLink/Axiom_DirectLink.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlElement import ControlElement
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionComponent import SessionComponent
from TransportViewModeSelector import TransportViewModeSelector
from ShiftableMixerComponent import ShiftableMixerComponent
from ShiftableSessionComponent import ShiftableSessionComponent
from ShiftableTransportComponent import ShiftableTransportComponent
from PeekableEncoderElement import PeekableEncoderElement
from BestBankDeviceComponent import BestBankDeviceComponent
from DetailViewCntrlComponent import DetailViewCntrlComponent
INITIAL_DISPLAY_DELAY = 20
STANDARD_DISPLAY_DELAY = 10
IS_MOMENTARY = True
SYSEX_START = (240, 0, 1, 5, 32, 127)
PAD_TRANSLATIONS = ((0, 3, 60, 15),
 (1, 3, 62, 15),
 (2, 3, 64, 15),
 (3, 3, 65, 15),
 (0, 2, 67, 15),
 (1, 2, 69, 15),
 (2, 2, 71, 15),
 (3, 2, 72, 15))

class Axiom_DirectLink(ControlSurface):
    """ Script for the M-Audio Axiom DirectLink """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._device_selection_follows_track_selection = True
            self._suggested_input_port = 'DirectLink'
            self._suggested_output_port = 'DirectLink'
            self._waiting_for_first_response = True
            self._has_sliders = True
            self._current_midi_map = None
            self._display_reset_delay = -1
            self._shift_pressed = False
            self._shift_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 13)
            self._master_slider = SliderElement(MIDI_CC_TYPE, 15, 41)
            self._next_nav_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 111)
            self._prev_nav_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 110)
            self._device_bank_buttons = None
            self._device_navigation = None
            self._shift_button.name = 'Shift_Button'
            self._master_slider.name = 'Master_Volume_Control'
            self._next_nav_button.name = 'Next_Track_Button'
            self._prev_nav_button.name = 'Prev_Track_Button'
            self._master_slider.add_value_listener(self._slider_value, identify_sender=True)
            self._shift_button.add_value_listener(self._shift_value)
            self._setup_mixer()
            self._setup_transport_and_session()
            self._setup_device()
            self._setup_display()
            for component in self.components:
                component.set_enabled(False)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self._waiting_for_first_response = True
        self.schedule_message(3, self._send_midi, SYSEX_START + (32, 46, 247))

    def handle_sysex(self, midi_bytes):
        if midi_bytes[0:-2] == SYSEX_START + (32,) and midi_bytes[-2] != 0:
            self._has_sliders = midi_bytes[-2] & 8 != 0
            if self._waiting_for_first_response:
                self._waiting_for_first_response = False
                self.schedule_message(1, self._show_startup_message)
                for component in self.components:
                    component.set_enabled(True)

            if self._has_sliders:
                self._mixer.master_strip().set_volume_control(self._master_slider)
                self._mixer.update()
            else:
                self._mixer.master_strip().set_volume_control(None)
                self._mixer.selected_strip().set_volume_control(self._master_slider)
            self.request_rebuild_midi_map()

    def disconnect(self):
        self._display_data_source.set_display_string('  ')
        self._shift_button.remove_value_listener(self._shift_value)
        self._inst_button.remove_value_listener(self._inst_value)
        for encoder in self._encoders:
            encoder.remove_value_listener(self._encoder_value)

        for slider in tuple(self._sliders) + (self._master_slider,):
            slider.remove_value_listener(self._slider_value)

        for button in tuple(self._strip_buttons) + (self._selected_mute_solo_button,):
            button.remove_value_listener(self._mixer_button_value)

        for button in self._device_bank_buttons:
            button.remove_value_listener(self._device_bank_value)

        self._encoders = None
        self._sliders = None
        self._strip_buttons = None
        self._master_slider = None
        self._current_midi_map = None
        self._selected_mute_solo_button = None
        self._inst_button = None
        self._shift_button = None
        self._device_navigation = None
        self._display = None
        ControlSurface.disconnect(self)
        self._send_midi(SYSEX_START + (32, 0, 247))

    def build_midi_map(self, midi_map_handle):
        self._current_midi_map = midi_map_handle
        ControlSurface.build_midi_map(self, midi_map_handle)

    def update_display(self):
        ControlSurface.update_display(self)
        if self._display_reset_delay >= 0:
            self._display_reset_delay -= 1
            if self._display_reset_delay == -1:
                self._show_current_track_name()

    def _setup_mixer(self):
        self._selected_mute_solo_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 12)
        mute_solo_flip_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 57)
        self._strip_buttons = []
        self._selected_mute_solo_button.name = 'Selected_Mute_Button'
        mute_solo_flip_button.name = 'Mute_Solo_Flip_Button'
        self._selected_mute_solo_button.add_value_listener(self._mixer_button_value, identify_sender=True)
        self._mixer = ShiftableMixerComponent(8)
        self._mixer.name = 'Mixer'
        self._mixer.set_shift_button(self._shift_button)
        self._mixer.set_selected_mute_solo_button(self._selected_mute_solo_button)
        self._mixer.set_select_buttons(self._next_nav_button, self._prev_nav_button)
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.master_strip().set_volume_control(self._master_slider)
        self._sliders = []
        for index in range(8):
            strip = self._mixer.channel_strip(index)
            strip.name = 'Channel_Strip_' + str(index)
            strip.set_invert_mute_feedback(True)
            self._sliders.append(SliderElement(MIDI_CC_TYPE, 15, 33 + index))
            self._sliders[-1].name = str(index) + '_Volume_Control'
            self._sliders[-1].set_feedback_delay(-1)
            self._sliders[-1].add_value_listener(self._slider_value, identify_sender=True)
            strip.set_volume_control(self._sliders[-1])
            self._strip_buttons.append(ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 49 + index))
            self._strip_buttons[-1].name = str(index) + '_Mute_Button'
            self._strip_buttons[-1].add_value_listener(self._mixer_button_value, identify_sender=True)

        self._mixer.set_strip_mute_solo_buttons(tuple(self._strip_buttons), mute_solo_flip_button)

    def _setup_transport_and_session(self):
        ffwd_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 115)
        rwd_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 114)
        loop_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 113)
        play_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 117)
        stop_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 116)
        rec_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 118)
        ffwd_button.name = 'FFwd_Button'
        rwd_button.name = 'Rwd_Button'
        loop_button.name = 'Loop_Button'
        play_button.name = 'Play_Button'
        stop_button.name = 'Stop_Button'
        rec_button.name = 'Record_Button'
        transport = ShiftableTransportComponent()
        transport.name = 'Transport'
        transport.set_shift_button(self._shift_button)
        transport.set_stop_button(stop_button)
        transport.set_play_button(play_button)
        transport.set_record_button(rec_button)
        pads = []
        for index in range(len(PAD_TRANSLATIONS)):
            pads.append(ButtonElement(IS_MOMENTARY, MIDI_NOTE_TYPE, 15, PAD_TRANSLATIONS[index][2]))
            pads[-1].name = 'Pad_' + str(index)

        self._session = ShiftableSessionComponent(8, 0)
        self._session.name = 'Session_Control'
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.set_mixer(self._mixer)
        self._session.set_shift_button(self._shift_button)
        self._session.set_clip_slot_buttons(tuple(pads))
        transport_view_modes = TransportViewModeSelector(transport, self._session, ffwd_button, rwd_button, loop_button)
        transport_view_modes.name = 'Transport_View_Modes'

    def _setup_device(self):
        self._encoders = []
        for offset in range(8):
            self._encoders.append(PeekableEncoderElement(MIDI_CC_TYPE, 15, 17 + offset, Live.MidiMap.MapMode.relative_smooth_two_compliment))
            self._encoders[-1].set_feedback_delay(-1)
            self._encoders[-1].add_value_listener(self._encoder_value, identify_sender=True)
            self._encoders[-1].name = 'Device_Control_' + str(offset)

        prev_bank_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 14)
        next_bank_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 15)
        prev_bank_button.name = 'Device_Bank_Down_Button'
        next_bank_button.name = 'Device_Bank_Up_Button'
        device = BestBankDeviceComponent()
        device.name = 'Device_Component'
        self.set_device_component(device)
        device.set_parameter_controls(tuple(self._encoders))
        device.set_bank_nav_buttons(prev_bank_button, next_bank_button)
        self._device_bank_buttons = (prev_bank_button, next_bank_button)
        prev_bank_button.add_value_listener(self._device_bank_value)
        next_bank_button.add_value_listener(self._device_bank_value)
        self._inst_button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 15, 109)
        self._inst_button.name = 'Inst_Button'
        self._inst_button.add_value_listener(self._inst_value)
        self._device_navigation = DetailViewCntrlComponent()
        self._device_navigation.name = 'Device_Navigation_Component'

    def _setup_display(self):
        self._display = PhysicalDisplayElement(5, 1)
        self._display.name = 'Display'
        self._display.set_message_parts(SYSEX_START + (17, 1, 0, 0), (247,))
        self._display_data_source = DisplayDataSource()
        self._display.segment(0).set_data_source(self._display_data_source)

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        self._show_current_track_name()

    def _shift_value(self, value):
        if not value in range(128):
            raise AssertionError
            self._shift_pressed = value > 0
            for encoder in self._encoders:
                encoder.set_peek_mode(self._shift_pressed)

            self._shift_pressed and self._mixer.set_select_buttons(None, None)
            self._session.set_track_bank_buttons(self._next_nav_button, self._prev_nav_button)
            self._device_component.set_bank_nav_buttons(None, None)
            self._device_navigation.set_device_nav_buttons(self._device_bank_buttons[0], self._device_bank_buttons[1])
        else:
            self._session.set_track_bank_buttons(None, None)
            self._mixer.set_select_buttons(self._next_nav_button, self._prev_nav_button)
            self._device_navigation.set_device_nav_buttons(None, None)
            self._device_component.set_bank_nav_buttons(self._device_bank_buttons[0], self._device_bank_buttons[1])
        self.request_rebuild_midi_map()

    def _encoder_value(self, value, sender):
        if not sender in self._encoders:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                display_string = self._device_component.is_enabled() and ' - '
                display_string = sender.mapped_parameter() != None and sender.mapped_parameter().name
            self._display_data_source.set_display_string(display_string)
            self._set_display_data_source(self._display_data_source)
            self._display_reset_delay = STANDARD_DISPLAY_DELAY

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
                    display_string = track == master and 'Ma'
                elif track in tracks:
                    display_string = str(list(tracks).index(track) + 1)
                elif track in returns:
                    display_string = str(chr(ord('A') + list(returns).index(track)))
                else:
                    raise False or AssertionError
                display_string += ' Vol'
            self._display_data_source.set_display_string(display_string)
            self._set_display_data_source(self._display_data_source)
            self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _mixer_button_value(self, value, sender):
        if not sender in tuple(self._strip_buttons) + (self._selected_mute_solo_button,):
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self._mixer.is_enabled() and value > 0:
                    strip = None
                    strip = sender == self._selected_mute_solo_button and self._mixer.selected_strip()
                else:
                    strip = self._mixer.channel_strip(self._strip_buttons.index(sender))
                strip != None and self._set_display_data_source(strip.track_name_data_source())
            else:
                self._display_data_source.set_display_string(' - ')
                self._set_display_data_source(self._display_data_source)
            self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _device_bank_value(self, value):
        if not value in range(128):
            raise AssertionError
            if self._device_component.is_enabled() and value > 0:
                data_source = self._device_component.bank_name_data_source()
                data_source = self._shift_pressed and self._device_component.device_name_data_source()
            self._set_display_data_source(data_source)
            self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _inst_value(self, value):
        if not value in range(128):
            raise AssertionError
            value > 0 and self._device_component.is_enabled() and self.song().view.selected_track.view.select_instrument() and self._set_display_data_source(self._device_component.device_name_data_source())
            self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _show_current_track_name(self):
        if self._display != None and self._mixer != None:
            self._set_display_data_source(self._mixer.selected_strip().track_name_data_source())

    def _show_startup_message(self):
        self._display.display_message('LIVE')
        self._display_reset_delay = INITIAL_DISPLAY_DELAY

    def _set_display_data_source(self, data_source):
        raise isinstance(data_source, DisplayDataSource) or AssertionError
        self._display.segment(0).set_data_source(data_source)
        data_source.update()