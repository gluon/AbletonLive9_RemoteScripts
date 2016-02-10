#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/Axiom_AIR_25_49_61.py
from __future__ import with_statement
import Live
from Live import MidiMap
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import InputControlElement, MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.TransportComponent import TransportComponent
from ConfigurableButtonElement import ConfigurableButtonElement
from IdentifyingEncoderElement import IdentifyingEncoderElement
from NumericalDisplayElement import NumericalDisplayElement
from FaderModeSelector import FaderModeSelector
from FaderButtonModeSelector import FaderButtonModeSelector
from SingleFaderButtonModeSelector import SingleFaderButtonModeSelector
from EncoderModeSelector import EncoderModeSelector
from MainModeSelector import MainModeSelector
from DeviceNavComponent import DeviceNavComponent
from SpecialSessionComponent import SpecialSessionComponent
from SpecialMixerComponent import SpecialMixerComponent
from BestBankDeviceComponent import BestBankDeviceComponent
from TransportViewModeSelector import TransportViewModeSelector
from consts import *

def create_configurable_button(identifier, name, send_channel_offset = 0, identifier_send_offset = 0, send_msg_type = None):
    button = ConfigurableButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, GLOBAL_CHANNEL, identifier, GLOBAL_SEND_CHANNEL + send_channel_offset, identifier_send_offset, send_msg_type)
    button.name = name
    return button


def create_button(identifier, name):
    button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, GLOBAL_CHANNEL, identifier)
    button.name = name
    return button


def create_encoder(identifier, name):
    encoder = IdentifyingEncoderElement(MIDI_CC_TYPE, GLOBAL_CHANNEL, identifier, MidiMap.MapMode.relative_smooth_two_compliment, 12)
    encoder.name = name
    encoder.set_feedback_delay(-1)
    return encoder


def create_slider(identifier, name):
    slider = IdentifyingEncoderElement(MIDI_CC_TYPE, GLOBAL_CHANNEL, identifier, MidiMap.MapMode.absolute)
    slider.name = name
    slider.set_feedback_delay(-1)
    return slider


