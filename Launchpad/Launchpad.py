#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad/Launchpad.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from ConfigurableButtonElement import ConfigurableButtonElement
from MainSelectorComponent import MainSelectorComponent
SIDE_NOTES = (8, 24, 40, 56, 72, 88, 104, 120)
DRUM_NOTES = (41, 42, 43, 44, 45, 46, 47, 57, 58, 59, 60, 61, 62, 63, 73, 74, 75, 76, 77, 78, 79, 89, 90, 91, 92, 93, 94, 95, 105, 106, 107)

class Launchpad(ControlSurface):
    """ Script for Novation's Launchpad Controller """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self._suppress_send_midi = True
            self._suppress_session_highlight = True
            is_momentary = True
            self._suggested_input_port = 'Launchpad'
            self._suggested_output_port = 'Launchpad'
            self._control_is_with_automap = False
            self._user_byte_write_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 16)
            self._user_byte_write_button.name = 'User_Byte_Button'
            self._user_byte_write_button.send_value(1)
            self._user_byte_write_button.add_value_listener(self._user_byte_value)
            self._wrote_user_byte = False
            self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
            matrix = ButtonMatrixElement()
            matrix.name = 'Button_Matrix'
            for row in range(8):
                button_row = []
                for column in range(8):
                    button = ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, row * 16 + column)
                    button.name = str(column) + '_Clip_' + str(row) + '_Button'
                    button_row.append(button)

                matrix.add_row(tuple(button_row))

            self._config_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 0, optimized_send_midi=False)
            self._config_button.add_value_listener(self._config_value)
            top_buttons = [ ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, 104 + index) for index in range(8) ]
            side_buttons = [ ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, SIDE_NOTES[index]) for index in range(8) ]
            top_buttons[0].name = 'Bank_Select_Up_Button'
            top_buttons[1].name = 'Bank_Select_Down_Button'
            top_buttons[2].name = 'Bank_Select_Left_Button'
            top_buttons[3].name = 'Bank_Select_Right_Button'
            top_buttons[4].name = 'Session_Button'
            top_buttons[5].name = 'User1_Button'
            top_buttons[6].name = 'User2_Button'
            top_buttons[7].name = 'Mixer_Button'
            side_buttons[0].name = 'Vol_Button'
            side_buttons[1].name = 'Pan_Button'
            side_buttons[2].name = 'SndA_Button'
            side_buttons[3].name = 'SndB_Button'
            side_buttons[4].name = 'Stop_Button'
            side_buttons[5].name = 'Trk_On_Button'
            side_buttons[6].name = 'Solo_Button'
            side_buttons[7].name = 'Arm_Button'
            self._selector = MainSelectorComponent(matrix, tuple(top_buttons), tuple(side_buttons), self._config_button)
            self._selector.name = 'Main_Modes'
            for control in self.controls:
                if isinstance(control, ConfigurableButtonElement):
                    control.add_value_listener(self._button_value)

            self.set_highlighting_session_component(self._selector.session_component())
            self._suppress_session_highlight = False

    def disconnect(self):
        self._suppress_send_midi = True
        for control in self.controls:
            if isinstance(control, ConfigurableButtonElement):
                control.remove_value_listener(self._button_value)

        self._selector = None
        self._user_byte_write_button.remove_value_listener(self._user_byte_value)
        self._config_button.remove_value_listener(self._config_value)
        ControlSurface.disconnect(self)
        self._suppress_send_midi = False
        self._config_button.send_value(32)
        self._config_button.send_value(0)
        self._config_button = None
        self._user_byte_write_button.send_value(0)
        self._user_byte_write_button = None

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self.schedule_message(5, self._update_hardware)

    def handle_sysex(self, midi_bytes):
        if len(midi_bytes) == 8:
            if midi_bytes[1:5] == (0, 32, 41, 6):
                response = long(midi_bytes[5])
                response += long(midi_bytes[6]) << 8
                if response == Live.Application.encrypt_challenge2(self._challenge):
                    self._on_handshake_successful()

    def _on_handshake_successful(self):
        self._suppress_send_midi = False
        self.set_enabled(True)

    def build_midi_map(self, midi_map_handle):
        ControlSurface.build_midi_map(self, midi_map_handle)
        if self._selector.mode_index == 1:
            new_channel = self._selector.channel_for_current_mode()
            for note in DRUM_NOTES:
                self._translate_message(MIDI_NOTE_TYPE, note, 0, note, new_channel)

    def _send_midi(self, midi_bytes, optimized = None):
        sent_successfully = False
        if not self._suppress_send_midi:
            sent_successfully = ControlSurface._send_midi(self, midi_bytes, optimized=optimized)
        return sent_successfully

    def _update_hardware(self):
        self._suppress_send_midi = False
        self._wrote_user_byte = True
        self._user_byte_write_button.send_value(1)
        self._suppress_send_midi = True
        self.set_enabled(False)
        self._suppress_send_midi = False
        self._send_challenge()

    def _send_challenge(self):
        for index in range(4):
            challenge_byte = self._challenge >> 8 * index & 127
            self._send_midi((176, 17 + index, challenge_byte))

    def _user_byte_value(self, value):
        if not value in range(128):
            raise AssertionError
            enabled = self._wrote_user_byte or value == 1
            self._control_is_with_automap = not enabled
            self._suppress_send_midi = self._control_is_with_automap
            if not self._control_is_with_automap:
                for control in self.controls:
                    if isinstance(control, ConfigurableButtonElement):
                        control.set_force_next_value()

            self._selector.set_mode(0)
            self.set_enabled(enabled)
            self._suppress_send_midi = False
        else:
            self._wrote_user_byte = False

    def _button_value(self, value):
        raise value in range(128) or AssertionError

    def _config_value(self, value):
        raise value in range(128) or AssertionError

    def _set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
        if not self._suppress_session_highlight:
            ControlSurface._set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks)