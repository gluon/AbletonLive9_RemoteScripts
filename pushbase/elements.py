#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/elements.py
from __future__ import absolute_import, print_function
from ableton.v2.base import depends, recursive_map
from ableton.v2.control_surface import PrioritizedResource, MIDI_NOTE_TYPE
from ableton.v2.control_surface.elements import ButtonMatrixElement, DoublePressElement, FineGrainWithModifierEncoderElement, MultiElement
from . import consts
from .configurable_button_element import PadButtonElement
from .control_element_factory import create_button, create_modifier_button, create_note_button
from .playhead_element import PlayheadElement
from .touch_encoder_element import TouchEncoderElement

class Elements(object):

    def __init__(self, deleter = None, undo_handler = None, pad_sensitivity_update = None, playhead = None, continuous_mapping_sensitivity = consts.CONTINUOUS_MAPPING_SENSITIVITY, fine_grained_continuous_mapping_sensitivity = consts.FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY, *a, **k):
        raise deleter is not None or AssertionError
        raise undo_handler is not None or AssertionError
        raise playhead is not None or AssertionError
        super(Elements, self).__init__(*a, **k)
        self.foot_pedal_button = DoublePressElement(create_button(69, 'Foot_Pedal', is_rgb=True))
        self.nav_up_button = create_button(46, 'Up_Arrow')
        self.nav_down_button = create_button(47, 'Down_Arrow')
        self.nav_left_button = create_button(44, 'Left_Arrow')
        self.nav_right_button = create_button(45, 'Right_Arrow')
        self.shift_button = create_modifier_button(49, 'Shift_Button')
        self.select_button = create_modifier_button(48, 'Select_Button')
        self.delete_button = create_modifier_button(118, 'Delete_Button', undo_step_handler=undo_handler)
        self.duplicate_button = create_modifier_button(88, 'Duplicate_Button', undo_step_handler=undo_handler)
        self.quantize_button = create_modifier_button(116, 'Quantization_Button', undo_step_handler=undo_handler)
        self.accent_button = create_modifier_button(57, 'Accent_Button')
        self.in_button = create_button(62, 'In_Button')
        self.out_button = create_button(63, 'Out_Button')
        self.master_select_button = create_button(28, 'Master_Select_Button')
        self.octave_down_button = create_button(54, 'Octave_Down_Button')
        self.octave_up_button = create_button(55, 'Octave_Up_Button')
        self.repeat_button = create_button(56, 'Repeat_Button')
        self.global_mute_button = create_modifier_button(60, 'Global_Mute_Button')
        self.global_solo_button = create_modifier_button(61, 'Global_Solo_Button')
        self.global_track_stop_button = create_modifier_button(29, 'Track_Stop_Button')
        self.scale_presets_button = create_button(58, 'Scale_Presets_Button')
        self.vol_mix_mode_button = create_button(114, 'Vol_Mix_Mode_Button')
        self.device_mode_button = create_button(110, 'Device_Mode_Button')
        self.clip_mode_button = create_button(113, 'Clip_Mode_Button')
        self.browse_mode_button = create_button(111, 'Browse_Mode_Button')
        self.single_track_mix_mode_button = create_button(112, 'Single_Track_Mode_Button')
        self.pan_send_mix_mode_button = create_button(115, 'Pan_Send_Mode_Button', resource_type=PrioritizedResource)
        self.note_mode_button = create_button(50, 'Note_Mode_Button')
        self.session_mode_button = create_button(51, 'Session_Mode_Button')
        self.play_button = create_button(85, 'Play_Button')
        self.new_button = create_button(87, 'New_Button')
        self.automation_button = create_button(89, 'Automation_Button')
        self.tap_tempo_button = create_button(3, 'Tap_Tempo_Button')
        self.metronome_button = create_button(9, 'Metronome_Button')
        self.fixed_length_button = create_button(90, 'Fixed_Length_Button')
        self.record_button = create_modifier_button(86, 'Record_Button')
        self.undo_button = create_button(119, 'Undo_Button')
        self.create_device_button = create_button(52, 'Create_Device_Button', undo_step_handler=undo_handler)
        self.create_track_button = create_button(53, 'Create_Track_Button', undo_step_handler=undo_handler)
        self.double_button = create_button(117, 'Double_Button', undo_step_handler=undo_handler)
        self.user_button = create_button(59, 'User_Button', undo_step_handler=undo_handler)
        self.select_buttons_raw = [ create_button(20 + idx, 'Track_Select_Button' + str(idx)) for idx in xrange(8) ]
        self.select_buttons = ButtonMatrixElement(name='Track_Select_Buttons', rows=[self.select_buttons_raw])
        self.track_state_buttons_raw = [ create_button(102 + idx, 'Track_State_Button' + str(idx), is_rgb=True) for idx in xrange(8) ]
        self.track_state_buttons = ButtonMatrixElement(name='Track_State_Buttons', rows=[self.track_state_buttons_raw])
        self.side_buttons_raw = [ create_button(36 + idx, 'Scene_Launch_Button' + str(idx)) for idx in reversed(xrange(8)) ]
        self.side_buttons = ButtonMatrixElement(name='Scene_Launch_Buttons', rows=[self.side_buttons_raw])

        @depends(skin=None)
        def create_pad_button(pad_id, name, skin = None, **k):
            return PadButtonElement(pad_id, pad_sensitivity_update, True, MIDI_NOTE_TYPE, 0, (36 + pad_id), skin=skin, name=name, **k)

        self.matrix_rows_raw = [ [ create_pad_button((7 - row) * 8 + column, str(column) + '_Clip_' + str(row) + '_Button', is_rgb=True, default_states={True: 'DefaultMatrix.On',
         False: 'DefaultMatrix.Off'}) for column in xrange(8) ] for row in xrange(8) ]
        double_press_rows = recursive_map(DoublePressElement, self.matrix_rows_raw)
        self.matrix = ButtonMatrixElement(name='Button_Matrix', rows=self.matrix_rows_raw)
        self.double_press_matrix = ButtonMatrixElement(name='Double_Press_Matrix', rows=double_press_rows)
        self.single_press_event_matrix = ButtonMatrixElement(name='Single_Press_Event_Matrix', rows=recursive_map(lambda x: x.single_press, double_press_rows))
        self.double_press_event_matrix = ButtonMatrixElement(name='Double_Press_Event_Matrix', rows=recursive_map(lambda x: x.double_press, double_press_rows))
        self.tempo_control_tap = create_note_button(10, 'Tempo_Control_Tap')
        self.tempo_control = TouchEncoderElement(channel=0, identifier=14, map_mode=consts.GLOBAL_MAP_MODE, name='Tempo_Control', undo_step_handler=undo_handler, delete_handler=deleter, encoder_sensitivity=consts.ENCODER_SENSITIVITY, touch_element=self.tempo_control_tap)
        self.swing_control_tap = create_note_button(9, 'Swing_Control_Tap')
        self.swing_control = TouchEncoderElement(channel=0, identifier=15, map_mode=consts.GLOBAL_MAP_MODE, name='Swing_Control', undo_step_handler=undo_handler, delete_handler=deleter, encoder_sensitivity=consts.ENCODER_SENSITIVITY, touch_element=self.swing_control_tap)
        self.master_volume_control_tap = create_note_button(8, 'Master_Volume_Tap')
        self.master_volume_control = TouchEncoderElement(channel=0, identifier=79, map_mode=consts.GLOBAL_MAP_MODE, undo_step_handler=undo_handler, delete_handler=deleter, name='Master_Volume_Control', encoder_sensitivity=consts.ENCODER_SENSITIVITY, touch_element=self.master_volume_control_tap)
        self.master_volume_control.mapping_sensitivity = continuous_mapping_sensitivity
        self.global_param_touch_buttons_raw = [ create_note_button(index, 'Track_Control_Touch_' + str(index), resource_type=PrioritizedResource) for index in range(8) ]
        self.global_param_touch_buttons = ButtonMatrixElement(name='Track_Control_Touches', rows=[self.global_param_touch_buttons_raw])
        self.parameter_controls_raw = [ TouchEncoderElement(channel=0, identifier=71 + index, map_mode=consts.GLOBAL_MAP_MODE, undo_step_handler=undo_handler, delete_handler=deleter, encoder_sensitivity=consts.ENCODER_SENSITIVITY, name='Track_Control_' + str(index), touch_element=self.global_param_touch_buttons_raw[index]) for index in xrange(8) ]
        self.global_param_controls = ButtonMatrixElement(name='Track_Controls', rows=[self.parameter_controls_raw])
        self.fine_grain_param_controls_raw = [ FineGrainWithModifierEncoderElement(encoder, self.shift_button, fine_grained_continuous_mapping_sensitivity, continuous_mapping_sensitivity) for encoder in self.parameter_controls_raw ]
        self.fine_grain_param_controls = ButtonMatrixElement(rows=[self.fine_grain_param_controls_raw])
        self.any_touch_button = MultiElement(*self.global_param_touch_buttons.nested_control_elements())
        self.playhead_element = PlayheadElement(playhead)