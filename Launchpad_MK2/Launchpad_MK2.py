#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_MK2/Launchpad_MK2.py
from __future__ import with_statement
from functools import partial
import Live
from _Framework.Util import const, mixin, recursive_map
from _Framework.Dependency import inject
from _Framework.Layer import Layer
from _Framework.ControlSurface import OptimizedControlSurface
from _Framework.IdentifiableControlSurface import IdentifiableControlSurface
from _Framework.ModesComponent import ImmediateBehaviour, LayerMode, AddLayerMode
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from .Skin import make_default_skin
from .Colors import CLIP_COLOR_TABLE, RGB_COLOR_TABLE
from .ModeUtils import NotifyingModesComponent, SkinableBehaviourMixin, EnablingReenterBehaviour
from .ControlElementUtils import make_button, with_modifier, FilteringMultiElement
from .SliderElement import SliderElement
from .BackgroundComponent import TranslatingBackgroundComponent
from .SessionComponent import SessionComponent
from .SessionZoomingComponent import SessionZoomingComponent
from .MixerComponent import MixerComponent
import consts

class Launchpad_MK2(IdentifiableControlSurface, OptimizedControlSurface):

    def __init__(self, c_instance, *a, **k):
        super(Launchpad_MK2, self).__init__(product_id_bytes=consts.PRODUCT_ID_BYTES, c_instance=c_instance, *a, **k)
        self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
        with self.component_guard():
            self._skin = make_default_skin()
            with inject(skin=const(self._skin)).everywhere():
                self._create_controls()
            self._create_session()
            self._create_mixer()
            self._last_sent_layout_byte = None
            with inject(switch_layout=const(self._switch_layout)).everywhere():
                self._create_modes()

    def _create_controls(self):
        multi_button_channels = consts.USER_MODE_CHANNELS
        self._session_button_single = make_button(108, 0, 'Session_Mode_Button', msg_type=MIDI_CC_TYPE, is_modifier=True)
        self._session_button = FilteringMultiElement([self._session_button_single] + [ make_button(108, channel, msg_type=MIDI_CC_TYPE, name='Session_Mode_Button_ch_%d' % (channel,)) for channel in multi_button_channels ], feedback_channels=[0])
        self._user_1_button = FilteringMultiElement([ make_button(109, channel, msg_type=MIDI_CC_TYPE, name='User_1_Mode_Button_ch_%d' % (channel,)) for channel in (0,) + multi_button_channels ], feedback_channels=[0,
         5,
         6,
         7])
        self._user_2_button = FilteringMultiElement([ make_button(110, channel, msg_type=MIDI_CC_TYPE, name='User_2_Mode_Button_ch_%d' % (channel,)) for channel in (0,) + multi_button_channels ], feedback_channels=[0,
         13,
         14,
         15])
        self._mixer_button = FilteringMultiElement([ make_button(111, channel, msg_type=MIDI_CC_TYPE, name='Mixer_Mode_Button_ch_%d' % (channel,)) for channel in (0,) + multi_button_channels ], feedback_channels=[0])
        self._up_button = make_button(104, 0, msg_type=MIDI_CC_TYPE, name='Up_Button')
        self._down_button = make_button(105, 0, msg_type=MIDI_CC_TYPE, name='Down_Button')
        self._left_button = make_button(106, 0, msg_type=MIDI_CC_TYPE, name='Left_Button')
        self._right_button = make_button(107, 0, msg_type=MIDI_CC_TYPE, name='Right_Button')
        self._session_matrix_raw = [ [ make_button(col + offset, 0, name='Session_Matrix_Button_%d_%d' % (col, row)) for col in xrange(consts.SESSION_WIDTH) ] for row, offset in enumerate(xrange(81, 10, -10)) ]
        self._session_matrix = ButtonMatrixElement(rows=self._session_matrix_raw, name='Session_Matrix')
        self._scene_launch_matrix_raw = [ make_button(identifier, 0, name='Scene_Launch_Button_%d' % (index,)) for index, identifier in enumerate(xrange(89, 18, -10)) ]
        self._scene_launch_matrix = ButtonMatrixElement(rows=[self._scene_launch_matrix_raw], name='Scene_Launch_Buttons')
        self._session_zoom_matrix = ButtonMatrixElement(rows=recursive_map(partial(with_modifier, self._session_button_single), self._session_matrix_raw))
        self._volume_reset_buttons = self._session_matrix.submatrix[:, :1]
        self._pan_reset_buttons = self._session_matrix.submatrix[:, 1:2]
        self._send_a_reset_buttons = self._session_matrix.submatrix[:, 2:3]
        self._send_b_reset_buttons = self._session_matrix.submatrix[:, 3:4]
        self._stop_clip_buttons = self._session_matrix.submatrix[:, 4:5]
        self._mute_buttons = self._session_matrix.submatrix[:, 5:6]
        self._solo_buttons = self._session_matrix.submatrix[:, 6:7]
        self._arm_buttons = self._session_matrix.submatrix[:, 7:]
        self._volume_button = self._scene_launch_matrix_raw[0]
        self._pan_button = self._scene_launch_matrix_raw[1]
        self._send_a_button = self._scene_launch_matrix_raw[2]
        self._send_b_button = self._scene_launch_matrix_raw[3]
        self._stop_button = self._scene_launch_matrix_raw[4]
        self._mute_button = self._scene_launch_matrix_raw[5]
        self._solo_button = self._scene_launch_matrix_raw[6]
        self._record_arm_button = self._scene_launch_matrix_raw[7]
        self._sliders = ButtonMatrixElement(rows=[[ SliderElement(MIDI_CC_TYPE, 0, identifier) for identifier in xrange(21, 29) ]])

    def _create_session(self):
        self._session = SessionComponent(is_enabled=False, num_tracks=self._session_matrix.width(), num_scenes=self._session_matrix.height(), enable_skinning=True, name='Session', is_root=True, layer=Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button, scene_bank_up_button=self._up_button, scene_bank_down_button=self._down_button))
        self._session.set_rgb_mode(CLIP_COLOR_TABLE, RGB_COLOR_TABLE)
        self._session_layer_mode = AddLayerMode(self._session, Layer(clip_launch_buttons=self._session_matrix, scene_launch_buttons=self._scene_launch_matrix))
        self._session_zoom = SessionZoomingComponent(self._session, is_enabled=False, enable_skinning=True, layer=Layer(nav_up_button=with_modifier(self._session_button_single, self._up_button), nav_down_button=with_modifier(self._session_button_single, self._down_button), nav_left_button=with_modifier(self._session_button_single, self._left_button), nav_right_button=with_modifier(self._session_button_single, self._right_button), button_matrix=self._session_zoom_matrix))
        self._stop_clip_layer_mode = AddLayerMode(self._session, Layer(stop_track_clip_buttons=self._stop_clip_buttons, stop_all_clips_button=self._stop_button))

    def _create_mixer(self):
        self._mixer = MixerComponent(is_enabled=False, num_tracks=consts.SESSION_WIDTH, invert_mute_feedback=True, enable_skinning=True, name='Mixer', is_root=True)
        self._session.set_mixer(self._mixer)
        self._mixer_home_page_layer = LayerMode(self._mixer, Layer(volume_reset_buttons=self._volume_reset_buttons, pan_reset_buttons=self._pan_reset_buttons, send_a_reset_buttons=self._send_a_reset_buttons, send_b_reset_buttons=self._send_b_reset_buttons, mute_buttons=self._mute_buttons, solo_buttons=self._solo_buttons, arm_buttons=self._arm_buttons, unmute_all_button=self._mute_button, unsolo_all_button=self._solo_button, unarm_all_button=self._record_arm_button))
        self._mixer_volume_layer = LayerMode(self._mixer, Layer(volume_controls=self._sliders))
        self._mixer_pan_layer = LayerMode(self._mixer, Layer(pan_controls=self._sliders))
        self._mixer_sends_layer = LayerMode(self._mixer, Layer(send_controls=self._sliders))

    def _create_translating_mixer_background(self, translation_channel):
        return TranslatingBackgroundComponent(translation_channel=translation_channel, is_enabled=False, name='Background', layer=Layer(stop_button=self._stop_button, mute_buttons=self._mute_button, solo_button=self._solo_button, record_arm_button=self._record_arm_button))

    def _create_modes(self):
        self._modes = NotifyingModesComponent(is_root=True)
        self._modes.default_behaviour = mixin(SkinableBehaviourMixin, ImmediateBehaviour)()
        self._modes.add_mode('session_mode', [self._session, self._session_layer_mode], layout_byte=0, behaviour=EnablingReenterBehaviour(self._session_zoom))
        self._modes.add_mode('user_1_mode', [], layout_byte=1)
        self._modes.add_mode('user_2_mode', [], layout_byte=2)
        self._modes.add_mode('volume_mode', [self._session, self._create_translating_mixer_background(consts.VOLUME_MODE_CHANNEL), self._mixer_volume_layer], layout_byte=4, groups=set('mixer'))
        self._modes.add_mode('pan_mode', [self._session, self._create_translating_mixer_background(consts.PAN_MODE_CHANNEL), self._mixer_pan_layer], layout_byte=5, groups=set('mixer'))
        self._modes.add_mode('send_a_mode', [self._session,
         self._create_translating_mixer_background(consts.SEND_A_MODE_CHANNEL),
         partial(self._set_send_index, 0),
         self._mixer_sends_layer], layout_byte=6, groups=set('mixer'))
        self._modes.add_mode('send_b_mode', [self._session,
         self._create_translating_mixer_background(consts.SEND_B_MODE_CHANNEL),
         partial(self._set_send_index, 1),
         self._mixer_sends_layer], layout_byte=7, groups=set('mixer'))
        self._modes.add_mode('mixer_mode', [self._session, self._stop_clip_layer_mode, self._mixer_home_page_layer], layout_byte=3, groups=set('mixer'))
        self._modes.layer = Layer(session_mode_button=self._session_button, user_1_mode_button=self._user_1_button, user_2_mode_button=self._user_2_button, mixer_mode_button=self._mixer_button, volume_mode_button=self._volume_button, pan_mode_button=self._pan_button, send_a_mode_button=self._send_a_button, send_b_mode_button=self._send_b_button)
        self._modes.selected_mode = 'session_mode'

    def _set_send_index(self, index):
        self._mixer.send_index = index

    def _switch_layout(self, layout_byte):
        if layout_byte != self._last_sent_layout_byte:
            prefix = consts.STANDARD_SYSEX_PREFIX + consts.LAYOUT_CHANGE_BYTE
            self._send_midi(prefix + (layout_byte, 247))
            self._clear_send_cache()
            self._last_sent_layout_byte = layout_byte

    def _clear_send_cache(self):
        with self.component_guard():
            for control in self.controls:
                control.clear_send_cache()

    def _send_identity_request(self):
        self._send_midi(consts.IDENTITY_REQUEST)

    def on_identified(self):
        self._send_challenge()

    def _send_challenge(self):
        challenge_bytes = tuple([ self._challenge >> 8 * index & 127 for index in xrange(4) ])
        self._send_midi(consts.STANDARD_SYSEX_PREFIX + consts.CHALLENGE_RESPONSE_BYTE + challenge_bytes + (247,))

    def handle_sysex(self, midi_bytes):
        if self._is_challenge_response(midi_bytes) and self._is_response_valid(midi_bytes):
            self._on_handshake_successful()
        else:
            super(Launchpad_MK2, self).handle_sysex(midi_bytes)

    def _is_challenge_response(self, midi_bytes):
        return len(midi_bytes) == 10 and midi_bytes[:7] == consts.STANDARD_SYSEX_PREFIX + consts.CHALLENGE_RESPONSE_BYTE

    def _is_response_valid(self, midi_bytes):
        response = long(midi_bytes[7])
        response += long(midi_bytes[8] << 8)
        return response == Live.Application.encrypt_challenge2(self._challenge)

    def _on_handshake_successful(self):
        self._modes.set_enabled(True)
        self._mixer.set_enabled(True)
        self._last_sent_layout_byte = None
        self._modes.send_switch_layout_message()
        self.set_highlighting_session_component(self._session)
        self.update()

    def disconnect(self):
        self._send_midi(consts.QUIT_MESSAGE)
        super(Launchpad_MK2, self).disconnect()