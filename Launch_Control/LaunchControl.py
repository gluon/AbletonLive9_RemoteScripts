#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control/LaunchControl.py
from __future__ import with_statement
from functools import partial
import Live
from _Framework import Task
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ControlSurface import ControlSurface
from _Framework.DeviceBankRegistry import DeviceBankRegistry
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import ModesComponent, LayerMode
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import nop
from _Framework.ViewControlComponent import ViewControlComponent
from ButtonSysexControl import ButtonSysexControl
from ConfigurableButtonElement import ConfigurableButtonElement
from DeviceNavigationComponent import DeviceNavigationComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialSessionComponent import SpecialSessionComponent
import Colors
import Sysex

def make_launch_control_button(identifier, name, channel = 0, is_pad = False):
    button = ConfigurableButtonElement(True, MIDI_NOTE_TYPE if is_pad else MIDI_CC_TYPE, channel, identifier)
    button.name = name
    button.set_on_off_values(Colors.LED_ON, Colors.LED_OFF)
    return button


def make_launch_control_encoder(identifier, name, channel = 0):
    encoder = EncoderElement(MIDI_CC_TYPE, channel, identifier, Live.MidiMap.MapMode.absolute)
    encoder.reset = nop
    encoder.set_feedback_delay(-1)
    encoder.name = name
    return encoder


def make_all_encoders(name_prefix = '', make_encoder = make_launch_control_encoder):
    return ([ make_encoder(41 + index, name_prefix + '_Bottom_Encoder_' + str(index)) for index in xrange(8) ], [ make_encoder(21 + index, name_prefix + '_Top_Encoder_' + str(index)) for index in xrange(8) ])


pad_identifiers = [ (9 + i if i < 4 else 21 + i) for i in xrange(8) ]
CC_STATUS = 176
MODE_SYSEX_MAP = {'mixer': Sysex.MIXER_MODE,
 'session': Sysex.SESSION_MODE,
 'device': Sysex.DEVICE_MODE}
SYSEX_MODE_MAP = dict([ (v, k) for k, v in MODE_SYSEX_MAP.iteritems() ])

