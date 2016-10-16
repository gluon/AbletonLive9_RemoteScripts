#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchkey/Launchkey.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import InputControlElement, MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.DeviceComponent import DeviceComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.TransportComponent import TransportComponent
from Launchpad.ConfigurableButtonElement import ConfigurableButtonElement
from SessionNavigationComponent import SessionNavigationComponent
from TransportViewModeSelector import TransportViewModeSelector
from SpecialMixerComponent import SpecialMixerComponent
from consts import *
IS_MOMENTARY = True

def make_button(cc_no, name):
    button = ButtonElement(IS_MOMENTARY, MIDI_CC_TYPE, 0, cc_no)
    button.name = name
    return button


def make_configurable_button(cc_no, name, type = MIDI_NOTE_TYPE, channel = 0):
    button = ConfigurableButtonElement(IS_MOMENTARY, type, channel, cc_no)
    button.name = name
    return button


def make_encoder(cc_no, name):
    encoder = EncoderElement(MIDI_CC_TYPE, 0, cc_no, Live.MidiMap.MapMode.absolute)
    encoder.set_feedback_delay(-1)
    encoder.name = name
    return encoder


def make_slider(cc_no, name):
    slider = SliderElement(MIDI_CC_TYPE, 0, cc_no)
    slider.set_feedback_delay(-1)
    slider.name = name
    return slider


class LaunchkeyControlFactory(object):

    def create_next_track_button(self):
        return make_button(103, 'Next_Track_Button')

    def create_prev_track_button(self):
        return make_button(102, 'Prev_Track_Button')

    def create_scene_launch_button(self):
        return make_configurable_button(104, 'Scene_Launch_Button')

    def create_scene_stop_button(self):
        return make_configurable_button(120, 'Scene_Stop_Button')

    def create_clip_launch_button(self, index):
        return make_configurable_button(96 + index, 'Clip_Launch_%d' % index)

    def create_clip_stop_button(self, index):
        return make_configurable_button(112 + index, 'Clip_Stop_%d' % index)


