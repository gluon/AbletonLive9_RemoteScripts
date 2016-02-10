#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchkey_MK2/Launchkey_MK2.py
from __future__ import with_statement
from functools import partial
from _Framework import Task
from _Framework.Util import const, nop, mixin
from _Framework.Dependency import inject
from _Framework.SubjectSlot import subject_slot
from _Framework.ControlSurface import OptimizedControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.Layer import Layer
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ModesComponent import ModesComponent, LayerMode, AddLayerMode, ImmediateBehaviour, CancellableBehaviour
from _Framework.BackgroundComponent import BackgroundComponent
from _Framework.TransportComponent import TransportComponent
from Launchkey.SessionNavigationComponent import SessionNavigationComponent
from .Skin import make_skin
from .Colors import RGB_COLOR_TABLE, CLIP_COLOR_TABLE
from .ControlElementUtils import make_button, make_encoder, make_slider
from .ModeUtils import MomentaryBehaviour, SkinableBehaviourMixin, DisablingModesComponent
from .SessionComponent import SessionComponent
from .DeviceComponent import DeviceComponent
from .MixerComponent import MixerComponent
from .InControlStatusComponent import InControlStatusComponent
import consts

class Launchkey_MK2(OptimizedControlSurface):
    identity_request_delay = 0.5

    def __init__(self, c_instance, *a, **k):
        super(Launchkey_MK2, self).__init__(c_instance=c_instance, *a, **k)
        self._is_25_key_model = False
        self._is_in_control_on = True
        with self.component_guard():
            self._skin = make_skin()
            with inject(skin=const(self._skin)).everywhere():
                self._create_controls()
        self._request_task = self._tasks.add(Task.sequence(Task.wait(self.identity_request_delay), Task.run(self._send_identity_request)))
        self._request_task.kill()

    def _create_controls(self):
        self._encoders = ButtonMatrixElement(rows=[[ make_encoder(identifier, name='Encoder_%d' % (index,)) for index, identifier in enumerate(xrange(21, 29)) ]])
        self._top_pad_row = ButtonMatrixElement(rows=[[ make_button(identifier, name='Pad_0_%d' % (index,)) for index, identifier in enumerate(xrange(96, 104)) ]])
        self._bottom_pad_row_raw = [ make_button(identifier, name='Pad_1_%d' % (index,)) for index, identifier in enumerate(xrange(112, 120)) ]
        self._bottom_pad_row = ButtonMatrixElement(rows=[self._bottom_pad_row_raw])
        self._top_launch_button = make_button(104, name='Scene_Launch_Button')
        self._bottom_launch_button = make_button(120, name='Stop_All_Clips_Button')
        self._scene_up_button = make_button(112, MIDI_CC_TYPE, name='Scene_Up_Button')
        self._scene_down_button = make_button(113, MIDI_CC_TYPE, name='Scene_Down_Button')
        self._stop_button = make_button(114, MIDI_CC_TYPE, name='Stop_Button')
        self._play_button = make_button(115, MIDI_CC_TYPE, name='Play_Button')
        self._loop_button = make_button(116, MIDI_CC_TYPE, name='Loop_Button')
        self._record_button = make_button(117, MIDI_CC_TYPE, name='Record_Button')
        self._sliders = ButtonMatrixElement(rows=[[ make_slider(identifier, name='Slider_%d' % (index,)) for index, identifier in enumerate(xrange(41, 49)) ]])
        self._master_slider = make_slider(7, name='Master_Slider')
        self._25_key_slider = make_slider(7, name='Slider', channel=0)
        self._mute_buttons_raw = [ make_button(identifier, MIDI_CC_TYPE, name='Mute_Button_%d' % (index,)) for index, identifier in enumerate(xrange(51, 59)) ]
        self._mute_buttons = ButtonMatrixElement(rows=[self._mute_buttons_raw])
        self._master_button = make_button(59, MIDI_CC_TYPE, name='Master_Button')
        self._track_left_button = make_button(102, MIDI_CC_TYPE, name='Track_Left_Button')
        self._track_right_button = make_button(103, MIDI_CC_TYPE, name='Track_Right_Button')
        self._device_mode_button = self._bottom_pad_row_raw[0]
        self._pan_mode_button = self._bottom_pad_row_raw[1]
        self._send_mode_buttons = dict()
        for index in xrange(consts.MAX_SENDS):
            setattr(self, '_send_%d_button' % (index,), self._bottom_pad_row_raw[index + 2])
            self._send_mode_buttons['send_%d_mode_button' % (index,)] = getattr(self, '_send_%d_button' % (index,))

        self._extended_mode_button = make_button(12, name='Dummy_Extended_Mode_Button')
        self._extended_mode_button.add_value_listener(nop)
        self._encoder_incontrol_button = make_button(13, is_momentary=False, name='Encoder_InControl_Button')
        self._encoder_incontrol_button.add_value_listener(nop)
        self._slider_incontrol_button = make_button(14, is_momentary=False, name='Fader_InControl_Button')
        self._slider_incontrol_button.add_value_listener(nop)
        self._pad_incontrol_button = make_button(15, is_momentary=False, name='Pad_InControl_Button')
        self._pad_incontrol_button.add_value_listener(self._update_pads)
        self._encoder_incontrol_button2 = make_button(16, name='Encoder_InControl_Button')
        self._pad_in_control_status_button = make_button(11, name='Dummy_InControl_Button')

    def _create_session(self):
        self._session = SessionComponent(name='Session', is_enabled=False, num_tracks=self._top_pad_row.width(), num_scenes=self._top_pad_row.height(), enable_skinning=True, layer=Layer(clip_launch_buttons=self._top_pad_row, scene_launch_buttons=ButtonMatrixElement(rows=[[self._top_launch_button]]), stop_track_clip_buttons=self._bottom_pad_row, stop_all_clips_button=self._bottom_launch_button))
        self._session.set_rgb_mode(CLIP_COLOR_TABLE, RGB_COLOR_TABLE)
        self._session.set_mixer(self._mixer)
        self._session.set_enabled(True)

    def _setup_navigation(self):
        self._session_navigation = SessionNavigationComponent(is_enabled=False, name='Session_Navigation', layer=Layer(next_track_button=self._track_right_button, prev_track_button=self._track_left_button, next_scene_button=self._scene_down_button, prev_scene_button=self._scene_up_button))
        self._session_navigation.set_enabled(True)

    def _create_transport(self):
        self._transport = TransportComponent(is_enabled=False, name='Transport', layer=Layer(play_button=self._play_button, stop_button=self._stop_button, loop_button=self._loop_button, record_button=self._record_button))
        self._transport.set_enabled(True)

    def _create_mixer(self):
        mixer_volume_layer = None
        if self._is_25_key_model:
            mixer_volume_layer = Layer(volume_control=self._25_key_slider)
        else:
            mixer_volume_layer = Layer(volume_controls=self._sliders)
        self._mixer = MixerComponent(is_enabled=False, name='Mixer', num_tracks=self._sliders.width(), layer=mixer_volume_layer)
        if not self._is_25_key_model:
            self._mixer.master_strip().layer = Layer(volume_control=self._master_slider)
        self._mixer.set_enabled(True)
        self._mute_button_modes = ModesComponent()
        mute_mode = AddLayerMode(self._mixer, Layer(mute_buttons=self._mute_buttons))
        solo_mode = AddLayerMode(self._mixer, Layer(solo_buttons=self._mute_buttons))
        self._mute_button_modes.add_mode('mute_mode', mute_mode)
        self._mute_button_modes.add_mode('solo_mode', solo_mode, behaviour=CancellableBehaviour())
        self._mute_button_modes.layer = Layer(solo_mode_button=self._master_button)
        self._mute_button_modes.selected_mode = 'mute_mode'
        self._mute_button_modes.set_enabled(True)

    def _create_device(self):
        self._device = DeviceComponent(name='Device', is_enabled=False)
        self.set_device_component(self._device)
        self._device_selection_follows_track_selection = True
        self._device.set_enabled(True)

    def _create_background(self):
        self._background = BackgroundComponent(name='BackgroundComponent')

    def _create_encoder_modes(self):
        self._encoder_modes = DisablingModesComponent()
        self._encoder_modes.default_behaviour = mixin(SkinableBehaviourMixin, ImmediateBehaviour)()
        device_mode = LayerMode(self._device, Layer(parameter_controls=self._encoders, bank_buttons=self._top_pad_row))
        pan_mode = AddLayerMode(self._mixer, Layer(pan_controls=self._encoders))
        sends_mode = AddLayerMode(self._mixer, Layer(send_controls=self._encoders))
        background_mode = LayerMode(self._background, Layer(bank_buttons=self._top_pad_row))
        self._encoder_modes.add_mode('device_mode', device_mode, is_enabled=True)
        self._encoder_modes.add_mode('pan_mode', [pan_mode, background_mode], is_enabled=True)
        for index in xrange(6):
            self._encoder_modes.add_mode('send_%d_mode' % (index,), [sends_mode, partial(self._set_send_index, index), background_mode], is_enabled=False)

        self._encoder_modes.selected_mode = 'device_mode'
        self._encoder_modes.set_enabled(True)

    def _create_mode_selector(self):
        self._mode_selector = ModesComponent()
        mode_selection = LayerMode(self._encoder_modes, Layer(device_mode_button=self._device_mode_button, pan_mode_button=self._pan_mode_button, **self._send_mode_buttons))
        device_navigation = AddLayerMode(self._device, Layer(device_nav_left_button=self._track_left_button, device_nav_right_button=self._track_right_button))
        self._mode_selector.add_mode('mode_selection', [partial(self._toggle_in_control, True), mode_selection, device_navigation], behaviour=MomentaryBehaviour())
        session_control = AddLayerMode(self._session, Layer(clip_launch_buttons=self._top_pad_row))
        self._mode_selector.add_mode('session_mode', [partial(self._toggle_in_control, False), session_control])
        self._mode_selector.layer = Layer(mode_selection_button=self._encoder_incontrol_button2)

    def _create_in_control_status_listener(self):
        self._in_control_status = InControlStatusComponent(set_is_in_control_on=self._set_is_in_control_on, is_enabled=False, layer=Layer(in_control_status_button=self._pad_in_control_status_button))
        self._in_control_status.set_enabled(True)

    @subject_slot('value')
    def _update_pads(self, value):
        if value:
            self.update()

    @subject_slot('return_tracks')
    def _on_return_tracks_changed(self):
        num_sends = self._mixer.num_sends
        for index in xrange(6):
            self._encoder_modes.set_mode_enabled('send_%d_mode' % (index,), True if index < num_sends else False)

    def _set_send_index(self, index):
        self._mixer.send_index = index

    def _set_is_in_control_on(self, value):
        self._is_in_control_on = value

    def _toggle_in_control(self, value):
        if not self._is_in_control_on:
            self._send_midi(consts.DRUM_IN_CONTROL_ON_MESSAGE if value else consts.DRUM_IN_CONTROL_OFF_MESSAGE)

    def port_settings_changed(self):
        self._disconnect_and_unregister_all_components()
        self._request_task.restart()

    def handle_sysex(self, midi_bytes):
        if self._is_identity_response(midi_bytes):
            product_id_bytes = self._extract_product_id_bytes(midi_bytes)
            if self._is_identity_response_valid(product_id_bytes):
                self._set_model_type(product_id_bytes)
                self._request_task.kill()
                self.on_identified()
            else:
                self.log_message('MIDI device responded with wrong product id (%s).' % (str(product_id_bytes),))
        else:
            super(Launchkey_MK2, self).handle_sysex(midi_bytes)

    def _extract_product_id_bytes(self, midi_bytes):
        return midi_bytes[5:]

    def _is_identity_response(self, midi_bytes):
        return midi_bytes[3:5] == (6, 2)

    def _is_identity_response_valid(self, product_id_bytes):
        return product_id_bytes[:3] == consts.PRODUCT_ID_BYTE_PREFIX and product_id_bytes[3] in consts.PRODUCT_ID_BYTES

    def _set_model_type(self, product_id_bytes):
        self._is_25_key_model = product_id_bytes[3] == consts.LAUNCHKEY_25_ID_BYTE

    def _send_identity_request(self):
        self._send_midi(consts.IDENTITY_REQUEST)

    def on_identified(self):
        self._extended_mode_button.turn_on()
        with self.component_guard():
            self._create_mixer()
            self._create_session()
            self._setup_navigation()
            self._create_transport()
            self._create_device()
            self._create_background()
            self._create_encoder_modes()
            self._create_mode_selector()
            self._create_in_control_status_listener()
            self._on_return_tracks_changed.subject = self.song()
            self._on_return_tracks_changed()
        self._mode_selector.selected_mode = 'session_mode'
        self.update()

    def disconnect(self):
        self._extended_mode_button.turn_off()
        super(Launchkey_MK2, self).disconnect()