class LaunchControl(ControlSurface):

    def __init__(self, c_instance):
        super(LaunchControl, self).__init__(c_instance)
        with self.component_guard():
            self._device_selection_follows_track_selection = True
            self._init_mixer()
            self._init_session()
            self._init_device()
            self._init_modes()
            self._refresh_state_task = self._tasks.add(Task.sequence(Task.delay(3), Task.run(self._do_refresh_state)))
            self._refresh_state_task.kill()
        self.log_message('Launch Control script loaded')

    def disconnect(self):
        super(LaunchControl, self).disconnect()
        for channel in xrange(16):
            self._send_midi((CC_STATUS + channel, 0, 0))

    def refresh_state(self):
        self._refresh_state_task.restart()

    def _do_refresh_state(self):
        self._send_current_mode()
        self._update_hardware()
        self.schedule_message(3, super(LaunchControl, self).refresh_state)

    def _update_hardware(self):
        for channel in xrange(8, 11):
            self._send_midi(Sysex.make_automatic_flashing_message(channel))

    def _send_current_mode(self):
        try:
            self._send_midi(MODE_SYSEX_MAP[self._modes.selected_mode])
        except KeyError:
            pass

    def _init_mixer(self):
        make_button = partial(make_launch_control_button, channel=8)
        make_encoder = partial(make_launch_control_encoder, channel=8)
        bottom_encoders, top_encoders = make_all_encoders('Mixer', make_encoder)
        pan_volume_layer = Layer(volume_controls=ButtonMatrixElement(rows=[bottom_encoders]), pan_controls=ButtonMatrixElement(rows=[top_encoders]))
        sends_layer = Layer(sends_controls=ButtonMatrixElement(rows=[bottom_encoders, top_encoders]))
        modes_layer = Layer(pan_volume_button=make_button(114, 'Pan_Volume_Mode_Button'), sends_button=make_button(115, 'Sends_Mode_Button'))
        self._mixer = SpecialMixerComponent(8, modes_layer, pan_volume_layer, sends_layer)
        self._mixer.set_enabled(False)
        self._mixer.name = 'Mixer'
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer_track_nav_layer = Layer(track_bank_left_button=make_button(116, 'Mixer_Track_Left_Button'), track_bank_right_button=make_button(117, 'Mixer_Track_Right_Button'))
        for index in xrange(8):
            strip = self._mixer.channel_strip(index)
            strip.name = 'Channel_Strip_' + str(index)
            strip.empty_color = Colors.LED_OFF
            strip.set_invert_mute_feedback(True)
            mute_button = make_button(pad_identifiers[index], 'Track_Mute_Button_' + str(index), is_pad=True)
            mute_button.set_on_off_values(Colors.AMBER_FULL, Colors.AMBER_THIRD)
            strip.set_mute_button(mute_button)

        self._on_selected_send_index.subject = self._mixer
        self._on_selected_mixer_mode.subject = self._mixer

    def _init_session(self):
        make_button = partial(make_launch_control_button, channel=9)
        make_encoder = partial(make_launch_control_encoder, channel=9)
        bottom_encoders, top_encoders = make_all_encoders('Session_Mixer', make_encoder)
        pan_volume_layer = Layer(volume_controls=ButtonMatrixElement(rows=[bottom_encoders]), pan_controls=ButtonMatrixElement(rows=[top_encoders]))
        self._session_mixer = SpecialMixerComponent(8, Layer(), pan_volume_layer, Layer())
        self._session_mixer.set_enabled(False)
        self._session_mixer.name = 'Session_Mixer'
        clip_launch_buttons = [ make_button(identifier, 'Clip_Launch_Button_' + str(i), is_pad=True) for i, identifier in enumerate(pad_identifiers) ]
        self._session = SpecialSessionComponent(num_tracks=8, num_scenes=0, name='Session')
        self._session.set_enabled(False)
        self._session.set_mixer(self._session_mixer)
        self._session_layer = Layer(track_bank_left_button=make_button(116, 'Track_Bank_Left_Button'), track_bank_right_button=make_button(117, 'Track_Bank_Right_Button'), select_prev_button=make_button(114, 'Scene_Bank_Up_Button'), select_next_button=make_button(115, 'Scene_Bank_Down_Button'), clip_launch_buttons=ButtonMatrixElement(rows=[clip_launch_buttons]))
        scene = self._session.selected_scene()
        for index in range(8):
            clip_slot = scene.clip_slot(index)
            clip_slot.set_triggered_to_play_value(Colors.GREEN_BLINK)
            clip_slot.set_triggered_to_record_value(Colors.RED_BLINK)
            clip_slot.set_stopped_value(Colors.AMBER_FULL)
            clip_slot.set_started_value(Colors.GREEN_FULL)
            clip_slot.set_recording_value(Colors.RED_FULL)
            clip_slot.name = 'Selected_Clip_Slot_' + str(index)

        self._on_track_offset.subject = self._session

    def _init_device(self):
        make_button = partial(make_launch_control_button, channel=10)
        make_encoder = partial(make_launch_control_encoder, channel=10)
        bottom_encoders, top_encoders = make_all_encoders('Device', make_encoder)
        parameter_controls = top_encoders[:4] + bottom_encoders[:4]
        bank_buttons = [ make_button(identifier, 'Device_Bank_Button_' + str(i), is_pad=True) for i, identifier in enumerate(pad_identifiers) ]
        for button in bank_buttons:
            button.set_on_off_values(Colors.LED_ON, Colors.LED_OFF)

        self._device_bank_registry = DeviceBankRegistry()
        self._device = DeviceComponent(device_bank_registry=self._device_bank_registry, name='Device')
        self._device.set_enabled(False)
        self._device.layer = Layer(parameter_controls=ButtonMatrixElement(rows=[parameter_controls]), bank_buttons=ButtonMatrixElement(rows=[bank_buttons]))
        self.set_device_component(self._device)
        self._device_navigation = DeviceNavigationComponent()
        self._device_navigation.set_enabled(False)
        self._device_navigation.name = 'Device_Navigation'
        self._device_navigation.layer = Layer(next_device_button=make_button(115, 'Next_Device_Button'), previous_device_button=make_button(114, 'Prev_Device_Button'))
        self._view_control = ViewControlComponent()
        self._view_control.set_enabled(False)
        self._view_control.name = 'View_Control'
        self._view_control.layer = Layer(next_track_button=make_button(117, 'Device_Next_Track_Button'), prev_track_button=make_button(116, 'Device_Prev_Track_Button'))

    def _init_modes(self):
        self._modes = ModesComponent(is_root=True)
        self._modes.add_mode('mixer', [partial(self._session.set_mixer, self._mixer),
         LayerMode(self._session, self._mixer_track_nav_layer),
         self._mixer,
         self._session,
         self._show_controlled_tracks_message])
        self._modes.add_mode('session', [partial(self._session.set_mixer, self._session_mixer),
         LayerMode(self._session, self._session_layer),
         self._session_mixer,
         self._session,
         self._show_controlled_tracks_message])
        self._modes.add_mode('device', [self._device, self._device_navigation, self._view_control])
        self._modes.add_mode('user', None)
        self._modes.selected_mode = 'mixer'
        self._modes.layer = Layer(mixer_button=ButtonSysexControl(Sysex.MIXER_MODE), session_button=ButtonSysexControl(Sysex.SESSION_MODE), device_button=ButtonSysexControl(Sysex.DEVICE_MODE))

    @subject_slot('offset')
    def _on_track_offset(self):
        self._show_controlled_tracks_message()

    @subject_slot('selected_send_index')
    def _on_selected_send_index(self, index):
        self._show_controlled_sends_message()

    @subject_slot('selected_mixer_mode')
    def _on_selected_mixer_mode(self, mode):
        if mode == 'sends':
            self._show_controlled_sends_message()
        else:
            self.show_message('Controlling Pan and Volume')

    def _show_controlled_tracks_message(self):
        start = self._session.track_offset() + 1
        end = min(start + 8, len(self._session.tracks_to_use()))
        if start < end:
            self.show_message('Controlling Track %d to %d' % (start, end))
        else:
            self.show_message('Controlling Track %d' % start)

    def _show_controlled_sends_message(self):
        send_index = self._mixer.selected_send_index
        send_name1 = chr(ord('A') + send_index)
        if send_index + 1 < self._mixer.num_sends:
            send_name2 = chr(ord('A') + send_index + 1)
            self.show_message('Controlling Send %s and %s' % (send_name1, send_name2))
        else:
            self.show_message('Controlling Send %s' % send_name1)

    def handle_sysex(self, midi_bytes):
        super(LaunchControl, self).handle_sysex(midi_bytes)
        if self._is_user_mode_message(midi_bytes):
            self._modes.selected_mode = 'user'
            self.request_rebuild_midi_map()

    def _is_user_mode_message(self, midi_bytes):
        """
        True if midi_byes refer to a mode change, but none of the three
        predefined Live modes
        """
        return midi_bytes[:7] == Sysex.MODE_CHANGE_PREFIX and midi_bytes not in SYSEX_MODE_MAP