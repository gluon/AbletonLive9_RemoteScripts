#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/OpenLabs/OpenLabs.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.MixerComponent import MixerComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionComponent import SessionComponent
from SpecialTransportComponent import SpecialTransportComponent
from SpecialDeviceComponent import SpecialDeviceComponent

class OpenLabs(ControlSurface):
    """ Script for OpenLabs Controllers """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self._suppress_session_highlight = True
            self._suggested_input_port = 'Open Labs Midi Driver'
            self._suggested_output_port = ''
            self.set_pad_translations(((0, 0, 12, 15),
             (1, 0, 13, 15),
             (2, 0, 14, 15),
             (3, 0, 15, 15),
             (0, 1, 8, 15),
             (1, 1, 9, 15),
             (2, 1, 10, 15),
             (3, 1, 11, 15),
             (0, 2, 4, 15),
             (1, 2, 5, 15),
             (2, 2, 6, 15),
             (3, 2, 7, 15),
             (0, 3, 0, 15),
             (1, 3, 1, 15),
             (2, 3, 2, 15),
             (3, 3, 3, 15)))
            self._setup_mixer_control()
            self._setup_device_and_transport_control()

    def handle_sysex(self, midi_bytes):
        pass

    def _setup_mixer_control(self):
        is_momentary = True
        num_tracks = 8
        num_returns = 7
        mixer = MixerComponent(num_tracks, num_returns)
        for track in range(num_tracks):
            strip = mixer.channel_strip(track)
            strip.set_volume_control(SliderElement(MIDI_CC_TYPE, 15, 54 - track))
            strip.set_pan_control(SliderElement(MIDI_CC_TYPE, 15, 80 - track))
            strip.set_mute_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 117 - track))
            strip.set_invert_mute_feedback(True)

        for track in range(num_returns):
            strip = mixer.return_strip(track)
            strip.set_volume_control(SliderElement(MIDI_CC_TYPE, 15, 10 + track))

        mixer.set_bank_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 108), ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 109))
        mixer.set_crossfader_control(SliderElement(MIDI_CC_TYPE, 15, 9))
        mixer.master_strip().set_volume_control(SliderElement(MIDI_CC_TYPE, 15, 46))
        session = SessionComponent(0, 0)
        session.set_select_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 95), ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 92))
        session.selected_scene().set_launch_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 91))

    def _setup_device_and_transport_control(self):
        is_momentary = True
        device_param_controls = []
        for index in range(8):
            device_param_controls.append(EncoderElement(MIDI_CC_TYPE, 15, 62 - index, Live.MidiMap.MapMode.absolute))

        device = SpecialDeviceComponent()
        device.set_bank_nav_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 107), ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 106))
        device.set_parameter_controls(tuple(device_param_controls))
        self.set_device_component(device)
        transport = SpecialTransportComponent()
        transport.set_play_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 20))
        transport.set_stop_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 21))
        transport.set_record_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 22))
        transport.set_seek_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 24), ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 25))
        transport.set_tap_tempo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 94))
        transport.set_undo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 23))
        transport.set_redo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 27))
        transport.set_bts_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 15, 26))