class Axiom_AIR_25_49_61(ControlSurface):
    """ Script for the M-Audio Axiom A.I.R. 25, 49 and 61 """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._alt_device_component = None
        with self.component_guard():
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._device_selection_follows_track_selection = True
            self._suggested_input_port = 'HyperControl'
            self._suggested_output_port = 'HyperControl'
            self._single_fader_button_modes = None
            self._has_faders = True
            self._display_reset_delay = -1
            self._hc_byte = HC_BYTE
            self._waiting_for_first_response = True
            self._setup_controls()
            self._setup_displays()
            self._setup_mixer()
            self._setup_session()
            self._setup_transport()
            self._setup_device()
            self._setup_modes()
            self._drum_group_midi_button = None
            self._drum_group_hyper_button = None
            for component in self.components:
                component.set_enabled(False)

    def disconnect(self):
        self._scheduled_messages = []
        for encoder in self._encoders:
            encoder.remove_value_listener(self._encoder_value)

        for fader in self._faders:
            fader.remove_value_listener(self._fader_value)

        for fader_button in self._fader_buttons:
            fader_button.remove_value_listener(self._fader_button_value)

        self._master_fader.remove_value_listener(self._fader_value)
        self._master_fader_button.remove_value_listener(self._fader_button_value)
        self._select_button.remove_value_listener(self._select_button_value)
        self._identify_button.remove_value_listener(self._identify_value)
        self._fader_group_midi_button.remove_value_listener(self._midi_button_value)
        self._fader_group_mix_button.remove_value_listener(self._hyper_button_value)
        self._fader_group_fx_button.remove_value_listener(self._hyper_button_value)
        self._encoder_group_midi_button.remove_value_listener(self._midi_button_value)
        self._encoder_group_mix_button.remove_value_listener(self._hyper_button_value)
        self._encoder_group_fx_button.remove_value_listener(self._hyper_button_value)
        if self._drum_group_midi_button != None:
            self._drum_group_midi_button.remove_value_listener(self._midi_button_value)
        if self._drum_group_hyper_button != None:
            self._drum_group_hyper_button.remove_value_listener(self._hyper_button_value)
        self._alt_device_component = None
        self._name_display = None
        self._value_display = None
        self._bank_display = None
        self._pad_display = None
        self._name_display_data_source = None
        self._value_display_data_source = None
        self._bank_display_data_source = None
        self._pad_display_data_source = None
        self._select_button = None
        self._left_button = None
        self._right_button = None
        self._up_button = None
        self._down_button = None
        self._loop_button = None
        self._ffwd_button = None
        self._rwd_button = None
        self._play_button = None
        self._stop_button = None
        self._rec_button = None
        self._master_fader_button = None
        self._fader_buttons = None
        self._faders = None
        self._encoders = None
        self._drum_pads = None
        self._identify_button = None
        self._main_group_hyper_button = None
        self._main_group_track_button = None
        self._main_group_fx_button = None
        self._encoder_group_midi_button = None
        self._encoder_group_mix_button = None
        self._encoder_group_fx_button = None
        self._fader_group_mode_button = None
        self._fader_group_midi_button = None
        self._fader_group_mix_button = None
        self._fader_group_fx_button = None
        self._drum_group_midi_button = None
        self._drum_group_roll_button = None
        self._drum_group_hyper_button = None
        self._mixer_for_encoders = None
        self._mixer_for_faders = None
        self._device_for_encoders = None
        self._device_for_faders = None
        self._transport = None
        self._session = None
        ControlSurface.disconnect(self)
        self._send_midi(SYSEX_START + DISABLE_HYPERCONTROL)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self.schedule_message(5, self._send_midi, IDENTITY_REQUEST)

    def handle_sysex(self, midi_bytes):
        if midi_bytes[0:10] == AXIOM_AIR_RESPONSE:
            if midi_bytes[12:15] < AXIOM_REV4_RESPONSE:
                self.schedule_message(1, self._send_midi, SYSEX_START + ENGAGE_HYPERCONTROL)
                self.schedule_message(2, self._send_midi, SYSEX_START + CLEAR_ALL)
                self.schedule_message(3, self._name_display.display_message, 'Firmware')
                self.schedule_message(13, self._name_display.display_message, 'Update')
                self.schedule_message(23, self._name_display.display_message, 'Required')
                self.schedule_message(33, self._send_midi, SYSEX_START + DISABLE_HYPERCONTROL)
            elif midi_bytes[12:15] >= AXIOM_REV4_RESPONSE:
                if self._waiting_for_first_response == True:
                    self._waiting_for_first_response = False
                    self._has_faders = midi_bytes[10] != 50
                    self.schedule_message(1, self._send_midi, SYSEX_START + ENGAGE_HYPERCONTROL)
                    self.schedule_message(2, self._send_midi, SYSEX_START + SPECIAL_HYPERCONTROL)
                    self.schedule_message(3, self._complete_setup)
                else:
                    self._display_reset_delay = 0
        elif midi_bytes[0:8] == REQUEST_HYPERCONTROL:
            self.schedule_message(5, self._send_midi, IDENTITY_REQUEST)

    def update_display(self):
        ControlSurface.update_display(self)
        if self._display_reset_delay >= 0:
            self._display_reset_delay -= 1
            if self._display_reset_delay == -1:
                self._set_displays_to_default()

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        self._display_reset_delay = 0

    def restore_bank(self, bank_index):
        ControlSurface.restore_bank(self, bank_index)
        if self._alt_device_component != None:
            self._alt_device_component.restore_bank(bank_index)

    def set_appointed_device(self, device):
        ControlSurface.set_appointed_device(self, device)
        with self.component_guard():
            if self._alt_device_component != None:
                self._alt_device_component.set_device(device)

    def set_alt_device_component(self, device_component):
        self._alt_device_component = device_component

    def _update_device_selection(self):
        track = self.song().view.selected_track
        device_to_select = track.view.selected_device
        if device_to_select == None and len(track.devices) > 0:
            device_to_select = track.devices[0]
        if device_to_select != None:
            self.song().view.select_device(device_to_select)
        self._device_component.set_device(device_to_select)
        if self._alt_device_component != None:
            self._alt_device_component.set_device(device_to_select)

    def _setup_controls(self):
        self._left_button = create_button(99, 'Left_Button')
        self._right_button = create_button(100, 'Right_Button')
        self._up_button = create_button(101, 'Up_Button')
        self._down_button = create_button(102, 'Down_Button')
        self._loop_button = create_button(113, 'Loop_Button')
        self._rwd_button = create_button(114, 'Rwd_Button')
        self._ffwd_button = create_button(115, 'FFwd_Button')
        self._stop_button = create_button(116, 'Stop_Button')
        self._play_button = create_button(117, 'Play_Button')
        self._rec_button = create_button(118, 'Record_Button')
        self._select_button = ConfigurableButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, GLOBAL_CHANNEL, 98)
        self._select_button.name = 'Select_Button'
        self._select_button.add_value_listener(self._select_button_value)
        self._main_group_hyper_button = create_configurable_button(104, 'Fader_Group_HyperControl_Button', 2, 14)
        self._main_group_track_button = create_configurable_button(105, 'Main_Group_Track_Button', 2, 11)
        self._main_group_fx_button = create_configurable_button(106, 'Main_Group_Inst_FX_Button', 2, 11)
        self._identify_button = create_configurable_button(97, 'Identify_Button', 2, 16)
        self._identify_button.add_value_listener(self._identify_value)
        self._fader_buttons = []
        for index in range(8):
            self._fader_buttons.append(create_configurable_button(49 + index, 'Fader_Button_%d' % index))
            self._fader_buttons[-1].add_value_listener(self._fader_button_value, identify_sender=True)

        self._faders = []
        for index in range(8):
            self._faders.append(create_slider(33 + index, 'Fader_%d' % index))
            self._faders[-1].add_value_listener(self._fader_value, identify_sender=True)

        self._master_fader_button = create_configurable_button(57, 'Master_Fader_Button')
        self._master_fader_button.add_value_listener(self._fader_button_value, identify_sender=True)
        self._master_fader = create_slider(41, 'Master_Fader')
        self._master_fader.add_value_listener(self._fader_value, identify_sender=True)
        self._fader_group_mode_button = create_configurable_button(61, 'Fader_Group_Mode_Button')
        self._fader_group_midi_button = create_configurable_button(60, 'Fader_Group_MIDI_Button')
        self._fader_group_midi_button.add_value_listener(self._midi_button_value, identify_sender=True)
        self._fader_group_mix_button = create_configurable_button(58, 'Fader_Group_Mix_Button', 0, 1)
        self._fader_group_mix_button.add_value_listener(self._hyper_button_value, identify_sender=True)
        self._fader_group_fx_button = create_configurable_button(59, 'Fader_Group_Inst_FX_Button', 0, -1)
        self._fader_group_fx_button.add_value_listener(self._hyper_button_value, identify_sender=True)
        self._encoders = []
        for index in range(8):
            self._encoders.append(create_encoder(17 + index, 'Encoder_%d' % index))
            self._encoders[-1].add_value_listener(self._encoder_value, identify_sender=True)

        self._encoder_group_midi_button = create_configurable_button(27, 'Encoder_Group_MIDI_Button', 0, 72)
        self._encoder_group_midi_button.add_value_listener(self._midi_button_value, identify_sender=True)
        self._encoder_group_mix_button = create_configurable_button(25, 'Encoder_Group_Mix_Button', 0, 72)
        self._encoder_group_mix_button.add_value_listener(self._hyper_button_value, identify_sender=True)
        self._encoder_group_fx_button = create_configurable_button(26, 'Encoder_Group_Inst_FX_Button', 0, 72)
        self._encoder_group_fx_button.add_value_listener(self._hyper_button_value, identify_sender=True)

    def _setup_drum_pads(self):
        self._drum_pads = []
        num_pads = 12 if self._has_faders else 16
        for index in range(8):
            self._drum_pads.append(create_configurable_button(81 + index, 'Pad_%d' % index, 0, 0, MIDI_CC_TYPE))

        for index in range(num_pads - 8):
            self._drum_pads.append(ConfigurableButtonElement(IS_MOMENTARY, MIDI_NOTE_TYPE, GLOBAL_CHANNEL - 1, 81 + index, GLOBAL_SEND_CHANNEL, 8, MIDI_CC_TYPE))
            self._drum_pads[-1].name = 'Pad_' + str(index + 8)

        self._drum_group_midi_button = create_configurable_button(91, 'Drum_Group_MIDI_Button', 2, -2)
        self._drum_group_midi_button.add_value_listener(self._midi_button_value, identify_sender=True)
        self._drum_group_roll_button = create_configurable_button(90, 'Drum_Group_Roll_Button', -1)
        self._drum_group_hyper_button = create_configurable_button(89, 'Drum_Group_HyperControl_Button', 2, 2)
        self._drum_group_hyper_button.add_value_listener(self._hyper_button_value, identify_sender=True)

    def _setup_displays(self):
        self._name_display = PhysicalDisplayElement(12, 1)
        self._name_display.name = 'Name_Display'
        self._name_display.set_message_parts(SYSEX_START + (21,), (0, 247))
        self._name_display.set_clear_all_message(CLEAR_NAME)
        self._name_display_data_source = DisplayDataSource()
        self._name_display.segment(0).set_data_source(self._name_display_data_source)
        self._value_display = NumericalDisplayElement(3, 1)
        self._value_display.name = 'Value_Display'
        self._value_display.set_message_parts(SYSEX_START + (20, 48), (0, 247))
        self._value_display.set_clear_all_message(CLEAR_VALUE)
        self._value_display_data_source = DisplayDataSource()
        self._value_display.segment(0).set_data_source(self._value_display_data_source)
        self._bank_display = NumericalDisplayElement(3, 1)
        self._bank_display.name = 'Bank_Display'
        self._bank_display.set_message_parts(SYSEX_START + (19,), (0, 247))
        self._bank_display.set_clear_all_message(CLEAR_BANK)
        self._bank_display_data_source = DisplayDataSource()
        self._bank_display.segment(0).set_data_source(self._bank_display_data_source)
        self._pad_display = NumericalDisplayElement(2, 1)
        self._pad_display.name = 'Pad_Display'
        self._pad_display.set_message_parts(SYSEX_START + (18,), (0, 247))
        self._pad_display.set_clear_all_message(CLEAR_PAD)
        self._pad_display_data_source = DisplayDataSource()
        self._pad_display.segment(0).set_data_source(self._pad_display_data_source)

    def _setup_mixer(self):
        self._mixer_for_encoders = SpecialMixerComponent(self._name_display, self._value_display, 8)
        self._mixer_for_encoders.name = 'Mixer_for_encoders'
        self._mixer_for_faders = SpecialMixerComponent(self._name_display, self._value_display, 8)
        self._mixer_for_faders.name = 'Mixer_for_faders'

    def _setup_session(self):
        self._session = SpecialSessionComponent(8, 0)
        self._session.name = 'Session_Control'
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.set_mixer(self._mixer_for_encoders)
        self._session.set_alt_mixer(self._mixer_for_faders)
        self._session.add_offset_listener(self._update_bank_value)

    def _setup_transport(self):
        self._transport = TransportComponent()
        self._transport.name = 'Transport'
        self._transport.set_stop_button(self._stop_button)
        self._transport.set_play_button(self._play_button)
        self._transport.set_record_button(self._rec_button)
        transport_view_modes = TransportViewModeSelector(self._transport, self._session, self._ffwd_button, self._rwd_button, self._loop_button)
        transport_view_modes.name = 'Transport_View_Modes'

    def _setup_device(self):
        self._device_for_encoders = BestBankDeviceComponent()
        self._device_for_encoders.name = 'Device_Component_for_encoders'
        self._device_for_faders = BestBankDeviceComponent()
        self._device_for_faders.name = 'Device_Component_for_faders'
        self.set_device_component(self._device_for_encoders)
        self.set_alt_device_component(self._device_for_faders)
        self._device_nav = DeviceNavComponent()
        self._device_nav.name = 'Device_Nav_Component'

    def _setup_modes(self):
        self._fader_button_modes = FaderButtonModeSelector(self._mixer_for_faders, tuple(self._fader_buttons))
        self._fader_button_modes.name = 'Fader_Button_Modes'
        self._fader_button_modes.set_mode_toggle(self._fader_group_mode_button)
        self._fader_modes = FaderModeSelector(self._mixer_for_faders, self._device_for_faders, tuple(self._faders), self._fader_button_modes, self._master_fader_button)
        self._fader_modes.name = 'Fader_Modes'
        self._fader_modes.set_mode_buttons((self._fader_group_mix_button, self._fader_group_fx_button))
        self._encoder_modes = EncoderModeSelector(self._mixer_for_encoders, self._device_for_encoders, tuple(self._encoders))
        self._encoder_modes.name = 'Encoder_Modes'
        self._encoder_modes.set_mode_buttons((self._encoder_group_mix_button, self._encoder_group_fx_button))
        main_modes = MainModeSelector(self._device_for_encoders, self._device_for_faders, self._session, self._mixer_for_faders, self._device_nav, self._up_button, self._down_button, self._left_button, self._right_button, self._select_button)
        main_modes.name = 'Main_Modes'
        main_modes.set_mode_buttons((self._main_group_track_button, self._main_group_fx_button))

    def _setup_master_fader(self):
        if self._has_faders:
            self._mixer_for_encoders.master_strip().set_volume_control(self._master_fader)
        else:
            self._mixer_for_encoders.selected_strip().set_volume_control(self._master_fader)

    def _setup_single_fader_button_modes(self):
        self._single_fader_button_modes = SingleFaderButtonModeSelector(self._mixer_for_encoders, self._fader_group_midi_button)
        self._single_fader_button_modes.name = 'Single_Fader_Button_Modes'
        self._single_fader_button_modes.set_mode_toggle(self._fader_group_mode_button)

    def _complete_setup(self):
        self._setup_drum_pads()
        self._set_drum_pads_to_hc()
        self._setup_master_fader()
        if not self._has_faders:
            self._setup_single_fader_button_modes()
        for control in self.controls:
            if isinstance(control, InputControlElement):
                control.clear_send_cache()

        for component in self.components:
            component.set_enabled(True)

        self._fader_group_midi_button.send_value(LED_OFF, True)
        self._encoder_group_midi_button.send_value(LED_OFF, True)
        self._main_group_hyper_button.send_value(AMB_FULL, True)
        self.request_rebuild_midi_map()
        self._on_selected_track_changed()
        self.schedule_message(1, self._show_startup_message)

    def _show_startup_message(self):
        self._send_midi(SYSEX_START + CLEAR_ALL)
        self._name_display.display_message('Ableton Live')
        self._display_reset_delay = INITIAL_DISPLAY_DELAY

    def _select_button_value(self, value):
        self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _identify_value(self, value):
        for encoder in self._encoders:
            encoder.set_identify_mode(value > 0)

        for fader in self._faders:
            fader.set_identify_mode(value > 0)

        self._master_fader.set_identify_mode(value > 0)
        self._display_reset_delay = 0
        self._identify_button.turn_on() if value > 0 else self._identify_button.turn_off()

    def _midi_button_value(self, value, sender):
        if value > 0:
            if sender is self._drum_group_midi_button:
                hc_byte = self._hc_byte ^ PADS
                if hc_byte != self._hc_byte:
                    self._hc_byte = hc_byte
                    self._drum_group_hyper_button.send_value(LED_OFF, True)
                    self.schedule_message(1, self._send_midi, SYSEX_START + (32, self._hc_byte, 247))
            elif sender is self._encoder_group_midi_button:
                hc_byte = self._hc_byte ^ ENCODERS
                if hc_byte != self._hc_byte:
                    self._hc_byte = hc_byte
                    self._encoder_group_mix_button.send_value(LED_OFF, True)
                    self._encoder_group_fx_button.send_value(LED_OFF, True)
                    if self._encoder_modes.mode_index < 3:
                        self._encoder_modes.set_enabled(False)
                    self.schedule_message(1, self._send_midi, SYSEX_START + (32, self._hc_byte, 247))
            elif sender is self._fader_group_midi_button:
                if self._has_faders:
                    hc_byte = self._hc_byte ^ FADERS
                    if hc_byte != self._hc_byte:
                        self._hc_byte = hc_byte
                        self._fader_group_mix_button.send_value(LED_OFF, True)
                        self._fader_group_fx_button.send_value(LED_OFF, True)
                        self._fader_group_mode_button.send_value(LED_OFF, True)
                        if self._fader_modes.mode_index < 2:
                            self._fader_modes.set_enabled(False)
                            self._fader_button_modes.set_enabled(False)
                        self.schedule_message(1, self._send_midi, SYSEX_START + (32, self._hc_byte, 247))
                else:
                    self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _hyper_button_value(self, value, sender):
        if value > 0:
            if sender is self._drum_group_hyper_button:
                if self._hc_byte | PADS != self._hc_byte:
                    self._hc_byte = self._hc_byte | PADS
                    self._send_midi(SYSEX_START + (32, self._hc_byte, 247))
                    self.schedule_message(1, self._set_drum_pads_to_hc)
            elif sender is self._encoder_group_fx_button or sender is self._encoder_group_mix_button:
                if self._hc_byte | ENCODERS != self._hc_byte:
                    self._hc_byte = self._hc_byte | ENCODERS
                    self._send_midi(SYSEX_START + (32, self._hc_byte, 247))
                    self._encoder_group_midi_button.turn_off()
                    if sender is self._encoder_group_fx_button:
                        self._encoder_modes.set_enabled(True)
                        self._display_reset_delay = 0
                        return
                    else:
                        self.schedule_message(1, self._encoder_modes.set_enabled, True)
                        self.schedule_message(1, self._encoder_modes.update)
                        self._display_reset_delay = 2
                        return
            elif sender is self._fader_group_fx_button or sender is self._fader_group_mix_button:
                if self._hc_byte | FADERS != self._hc_byte:
                    self._hc_byte = self._hc_byte | FADERS
                    self._send_midi(SYSEX_START + (32, self._hc_byte, 247))
                    self._fader_group_midi_button.turn_off()
                    self._fader_button_modes.set_enabled(True)
                    if sender is self._fader_group_fx_button:
                        self._fader_modes.set_enabled(True)
                        self._fader_button_modes.set_enabled(True)
                        self._display_reset_delay = 0
                        return
                    else:
                        self.schedule_message(1, self._fader_modes.set_enabled, True)
                        self.schedule_message(1, self._fader_modes.update)
                        self.schedule_message(1, self._fader_button_modes.set_enabled, True)
                        self.schedule_message(1, self._fader_button_modes.update)
                        self._display_reset_delay = 2
                        return
            self._display_reset_delay = 0

    def _set_drum_pads_to_hc(self):
        self._drum_group_midi_button.send_value(LED_OFF, True)
        self._drum_group_hyper_button.send_value(RED_FULL, True)
        for index in range(len(self._drum_pads)):
            self._drum_pads[index].send_value(RED_LOW, True)

    def _fader_button_value(self, value, sender):
        self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _fader_value(self, value, sender):
        param = sender.mapped_parameter()
        if param != None:
            param_range = param.max - param.min
            if param.name == 'Track Volume':
                if sender == self._master_fader:
                    if self._has_faders:
                        name_string = 'Master  Vol'
                    else:
                        name_string = self._mixer_for_faders.selected_strip().track_name_data_source().display_string() + '   Vol'
                else:
                    name_string = self._mixer_for_faders.channel_strip(self._faders.index(sender)).track_name_data_source().display_string() + '   Vol'
            else:
                name_string = param.name
                value = int((param.value - param.min) / param_range * 127)
            value_string = str(value)
        else:
            name_string = '<unmapped>'
            value_string = None
            self.schedule_message(1, self._set_value_string)
        self._set_name_string(name_string)
        self._set_value_string(value_string)

    def _encoder_value(self, value, sender):
        param = sender.mapped_parameter()
        if param != None:
            param_range = param.max - param.min
            if param.name == 'Track Volume':
                name_string = self._mixer_for_encoders.channel_strip(self._encoders.index(sender)).track_name_data_source().display_string() + '   Vol'
                value = int((param.value - param.min) / param_range * 127)
            elif param.name == 'Track Panning':
                name_string = self._mixer_for_encoders.channel_strip(self._encoders.index(sender)).track_name_data_source().display_string() + '   Pan'
                value = int(param.value / param_range * 127)
                if value < 0:
                    name_string += '  L'
                elif value > 0:
                    name_string += '  R'
                else:
                    name_string += '  C'
            else:
                name_string = param.name
                value = int((param.value - param.min) / param_range * 127)
            value_string = str(value)
        else:
            name_string = '<unmapped>'
            value_string = None
            self.schedule_message(1, self._set_value_string)
        self._set_name_string(name_string)
        self._set_value_string(value_string)

    def _set_displays_to_default(self):
        self._name_display.segment(0).set_data_source(self._mixer_for_encoders.selected_strip().track_name_data_source())
        self._name_display.update()
        self._update_bank_value()
        self._set_value_string(None)
        self._send_midi(SYSEX_START + LCD_HC_DEFAULT)

    def _set_name_string(self, name_string):
        self._name_display.segment(0).set_data_source(self._name_display_data_source)
        self._name_display_data_source.set_display_string(name_string)
        self._display_reset_delay = STANDARD_DISPLAY_DELAY

    def _set_value_string(self, value_string = None):
        if value_string != None:
            self._value_display_data_source.set_display_string(value_string)
        else:
            self._value_display.reset()

    def _set_bank_string(self, bank_string = None):
        if bank_string != None:
            self._bank_display_data_source.set_display_string(bank_string)
        else:
            self._bank_display.reset()

    def _update_bank_value(self):
        bank = (self._session.track_offset() + 1) / self._session.width() + 1
        self._set_bank_string(str(bank))

    def _install_mapping(self, midi_map_handle, control, parameter, feedback_delay, feedback_map):
        if not self._in_build_midi_map:
            raise AssertionError
            raise midi_map_handle != None or AssertionError
            raise control != None and parameter != None or AssertionError
            raise isinstance(parameter, Live.DeviceParameter.DeviceParameter) or AssertionError
            raise isinstance(control, InputControlElement) or AssertionError
            raise isinstance(feedback_delay, int) or AssertionError
            if not isinstance(feedback_map, tuple):
                raise AssertionError
                success = False
                feedback_rule = None
                feedback_rule = control.message_type() is MIDI_NOTE_TYPE and Live.MidiMap.NoteFeedbackRule()
                feedback_rule.note_no = 0
                feedback_rule.vel_map = (0,)
            elif control.message_type() is MIDI_CC_TYPE:
                feedback_rule = Live.MidiMap.CCFeedbackRule()
                feedback_rule.cc_no = 0
                feedback_rule.cc_value_map = (0,)
            elif control.message_type() is MIDI_PB_TYPE:
                feedback_rule = Live.MidiMap.PitchBendFeedbackRule()
                feedback_rule.value_pair_map = feedback_map
            raise feedback_rule != None or AssertionError
            feedback_rule.channel = control.message_channel()
            feedback_rule.delay_in_ms = feedback_delay
            success = control.message_type() is MIDI_NOTE_TYPE and Live.MidiMap.map_midi_note_with_feedback_map(midi_map_handle, parameter, control.message_channel(), control.message_identifier(), feedback_rule)
        elif control.message_type() is MIDI_CC_TYPE:
            success = Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, control.message_channel(), control.message_identifier(), control.message_map_mode(), feedback_rule, not control.needs_takeover())
        elif control.message_type() is MIDI_PB_TYPE:
            success = Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, parameter, control.message_channel(), feedback_rule, not control.needs_takeover())
        return success