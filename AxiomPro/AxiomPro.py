#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AxiomPro/AxiomPro.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlElement import ControlElement
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from _Framework.LogicalDisplaySegment import LogicalDisplaySegment
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionComponent import SessionComponent
from TransportViewModeSelector import TransportViewModeSelector
from SelectButtonModeSelector import SelectButtonModeSelector
from PageableDeviceComponent import PageableDeviceComponent
from EncoderMixerModeSelector import EncoderMixerModeSelector
from MixerOrDeviceModeSelector import MixerOrDeviceModeSelector
from NotifyingMixerComponent import NotifyingMixerComponent
from DisplayingMixerComponent import DisplayingMixerComponent
from PeekableEncoderElement import PeekableEncoderElement
SYSEX_START = (240, 0, 1, 5, 32, 127)
PAD_TRANSLATIONS = ((0, 2, 85, 15),
 (1, 2, 86, 15),
 (2, 2, 87, 15),
 (3, 2, 88, 15),
 (0, 3, 81, 15),
 (1, 3, 82, 15),
 (2, 3, 83, 15),
 (3, 3, 84, 15))

class AxiomPro(ControlSurface):
    """ Script for the M-Audio Axiom Pro """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            is_momentary = True
            self._device_selection_follows_track_selection = True
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._suggested_input_port = 'HyperControl'
            self._suggested_output_port = 'HyperControl'
            self._display_on_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, 15, 79)
            self._waiting_for_first_response = True
            mixer1 = DisplayingMixerComponent(0)
            mixer1.set_select_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 111), ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 110))
            mixer1.set_mute_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 12))
            mixer1.set_solo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 13))
            mixer2 = NotifyingMixerComponent(8)
            mixer2.set_bank_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 15), ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 14))
            mixer2.master_strip().set_volume_control(SliderElement(MIDI_CC_TYPE, 15, 41))
            for index in range(8):
                mixer2.channel_strip(index).set_volume_control(SliderElement(MIDI_CC_TYPE, 15, 33 + index))

            device = PageableDeviceComponent()
            self.set_device_component(device)
            ffwd_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 115)
            rwd_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 114)
            loop_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 113)
            transport = TransportComponent()
            transport.set_stop_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 116))
            transport.set_play_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 117))
            transport.set_record_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 118))
            session = SessionComponent(0, 0)
            transport_view_modes = TransportViewModeSelector(transport, session, ffwd_button, rwd_button, loop_button)
            select_button_modes = SelectButtonModeSelector(mixer2, tuple([ ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 49 + offset) for offset in range(8) ]))
            select_button_modes.set_mode_toggle(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 57))
            self._mixer_encoder_modes = EncoderMixerModeSelector(mixer2)
            encoders = []
            for offset in range(8):
                encoders.append(PeekableEncoderElement(MIDI_CC_TYPE, 15, 17 + offset, Live.MidiMap.MapMode.relative_smooth_two_compliment))
                encoders[-1].set_feedback_delay(-1)

            mixer_or_device = MixerOrDeviceModeSelector(self._mixer_encoder_modes, device, tuple(encoders), tuple([ ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 74 + offset) for offset in range(4) ]))
            mixer_or_device.set_mode_toggle(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 109))
            mixer_or_device.set_peek_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 78))
            self._track_display = PhysicalDisplayElement(8, 1)
            self._track_display.set_clear_all_message(SYSEX_START + (16, 247))
            self._track_display.set_message_parts(SYSEX_START + (17, 1, 0, 0), (247,))
            self._track_display.segment(0).set_data_source(mixer1.selected_strip().track_name_data_source())
            device_display = PhysicalDisplayElement(8, 1)
            device_display.set_message_parts(SYSEX_START + (17, 1, 0, 10), (247,))
            parameter_display = PhysicalDisplayElement(16, 1)
            parameter_display.set_message_parts(SYSEX_START + (17, 2, 0, 0), (247,))
            select_button_modes.set_mode_display(parameter_display)
            mixer1.set_display(parameter_display)
            mixer2.set_bank_display(parameter_display)
            page_displays = []
            for index in range(4):
                page_displays.append(PhysicalDisplayElement(5, 1))
                page_displays[-1].set_message_parts(SYSEX_START + (17,
                 4,
                 index,
                 0), (247,))

            encoder_display = PhysicalDisplayElement(80, 8)
            encoder_display.set_message_parts(SYSEX_START + (17, 3), (247,))
            for index in range(8):
                pos_id = tuple()
                if index != 0:
                    pos_id += (0,)
                if index > 3:
                    pos_id += (index % 4, 13)
                else:
                    pos_id += (index % 4, 0)
                encoder_display.segment(index).set_position_identifier(pos_id)

            mixer_or_device.set_displays(encoder_display, parameter_display, device_display, tuple(page_displays))
            for component in self.components:
                component.set_enabled(False)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self._waiting_for_first_response = True
        self.schedule_message(10, self._send_midi, SYSEX_START + (32, 46, 247))

    def handle_sysex(self, midi_bytes):
        if midi_bytes[0:-2] == SYSEX_START + (32,):
            msg_id_byte = midi_bytes[-2]
            is_setup_response = msg_id_byte in (46, 38)
            has_sliders = msg_id_byte == 46
            if is_setup_response:
                if self._waiting_for_first_response:
                    self._waiting_for_first_response = False
                    self._display_on_button.send_value(0)
                    for component in self.components:
                        component.set_enabled(True)

                    self._display_on_button.send_value(127)
                    self._send_midi(SYSEX_START + (16, 247))
                    self._send_midi(SYSEX_START + (17, 3, 0, 1, 65, 98, 108, 101, 116, 111, 110, 32, 76, 105, 118, 101, 32, 67, 111, 110, 116, 114, 111, 108, 32, 0, 1, 4, 83, 117, 114, 102, 97, 99, 101, 32, 118, 49, 46, 48, 46, 48, 46, 247))
                self._mixer_encoder_modes.set_show_volume_page(not has_sliders)
                for display in self._displays:
                    display.set_block_messages(False)

                self.schedule_message(25, self._refresh_displays)
            elif msg_id_byte == 43:
                self._send_midi(SYSEX_START + (16, 247))
                for display in self._displays:
                    if display is self._track_display:
                        display.update()
                    else:
                        display.set_block_messages(True)

    def disconnect(self):
        ControlSurface.disconnect(self)
        self._send_midi(SYSEX_START + (32, 0, 247))
        self._send_midi(SYSEX_START + (16, 247))
        self._send_midi(SYSEX_START + (17, 3, 0, 4, 65, 98, 108, 101, 116, 111, 110, 32, 76, 105, 118, 101, 32, 67, 111, 110, 116, 114, 111, 108, 32, 0, 1, 4, 83, 117, 114, 102, 97, 99, 101, 32, 67, 108, 111, 115, 101, 100, 46, 247))