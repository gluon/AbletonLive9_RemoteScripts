#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/Push.py
from __future__ import with_statement
import Live
from contextlib import contextmanager
from functools import partial
from itertools import izip
from _Framework.Dependency import inject
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE, MIDI_CC_STATUS, MIDI_NOTE_ON_STATUS
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ModesComponent import AddLayerMode, MultiEntryMode, ModesComponent, SetAttributeMode, CancellableBehaviour, AlternativeBehaviour, ReenterBehaviour, DynamicBehaviourMixin, ExcludingBehaviourMixin
from _Framework.SysexValueControl import SysexValueControl
from _Framework.Layer import Layer
from _Framework.Resource import PrioritizedResource
from _Framework.DeviceBankRegistry import DeviceBankRegistry
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.Util import find_if, clamp, nop, mixin, const
from _Framework import Defaults
from _Framework import Task
from OptionalElement import OptionalElement
from ComboElement import ComboElement
from HandshakeComponent import HandshakeComponent, make_dongle_message
from ValueComponent import ValueComponent, ParameterValueComponent
from ConfigurableButtonElement import ConfigurableButtonElement
from SpecialSessionComponent import SpecialSessionComponent, SpecialSessionZoomingComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialTransportComponent import SpecialTransportComponent
from SpecialPhysicalDisplay import SpecialPhysicalDisplay
from InstrumentComponent import InstrumentComponent
from StepSeqComponent import StepSeqComponent
from LoopSelectorComponent import LoopSelectorComponent
from ViewControlComponent import ViewControlComponent
from ClipControlComponent import ClipControlComponent
from DisplayingDeviceComponent import DisplayingDeviceComponent
from DeviceNavigationComponent import DeviceNavigationComponent
from SessionRecordingComponent import SessionRecordingComponent
from NoteRepeatComponent import NoteRepeatComponent
from ClipCreator import ClipCreator
from MatrixMaps import PAD_TRANSLATIONS, FEEDBACK_CHANNELS
from BackgroundComponent import BackgroundComponent, ModifierBackgroundComponent
from BrowserComponent import BrowserComponent
from BrowserModes import BrowserHotswapMode
from Actions import CreateInstrumentTrackComponent, CreateDefaultTrackComponent, CaptureAndInsertSceneComponent, DuplicateLoopComponent, SelectComponent, DeleteComponent, DeleteSelectedClipComponent, DeleteSelectedSceneComponent, CreateDeviceComponent
from M4LInterfaceComponent import M4LInterfaceComponent
from UserSettingsComponent import UserComponent
from MessageBoxComponent import DialogComponent, NotificationComponent
from TouchEncoderElement import TouchEncoderElement
from TouchStripElement import TouchStripElement
from TouchStripController import TouchStripControllerComponent, TouchStripEncoderConnection
from Selection import L9CSelection
from AccentComponent import AccentComponent
from AutoArmComponent import AutoArmComponent
from PadSensitivity import PadSensitivity
from WithPriority import WithPriority
from Settings import SETTING_WORKFLOW, SETTING_THRESHOLD, SETTING_CURVE
import Skin
import consts
import Colors
import Sysex
import Settings
GLOBAL_MAP_MODE = Live.MidiMap.MapMode.relative_smooth_two_compliment

