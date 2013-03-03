#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC40/APC40.py
import Live
from APC import APC
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.MixerComponent import MixerComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from EncModeSelectorComponent import EncModeSelectorComponent
from RingedEncoderElement import RingedEncoderElement
from DetailViewCntrlComponent import DetailViewCntrlComponent
from ShiftableDeviceComponent import ShiftableDeviceComponent
from ShiftableTransportComponent import ShiftableTransportComponent
from ShiftTranslatorComponent import ShiftTranslatorComponent
from PedaledSessionComponent import PedaledSessionComponent
from SpecialMixerComponent import SpecialMixerComponent

class APC40(APC):
    """ Script for Akai's APC40 Controller """

    def __init__(self, c_instance):
        APC.__init__(self, c_instance)
        self._device_selection_follows_track_selection = True

    def _setup_session_control(self):
        is_momentary = True
        self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 98)
        right_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 96)
        left_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 97)
        up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 94)
        down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 95)
        right_button.name = 'Bank_Select_Right_Button'
        left_button.name = 'Bank_Select_Left_Button'
        up_button.name = 'Bank_Select_Up_Button'
        down_button.name = 'Bank_Select_Down_Button'
        self._session = PedaledSessionComponent(8, 5)
        self._session.name = 'Session_Control'
        self._session.set_track_bank_buttons(right_button, left_button)
        self._session.set_scene_bank_buttons(down_button, up_button)
        matrix = ButtonMatrixElement()
        matrix.name = 'Button_Matrix'
        scene_launch_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, index + 82) for index in range(5) ]
        track_stop_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, index, 52) for index in range(8) ]
        for index in range(len(scene_launch_buttons)):
            scene_launch_buttons[index].name = 'Scene_' + str(index) + '_Launch_Button'

        for index in range(len(track_stop_buttons)):
            track_stop_buttons[index].name = 'Track_' + str(index) + '_Stop_Button'

        stop_all_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 81)
        stop_all_button.name = 'Stop_All_Clips_Button'
        self._session.set_stop_all_clips_button(stop_all_button)
        self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
        self._session.set_stop_track_clip_value(2)
        for scene_index in range(5):
            scene = self._session.scene(scene_index)
            scene.name = 'Scene_' + str(scene_index)
            button_row = []
            scene.set_launch_button(scene_launch_buttons[scene_index])
            scene.set_triggered_value(2)
            for track_index in range(8):
                button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track_index, scene_index + 53)
                button.name = str(track_index) + '_Clip_' + str(scene_index) + '_Button'
                button_row.append(button)
                clip_slot = scene.clip_slot(track_index)
                clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
                clip_slot.set_triggered_to_play_value(2)
                clip_slot.set_triggered_to_record_value(4)
                clip_slot.set_stopped_value(5)
                clip_slot.set_started_value(1)
                clip_slot.set_recording_value(3)
                clip_slot.set_launch_button(button)

            matrix.add_row(tuple(button_row))

        self._session.set_slot_launch_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 67))
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.selected_scene().set_launch_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 64))
        self._session_zoom = SessionZoomingComponent(self._session)
        self._session_zoom.name = 'Session_Overview'
        self._session_zoom.set_button_matrix(matrix)
        self._session_zoom.set_zoom_button(self._shift_button)
        self._session_zoom.set_nav_buttons(up_button, down_button, left_button, right_button)
        self._session_zoom.set_scene_bank_buttons(tuple(scene_launch_buttons))
        self._session_zoom.set_stopped_value(3)
        self._session_zoom.set_selected_value(5)

    def _setup_mixer_control(self):
        is_momentary = True
        self._mixer = SpecialMixerComponent(8)
        self._mixer.name = 'Mixer'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        for track in range(8):
            strip = self._mixer.channel_strip(track)
            strip.name = 'Channel_Strip_' + str(track)
            volume_control = SliderElement(MIDI_CC_TYPE, track, 7)
            arm_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 48)
            solo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 49)
            mute_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 50)
            select_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 51)
            volume_control.name = str(track) + '_Volume_Control'
            arm_button.name = str(track) + '_Arm_Button'
            solo_button.name = str(track) + '_Solo_Button'
            mute_button.name = str(track) + '_Mute_Button'
            select_button.name = str(track) + '_Select_Button'
            strip.set_volume_control(volume_control)
            strip.set_arm_button(arm_button)
            strip.set_solo_button(solo_button)
            strip.set_mute_button(mute_button)
            strip.set_select_button(select_button)
            strip.set_shift_button(self._shift_button)
            strip.set_invert_mute_feedback(True)

        crossfader = SliderElement(MIDI_CC_TYPE, 0, 15)
        master_volume_control = SliderElement(MIDI_CC_TYPE, 0, 14)
        master_select_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 80)
        prehear_control = EncoderElement(MIDI_CC_TYPE, 0, 47, Live.MidiMap.MapMode.relative_two_compliment)
        crossfader.name = 'Crossfader'
        master_volume_control.name = 'Master_Volume_Control'
        master_select_button.name = 'Master_Select_Button'
        prehear_control.name = 'Prehear_Volume_Control'
        self._mixer.set_crossfader_control(crossfader)
        self._mixer.set_prehear_volume_control(prehear_control)
        self._mixer.master_strip().set_volume_control(master_volume_control)
        self._mixer.master_strip().set_select_button(master_select_button)

    def _setup_custom_components(self):
        self._setup_device_and_transport_control()
        self._setup_global_control()

    def _setup_device_and_transport_control(self):
        is_momentary = True
        device_bank_buttons = []
        device_param_controls = []
        bank_button_labels = ('Clip_Track_Button', 'Device_On_Off_Button', 'Previous_Device_Button', 'Next_Device_Button', 'Detail_View_Button', 'Rec_Quantization_Button', 'Midi_Overdub_Button', 'Metronome_Button')
        for index in range(8):
            device_bank_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 58 + index))
            device_bank_buttons[-1].name = bank_button_labels[index]
            ring_mode_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, 0, 24 + index)
            ringed_encoder = RingedEncoderElement(MIDI_CC_TYPE, 0, 16 + index, Live.MidiMap.MapMode.absolute)
            ringed_encoder.set_ring_mode_button(ring_mode_button)
            ringed_encoder.name = 'Device_Control_' + str(index)
            ring_mode_button.name = ringed_encoder.name + '_Ring_Mode_Button'
            device_param_controls.append(ringed_encoder)

        device = ShiftableDeviceComponent()
        device.name = 'Device_Component'
        device.set_bank_buttons(tuple(device_bank_buttons))
        device.set_shift_button(self._shift_button)
        device.set_parameter_controls(tuple(device_param_controls))
        device.set_on_off_button(device_bank_buttons[1])
        self.set_device_component(device)
        detail_view_toggler = DetailViewCntrlComponent()
        detail_view_toggler.name = 'Detail_View_Control'
        detail_view_toggler.set_shift_button(self._shift_button)
        detail_view_toggler.set_device_clip_toggle_button(device_bank_buttons[0])
        detail_view_toggler.set_detail_toggle_button(device_bank_buttons[4])
        detail_view_toggler.set_device_nav_buttons(device_bank_buttons[2], device_bank_buttons[3])
        transport = ShiftableTransportComponent()
        transport.name = 'Transport'
        play_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 91)
        stop_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 92)
        record_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 93)
        nudge_up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 100)
        nudge_down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 101)
        tap_tempo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 99)
        play_button.name = 'Play_Button'
        stop_button.name = 'Stop_Button'
        record_button.name = 'Record_Button'
        nudge_up_button.name = 'Nudge_Up_Button'
        nudge_down_button.name = 'Nudge_Down_Button'
        tap_tempo_button.name = 'Tap_Tempo_Button'
        transport.set_shift_button(self._shift_button)
        transport.set_play_button(play_button)
        transport.set_stop_button(stop_button)
        transport.set_record_button(record_button)
        transport.set_nudge_buttons(nudge_up_button, nudge_down_button)
        transport.set_tap_tempo_button(tap_tempo_button)
        transport.set_quant_toggle_button(device_bank_buttons[5])
        transport.set_overdub_button(device_bank_buttons[6])
        transport.set_metronome_button(device_bank_buttons[7])
        bank_button_translator = ShiftTranslatorComponent()
        bank_button_translator.set_controls_to_translate(tuple(device_bank_buttons))
        bank_button_translator.set_shift_button(self._shift_button)

    def _setup_global_control(self):
        is_momentary = True
        global_bank_buttons = []
        global_param_controls = []
        for index in range(8):
            ring_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, 0, 56 + index)
            ringed_encoder = RingedEncoderElement(MIDI_CC_TYPE, 0, 48 + index, Live.MidiMap.MapMode.absolute)
            ringed_encoder.name = 'Track_Control_' + str(index)
            ring_button.name = ringed_encoder.name + '_Ring_Mode_Button'
            ringed_encoder.set_ring_mode_button(ring_button)
            global_param_controls.append(ringed_encoder)

        global_bank_buttons = []
        global_bank_labels = ('Pan_Button', 'Send_A_Button', 'Send_B_Button', 'Send_C_Button')
        for index in range(4):
            global_bank_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 87 + index))
            global_bank_buttons[-1].name = global_bank_labels[index]

        encoder_modes = EncModeSelectorComponent(self._mixer)
        encoder_modes.name = 'Track_Control_Modes'
        encoder_modes.set_modes_buttons(global_bank_buttons)
        encoder_modes.set_controls(tuple(global_param_controls))
        global_translation_selector = ChannelTranslationSelector()
        global_translation_selector.name = 'Global_Translations'
        global_translation_selector.set_controls_to_translate(tuple(global_param_controls))
        global_translation_selector.set_mode_buttons(tuple(global_bank_buttons))

    def _product_model_id_byte(self):
        return 115