class Launchkey(ControlSurface):
    """ Script for Novation's Launchkey 25/49/61 keyboards """

    def __init__(self, c_instance, control_factory = LaunchkeyControlFactory(), identity_response = SIZE_RESPONSE):
        ControlSurface.__init__(self, c_instance)
        self._control_factory = control_factory
        self._identity_response = identity_response
        with self.component_guard():
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._device_selection_follows_track_selection = True
            self._suggested_input_port = 'Launchkey InControl'
            self._suggested_output_port = 'Launchkey InControl'
            self._has_sliders = True
            self._current_midi_map = None
            self._master_slider = make_slider(7, 'Master_Volume_Control')
            self._modes_buttons = []
            for index in range(3):
                button = ButtonElement(IS_MOMENTARY, MIDI_NOTE_TYPE, 0, 13 + index)
                self._modes_buttons.append(button)
                self._modes_buttons[-1].add_value_listener(self._dummy_listener)

            self._setup_mixer()
            self._setup_session()
            self._setup_transport()
            self._setup_device()
            self._setup_navigation()
            for component in self.components:
                component.set_enabled(False)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self.schedule_message(2, self._send_midi, LIVE_MODE_ON)
        self.schedule_message(3, self._send_midi, SIZE_QUERY)

    def handle_sysex(self, midi_bytes):
        if midi_bytes[0:11] == self._identity_response:
            self._has_sliders = midi_bytes[11] != 48
            self._send_midi(LED_FLASHING_ON)
            self._update_mixer_offset()
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
                for index in range(len(self._sliders)):
                    self._mixer.channel_strip(index).set_volume_control(None)
                    self._mixer.channel_strip(index).set_mute_button(None)
                    slider = self._sliders[index]
                    slider.release_parameter()

                self._mixer.selected_strip().set_volume_control(self._master_slider)
            self.request_rebuild_midi_map()

    def disconnect(self):
        ControlSurface.disconnect(self)
        for button in self._modes_buttons:
            if button.value_has_listener(self._dummy_listener):
                button.remove_value_listener(self._dummy_listener)

        self._modes_buttons = None
        self._encoders = None
        self._sliders = None
        self._strip_buttons = None
        self._master_slider = None
        self._current_midi_map = None
        self._transport_view_modes = None
        self._send_midi(LED_FLASHING_OFF)
        self._send_midi(LIVE_MODE_OFF)

    def build_midi_map(self, midi_map_handle):
        self._current_midi_map = midi_map_handle
        ControlSurface.build_midi_map(self, midi_map_handle)

    def _setup_mixer(self):
        mute_solo_flip_button = make_button(59, 'Master_Button')
        self._mixer = SpecialMixerComponent(8)
        self._mixer.name = 'Mixer'
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.master_strip().set_volume_control(self._master_slider)
        self._sliders = []
        self._strip_buttons = []
        for index in range(8):
            strip = self._mixer.channel_strip(index)
            strip.name = 'Channel_Strip_' + str(index)
            strip.set_invert_mute_feedback(True)
            self._sliders.append(make_slider(41 + index, 'Volume_Control_%d' % index))
            strip.set_volume_control(self._sliders[-1])
            self._strip_buttons.append(make_button(51 + index, 'Mute_Button_%d' % index))

        self._mixer.set_strip_mute_solo_buttons(tuple(self._strip_buttons), mute_solo_flip_button)

    def _setup_session(self):
        scene_launch_button = self._control_factory.create_scene_launch_button()
        scene_stop_button = self._control_factory.create_scene_stop_button()
        self._session = SessionComponent(8, 0)
        self._session.name = 'Session_Control'
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.selected_scene().set_launch_button(scene_launch_button)
        self._session.selected_scene().set_triggered_value(GREEN_BLINK)
        self._session.set_stop_all_clips_button(scene_stop_button)
        scene_stop_button.set_on_off_values(AMBER_FULL, LED_OFF)
        self._session.set_mixer(self._mixer)
        self._session.set_stop_clip_value(AMBER_HALF)
        self._session.set_stop_clip_triggered_value(GREEN_BLINK)
        clip_launch_buttons = []
        clip_stop_buttons = []
        for index in range(8):
            clip_launch_buttons.append(self._control_factory.create_clip_launch_button(index))
            clip_stop_buttons.append(self._control_factory.create_clip_stop_button(index))
            clip_slot = self._session.selected_scene().clip_slot(index)
            clip_slot.set_triggered_to_play_value(GREEN_BLINK)
            clip_slot.set_triggered_to_record_value(RED_BLINK)
            clip_slot.set_stopped_value(AMBER_FULL)
            clip_slot.set_started_value(GREEN_FULL)
            clip_slot.set_recording_value(RED_FULL)
            clip_slot.set_launch_button(clip_launch_buttons[-1])
            clip_slot.name = 'Selected_Clip_Slot_' + str(index)

        self._session.set_stop_track_clip_buttons(tuple(clip_stop_buttons))

    def _setup_transport(self):
        rwd_button = make_button(112, 'Rwd_Button')
        ffwd_button = make_button(113, 'FFwd_Button')
        stop_button = make_button(114, 'Stop_Button')
        play_button = make_button(115, 'Play_Button')
        loop_button = make_button(116, 'Loop_Button')
        rec_button = make_button(117, 'Record_Button')
        transport = TransportComponent()
        transport.name = 'Transport'
        transport.set_stop_button(stop_button)
        transport.set_play_button(play_button)
        transport.set_record_button(rec_button)
        transport.set_loop_button(loop_button)
        self._transport_view_modes = TransportViewModeSelector(transport, self._session, ffwd_button, rwd_button)
        self._transport_view_modes.name = 'Transport_View_Modes'

    def _setup_device(self):
        encoders = [ make_encoder(21 + index, 'Device_Control_%d' % index) for index in xrange(8) ]
        self._encoders = tuple(encoders)
        device = DeviceComponent()
        device.name = 'Device_Component'
        self.set_device_component(device)
        device.set_parameter_controls(self._encoders)

    def _setup_navigation(self):
        self._next_track_button = self._control_factory.create_next_track_button()
        self._prev_track_button = self._control_factory.create_prev_track_button()
        self._session_navigation = SessionNavigationComponent(name='Session_Navigation')
        self._session_navigation.set_next_track_button(self._next_track_button)
        self._session_navigation.set_prev_track_button(self._prev_track_button)

    def _dummy_listener(self, value):
        pass

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        self._update_mixer_offset()

    def _update_mixer_offset(self):
        all_tracks = self._session.tracks_to_use()
        selected_track = self.song().view.selected_track
        num_strips = self._session.width()
        if selected_track in all_tracks:
            track_index = list(all_tracks).index(selected_track)
            new_offset = track_index - track_index % num_strips
            self._session.set_offsets(new_offset, self._session.scene_offset())