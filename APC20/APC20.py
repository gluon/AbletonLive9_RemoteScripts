#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC20/APC20.py
import Live
from APC40.APC import APC
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.TransportComponent import TransportComponent
from APC40.APCSessionComponent import APCSessionComponent
from APC40.SpecialMixerComponent import SpecialMixerComponent
from ShiftableZoomingComponent import ShiftableZoomingComponent
from ShiftableSelectorComponent import ShiftableSelectorComponent
from SliderModesComponent import SliderModesComponent
from consts import *

class APC20(APC):
    """ Script for Akai's APC20 Controller """

    def __init__(self, c_instance):
        self._shift_modes = None
        APC.__init__(self, c_instance)

    def disconnect(self):
        self._shift_modes = None
        APC.disconnect(self)

    def _activate_combination_mode(self, track_offset, support_devices):
        APC._activate_combination_mode(self, track_offset, support_devices)
        if support_devices:
            self._shift_modes.invert_assignment()

    def _setup_session_control(self):
        is_momentary = True
        self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 81)
        self._session = APCSessionComponent(8, 5)
        self._session.name = 'Session_Control'
        self._matrix = ButtonMatrixElement()
        self._matrix.name = 'Button_Matrix'
        scene_launch_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, index + 82) for index in range(5) ]
        track_stop_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, index, 52) for index in range(8) ]
        for index in range(len(scene_launch_buttons)):
            scene_launch_buttons[index].name = 'Scene_' + str(index) + '_Launch_Button'

        for index in range(len(track_stop_buttons)):
            track_stop_buttons[index].name = 'Track_' + str(index) + '_Stop_Button'

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

            self._matrix.add_row(tuple(button_row))

        self._session.selected_scene().name = 'Selected_Scene'
        self._session.selected_scene().set_launch_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 64))
        self._session_zoom = ShiftableZoomingComponent(self._session, tuple(track_stop_buttons))
        self._session_zoom.name = 'Session_Overview'
        self._session_zoom.set_button_matrix(self._matrix)
        self._session_zoom.set_zoom_button(self._shift_button)
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
            solo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 49)
            mute_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 50)
            solo_button.name = str(track) + '_Solo_Button'
            mute_button.name = str(track) + '_Mute_Button'
            strip.set_solo_button(solo_button)
            strip.set_mute_button(mute_button)
            strip.set_shift_button(self._shift_button)
            strip.set_invert_mute_feedback(True)

        master_volume_control = SliderElement(MIDI_CC_TYPE, 0, 14)
        prehear_control = EncoderElement(MIDI_CC_TYPE, 0, 47, Live.MidiMap.MapMode.relative_two_compliment)
        master_volume_control.name = 'Master_Volume_Control'
        prehear_control.name = 'Prehear_Volume_Control'
        self._mixer.set_prehear_volume_control(prehear_control)
        self._mixer.master_strip().set_volume_control(master_volume_control)

    def _setup_custom_components(self):
        is_momentary = True
        master_select_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 80)
        master_select_button.name = 'Master_Select_Button'
        select_buttons = []
        arm_buttons = []
        sliders = []
        for track in range(8):
            select_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 51))
            arm_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, track, 48))
            sliders.append(SliderElement(MIDI_CC_TYPE, track, 7))
            select_buttons[-1].name = str(track) + '_Select_Button'
            arm_buttons[-1].name = str(track) + '_Arm_Button'
            sliders[-1].name = str(track) + '_Volume_Control'

        transport = TransportComponent()
        transport.name = 'Transport'
        slider_modes = SliderModesComponent(self._mixer, tuple(sliders))
        slider_modes.name = 'Slider_Modes'
        self._shift_modes = ShiftableSelectorComponent(tuple(select_buttons), master_select_button, tuple(arm_buttons), self._matrix, self._session, self._session_zoom, self._mixer, transport, slider_modes, self._send_introduction_message)
        self._shift_modes.name = 'Shift_Modes'
        self._shift_modes.set_mode_toggle(self._shift_button)

    def _product_model_id_byte(self):
        return 123