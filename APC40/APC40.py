#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/APC40/APC40.py
from __future__ import with_statement
from functools import partial
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ComboElement import ComboElement
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from _Framework.ControlSurface import OptimizedControlSurface
from _Framework.Layer import Layer, SimpleLayerOwner
from _Framework.ModesComponent import ModesComponent
from _Framework.Resource import PrioritizedResource
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.Util import nop, recursive_map
from _APC.APC import APC
from _APC.ControlElementUtils import make_button, make_pedal_button, make_encoder, make_ring_encoder, make_slider
from _APC.DeviceBankButtonElement import DeviceBankButtonElement
from _APC.DeviceComponent import DeviceComponent
from _APC.MixerComponent import MixerComponent
from _APC.SkinDefault import make_default_skin, make_biled_skin
from _APC.DetailViewCntrlComponent import DetailViewCntrlComponent
from TransportComponent import TransportComponent
from SessionComponent import SessionComponent
SESSION_WIDTH = 8
SESSION_HEIGHT = 5
MIXER_SIZE = 8
FALLBACK_CONTROL_OWNER_PRIORITY = -1

class APC40(APC, OptimizedControlSurface):
    """ Script for Akai's APC40 Controller """

    def __init__(self, *a, **k):
        super(APC40, self).__init__(*a, **k)
        self._color_skin = make_biled_skin()
        self._default_skin = make_default_skin()
        with self.component_guard():
            self._create_controls()
            self._create_session()
            self._create_mixer()
            self._create_device()
            self._create_detail_view_control()
            self._create_transport()
            self._create_global_control()
            self._create_fallback_control_owner()
            self._session.set_mixer(self._mixer)
            self.set_highlighting_session_component(self._session)
            self.set_device_component(self._device)
            for component in self.components:
                component.set_enabled(False)

        self._device_selection_follows_track_selection = True

    def _with_shift(self, button):
        return ComboElement(button, modifiers=[self._shift_button])

    def _create_controls(self):
        make_on_off_button = partial(make_button, skin=self._default_skin)
        make_color_button = partial(make_button, skin=self._color_skin)
        self._shift_button = make_button(0, 98, resource_type=PrioritizedResource, name='Shift_Button')
        self._right_button = make_button(0, 96, name='Bank_Select_Right_Button')
        self._left_button = make_button(0, 97, name='Bank_Select_Left_Button')
        self._up_button = make_button(0, 94, name='Bank_Select_Up_Button')
        self._down_button = make_button(0, 95, name='Bank_Select_Down_Button')
        self._session_matrix = ButtonMatrixElement(name='Button_Matrix')
        self._scene_launch_buttons_raw = [ make_color_button(0, index + 82, name='Scene_%d_Launch_Button' % index) for index in xrange(SESSION_HEIGHT) ]
        self._track_stop_buttons = [ make_color_button(index, 52, name='Track_%d_Stop_Button' % index) for index in xrange(SESSION_WIDTH) ]
        self._stop_all_button = make_color_button(0, 81, name='Stop_All_Clips_Button')
        self._matrix_rows_raw = [ [ make_color_button(track_index, scene_index + 53, name='%d_Clip_%d_Button' % (track_index, scene_index)) for track_index in xrange(SESSION_WIDTH) ] for scene_index in xrange(SESSION_HEIGHT) ]
        for row in self._matrix_rows_raw:
            self._session_matrix.add_row(row)

        self._selected_slot_launch_button = make_pedal_button(67, name='Selected_Slot_Launch_Button')
        self._selected_scene_launch_button = make_pedal_button(64, name='Selected_Scene_Launch_Button')
        self._volume_controls = []
        self._arm_buttons = []
        self._solo_buttons = []
        self._mute_buttons = []
        self._select_buttons = []
        for index in xrange(MIXER_SIZE):
            self._volume_controls.append(make_slider(index, 7, name='%d_Volume_Control' % index))
            self._arm_buttons.append(make_on_off_button(index, 48, name='%d_Arm_Button' % index))
            self._solo_buttons.append(make_on_off_button(index, 49, name='%d_Solo_Button' % index))
            self._mute_buttons.append(make_on_off_button(index, 50, name='%d_Mute_Button' % index))
            self._select_buttons.append(make_on_off_button(index, 51, name='%d_Select_Button' % index))

        self._crossfader_control = make_slider(0, 15, name='Crossfader')
        self._master_volume_control = make_slider(0, 14, name='Master_Volume_Control')
        self._master_select_button = make_on_off_button(0, 80, name='Master_Select_Button')
        self._prehear_control = make_encoder(0, 47, name='Prehear_Volume_Control')
        self._device_bank_buttons = []
        self._device_param_controls_raw = []
        bank_button_labels = ('Clip_Track_Button', 'Device_On_Off_Button', 'Previous_Device_Button', 'Next_Device_Button', 'Detail_View_Button', 'Rec_Quantization_Button', 'Midi_Overdub_Button', 'Metronome_Button')
        for index in range(8):
            self._device_bank_buttons.append(make_on_off_button(0, 58 + index, name=bank_button_labels[index]))
            encoder_name = 'Device_Control_%d' % index
            ringed_encoder = make_ring_encoder(16 + index, 24 + index, name=encoder_name)
            self._device_param_controls_raw.append(ringed_encoder)

        self._play_button = make_button(0, 91, name='Play_Button')
        self._stop_button = make_button(0, 92, name='Stop_Button')
        self._record_button = make_button(0, 93, name='Record_Button')
        self._nudge_up_button = make_button(0, 100, name='Nudge_Up_Button')
        self._nudge_down_button = make_button(0, 101, name='Nudge_Down_Button')
        self._tap_tempo_button = make_button(0, 99, name='Tap_Tempo_Button')
        self._global_bank_buttons = []
        self._global_param_controls = []
        for index in range(8):
            encoder_name = 'Track_Control_%d' % index
            ringed_encoder = make_ring_encoder(48 + index, 56 + index, name=encoder_name)
            self._global_param_controls.append(ringed_encoder)

        self._global_bank_buttons = [ make_on_off_button(0, 87 + index, name=name) for index, name in enumerate(('Pan_Button', 'Send_A_Button', 'Send_B_Button', 'Send_C_Button')) ]
        self._device_clip_toggle_button = self._device_bank_buttons[0]
        self._device_on_off_button = self._device_bank_buttons[1]
        self._detail_left_button = self._device_bank_buttons[2]
        self._detail_right_button = self._device_bank_buttons[3]
        self._detail_toggle_button = self._device_bank_buttons[4]
        self._rec_quantization_button = self._device_bank_buttons[5]
        self._overdub_button = self._device_bank_buttons[6]
        self._metronome_button = self._device_bank_buttons[7]

        def wrap_matrix(control_list, wrapper = nop):
            return ButtonMatrixElement(rows=[map(wrapper, control_list)])

        self._scene_launch_buttons = wrap_matrix(self._scene_launch_buttons_raw)
        self._track_stop_buttons = wrap_matrix(self._track_stop_buttons)
        self._volume_controls = wrap_matrix(self._volume_controls)
        self._arm_buttons = wrap_matrix(self._arm_buttons)
        self._solo_buttons = wrap_matrix(self._solo_buttons)
        self._mute_buttons = wrap_matrix(self._mute_buttons)
        self._select_buttons = wrap_matrix(self._select_buttons)
        self._device_param_controls = wrap_matrix(self._device_param_controls_raw)
        self._device_bank_buttons = wrap_matrix(self._device_bank_buttons, partial(DeviceBankButtonElement, modifiers=[self._shift_button]))
        self._shifted_matrix = ButtonMatrixElement(rows=recursive_map(self._with_shift, self._matrix_rows_raw))
        self._shifted_scene_buttons = ButtonMatrixElement(rows=[[ self._with_shift(button) for button in self._scene_launch_buttons_raw ]])

    def _create_session(self):
        self._session = SessionComponent(SESSION_WIDTH, SESSION_HEIGHT, auto_name=True, enable_skinning=True, is_enabled=False, layer=Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button, scene_bank_up_button=self._up_button, scene_bank_down_button=self._down_button, stop_all_clips_button=self._stop_all_button, stop_track_clip_buttons=self._track_stop_buttons, scene_launch_buttons=self._scene_launch_buttons, clip_launch_buttons=self._session_matrix, slot_launch_button=self._selected_slot_launch_button, selected_scene_launch_button=self._selected_scene_launch_button))
        self._session_zoom = SessionZoomingComponent(self._session, name='Session_Overview', enable_skinning=True, is_enabled=False, layer=Layer(button_matrix=self._shifted_matrix, nav_up_button=self._with_shift(self._up_button), nav_down_button=self._with_shift(self._down_button), nav_left_button=self._with_shift(self._left_button), nav_right_button=self._with_shift(self._right_button), scene_bank_buttons=self._shifted_scene_buttons))

    def _create_mixer(self):
        self._mixer = MixerComponent(MIXER_SIZE, auto_name=True, is_enabled=False, invert_mute_feedback=True, layer=Layer(volume_controls=self._volume_controls, arm_buttons=self._arm_buttons, solo_buttons=self._solo_buttons, mute_buttons=self._mute_buttons, track_select_buttons=self._select_buttons, shift_button=self._shift_button, crossfader_control=self._crossfader_control, prehear_volume_control=self._prehear_control))
        self._mixer.master_strip().layer = Layer(volume_control=self._master_volume_control, select_button=self._master_select_button)

    def _create_device(self):
        self._device = DeviceComponent(name='Device_Component', is_enabled=False, layer=Layer(bank_buttons=self._device_bank_buttons, on_off_button=self._device_on_off_button), use_fake_banks=True)
        ChannelTranslationSelector(8, name='Control_Translations')
        self._device.set_parameter_controls(tuple(self._device_param_controls_raw))

    def _create_detail_view_control(self):
        self._detail_view_toggler = DetailViewCntrlComponent(name='Detail_View_Control', is_enabled=False, layer=Layer(device_clip_toggle_button=self._device_clip_toggle_button, detail_toggle_button=self._detail_toggle_button, device_nav_left_button=self._detail_left_button, device_nav_right_button=self._detail_right_button))

    def _create_transport(self):
        self._transport = TransportComponent(name='Transport', is_enabled=False, layer=Layer(play_button=self._play_button, stop_button=self._stop_button, record_button=self._record_button, nudge_up_button=self._nudge_up_button, nudge_down_button=self._nudge_down_button, tap_tempo_button=self._tap_tempo_button, quant_toggle_button=self._rec_quantization_button, overdub_button=self._overdub_button, metronome_button=self._metronome_button))
        self._bank_button_translator = ChannelTranslationSelector(name='Bank_Button_Translations', is_enabled=False)

    def _create_global_control(self):

        def set_pan_controls():
            for index, control in enumerate(self._global_param_controls):
                self._mixer.channel_strip(index).set_pan_control(control)
                self._mixer.channel_strip(index).set_send_controls((None, None, None))
                control.set_channel(0)

        def set_send_controls(send_index):
            for index, control in enumerate(self._global_param_controls):
                self._mixer.channel_strip(index).set_pan_control(None)
                send_controls = [None] * 3
                send_controls[send_index] = control
                self._mixer.channel_strip(index).set_send_controls(send_controls)
                control.set_channel(send_index + 1)

        encoder_modes = ModesComponent(name='Track_Control_Modes', is_enabled=False)
        encoder_modes.add_mode('pan', [set_pan_controls])
        encoder_modes.add_mode('send_a', [partial(set_send_controls, 0)])
        encoder_modes.add_mode('send_b', [partial(set_send_controls, 1)])
        encoder_modes.add_mode('send_c', [partial(set_send_controls, 2)])
        encoder_modes.selected_mode = 'pan'
        encoder_modes.layer = Layer(pan_button=self._global_bank_buttons[0], send_a_button=self._global_bank_buttons[1], send_b_button=self._global_bank_buttons[2], send_c_button=self._global_bank_buttons[3])
        self._translation_selector = ChannelTranslationSelector(name='Global_Translations')

    def _create_fallback_control_owner(self):
        self.register_disconnectable(SimpleLayerOwner(layer=Layer(_matrix=self._session_matrix, priority=FALLBACK_CONTROL_OWNER_PRIORITY)))

    def get_matrix_button(self, column, row):
        return self._matrix_rows_raw[row][column]

    def _product_model_id_byte(self):
        return 115