class Push(ControlSurface):
    """
    Push controller script.
    
    Disclaimer: Any use of the Push control surface code (the "Code")
    or parts thereof for commercial purposes or in a commercial context
    is not allowed. Though we do not grant a license for non-commercial
    use of the Code, you may use it in this regard but should be aware that
    (1) we reserve the right to deny the future use any time and
    (2) you need to check whether the use is allowed under the national law
    applicable to your use.
    """

    def __init__(self, c_instance):
        super(Push, self).__init__(c_instance)
        injecting = inject(expect_dialog=const(self.expect_dialog), show_notification=const(self.show_notification), selection=lambda : L9CSelection(application=self.application(), device_component=self._device, navigation_component=self._device_navigation))
        self._push_injector = injecting.everywhere()
        with self.component_guard():
            self._suppress_sysex = False
            self._skin = Skin.make_default_skin()
            self._clip_creator = ClipCreator()
            self._device_selection_follows_track_selection = True
            self._create_controls()
            self._init_settings()
            self._init_message_box()
            self._init_background()
            self._init_touch_strip_controller()
            self._init_transport_and_recording()
            self._init_global_actions()
            self._init_mixer()
            self._init_session()
            self._init_step_sequencer()
            self._init_instrument()
            self._init_note_repeat()
            self._init_pad_sensitivity()
            self._init_user()
            self._init_matrix_modes()
            self._init_track_modes()
            self._init_device()
            self._init_browser()
            self._init_clip_settings()
            self._init_main_modes()
            self._init_m4l_interface()
            self._init_handshake()
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._on_selected_track_changed()
            self._on_session_record_changed.subject = self.song()
            self._on_session_record_changed()
            self.set_highlighting_session_component(self._session)
            self.set_feedback_channels(FEEDBACK_CHANNELS)
        self.log_message('Push script loaded')
        self._send_midi(Sysex.WELCOME_MESSAGE)

    def disconnect(self):
        self._pre_serialize()
        with self.component_guard():
            self._user.mode = Sysex.USER_MODE
        super(Push, self).disconnect()
        self._send_midi(Sysex.GOOD_BYE_MESSAGE)
        self.log_message('Push script unloaded')

    @contextmanager
    def component_guard(self):
        with super(Push, self).component_guard():
            with self._push_injector:
                song_view = self.song().view
                old_selected_track = song_view.selected_track
                yield
                if song_view.selected_track != old_selected_track:
                    self._track_selection_changed_by_action()

    def _track_selection_changed_by_action(self):
        if self._matrix_modes.selected_mode == 'note':
            self._session_recording.deactivate_recording()
        if self._auto_arm.needs_restore_auto_arm:
            self._auto_arm.restore_auto_arm()

    def enable_test_mode(self):
        """
        Enable a series of hacks that make the script testable from
        Cucumber.
        """
        Defaults.MOMENTARY_DELAY = 0.5
        consts.CUKE_MODE = True
        self._handshake._identification_timeout_task.kill()
        self._handshake._identification_timeout_task = Task.Task()
        self.update()

    def refresh_state(self):
        super(Push, self).refresh_state()
        if self._user.mode == Sysex.LIVE_MODE:
            self.schedule_message(5, self._start_handshake)

    def _pre_serialize(self):
        """ This will pre-serialize all settings, as a later access to Push's objects
        might cause problems with Pickle """
        from pickle import dumps
        from encodings import ascii
        nop(ascii)
        preferences = self._c_instance.preferences('Push')
        dump = dumps(self._pref_dict)
        preferences.set_serializer(lambda : dump)

    def _init_settings(self):
        from pickle import loads, dumps
        from encodings import ascii
        nop(ascii)
        preferences = self._c_instance.preferences('Push')
        self._pref_dict = {}
        try:
            self._pref_dict = loads(str(preferences))
        except Exception:
            pass

        pref_dict = self._pref_dict
        preferences.set_serializer(lambda : dumps(pref_dict))
        self._settings = Settings.create_settings(preferences=self._pref_dict)
        self._on_pad_curve.subject = self._settings[SETTING_CURVE]
        self._on_pad_threshold.subject = self._settings[SETTING_THRESHOLD]

    def _init_handshake(self):
        dongle_message, dongle = make_dongle_message(Sysex.DONGLE_ENQUIRY_PREFIX)
        identity_control = SysexValueControl(Sysex.IDENTITY_PREFIX, Sysex.IDENTITY_ENQUIRY)
        dongle_control = SysexValueControl(Sysex.DONGLE_PREFIX, dongle_message)
        presentation_control = SysexValueControl(Sysex.DONGLE_PREFIX, Sysex.make_presentation_message(self.application()))
        self._handshake = HandshakeComponent(identity_control=identity_control, dongle_control=dongle_control, presentation_control=presentation_control, dongle=dongle)
        self._on_handshake_success.subject = self._handshake
        self._on_handshake_failure.subject = self._handshake

    def _start_handshake(self):
        for control in self.controls:
            receive_value_backup = getattr(control, '_receive_value_backup', nop)
            if receive_value_backup != nop:
                control.receive_value = receive_value_backup
            send_midi_backup = getattr(control, '_send_midi_backup', nop)
            if send_midi_backup != nop:
                control.send_midi = send_midi_backup

        self._handshake._start_handshake()
        self.update()

    def update(self):
        self._on_session_record_changed()
        self._on_note_repeat_mode_changed(self._note_repeat.selected_mode)
        self.set_feedback_channels(FEEDBACK_CHANNELS)
        self._update_calibration()
        super(Push, self).update()

    @subject_slot('success')
    def _on_handshake_success(self):
        self.log_message('Handshake succeded!')
        self.update()

    @subject_slot('failure')
    def _on_handshake_failure(self):
        self.log_message('Handshake failed, performing harakiri!')
        for control in self.controls:
            receive_value_backup = getattr(control, 'receive_value', nop)
            if receive_value_backup != nop:
                control._receive_value_backup = receive_value_backup
            send_midi_backup = getattr(control, 'send_midi', nop)
            if send_midi_backup != nop:
                control._send_midi_backup = send_midi_backup
            control.receive_value = nop
            control.send_midi = nop

    def _update_calibration(self):
        self._send_midi(Sysex.CALIBRATION_SET)

    def _create_controls(self):
        is_momentary = True

        def create_button(note, name, **k):
            button = ConfigurableButtonElement(is_momentary, MIDI_CC_TYPE, 0, note, name=name, skin=self._skin, **k)
            return button

        def create_modifier_button(note, name, **k):
            button = create_button(note, name, resource_type=PrioritizedResource, **k)
            return button

        undo_handler = self.song()
        self._nav_up_button = create_button(46, 'Up_Arrow')
        self._nav_down_button = create_button(47, 'Down_Arrow')
        self._nav_left_button = create_button(44, 'Left_Arrow')
        self._nav_right_button = create_button(45, 'Right_arrow')
        self._nav_up_button.default_states = consts.SCROLL_SIDE_BUTTON_STATES
        self._nav_down_button.default_states = consts.SCROLL_SIDE_BUTTON_STATES
        self._nav_left_button.default_states = consts.SCROLL_SIDE_BUTTON_STATES
        self._nav_right_button.default_states = consts.SCROLL_SIDE_BUTTON_STATES
        self._shift_button = create_modifier_button(49, 'Shift_Button')
        self._select_button = create_modifier_button(48, 'Select_Button')
        self._delete_button = create_modifier_button(118, 'Delete_Button', undo_step_handler=undo_handler)
        self._duplicate_button = create_modifier_button(88, 'Duplicate_Button', undo_step_handler=undo_handler)
        self._quantize_button = create_modifier_button(116, 'Quantization_Button', undo_step_handler=undo_handler)
        self._accent_button = create_modifier_button(57, 'Accent_Button')
        self._in_button = create_button(62, 'In_Button')
        self._out_button = create_button(63, 'Out_Button')
        self._master_select_button = create_button(28, 'Master_Select_Button')
        self._octave_down_button = create_button(54, 'Octave_Down_Button')
        self._octave_up_button = create_button(55, 'Octave_Up_Button')
        self._repeat_button = create_button(56, 'Repeat_Button')
        self._octave_up_button.default_states = consts.SCROLL_SIDE_BUTTON_STATES
        self._octave_down_button.default_states = consts.SCROLL_SIDE_BUTTON_STATES
        self._global_mute_button = create_modifier_button(60, 'Global_Mute_Button')
        self._global_solo_button = create_modifier_button(61, 'Global_Solo_Button')
        self._global_track_stop_button = create_modifier_button(29, 'Track_Stop_Button')
        self._scale_presets_button = create_button(58, 'Scale_Presets_Button')
        self._vol_mix_mode_button = create_button(114, 'Vol_Mix_Mode_Button')
        self._device_mode_button = create_button(110, 'Device_Mode_Button')
        self._clip_mode_button = create_button(113, 'Clip_Mode_Button')
        self._browse_mode_button = create_button(111, 'Browse_Mode_Button')
        self._single_track_mix_mode_button = create_button(112, 'Single_Track_Mode_Button')
        self._pan_send_mix_mode_button = create_button(115, 'Pan_Send_Mode_Button', resource_type=PrioritizedResource)
        self._note_mode_button = create_button(50, 'Note_Mode_Button')
        self._session_mode_button = create_button(51, 'Session_Mode_Button')
        self._play_button = create_button(85, 'Play_Button')
        self._new_button = create_button(87, 'New_Button')
        self._automation_button = create_button(89, 'Automation_Button')
        self._tap_tempo_button = create_button(3, 'Tap_Tempo_Button')
        self._metronome_button = create_button(9, 'Metronome_Button')
        self._fixed_length_button = create_button(90, 'Fixed_Length_Button')
        self._record_button = create_button(86, 'Record_Button')
        self._undo_button = create_button(119, 'Undo_Button')
        self._create_device_button = create_button(52, 'Create_Device_Button', undo_step_handler=undo_handler)
        self._create_track_button = create_button(53, 'Create_Track_Button', undo_step_handler=undo_handler)
        self._double_button = create_button(117, 'Double_Button', undo_step_handler=undo_handler)
        self._user_button = create_button(59, 'User_Button', undo_step_handler=undo_handler)
        self._select_buttons = ButtonMatrixElement(name='Track_Select_Buttons')
        self._select_buttons.add_row([ create_button(20 + idx, 'Track_Select_Button' + str(idx)) for idx in xrange(8) ])
        self._track_state_buttons = ButtonMatrixElement(name='Track_State_Buttons')
        self._track_state_buttons.add_row([ create_button(102 + idx, 'Track_State_Button' + str(idx), is_rgb=True) for idx in xrange(8) ])
        self._side_buttons = ButtonMatrixElement(name='Scene_Launch_Buttons')
        self._side_buttons.add_row([ create_button(36 + idx, 'Scene_Launch_Button' + str(idx)) for idx in reversed(xrange(8)) ])
        for button in self._side_buttons:
            button.set_on_off_values('Session.SceneSelected', 'Session.SceneUnselected')

        def create_display_line(clear_cmd, write_cmd, index):
            line = SpecialPhysicalDisplay(consts.DISPLAY_LENGTH, 1)
            line.set_clear_all_message(clear_cmd)
            line.set_message_parts(write_cmd, (247,))
            line.name = 'Display_Line_%d' % index
            line.reset()
            return line

        self._display_line1 = create_display_line(Sysex.CLEAR_LINE1, Sysex.WRITE_LINE1, 0)
        self._display_line2 = create_display_line(Sysex.CLEAR_LINE2, Sysex.WRITE_LINE2, 1)
        self._display_line3 = create_display_line(Sysex.CLEAR_LINE3, Sysex.WRITE_LINE3, 2)
        self._display_line4 = create_display_line(Sysex.CLEAR_LINE4, Sysex.WRITE_LINE4, 3)
        self._display_lines = [self._display_line1,
         self._display_line2,
         self._display_line3,
         self._display_line4]

        def create_note_button(note, name, **k):
            return ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, note, skin=self._skin, name=name, **k)

        self._matrix = ButtonMatrixElement(name='Button_Matrix')
        for row in xrange(8):
            self._matrix.add_row([ create_note_button(36 + (7 - row) * 8 + column, str(column) + '_Clip_' + str(row) + '_Button', is_rgb=True, default_states={True: 'DefaultMatrix.On',
             False: 'DefaultMatrix.Off'}) for column in xrange(8) ])

        self._touch_strip_control = TouchStripElement(name='Touch_Strip_Control')
        self._touch_strip_tap = create_note_button(12, 'Touch_Strip_Tap')
        self._touch_strip_control.set_feedback_delay(-1)
        self._touch_strip_control.set_needs_takeover(False)
        self._touch_strip_control.set_touch_button(self._touch_strip_tap)

        class Deleter(object):

            @property
            def is_deleting(_):
                return self._delete_component.is_deleting

            def delete_clip_envelope(_, param):
                return self._delete_component.delete_clip_envelope(param)

        deleter = Deleter()
        self._tempo_control = TouchEncoderElement(self.song(), deleter, MIDI_CC_TYPE, 0, 14, GLOBAL_MAP_MODE, name='Tempo_Control', encoder_sensitivity=consts.ENCODER_SENSITIVITY)
        self._tempo_control_tap = create_note_button(10, 'Tempo_Control_Tap')
        self._tempo_control.set_touch_button(self._tempo_control_tap)
        self._swing_control = TouchEncoderElement(self.song(), deleter, MIDI_CC_TYPE, 0, 15, GLOBAL_MAP_MODE, name='Swing_Control', encoder_sensitivity=consts.ENCODER_SENSITIVITY)
        self._swing_control_tap = create_note_button(9, 'Swing_Control_Tap')
        self._swing_control.set_touch_button(self._swing_control_tap)
        self._master_volume_control = TouchEncoderElement(self.song(), deleter, MIDI_CC_TYPE, 0, 79, GLOBAL_MAP_MODE, name='Master_Volume_Control', encoder_sensitivity=consts.ENCODER_SENSITIVITY)
        self._master_volume_control_tap = create_note_button(8, 'Master_Volume_Tap')
        self._master_volume_control.set_touch_button(self._master_volume_control_tap)
        self._global_param_controls = ButtonMatrixElement(name='Track_Controls')
        self._global_param_controls.add_row([ TouchEncoderElement(self.song(), deleter, MIDI_CC_TYPE, 0, 71 + index, GLOBAL_MAP_MODE, encoder_sensitivity=consts.ENCODER_SENSITIVITY, name='Track_Control_' + str(index)) for index in xrange(8) ])
        self._global_param_touch_buttons = ButtonMatrixElement(name='Track_Control_Touches')
        self._global_param_touch_buttons.add_row([ ConfigurableButtonElement(True, MIDI_NOTE_TYPE, 0, index, skin=self._skin, name='Track_Control_Touch_' + str(index)) for index in range(8) ])
        for encoder, touch_button in izip(self._global_param_controls, self._global_param_touch_buttons):
            encoder.set_touch_button(touch_button)

        self._on_param_encoder_touched.replace_subjects(self._global_param_touch_buttons)

    def _init_background(self):
        self._background = BackgroundComponent()
        self._background.layer = Layer(display_line1=self._display_line1, display_line2=self._display_line2, display_line3=self._display_line3, display_line4=self._display_line4, top_buttons=self._select_buttons, bottom_buttons=self._track_state_buttons, scales_button=self._scale_presets_button, octave_up=self._octave_up_button, octave_down=self._octave_down_button, side_buttons=self._side_buttons, repeat_button=self._repeat_button, accent_button=self._accent_button, in_button=self._in_button, out_button=self._out_button, param_controls=self._global_param_controls, param_touch=self._global_param_touch_buttons, tempo_control_tap=self._tempo_control_tap, master_control_tap=self._master_volume_control_tap, touch_strip=self._touch_strip_control, touch_strip_tap=self._touch_strip_tap, nav_up_button=self._nav_up_button, nav_down_button=self._nav_down_button, nav_left_button=self._nav_left_button, nav_right_button=self._nav_right_button, _notification=self._notification.use_single_line(2))
        self._background.layer.priority = consts.BACKGROUND_PRIORITY
        self._matrix_background = BackgroundComponent()
        self._matrix_background.set_enabled(False)
        self._matrix_background.layer = Layer(matrix=self._matrix)
        self._mod_background = ModifierBackgroundComponent()
        self._mod_background.layer = Layer(shift_button=self._shift_button, select_button=self._select_button, delete_button=self._delete_button, duplicate_button=self._duplicate_button, quantize_button=self._quantize_button)

    def _can_auto_arm_track(self, track):
        routing = track.current_input_routing
        return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith('Push Input')

    def _init_touch_strip_controller(self):
        strip_controller = TouchStripControllerComponent()
        strip_controller.set_enabled(False)
        strip_controller.layer = Layer(touch_strip=self._touch_strip_control)
        strip_controller.layer.priority = consts.MODAL_DIALOG_PRIORITY
        self._strip_connection = TouchStripEncoderConnection(strip_controller, self._touch_strip_tap)
        self._tempo_control.set_observer(self._strip_connection)
        self._swing_control.set_observer(self._strip_connection)
        self._master_volume_control.set_observer(self._strip_connection)
        for encoder in self._global_param_controls:
            encoder.set_observer(self._strip_connection)

    def _init_matrix_modes(self):
        self._auto_arm = AutoArmComponent(name='Auto_Arm')
        self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
        self._auto_arm.notification_layer = Layer(display_line1=self._display_line3)
        self._auto_arm.notification_layer.priority = consts.NOTIFICATION_PRIORITY
        self._note_modes = ModesComponent(name='Note_Modes')
        self._note_modes.add_mode('sequencer', [self._note_repeat,
         self._accent_component,
         self._step_sequencer,
         self._action_pad_sensitivity,
         self._drum_pad_sensitivity])
        self._note_modes.add_mode('looper', self._audio_loop if consts.PROTO_AUDIO_NOTE_MODE else self._matrix_background)
        self._note_modes.add_mode('instrument', [self._note_repeat,
         self._accent_component,
         self._instrument,
         self._instrument_pad_sensitivity])
        self._note_modes.add_mode('disabled', self._matrix_background)
        self._note_modes.selected_mode = 'disabled'
        self._note_modes.set_enabled(False)
        self._matrix_modes = ModesComponent(name='Matrix_Modes')
        self._matrix_modes.add_mode('session', [(self._zooming, self._zooming_layer),
         (self._session, self._session_layer),
         AddLayerMode(self._session, self._restricted_session_layer),
         self._action_pad_sensitivity])
        self._matrix_modes.add_mode('note', [self._view_control,
         self._note_modes,
         self._delete_clip,
         (self._session, self._restricted_session_layer)], behaviour=self._auto_arm.auto_arm_restore_behaviour)
        self._matrix_modes.selected_mode = 'note'
        self._matrix_modes.layer = Layer(session_button=self._session_mode_button, note_button=self._note_mode_button)
        self._on_matrix_mode_changed.subject = self._matrix_modes
        self._matrix_modes.selected_mode = 'note'

    def _init_pad_sensitivity(self):
        self._accent_component = AccentComponent(self._c_instance.full_velocity)
        self._accent_component.set_enabled(False)
        self._accent_component.layer = Layer(toggle_button=self._accent_button)
        self._on_accent_mode_changed.subject = self._accent_component
        all_pad_sysex_control = SysexValueControl(Sysex.ALL_PADS_SENSITIVITY_PREFIX)
        pad_sysex_control = SysexValueControl(Sysex.PAD_SENSITIVITY_PREFIX)
        self._instrument_pad_sensitivity = PadSensitivity(value_control=all_pad_sysex_control)
        self._instrument_pad_sensitivity.set_enabled(False)
        self._instrument_pad_sensitivity.parameters = self._create_pad_parameters(self._settings[SETTING_CURVE].value, self._settings[SETTING_THRESHOLD].value)
        self._action_pad_sensitivity = PadSensitivity(value_control=all_pad_sysex_control)
        self._action_pad_sensitivity.set_enabled(False)
        self._action_pad_sensitivity.parameters = Settings.action_pad_sensitvity
        self._drum_pad_sensitivity = PadSensitivity(value_control=pad_sysex_control, pads=[0,
         1,
         2,
         3,
         8,
         9,
         10,
         11,
         16,
         17,
         18,
         19,
         24,
         25,
         26,
         27])
        self._drum_pad_sensitivity.set_enabled(False)
        self._drum_pad_sensitivity.parameters = self._create_pad_parameters(self._settings[SETTING_CURVE].value, self._settings[SETTING_THRESHOLD].value)

    def _init_user(self):
        sysex_control = SysexValueControl(Sysex.MODE_CHANGE)
        self._user = UserComponent(value_control=sysex_control)
        self._user.layer = Layer(action_button=self._user_button)
        self._user.settings_layer = Layer(display_line1=self._display_line1, display_line2=self._display_line2, display_line3=self._display_line3, display_line4=self._display_line4, encoders=self._global_param_controls)
        self._user.settings_layer.priority = consts.DIALOG_PRIORITY
        self._user.settings = self._settings
        self._on_hardware_mode_changed.subject = self._user
        self._on_before_hardware_mode_sent.subject = self._user
        self._on_after_hardware_mode_sent.subject = self._user

    def _init_session(self):
        self._session = SpecialSessionComponent(8, 8, name='Session_Control')
        self._session.set_mixer(self._mixer)
        for scene_index in xrange(8):
            scene = self._session.scene(scene_index)
            scene.set_triggered_value(self._skin['Session.SceneTriggered'])
            scene.name = 'Scene_' + str(scene_index)
            scene.layer = Layer(select_button=self._select_button, delete_button=self._delete_button)
            scene._do_select_scene = self._selector.on_select_scene
            for track_index in xrange(8):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
                clip_slot.set_triggered_to_play_value('Session.ClipTriggeredPlay')
                clip_slot.set_triggered_to_record_value('Session.ClipTriggeredRecord')
                clip_slot.set_clip_palette(Colors.CLIP_COLOR_TABLE)
                clip_slot.set_clip_rgb_table(Colors.RGB_COLOR_TABLE)
                clip_slot.set_record_button_value('Session.RecordButton')
                clip_slot.set_started_value('Session.ClipStarted')
                clip_slot.set_recording_value('Session.ClipRecording')
                clip_slot._do_select_clip = self._selector.on_select_clip
                clip_slot.layer = Layer(delete_button=self._delete_button, select_button=self._select_button, duplicate_button=self._duplicate_button)

        self._session_layer = Layer(page_up_button=self._octave_up_button, page_down_button=self._octave_down_button, track_bank_left_button=self._nav_left_button, track_bank_right_button=self._nav_right_button, scene_bank_up_button=self._nav_up_button, scene_bank_down_button=self._nav_down_button, clip_launch_buttons=self._matrix, scene_launch_buttons=self._side_buttons, duplicate_button=self._duplicate_button)
        self._restricted_session_layer = Layer(stop_all_clips_button=ComboElement((self._shift_button,), self._global_track_stop_button))
        self._session_stop_track_layer = Layer(stop_track_clip_buttons=self._track_state_buttons)
        self._session.duplicate_layer = Layer(scene_buttons=self._side_buttons)
        self._zooming = SpecialSessionZoomingComponent(self._session, name='Session_Overview')
        self._zooming.set_enabled(False)
        self._zooming.set_stopped_value(self._skin['Zooming.Stopped'])
        self._zooming.set_selected_value(self._skin['Zooming.Selected'])
        self._zooming.set_playing_value(self._skin['Zooming.Playing'])
        self._zooming.set_empty_value(self._skin['Zooming.Empty'])
        self._zooming_layer = Layer(button_matrix=self._matrix, zoom_button=self._shift_button, nav_up_button=self._nav_up_button, nav_down_button=self._nav_down_button, nav_left_button=self._nav_left_button, nav_right_button=self._nav_right_button)
        self._session.set_enabled(True)
        self._zooming.set_enabled(True)

    def _init_track_modes(self):
        self._track_modes = ModesComponent(name='Track_Modes')
        self._track_modes.set_enabled(False)
        self._track_modes.add_mode('stop', AddLayerMode(self._session, self._session_stop_track_layer))
        self._track_modes.add_mode('solo', AddLayerMode(self._mixer, self._mixer_solo_layer))
        self._track_modes.add_mode('mute', AddLayerMode(self._mixer, self._mixer_mute_layer))
        self._track_modes.layer = Layer(stop_button=self._global_track_stop_button, mute_button=self._global_mute_button, solo_button=self._global_solo_button, shift_button=self._shift_button)
        self._track_modes.selected_mode = 'mute'

    def _init_main_modes(self):
        enable_stop_mute_solo_as_modifiers = AddLayerMode(self._mod_background, Layer(stop=self._global_track_stop_button, mute=self._global_mute_button, solo=self._global_solo_button))
        self._main_modes = ModesComponent()
        self._main_modes.add_mode('volumes', [self._track_modes, (self._mixer, self._mixer_volume_layer)])
        self._main_modes.add_mode('pan_sends', [self._track_modes, (self._mixer, self._mixer_pan_send_layer)])
        self._main_modes.add_mode('track', [self._track_modes, (self._mixer, self._mixer_track_layer)])
        self._main_modes.add_mode('clip', [self._track_modes,
         partial(self._view_control.show_view, 'Detail/Clip'),
         (self._mixer, self._mixer_layer),
         self._clip_control])
        self._main_modes.add_mode('device', [enable_stop_mute_solo_as_modifiers,
         partial(self._view_control.show_view, 'Detail/DeviceChain'),
         self._device,
         self._device_navigation], behaviour=ReenterBehaviour(self._device_navigation.back_to_top))
        self._main_modes.add_mode('browse', [enable_stop_mute_solo_as_modifiers,
         partial(self._view_control.show_view, 'Browser'),
         self._browser.back_to_top,
         self._browser_hotswap_mode,
         self._browser_mode,
         self._browser.reset_load_memory], groups=['add_effect', 'add_track', 'browse'], behaviour=mixin(DynamicBehaviourMixin, CancellableBehaviour)(lambda : not self._browser_hotswap_mode._mode.can_hotswap() and 'add_effect_left'))
        self._main_modes.add_mode('add_effect_right', [enable_stop_mute_solo_as_modifiers, self._browser.back_to_top, self._create_device_right], behaviour=mixin(ExcludingBehaviourMixin, CancellableBehaviour)(['add_track', 'browse']), groups=['add_effect'])
        self._main_modes.add_mode('add_effect_left', [enable_stop_mute_solo_as_modifiers, self._browser.back_to_top, self._create_device_left], behaviour=mixin(ExcludingBehaviourMixin, CancellableBehaviour)(['add_track', 'browse']), groups=['add_effect'])
        self._main_modes.add_mode('add_instrument_track', [enable_stop_mute_solo_as_modifiers, self._browser.back_to_top, self._create_instrument_track], behaviour=mixin(ExcludingBehaviourMixin, AlternativeBehaviour)(excluded_groups=['browse', 'add_effect'], alternative_mode='add_default_track'), groups=['add_track'])
        self._main_modes.add_mode('add_default_track', [enable_stop_mute_solo_as_modifiers, self._browser.back_to_top, self._create_default_track], groups=['add_track'])
        self._main_modes.selected_mode = 'device'
        self._main_modes.layer = Layer(volumes_button=self._vol_mix_mode_button, pan_sends_button=self._pan_send_mix_mode_button, track_button=self._single_track_mix_mode_button, clip_button=self._clip_mode_button, device_button=self._device_mode_button, browse_button=self._browse_mode_button, add_effect_right_button=self._create_device_button, add_effect_left_button=ComboElement((self._shift_button,), self._create_device_button), add_instrument_track_button=self._create_track_button)
        self._on_main_mode_button_value.replace_subjects([self._vol_mix_mode_button,
         self._pan_send_mix_mode_button,
         self._single_track_mix_mode_button,
         self._clip_mode_button,
         self._device_mode_button,
         self._browse_mode_button])

    @subject_slot_group('value')
    def _on_main_mode_button_value(self, value, sender):
        if value:
            self._instrument._scales_modes.selected_mode = 'disabled'

    def _init_mixer(self):
        self._mixer = SpecialMixerComponent(self._matrix.width())
        self._mixer.set_enabled(False)
        self._mixer.name = 'Mixer'
        self._mixer_layer = Layer(track_names_display=self._display_line4, track_select_buttons=self._select_buttons)
        self._mixer_pan_send_layer = Layer(track_names_display=self._display_line4, track_select_buttons=self._select_buttons, pan_send_toggle=self._pan_send_mix_mode_button, pan_send_controls=self._global_param_controls, pan_send_touch_buttons=self._global_param_touch_buttons, pan_send_names_display=self._display_line1, pan_send_graphics_display=self._display_line2, pan_send_alt_display=self._display_line3)
        self._mixer_volume_layer = Layer(track_names_display=self._display_line4, track_select_buttons=self._select_buttons, volume_controls=self._global_param_controls, volume_touch_buttons=self._global_param_touch_buttons, volume_names_display=self._display_line1, volume_graphics_display=self._display_line2, volume_alt_display=self._display_line3)
        self._mixer_track_layer = Layer(track_names_display=self._display_line4, track_select_buttons=self._select_buttons, selected_controls=self._global_param_controls, track_mix_touch_buttons=self._global_param_touch_buttons, selected_names_display=self._display_line1, selected_graphics_display=self._display_line2, track_mix_alt_display=self._display_line3)
        self._mixer_solo_layer = Layer(solo_buttons=self._track_state_buttons)
        self._mixer_mute_layer = Layer(mute_buttons=self._track_state_buttons)
        self._mixer.layer = self._mixer_layer
        for track in xrange(self._matrix.width()):
            strip = self._mixer.channel_strip(track)
            strip.name = 'Channel_Strip_' + str(track)
            strip.set_invert_mute_feedback(True)
            strip._do_select_track = self._selector.on_select_track
            strip.layer = Layer(shift_button=self._shift_button, delete_button=self._delete_button, duplicate_button=self._duplicate_button, selector_button=self._select_button)

        self._mixer.selected_strip().name = 'Selected_Channel_strip'
        self._mixer.master_strip().name = 'Master_Channel_strip'
        self._mixer.master_strip()._do_select_track = self._selector.on_select_track
        self._mixer.master_strip().layer = Layer(volume_control=self._master_volume_control, cue_volume_control=ComboElement((self._shift_button,), self._master_volume_control), select_button=self._master_select_button, selector_button=self._select_button)
        self._mixer.set_enabled(True)

    def _init_device(self):
        self._device_bank_registry = DeviceBankRegistry()
        self._device = DisplayingDeviceComponent(device_bank_registry=self._device_bank_registry, name='DeviceComponent')
        self._device.set_enabled(False)
        self.set_device_component(self._device)
        self._device.layer = Layer(parameter_controls=self._global_param_controls, encoder_touch_buttons=self._global_param_touch_buttons, name_display_line=self._display_line1, value_display_line=self._display_line2, alternating_display=self._display_line3)
        self._device_navigation = DeviceNavigationComponent(self._device_bank_registry)
        self._device_navigation.set_enabled(False)
        self._device_navigation.layer = Layer(enter_button=self._in_button, delete_button=self._delete_button, exit_button=self._out_button, select_buttons=self._select_buttons, state_buttons=self._track_state_buttons, display_line=self._display_line4)
        self._device_navigation.info_layer = Layer(display_line1=self._display_line1, display_line2=self._display_line2, display_line3=self._display_line3, display_line4=self._display_line4, _notification=self._notification.use_full_display(2))
        self._device_navigation.info_layer.priority = consts.MODAL_DIALOG_PRIORITY

    def _init_transport_and_recording(self):
        self._view_control = ViewControlComponent(name='View_Control')
        self._view_control.set_enabled(False)
        self._view_control.layer = Layer(prev_track_button=self._nav_left_button, next_track_button=self._nav_right_button, prev_scene_button=OptionalElement(self._nav_up_button, self._settings[SETTING_WORKFLOW], False), next_scene_button=OptionalElement(self._nav_down_button, self._settings[SETTING_WORKFLOW], False), prev_scene_list_button=OptionalElement(self._nav_up_button, self._settings[SETTING_WORKFLOW], True), next_scene_list_button=OptionalElement(self._nav_down_button, self._settings[SETTING_WORKFLOW], True))
        self._session_recording = SessionRecordingComponent(self._clip_creator, self._view_control, name='Session_Recording')
        self._session_recording.layer = Layer(new_button=OptionalElement(self._new_button, self._settings[SETTING_WORKFLOW], False), scene_list_new_button=OptionalElement(self._new_button, self._settings[SETTING_WORKFLOW], True), record_button=self._record_button, automation_button=self._automation_button, new_scene_button=ComboElement((self._shift_button,), self._new_button), re_enable_automation_button=ComboElement((self._shift_button,), self._automation_button), delete_automation_button=ComboElement((self._delete_button,), self._automation_button), length_button=self._fixed_length_button)
        self._session_recording.length_layer = Layer(display_line=self._display_line4, label_display_line=self._display_line3, blank_display_line2=self._display_line2, blank_display_line1=self._display_line1, select_buttons=self._select_buttons, state_buttons=self._track_state_buttons, _notification=self._notification.use_single_line(1))
        self._session_recording.length_layer.priority = consts.DIALOG_PRIORITY
        self._transport = SpecialTransportComponent(name='Transport')
        self._transport.layer = Layer(shift_button=self._shift_button, play_button=self._play_button, tap_tempo_button=self._tap_tempo_button, metronome_button=self._metronome_button, quantization_button=self._quantize_button, tempo_encoder=self._tempo_control, undo_button=self._undo_button)
        self._transport.quantization_layer = Layer(encoder_controls=self._global_param_controls, display_line1=self._display_line1, display_line2=self._display_line2, display_line3=self._display_line3, display_line4=self._display_line4, select_buttons=self._select_buttons, state_buttons=self._track_state_buttons)
        self._transport.quantization_layer.priority = consts.DIALOG_PRIORITY

    def _init_clip_settings(self):
        self._clip_control = ClipControlComponent(name='Clip_Control')
        self._clip_control.set_enabled(False)
        self._clip_control.layer = Layer(controls=self._global_param_controls, param_display=self._display_line1, value_display=self._display_line2, clip_name_display=self._display_line3, shift_button=self._shift_button)

    def _init_browser(self):
        self._browser_hotswap_mode = MultiEntryMode(BrowserHotswapMode(application_view=self.application().view))
        self._browser = BrowserComponent(name='Browser')
        self._browser.set_enabled(False)
        self._browser.layer = Layer(encoder_controls=self._global_param_controls, display_line1=self._display_line1, display_line2=self._display_line2, display_line3=self._display_line3, display_line4=self._display_line4, select_buttons=self._select_buttons, state_buttons=self._track_state_buttons, enter_button=self._in_button, exit_button=self._out_button, shift_button=WithPriority(consts.SHARED_PRIORITY, self._shift_button), _notification=self._notification.use_full_display(2))
        self._browser.layer.priority = consts.BROWSER_PRIORITY
        self._browser_mode = MultiEntryMode([SetAttributeMode(self._instrument._scales, 'release_info_display_with_encoders', False), self._browser])
        self._browser_dialog_mode = MultiEntryMode([SetAttributeMode(self._browser.layer, 'priority', consts.MODAL_DIALOG_PRIORITY), self._browser_mode])
        self._create_device_right = CreateDeviceComponent(name='Create_Device_Right', browser_component=self._browser, browser_mode=self._browser_dialog_mode, browser_hotswap_mode=self._browser_hotswap_mode, insert_left=False)
        self._create_device_right.set_enabled(False)
        self._create_device_left = CreateDeviceComponent(name='Create_Device_Right', browser_component=self._browser, browser_mode=self._browser_dialog_mode, browser_hotswap_mode=self._browser_hotswap_mode, insert_left=True)
        self._create_device_left.set_enabled(False)
        self._create_default_track = CreateDefaultTrackComponent(name='Create_Default_Track')
        self._create_default_track.options.layer = Layer(display_line=self._display_line4, label_display_line=self._display_line3, blank_display_line2=self._display_line2, blank_display_line1=self._display_line1, select_buttons=self._select_buttons, state_buttons=self._track_state_buttons)
        self._create_default_track.options.layer.priority = consts.MODAL_DIALOG_PRIORITY
        self._create_default_track.set_enabled(False)
        self._create_instrument_track = CreateInstrumentTrackComponent(name='Create_Instrument_Track', browser_component=self._browser, browser_mode=self._browser_dialog_mode, browser_hotswap_mode=self._browser_hotswap_mode)
        self._create_instrument_track.set_enabled(False)
        self._on_hotswap_target_changed.subject = self.application().browser

    @subject_slot('hotswap_target')
    def _on_hotswap_target_changed(self):
        if not self.application().browser.hotswap_target:
            if self._main_modes.selected_mode == 'browse' or self._browser_hotswap_mode.is_entered:
                self._main_modes.selected_mode = 'device'

    def _init_instrument(self):
        self._instrument = InstrumentComponent(name='Instrument_Component')
        self._instrument.set_enabled(False)
        self._instrument.layer = Layer(matrix=self._matrix, touch_strip=self._touch_strip_control, scales_toggle_button=self._scale_presets_button, presets_toggle_button=self._shift_button, octave_up_button=self._octave_up_button, octave_down_button=self._octave_down_button)
        self._instrument.scales_layer = Layer(top_display_line=self._display_line3, bottom_display_line=self._display_line4, top_buttons=self._select_buttons, bottom_buttons=self._track_state_buttons, encoder_touch_buttons=self._global_param_touch_buttons, _notification=self._notification.use_single_line(1))
        self._instrument.scales_layer.priority = consts.MODAL_DIALOG_PRIORITY
        self._instrument._scales.presets_layer = Layer(top_display_line=self._display_line3, bottom_display_line=self._display_line4, top_buttons=self._select_buttons, bottom_buttons=self._track_state_buttons)
        self._instrument._scales.presets_layer.priority = consts.DIALOG_PRIORITY
        self._instrument._scales.scales_info_layer = Layer(info_line=self._display_line1, blank_line=self._display_line2)
        self._instrument._scales.scales_info_layer.priority = consts.MODAL_DIALOG_PRIORITY

    def _init_step_sequencer(self):
        self._step_sequencer = StepSeqComponent(self._clip_creator, self._c_instance.playhead, self._skin, name='Step_Sequencer')
        self._step_sequencer._drum_group._do_select_drum_pad = self._selector.on_select_drum_pad
        self._step_sequencer._drum_group._do_quantize_pitch = self._transport._quantization.quantize_pitch
        self._step_sequencer.set_enabled(False)
        step_sequencer_matrix = ButtonMatrixElement(name='Step_Buttons')
        for row in xrange(4):
            step_sequencer_matrix.add_row([ self._matrix.get_button(column, row) for column in xrange(8) ])

        step_sequencer_drum_matrix = ButtonMatrixElement(name='Drum_Buttons')
        for row in xrange(4, 8):
            step_sequencer_drum_matrix.add_row([ self._matrix.get_button(column, row) for column in xrange(4) ])

        step_sequencer_bank_matrix = ButtonMatrixElement(name='Bank_Buttons')
        for row in xrange(4, 8):
            step_sequencer_bank_matrix.add_row([ self._matrix.get_button(column, row) for column in xrange(4, 8) ])

        self._step_sequencer.layer = Layer(button_matrix=step_sequencer_matrix, drum_matrix=step_sequencer_drum_matrix, loop_selector_matrix=step_sequencer_bank_matrix, touch_strip=self._touch_strip_control, quantization_buttons=self._side_buttons, mute_button=self._global_mute_button, solo_button=self._global_solo_button, select_button=self._select_button, delete_button=self._delete_button, shift_button=self._shift_button, drum_bank_up_button=self._octave_up_button, drum_bank_down_button=self._octave_down_button, quantize_button=self._quantize_button)
        self._step_sequencer.note_settings_layer = Layer(top_display_line=self._display_line1, bottom_display_line=self._display_line2, clear_display_line1=self._display_line3, clear_display_line2=self._display_line4, encoder_controls=self._global_param_controls, encoder_touch_buttons=self._global_param_touch_buttons, full_velocity_button=self._accent_button)
        self._step_sequencer.note_settings_layer.priority = consts.MODAL_DIALOG_PRIORITY
        self._audio_loop = LoopSelectorComponent(follow_detail_clip=True, measure_length=1.0, name='Loop_Selector')
        self._audio_loop.set_enabled(False)
        self._audio_loop.layer = Layer(loop_selector_matrix=self._matrix)

    def _init_note_repeat(self):
        self._note_repeat = NoteRepeatComponent(self._c_instance.note_repeat, name='Note_Repeat')
        self._note_repeat.set_enabled(False)
        self._note_repeat.layer = Layer(toggle_button=self._repeat_button)
        self._note_repeat.options_layer = Layer(select_buttons=self._side_buttons)
        self._note_repeat.options_layer.priority = consts.DIALOG_PRIORITY
        self._on_note_repeat_mode_changed.subject = self._note_repeat

    def _init_message_box(self):
        self._notification = NotificationComponent(display_lines=self._display_lines)
        self._notification.set_enabled(True)
        self._dialog = DialogComponent()
        self._dialog.message_box_layer = Layer(display_line1=self._display_line1, display_line2=self._display_line2, display_line3=self._display_line3, display_line4=self._display_line4, top_buttons=self._select_buttons, bottom_buttons=self._track_state_buttons, scales_button=self._scale_presets_button, octave_up=self._octave_up_button, octave_down=self._octave_down_button, side_buttons=self._side_buttons, repeat_button=self._repeat_button, accent_button=self._accent_button, in_button=self._in_button, out_button=self._out_button, param_controls=self._global_param_controls, param_touch=self._global_param_touch_buttons, tempo_control_tap=self._tempo_control_tap, master_control_tap=self._master_volume_control_tap, touch_strip=self._touch_strip_control, touch_strip_tap=self._touch_strip_tap, matrix=self._matrix, nav_up_button=self._nav_up_button, nav_down_button=self._nav_down_button, nav_left_button=self._nav_left_button, nav_right_button=self._nav_right_button, shift_button=self._shift_button, select_button=self._select_button, delete_button=self._delete_button, duplicate_button=self._duplicate_button, double_button=self._double_button, quantize_button=self._quantize_button, play_button=self._play_button, new_button=self._new_button, automation_button=self._automation_button, tap_tempo_button=self._tap_tempo_button, metronome_button=self._metronome_button, fixed_length_button=self._fixed_length_button, record_button=self._record_button, undo_button=self._undo_button, tempo_control=self._tempo_control, swing_control=self._swing_control, master_volume_control=self._master_volume_control, global_param_controls=self._global_param_controls, swing_control_tap=self._swing_control_tap, master_volume_tap=self._master_volume_control_tap, global_param_tap=self._global_param_touch_buttons, volumes_button=self._vol_mix_mode_button, pan_sends_button=self._pan_send_mix_mode_button, track_button=self._single_track_mix_mode_button, clip_button=self._clip_mode_button, device_button=self._device_mode_button, browse_button=self._browse_mode_button, user_button=self._user_button, master_select_button=self._master_select_button, create_device_button=self._create_device_button, create_track_button=self._create_track_button, global_track_stop_button=self._global_track_stop_button, global_mute_button=self._global_mute_button, global_solo_button=self._global_solo_button, note_mode_button=self._note_mode_button, session_mode_button=self._session_mode_button)
        self._dialog.message_box_layer.priority = consts.MESSAGE_BOX_PRIORITY
        self._dialog.set_enabled(True)

    def _init_global_actions(self):
        self._capture_and_insert_scene = CaptureAndInsertSceneComponent(name='Capture_And_Insert_Scene')
        self._capture_and_insert_scene.set_enabled(True)
        self._capture_and_insert_scene.layer = Layer(action_button=self._duplicate_button)
        self._duplicate_loop = DuplicateLoopComponent(name='Duplicate_Loop')
        self._duplicate_loop.layer = Layer(action_button=self._double_button)
        self._duplicate_loop.set_enabled(True)
        self._selector = SelectComponent(name='Selector')
        self._selector.layer = Layer(select_button=self._select_button)
        self._selector.selection_display_layer = Layer(display_line=self._display_line3)
        self._selector.selection_display_layer.priority = consts.DIALOG_PRIORITY
        self._swing_amount = ValueComponent('swing_amount', self.song(), display_label='Swing Amount:', display_format='%d%%', model_transform=lambda x: clamp(x / 200.0, 0.0, 0.5), view_transform=lambda x: x * 200.0, encoder_factor=100.0, encoder=self._swing_control)
        self._swing_amount.layer = Layer(button=self._swing_control_tap, encoder=self._swing_control)
        self._swing_amount.display_layer = Layer(label_display=self._display_line1, value_display=self._display_line3, graphic_display=self._display_line2, clear_display1=self._display_line4)
        self._swing_amount.display_layer.priority = consts.DIALOG_PRIORITY
        self._tempo = ValueComponent('tempo', self.song(), display_label='Tempo:', display_format='%0.2f BPM', encoder=self._tempo_control)
        self._tempo.layer = Layer(button=self._tempo_control_tap)
        self._tempo.display_layer = Layer(label_display=self._display_line1, value_display=self._display_line2, clear_display1=self._display_line3, clear_display2=self._display_line4)
        self._tempo.display_layer.priority = consts.DIALOG_PRIORITY
        self._master_vol = ParameterValueComponent(self.song().master_track.mixer_device.volume, display_label='Master Volume:', display_seg_start=3, name='Master_Volume_Display', encoder=self._master_volume_control)
        self._master_vol.layer = Layer(button=self._master_volume_control_tap)
        self._master_vol.display_layer = Layer(label_display=self._display_line1, value_display=self._display_line3, graphic_display=self._display_line2, clear_display2=self._display_line4)
        self._master_vol.display_layer.priority = consts.DIALOG_PRIORITY
        self._master_cue_vol = ParameterValueComponent(self.song().master_track.mixer_device.cue_volume, display_label='Cue Volume:', display_seg_start=3, name='Cue_Volume_Display', encoder=ComboElement((self._shift_button,), self._master_volume_control))
        self._master_cue_vol.layer = Layer(button=ComboElement((self._shift_button,), self._master_volume_control_tap))
        self._master_cue_vol.display_layer = Layer(label_display=self._display_line1, value_display=self._display_line3, graphic_display=self._display_line2, clear_display2=self._display_line4)
        self._master_cue_vol.display_layer.priority = consts.DIALOG_PRIORITY
        self._value_components = [self._swing_amount,
         self._tempo,
         self._master_vol,
         self._master_cue_vol]
        self._delete_component = DeleteComponent(name='Deleter')
        self._delete_component.layer = Layer(delete_button=self._delete_button)
        self._delete_clip = DeleteSelectedClipComponent(name='Selected_Clip_Deleter')
        self._delete_clip.layer = Layer(action_button=self._delete_button)
        self._delete_scene = DeleteSelectedSceneComponent(name='Selected_Scene_Deleter')
        self._delete_scene.layer = Layer(action_button=ComboElement((self._shift_button,), self._delete_button))

    def _init_m4l_interface(self):
        self._m4l_interface = M4LInterfaceComponent(self.controls)
        self.get_control_names = self._m4l_interface.get_control_names
        self.get_control = self._m4l_interface.get_control
        self.grab_control = self._m4l_interface.grab_control
        self.release_control = self._m4l_interface.release_control

    def _on_selected_track_changed(self):
        super(Push, self)._on_selected_track_changed()
        self.set_controlled_track(self.song().view.selected_track)
        self._on_devices_changed.subject = self.song().view.selected_track
        self._select_note_mode()
        self._main_modes.pop_groups(['add_effect'])
        self._note_repeat.selected_mode = 'disabled'

    def _send_midi(self, midi_event_bytes, optimized = True):
        if not self._suppress_sysex or not self.is_sysex_message(midi_event_bytes):
            return super(Push, self)._send_midi(midi_event_bytes, optimized)

    @subject_slot('devices')
    def _on_devices_changed(self):
        self._select_note_mode()

    @subject_slot('session_record')
    def _on_session_record_changed(self):
        status = self.song().session_record
        playhead_color = int(self._skin['NoteEditor.PlayheadRecord'] if status else self._skin['NoteEditor.Playhead'])
        feedback_color = int(self._skin['Instrument.FeedbackRecord'] if status else self._skin['Instrument.Feedback'])
        self._c_instance.playhead.velocity = playhead_color
        self._c_instance.set_feedback_velocity(feedback_color)

    @subject_slot('selected_mode')
    def _on_note_repeat_mode_changed(self, mode_name):
        aftertouch_mode = 0 if mode_name == 'enabled' else 1
        self._send_midi(Sysex.SET_AFTERTOUCH_MODE + (aftertouch_mode, 247))

    @subject_slot('selected_mode')
    def _on_accent_mode_changed(self, mode_name):
        accent_is_active = mode_name == 'enabled'
        self._step_sequencer.set_full_velocity(accent_is_active)

    @subject_slot('value')
    def _on_pad_threshold(self, setting):
        self._user.set_settings_info_text('' if setting.value >= consts.CRITICAL_THRESHOLD_LIMIT else consts.MessageBoxText.STUCK_PAD_WARNING)
        new_pad_paramteres = self._create_pad_parameters(self._settings[SETTING_CURVE].value, setting.value)
        self._instrument_pad_sensitivity.parameters = new_pad_paramteres
        self._drum_pad_sensitivity.parameters = new_pad_paramteres

    @subject_slot('value')
    def _on_pad_curve(self, setting):
        new_pad_paramteres = self._create_pad_parameters(setting.value, self._settings[SETTING_THRESHOLD].value)
        self._instrument_pad_sensitivity.parameters = new_pad_paramteres
        self._drum_pad_sensitivity.parameters = new_pad_paramteres

    def _create_pad_parameters(self, curve_params, threshold):
        import copy
        params = copy.copy(curve_params)
        threshold_range = consts.MAX_THRESHOLD_STEP - consts.MIN_THRESHOLD_STEP
        t = float(threshold - consts.MIN_THRESHOLD_STEP) / float(threshold_range)
        params.on_threshold = int((1 - t) * consts.MIN_ON_THRESHOLD + t * consts.MAX_ON_THRESHOLD)
        params.off_threshold = int((1 - t) * consts.MIN_OFF_THRESHOLD + t * consts.MAX_OFF_THRESHOLD)
        return params

    @subject_slot('before_mode_sent')
    def _on_before_hardware_mode_sent(self, mode):
        self._suppress_sysex = False

    @subject_slot('after_mode_sent')
    def _on_after_hardware_mode_sent(self, mode):
        if mode == Sysex.USER_MODE:
            self._suppress_sysex = True

    @subject_slot('mode')
    def _on_hardware_mode_changed(self, mode):
        if mode == Sysex.LIVE_MODE:
            self.update()
        elif mode == Sysex.USER_MODE:
            self._suppress_sysex = True
        self._update_auto_arm()

    @subject_slot('selected_mode')
    def _on_matrix_mode_changed(self, mode):
        self._update_auto_arm(selected_mode=mode)

    def _update_auto_arm(self, selected_mode = None):
        self._auto_arm.set_enabled(self._user.mode == Sysex.LIVE_MODE and (selected_mode or self._matrix_modes.selected_mode == 'note'))

    def _select_note_mode(self):
        """
        Selects which note mode to use depending on the kind of
        current selected track and its device chain...
        """
        track = self.song().view.selected_track
        drum_device = find_if(lambda d: d.can_have_drum_pads, track.devices)
        self._step_sequencer.set_drum_group_device(drum_device)
        if track == None or track.is_foldable or track in self.song().return_tracks or track == self.song().master_track:
            self._note_modes.selected_mode = 'disabled'
        elif track and track.has_audio_input:
            self._note_modes.selected_mode = 'looper'
        elif drum_device:
            self._note_modes.selected_mode = 'sequencer'
        else:
            self._note_modes.selected_mode = 'instrument'

    def _on_toggle_encoder(self, value):
        pass

    @subject_slot_group('value')
    def _on_param_encoder_touched(self, value, encoder):
        """
        When using the parameter encoders, other encoders around it are often accidentally
        touched and will take over the screen. By putting all ValueComponents into timer
        based displaying mode while touching a parameter, this noise is prevented.
        """
        param_encoder_touched = find_if(lambda encoder: encoder.is_pressed(), self._global_param_touch_buttons) != None
        new_display_mode = ValueComponent.TIMER_BASED if param_encoder_touched else ValueComponent.TOUCH_BASED
        for value_component in self._value_components:
            value_component.display_mode = new_display_mode

    def expect_dialog(self, message):
        self.schedule_message(1, partial(self._dialog.expect_dialog, message))

    def show_notification(self, message):
        self._notification.show_notification(message)

    def handle_nonsysex(self, midi_bytes):
        status, _, value = midi_bytes
        if (status & MIDI_CC_STATUS or status & MIDI_NOTE_ON_STATUS) and value != 0:
            self._notification.hide_notification()
        super(Push, self).handle_nonsysex(midi_bytes)