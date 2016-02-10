#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/push_base.py
from __future__ import absolute_import, print_function
from contextlib import contextmanager
from functools import partial
from itertools import imap
from ableton.v2.base import inject, clamp, nop, const, NamedTuple, listens, listens_group
from ableton.v2.control_surface import BackgroundLayer, ClipCreator, ControlSurface, DeviceBankRegistry, Layer, midi
from ableton.v2.control_surface.components import BackgroundComponent, M4LInterfaceComponent, ModifierBackgroundComponent, SessionNavigationComponent, SessionRingComponent, SessionOverviewComponent, ViewControlComponent
from ableton.v2.control_surface.elements import adjust_string, ButtonElement, ButtonMatrixElement, ChoosingElement, ComboElement, DoublePressContext, MultiElement, OptionalElement, to_midi_value
from ableton.v2.control_surface.mode import AddLayerMode, LayerMode, LazyComponentMode, ReenterBehaviour, ModesComponent, EnablingModesComponent
from .accent_component import AccentComponent
from .actions import CaptureAndInsertSceneComponent, DeleteAndReturnToDefaultComponent, DeleteComponent, DeleteSelectedClipComponent, DeleteSelectedSceneComponent, DuplicateDetailClipComponent, DuplicateLoopComponent, UndoRedoComponent
from .auto_arm_component import AutoArmComponent
from .automation_component import AutomationComponent
from .banking_util import BankingInfo
from .clip_control_component import ClipControlComponent
from .device_parameter_component import DeviceParameterComponent
from .grid_resolution import GridResolution
from .fixed_length import FixedLengthComponent, FixedLengthSettingComponent, FixedLengthSetting, DEFAULT_LENGTH_OPTION_INDEX
from .instrument_component import NoteLayout
from .loop_selector_component import LoopSelectorComponent
from .matrix_maps import FEEDBACK_CHANNELS
from .melodic_component import MelodicComponent
from .message_box_component import DialogComponent, InfoComponent
from .note_editor_component import DEFAULT_VELOCITY_RANGE_THRESHOLDS
from .note_repeat_component import NoteRepeatComponent
from .note_settings_component import NoteEditorSettingsComponent
from .selected_track_parameter_provider import SelectedTrackParameterProvider
from .selection import PushSelection
from .select_playing_clip_component import SelectPlayingClipComponent
from .skin_default import make_default_skin
from .sliced_simpler_component import SlicedSimplerComponent
from .special_session_component import SpecialSessionComponent
from .step_seq_component import StepSeqComponent
from .percussion_instrument_finder_component import PercussionInstrumentFinderComponent
from .touch_strip_controller import TouchStripControllerComponent, TouchStripEncoderConnection, TouchStripPitchModComponent
from .track_frozen_mode import TrackFrozenModesComponent
from .transport_component import TransportComponent
from .value_component import ValueComponent, ParameterValueComponent
from . import consts
from . import sysex
NUM_TRACKS = 8
NUM_SCENES = 8
TEMPO_SWING_TOUCH_DELAY = 0.4

def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)


class PushBase(ControlSurface):
    preferences_key = 'Push'
    session_component_type = SpecialSessionComponent
    drum_group_note_editor_skin = 'NoteEditor'
    note_editor_velocity_range_thresholds = DEFAULT_VELOCITY_RANGE_THRESHOLDS
    device_component_class = None
    bank_definitions = None
    note_editor_class = None

    def __init__(self, *a, **k):
        super(PushBase, self).__init__(*a, **k)
        self.register_slot(self.song.view, self._on_selected_track_changed, 'selected_track')
        self._device_decorator_factory = self._create_device_decorator_factory()
        self.register_disconnectable(self._device_decorator_factory)
        self._double_press_context = DoublePressContext()
        injecting = self._create_injector()
        self._push_injector = injecting.everywhere()
        self._element_injector = inject(element_container=const(None)).everywhere()
        with self.component_guard():
            self._suppress_sysex = False
            self._skin = self._create_skin()
            self._clip_creator = ClipCreator()
            self._note_editor_settings = []
            self._notification = None
            self._user = None
            with inject(skin=const(self._skin)).everywhere():
                self._create_controls()
        self._element_injector = inject(element_container=const(self.elements)).everywhere()

    def initialize(self):
        self._setup_accidental_touch_prevention()
        self._create_components()
        self._init_main_modes()
        self._on_selected_track_changed()
        self.__on_session_record_changed.subject = self.song
        self.__on_session_record_changed()
        self.__on_selected_track_is_frozen_changed.subject = self.song.view
        self.set_feedback_channels(FEEDBACK_CHANNELS)

    def disconnect(self):
        if self._user is not None:
            with self.component_guard():
                self._user.mode = sysex.USER_MODE
        super(PushBase, self).disconnect()

    @contextmanager
    def _component_guard(self):
        with super(PushBase, self)._component_guard():
            with self._push_injector:
                with self._element_injector:
                    song_view = self.song.view
                    old_selected_track = song_view.selected_track
                    yield
                    if song_view.selected_track != old_selected_track:
                        self._track_selection_changed_by_action()

    def _create_device_decorator_factory(self):
        raise NotImplementedError

    def _create_components(self):
        self._init_settings()
        self._init_notification()
        self._init_message_box()
        self._init_background()
        self._init_user()
        self._init_touch_strip_controller()
        self._init_accent()
        self._init_track_frozen()
        self._init_undo_redo_actions()
        self._init_duplicate_actions()
        self._init_delete_actions()
        self._init_quantize_actions()
        self._init_session_ring()
        self._init_fixed_length()
        self._init_transport_and_recording()
        self._init_stop_clips_action()
        self._init_value_components()
        self._init_track_list()
        self._init_mixer()
        self._init_track_mixer()
        self._init_session()
        self._init_grid_resolution()
        self._init_drum_component()
        self._init_slicing_component()
        self._init_automation_component()
        self._init_note_settings_component()
        self._init_note_editor_settings_component()
        self._init_step_sequencer()
        self._init_instrument()
        self._init_scales()
        self._init_note_repeat()
        self._init_matrix_modes()
        self._init_device()
        self._init_m4l_interface()

    def _create_injector(self):
        return inject(double_press_context=const(self._double_press_context), expect_dialog=const(self.expect_dialog), show_notification=const(self.show_notification), selection=lambda : PushSelection(application=self.application(), device_component=self._device_component, navigation_component=self._device_navigation))

    def _create_skin(self):
        return make_default_skin()

    def _needs_to_deactivate_session_recording(self):
        return self._matrix_modes.selected_mode == 'note' and self.song.exclusive_arm

    def _track_selection_changed_by_action(self):
        if self._needs_to_deactivate_session_recording():
            self._session_recording.deactivate_recording()
        if self._auto_arm.needs_restore_auto_arm:
            self._auto_arm.restore_auto_arm()

    def port_settings_changed(self):
        self._switch_to_live_mode()

    def _switch_to_live_mode(self):
        self._user.mode = sysex.LIVE_MODE
        self._user.force_send_mode()

    def _init_settings(self):
        self._settings = self._create_settings()

    def _create_settings(self):
        raise RuntimeError

    def update(self):
        self.__on_session_record_changed()
        self.reset_controlled_track()
        self.set_feedback_channels(FEEDBACK_CHANNELS)
        super(PushBase, self).update()

    def _create_controls(self):
        raise NotImplementedError

    def _with_shift(self, button):
        return ComboElement(button, modifier='shift_button')

    def _with_firmware_version(self, major_version, minor_version, control_element):
        raise NotImplementedError

    def _init_background(self):
        self._background = BackgroundComponent(is_root=True)
        self._background.layer = self._create_background_layer()
        self._matrix_background = BackgroundComponent()
        self._matrix_background.set_enabled(False)
        self._matrix_background.layer = Layer(matrix='matrix')
        self._mod_background = ModifierBackgroundComponent(is_root=True)
        self._mod_background.layer = Layer(shift_button='shift_button', select_button='select_button', delete_button='delete_button', duplicate_button='duplicate_button', quantize_button='quantize_button')

    def _create_background_layer(self):
        return Layer(top_buttons='select_buttons', bottom_buttons='track_state_buttons', scales_button='scale_presets_button', octave_up='octave_up_button', octave_down='octave_down_button', side_buttons='side_buttons', repeat_button='repeat_button', accent_button='accent_button', double_button='double_button', param_controls='global_param_controls', param_touch='global_param_touch_buttons', touch_strip='touch_strip_control', nav_up_button='nav_up_button', nav_down_button='nav_down_button', nav_left_button='nav_left_button', nav_right_button='nav_right_button', aftertouch='aftertouch_control', _notification=self._notification.use_single_line(2), priority=consts.BACKGROUND_PRIORITY)

    def _init_track_list(self):
        pass

    def _can_auto_arm_track(self, track):
        routing = track.current_input_routing
        return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith(self.input_target_name_for_auto_arm)

    def _init_touch_strip_controller(self):
        strip_controller = TouchStripControllerComponent()
        strip_controller.set_enabled(False)
        strip_controller.layer = Layer(touch_strip='touch_strip_control')
        strip_controller.layer.priority = consts.DIALOG_PRIORITY
        self._strip_connection = TouchStripEncoderConnection(strip_controller, self.elements.touch_strip_tap, is_root=True)
        self.elements.tempo_control.set_observer(self._strip_connection)
        self.elements.swing_control.set_observer(self._strip_connection)
        self.elements.master_volume_control.set_observer(self._strip_connection)
        for encoder in self.elements.global_param_controls.nested_control_elements():
            encoder.set_observer(self._strip_connection)

        self._pitch_mod_touch_strip = TouchStripPitchModComponent()
        self._pitch_mod_touch_strip_layer = Layer(touch_strip='touch_strip_control', touch_strip_indication=self._with_firmware_version(1, 16, ComboElement('touch_strip_control', modifier='select_button')), touch_strip_toggle=self._with_firmware_version(1, 16, ComboElement('touch_strip_tap', modifier='select_button')))

    def _create_session_mode(self):
        raise NotImplementedError

    def _create_slicing_modes(self):
        slicing_modes = ModesComponent(name='Slicing_Modes', is_enabled=False)
        slicing_modes.add_mode('64pads', [AddLayerMode(self._slicing_component, Layer(matrix='matrix')), LayerMode(self._pitch_mod_touch_strip, self._pitch_mod_touch_strip_layer)])
        slicing_modes.add_mode('sequencer', [self._slice_step_sequencer, self._note_editor_settings_component, AddLayerMode(self._slicing_component, Layer(matrix=self.elements.matrix.submatrix[:4, 4:8], page_strip='touch_strip_control', scroll_strip=self._with_shift('touch_strip_control')))])
        slicing_modes.selected_mode = '64pads'
        return slicing_modes

    def _init_matrix_modes(self):
        self._auto_arm = AutoArmComponent(name='Auto_Arm')
        self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
        self._auto_arm.layer = Layer(_notification=self._notification.use_single_line(2))
        self._select_playing_clip = SelectPlayingClipComponent(name='Select_Playing_Clip', playing_clip_above_layer=Layer(action_button='nav_up_button'), playing_clip_below_layer=Layer(action_button='nav_down_button'))
        self._select_playing_clip.layer = Layer(_notification=self._notification.use_single_line(2))
        self._percussion_instrument_finder = PercussionInstrumentFinderComponent(device_parent=self.song.view.selected_track)
        self.__on_percussion_instrument_changed.subject = self._percussion_instrument_finder
        self._drum_modes = ModesComponent(name='Drum_Modes', is_enabled=False)
        self._drum_modes.add_mode('sequencer', [self._drum_step_sequencer, self._note_editor_settings_component, AddLayerMode(self._drum_component, Layer(matrix=self.elements.matrix.submatrix[:4, 4:8]))])
        self._drum_modes.add_mode('64pads', [AddLayerMode(self._drum_component, Layer(matrix='matrix'))])
        self._drum_modes.selected_mode = 'sequencer'
        self._slicing_modes = self._create_slicing_modes()
        self._note_modes = ModesComponent(name='Note_Modes')
        self._note_modes.add_mode('drums', [self._drum_component,
         self._note_repeat_enabler,
         self._accent_component,
         self._drum_modes])
        self._note_modes.add_mode('slicing', [self._slicing_component,
         self._note_repeat_enabler,
         self._accent_component,
         self._slicing_modes])
        self._note_modes.add_mode('looper', self._audio_loop if consts.PROTO_AUDIO_NOTE_MODE else self._matrix_background)
        self._note_modes.add_mode('instrument', [self._note_repeat_enabler,
         self._accent_component,
         self._instrument,
         self._scales_enabler])
        self._note_modes.add_mode('disabled', self._matrix_background)
        self._note_modes.selected_mode = 'disabled'
        self._note_modes.set_enabled(False)
        self._matrix_modes = ModesComponent(name='Matrix_Modes', is_root=True)
        self._matrix_modes.add_mode('session', self._create_session_mode())
        self._matrix_modes.add_mode('note', self._create_note_mode(), behaviour=self._create_note_mode_behaviour())
        self._matrix_modes.selected_mode = 'note'
        self._matrix_modes.layer = Layer(session_button='session_mode_button', note_button='note_mode_button')
        self.__on_matrix_mode_changed.subject = self._matrix_modes
        self._matrix_modes.selected_mode = 'note'

    def _switch_note_mode_layout(self):
        cyclable_mode = {'instrument': self._instrument,
         'drums': self._drum_modes,
         'slicing': self._slicing_modes}.get(self._note_modes.selected_mode, None)
        getattr(cyclable_mode, 'cycle_mode', nop)()

    def _create_note_mode(self):
        return [self._percussion_instrument_finder,
         self._view_control,
         self._note_modes,
         self._delete_clip,
         self._select_playing_clip]

    def _create_note_mode_behaviour(self):
        raise NotImplementedError

    def _init_accent(self):
        self._accent_component = AccentComponent()
        self._accent_component.set_full_velocity(self._c_instance.full_velocity)
        self._accent_component.set_enabled(False)
        self._accent_component.layer = Layer(cycle_mode_button='accent_button')
        self.__on_accent_mode_changed.subject = self._accent_component

    def _create_user_component(self):
        raise NotImplementedError

    def _init_user(self):
        self._user = self._create_user_component()
        self.__on_hardware_mode_changed.subject = self._user
        self.__on_before_hardware_mode_sent.subject = self._user
        self.__on_after_hardware_mode_sent.subject = self._user

    def _create_session_layer(self):
        return Layer(clip_launch_buttons='matrix', scene_launch_buttons='side_buttons', duplicate_button='duplicate_button', touch_strip='touch_strip_control')

    def _set_session_skin(self, session):
        pass

    def _create_session(self):
        session = self.session_component_type(session_ring=self._session_ring, enable_skinning=True, is_enabled=False, auto_name=True, layer=self._create_session_layer())
        self._set_session_skin(session)
        for scene_index in xrange(8):
            scene = session.scene(scene_index)
            scene.layer = Layer(select_button='select_button', delete_button='delete_button')
            scene._do_select_scene = self.on_select_scene
            for track_index in xrange(8):
                clip_slot = scene.clip_slot(track_index)
                clip_slot._do_select_clip = self.on_select_clip_slot
                clip_slot.layer = Layer(delete_button='delete_button', select_button='select_button', duplicate_button='duplicate_button')

        session.duplicate_layer = Layer(scene_buttons='side_buttons')
        return session

    def on_select_clip_slot(self, clip_slot):
        """
        Called when a clip slot is selected from Push. Override to create specific
        behaviour.
        """
        pass

    def on_select_scene(self, scene):
        """
        Called when a scene is selected from Push. Override to create specific behaviour.
        """
        pass

    def on_select_track(self, track):
        """
        Called when a track is selected from Push's channel strip components. Override
        to create specific behaviour.
        """
        pass

    def _create_session_overview(self):
        return SessionOverviewComponent(session_ring=self._session_ring, name='Session_Overview', enable_skinning=True, is_enabled=False, layer=self._create_session_overview_layer())

    def _create_session_overview_layer(self):
        raise NotImplementedError

    def _init_session_ring(self):
        self._session_ring = SessionRingComponent(num_tracks=NUM_TRACKS, num_scenes=NUM_SCENES, tracks_to_use=partial(tracks_to_use_from_song, self.song), is_enabled=True, is_root=True)

    def _init_session(self):
        self._session_mode = LazyComponentMode(self._create_session)
        self._session_overview_mode = LazyComponentMode(self._create_session_overview)
        self._session_navigation = SessionNavigationComponent(session_ring=self._session_ring, is_enabled=False, layer=self._create_session_navigation_layer())

    def _create_session_navigation_layer(self):
        return Layer(left_button='nav_left_button', right_button='nav_right_button', up_button='nav_up_button', down_button='nav_down_button', page_left_button=self._with_shift('nav_left_button'), page_right_button=self._with_shift('nav_right_button'), page_up_button=MultiElement('octave_up_button', self._with_shift('nav_up_button')), page_down_button=MultiElement('octave_down_button', self._with_shift('nav_down_button')))

    def _create_track_modes_layer(self):
        return Layer(stop_button='global_track_stop_button', mute_button='global_mute_button', solo_button='global_solo_button')

    def _when_track_is_not_frozen(self, *modes):
        return TrackFrozenModesComponent(default_mode=[modes], frozen_mode=self._track_frozen_info, is_enabled=False)

    def _create_device_mode(self):
        raise NotImplementedError

    def _create_main_mixer_modes(self):
        self._main_modes.add_mode('volumes', [self._track_modes, (self._mixer, self._mixer_volume_layer), self._track_note_editor_mode])
        self._main_modes.add_mode('pan_sends', [self._track_modes, (self._mixer, self._mixer_pan_send_layer), self._track_note_editor_mode])
        self._main_modes.add_mode('track', [self._track_modes,
         self._track_mixer,
         (self._mixer, self._mixer_track_layer),
         self._track_note_editor_mode])

    def _create_clip_mode(self):
        return [self._when_track_is_not_frozen(partial(self._view_control.show_view, 'Detail/Clip'), LazyComponentMode(self._create_clip_control))]

    def _init_main_modes(self):

        def configure_note_editor_settings(parameter_provider, mode):
            for note_editor_setting in self._note_editor_settings:
                note_editor_setting.component.parameter_provider = parameter_provider
                note_editor_setting.component.automation_layer = getattr(note_editor_setting, mode + '_automation_layer')

        self._track_note_editor_mode = partial(configure_note_editor_settings, self._track_parameter_provider, 'track')
        self._device_note_editor_mode = partial(configure_note_editor_settings, self._device_component, 'device')
        self._enable_stop_mute_solo_as_modifiers = AddLayerMode(self._mod_background, Layer(stop='global_track_stop_button', mute='global_mute_button', solo='global_solo_button'))
        self._main_modes = ModesComponent(is_root=True)
        self._create_main_mixer_modes()
        self._main_modes.add_mode('clip', self._create_clip_mode())
        self._main_modes.add_mode('device', self._create_device_mode(), behaviour=ReenterBehaviour(self._device_navigation.back_to_top))
        self._init_browse_mode()
        self._main_modes.selected_mode = 'device'
        self._main_modes.layer = self._create_main_modes_layer()

    def _init_browse_mode(self):
        raise NotImplementedError

    def _create_main_modes_layer(self):
        return Layer(volumes_button='vol_mix_mode_button', pan_sends_button='pan_send_mix_mode_button', track_button='single_track_mix_mode_button', clip_button='clip_mode_button', device_button='device_mode_button', browse_button='browse_mode_button', add_effect_right_button='create_device_button', add_effect_left_button=self._with_shift('create_device_button'), add_instrument_track_button='create_track_button')

    def _init_track_frozen(self):
        self._track_frozen_info = InfoComponent(info_text=consts.MessageBoxText.TRACK_FROZEN_INFO, is_enabled=False, layer=self._create_track_frozen_layer())

    def _create_track_frozen_layer(self):
        return Layer()

    def _init_mixer(self):
        pass

    def _init_track_mixer(self):
        self._track_parameter_provider = self.register_disconnectable(SelectedTrackParameterProvider())
        self._track_mixer = DeviceParameterComponent(parameter_provider=self._track_parameter_provider, is_enabled=False, layer=self._create_track_mixer_layer())

    def _create_track_mixer_layer(self):
        return Layer(parameter_controls='fine_grain_param_controls')

    def _create_device_component(self):
        return self.device_component_class(device_decorator_factory=self._device_decorator_factory, device_bank_registry=self._device_bank_registry, banking_info=self._banking_info, name='DeviceComponent', is_enabled=True, is_root=True)

    def _create_device_parameter_component(self):
        return DeviceParameterComponent(parameter_provider=self._device_component, is_enabled=False, layer=self._create_device_parameter_layer())

    def _create_device_parameter_layer(self):
        return Layer(parameter_controls='fine_grain_param_controls')

    def _create_device_navigation(self):
        raise NotImplementedError

    def _init_device(self):
        self._device_bank_registry = DeviceBankRegistry()
        self._banking_info = BankingInfo(self.bank_definitions)
        self._device_component = self._create_device_component()
        self._device_parameter_component = self._create_device_parameter_component()
        self._device_navigation = self._create_device_navigation()

    def _create_view_control_component(self):
        return ViewControlComponent(name='View_Control')

    def _init_fixed_length(self):
        self._fixed_length_setting = FixedLengthSetting()
        self._fixed_length_setting.enabled = self.preferences.setdefault('fixed_length_enabled', False)
        self._fixed_length_setting.selected_index = self.preferences.setdefault('fixed_length_option', DEFAULT_LENGTH_OPTION_INDEX)
        self.__on_fixed_length_enabled_changed.subject = self._fixed_length_setting
        self.__on_fixed_length_selected_index_changed.subject = self._fixed_length_setting
        self._fixed_length_settings_component = FixedLengthSettingComponent(fixed_length_setting=self._fixed_length_setting, is_enabled=False)
        self._fixed_length = FixedLengthComponent(settings_component=self._fixed_length_settings_component, fixed_length_setting=self._fixed_length_setting)
        self._fixed_length.layer = Layer(fixed_length_toggle_button='fixed_length_button')

    def _create_session_recording(self):
        raise NotImplementedError

    def _init_transport_and_recording(self):
        self._view_control = self._create_view_control_component()
        self._view_control.set_enabled(False)
        self._view_control.layer = Layer(prev_track_button='nav_left_button', next_track_button='nav_right_button', prev_scene_button=OptionalElement('nav_up_button', self._settings['workflow'], False), next_scene_button=OptionalElement('nav_down_button', self._settings['workflow'], False), prev_scene_list_button=OptionalElement('nav_up_button', self._settings['workflow'], True), next_scene_list_button=OptionalElement('nav_down_button', self._settings['workflow'], True))
        self._session_recording = self._create_session_recording()
        new_button = MultiElement(self.elements.new_button, self.elements.foot_pedal_button.double_press)
        self._session_recording.layer = Layer(new_button=OptionalElement(new_button, self._settings['workflow'], False), scene_list_new_button=OptionalElement(new_button, self._settings['workflow'], True), record_button='record_button', arrangement_record_button=self._with_shift('record_button'), automation_button='automation_button', new_scene_button=self._with_shift('new_button'), re_enable_automation_button=self._with_shift('automation_button'), delete_automation_button=ComboElement('automation_button', 'delete_button'), foot_switch_button=self.elements.foot_pedal_button.single_press, _uses_foot_pedal='foot_pedal_button')
        self._transport = TransportComponent(name='Transport', is_root=True)
        self._transport.layer = Layer(play_button='play_button', stop_button=self._with_shift('play_button'), tap_tempo_button='tap_tempo_button', metronome_button='metronome_button')

    def _create_clip_control(self):
        return ClipControlComponent(loop_layer=self._create_clip_loop_layer(), audio_layer=self._create_clip_audio_layer(), clip_name_layer=self._create_clip_name_layer(), name='Clip_Control', is_enabled=False)

    def _create_clip_loop_layer(self):
        return Layer(encoders=self.elements.global_param_controls.submatrix[:4, :], shift_button='shift_button')

    def _create_clip_audio_layer(self):
        return Layer(warp_mode_encoder='parameter_controls_raw[4]', transpose_encoder='parameter_controls_raw[5]', detune_encoder='parameter_controls_raw[6]', gain_encoder='parameter_controls_raw[7]', shift_button='shift_button')

    def _create_clip_name_layer(self):
        return Layer()

    def _init_grid_resolution(self):
        self._grid_resolution = self.register_disconnectable(GridResolution())

    def _init_note_settings_component(self):
        raise NotImplementedError

    def _init_automation_component(self):
        self._automation_component = AutomationComponent()

    def _init_note_editor_settings_component(self):
        self._note_editor_settings_component = NoteEditorSettingsComponent(note_settings_component=self._note_settings_component, automation_component=self._automation_component, initial_encoder_layer=Layer(initial_encoders='global_param_controls', priority=consts.MOMENTARY_DIALOG_PRIORITY), encoder_layer=Layer(encoders='global_param_controls', priority=consts.MOMENTARY_DIALOG_PRIORITY))
        self._note_editor_settings_component.mode_selector_layer = self._create_note_editor_mode_selector_layer()
        self._note_editor_settings.append(NamedTuple(component=self._note_editor_settings_component, track_automation_layer=self._create_note_editor_track_automation_layer(), device_automation_layer=self._create_note_editor_track_automation_layer()))

    def _create_note_editor_mode_selector_layer(self):
        return Layer(select_buttons='select_buttons', state_buttons='track_state_buttons', priority=consts.MOMENTARY_DIALOG_PRIORITY)

    def _create_note_editor_track_automation_layer(self):
        return Layer(priority=consts.MOMENTARY_DIALOG_PRIORITY)

    def _create_note_editor_device_automation_layer(self):
        return Layer(priority=consts.MOMENTARY_DIALOG_PRIORITY)

    def _create_instrument_layer(self):
        return Layer(playhead='playhead_element', mute_button='global_mute_button', quantization_buttons='side_buttons', loop_selector_matrix=self.elements.double_press_matrix.submatrix[:, 0], short_loop_selector_matrix=self.elements.double_press_event_matrix.submatrix[:, 0], note_editor_matrices=ButtonMatrixElement([[ self.elements.matrix.submatrix[:, 7 - row] for row in xrange(7) ]]))

    def _init_instrument(self):
        self._note_layout = NoteLayout(song=self.song, preferences=self.preferences)
        instrument_basic_layer = Layer(octave_strip=self._with_shift('touch_strip_control'), octave_up_button='octave_up_button', octave_down_button='octave_down_button', scale_up_button=self._with_shift('octave_up_button'), scale_down_button=self._with_shift('octave_down_button'))
        self._instrument = MelodicComponent(skin=self._skin, is_enabled=False, clip_creator=self._clip_creator, name='Melodic_Component', grid_resolution=self._grid_resolution, note_layout=self._note_layout, note_editor_settings=self._note_editor_settings_component, note_editor_class=self.note_editor_class, velocity_range_thresholds=self.note_editor_velocity_range_thresholds, layer=self._create_instrument_layer(), instrument_play_layer=instrument_basic_layer + Layer(matrix='matrix', aftertouch_control='aftertouch_control', delete_button='delete_button'), instrument_sequence_layer=instrument_basic_layer + Layer(note_strip='touch_strip_control'), pitch_mod_touch_strip_mode=LayerMode(self._pitch_mod_touch_strip, self._pitch_mod_touch_strip_layer))
        self.__on_note_editor_layout_changed.subject = self._instrument

    def _create_scales_enabler(self):
        raise NotImplementedError

    def _init_scales(self):
        self._scales_enabler = self._create_scales_enabler()

    def _create_step_sequencer_layer(self):
        return Layer(playhead='playhead_element', button_matrix=self.elements.matrix.submatrix[:8, :4], loop_selector_matrix=self.elements.double_press_matrix.submatrix[4:8, 4:8], short_loop_selector_matrix=self.elements.double_press_event_matrix.submatrix[4:8, 4:8], quantization_buttons='side_buttons', solo_button='global_solo_button', select_button='select_button', delete_button='delete_button', shift_button='shift_button', mute_button='global_mute_button')

    def _init_step_sequencer(self):
        drum_note_editor = self.note_editor_class(clip_creator=self._clip_creator, grid_resolution=self._grid_resolution, skin_base_key=self.drum_group_note_editor_skin, velocity_range_thresholds=self.note_editor_velocity_range_thresholds)
        self._note_editor_settings_component.add_editor(drum_note_editor)
        self._drum_step_sequencer = StepSeqComponent(self._clip_creator, self._skin, name='Drum_Step_Sequencer', grid_resolution=self._grid_resolution, note_editor_component=drum_note_editor, instrument_component=self._drum_component)
        self._drum_step_sequencer.set_enabled(False)
        self._drum_step_sequencer.layer = self._create_step_sequencer_layer()
        self._audio_loop = LoopSelectorComponent(follow_detail_clip=True, measure_length=1.0, name='Loop_Selector')
        self._audio_loop.set_enabled(False)
        self._audio_loop.layer = Layer(loop_selector_matrix='matrix')
        slice_note_editor = self.note_editor_class(clip_creator=self._clip_creator, grid_resolution=self._grid_resolution, skin_base_key=self.drum_group_note_editor_skin, velocity_range_thresholds=self.note_editor_velocity_range_thresholds)
        self._note_editor_settings_component.add_editor(slice_note_editor)
        self._slice_step_sequencer = StepSeqComponent(self._clip_creator, self._skin, name='Slice_Step_Sequencer', grid_resolution=self._grid_resolution, note_editor_component=slice_note_editor, instrument_component=self._slicing_component, is_enabled=False)
        self._slice_step_sequencer.layer = Layer(playhead='playhead_element', button_matrix=self.elements.matrix.submatrix[:8, :4], loop_selector_matrix=self.elements.double_press_matrix.submatrix[4:8, 4:8], short_loop_selector_matrix=self.elements.double_press_event_matrix.submatrix[4:8, 4:8], quantization_buttons='side_buttons', select_button='select_button')

    def _drum_pad_notification_formatter(self):
        return lambda x: adjust_string(x, 8)

    def _create_drum_component(self):
        raise NotImplementedError

    def _init_drum_component(self):
        self._drum_component = self._create_drum_component()
        self._drum_component.layer = Layer(page_strip='touch_strip_control', scroll_strip=self._with_shift('touch_strip_control'), solo_button='global_solo_button', select_button='select_button', delete_button='delete_button', scroll_page_up_button='octave_up_button', scroll_page_down_button='octave_down_button', quantize_button='quantize_button', duplicate_button='duplicate_button', mute_button='global_mute_button', scroll_up_button=self._with_shift('octave_up_button'), scroll_down_button=self._with_shift('octave_down_button'))

    def _init_slicing_component(self):
        self._slicing_component = SlicedSimplerComponent(is_enabled=False)
        self._slicing_component.layer = Layer(scroll_page_up_button='octave_up_button', scroll_page_down_button='octave_down_button', scroll_up_button=self._with_shift('octave_up_button'), scroll_down_button=self._with_shift('octave_down_button'), delete_button='delete_button', select_button='select_button')

    def _init_note_repeat(self):
        self._note_repeat = NoteRepeatComponent(name='Note_Repeat')
        self._note_repeat.set_enabled(False)
        self._note_repeat.set_note_repeat(self._c_instance.note_repeat)
        self._note_repeat.layer = self._create_note_repeat_layer()
        self._note_repeat_enabler = EnablingModesComponent(name='Note_Repeat_Enabler', component=self._note_repeat, enabled_color='DefaultButton.Alert', disabled_color='DefaultButton.On')
        self._note_repeat_enabler.set_enabled(False)
        self._note_repeat_enabler.layer = Layer(cycle_mode_button='repeat_button')

    def _create_note_repeat_layer(self):
        return Layer(aftertouch_control='aftertouch_control', select_buttons='side_buttons', priority=consts.DIALOG_PRIORITY)

    def _init_notification(self):
        self._notification = self._create_notification_component()

    def _create_notification_component(self):
        raise NotImplementedError

    def _create_message_box_background_layer(self):
        return BackgroundLayer('select_buttons', 'track_state_buttons', 'scale_presets_button', 'octave_up_button', 'octave_down_button', 'side_buttons', 'repeat_button', 'accent_button', 'global_param_controls', 'global_param_touch_buttons', 'touch_strip_control', 'touch_strip_tap', 'matrix', 'nav_up_button', 'nav_down_button', 'nav_left_button', 'nav_right_button', 'shift_button', 'select_button', 'delete_button', 'duplicate_button', 'double_button', 'quantize_button', 'play_button', 'new_button', 'automation_button', 'tap_tempo_button', 'metronome_button', 'fixed_length_button', 'record_button', 'undo_button', 'tempo_control', 'swing_control', 'master_volume_control', 'global_param_controls', 'vol_mix_mode_button', 'pan_send_mix_mode_button', 'single_track_mix_mode_button', 'clip_mode_button', 'device_mode_button', 'browse_mode_button', 'user_button', 'master_select_button', 'create_device_button', 'create_track_button', 'global_track_stop_button', 'global_mute_button', 'global_solo_button', 'note_mode_button', 'session_mode_button', priority=consts.MESSAGE_BOX_PRIORITY)

    def _create_message_box_layer(self):
        raise RuntimeError

    def _init_message_box(self):
        self._dialog = DialogComponent(is_enabled=True, is_root=True)
        self._dialog.message_box_layer = (self._create_message_box_background_layer(), self._create_message_box_layer())

    def _for_non_frozen_tracks(self, component, **k):
        """ Wrap component into a mode that will only enable it when
        the track is not frozen """
        TrackFrozenModesComponent(default_mode=component, frozen_mode=self._track_frozen_info, **k)
        return component

    def _init_undo_redo_actions(self):
        self._undo_redo = UndoRedoComponent(name='Undo_Redo', is_root=True)
        self._undo_redo.layer = Layer(undo_button='undo_button', redo_button=self._with_shift('undo_button'))

    def _init_stop_clips_action(self):
        pass

    def _create_capture_and_insert_scene_component(self):
        return CaptureAndInsertSceneComponent(name='Capture_And_Insert_Scene', is_root=True)

    def _init_duplicate_actions(self):
        capture_element = ChoosingElement(self._settings['workflow'], 'duplicate_button', self._with_shift('duplicate_button'))
        self._capture_and_insert_scene = self._create_capture_and_insert_scene_component()
        self._capture_and_insert_scene.set_enabled(True)
        self._capture_and_insert_scene.layer = Layer(action_button=capture_element)
        duplicate_element = OptionalElement('duplicate_button', self._settings['workflow'], False)
        self._duplicate_detail_clip = DuplicateDetailClipComponent(name='Duplicate_Detail_Clip', is_root=True)
        self._duplicate_detail_clip.set_enabled(True)
        self._duplicate_detail_clip.layer = Layer(action_button=duplicate_element)
        self._duplicate_loop = self._for_non_frozen_tracks(DuplicateLoopComponent(name='Duplicate_Loop', layer=Layer(action_button='double_button'), is_enabled=False), is_root=True)

    def _init_delete_actions(self):
        self._delete_component = DeleteComponent(name='Deleter', is_root=True)
        self._delete_component.layer = Layer(delete_button='delete_button')
        self._delete_default_component = DeleteAndReturnToDefaultComponent(name='DeleteAndDefault', is_root=True)
        self._delete_default_component.layer = Layer(delete_button='delete_button')
        self._delete_clip = DeleteSelectedClipComponent(name='Selected_Clip_Deleter', is_root=True)
        self._delete_clip.layer = Layer(action_button='delete_button')
        self._delete_scene = DeleteSelectedSceneComponent(name='Selected_Scene_Deleter', is_root=True)
        self._delete_scene.layer = Layer(action_button=self._with_shift('delete_button'))

    def _init_quantize_actions(self):
        raise NotImplementedError

    def _init_value_components(self):
        self._swing_amount = ValueComponent('swing_amount', self.song, display_label='Swing Amount:', display_format='%d%%', model_transform=lambda x: clamp(x / 200.0, 0.0, 0.5), view_transform=lambda x: x * 200.0, encoder_factor=100.0, encoder_touch_delay=TEMPO_SWING_TOUCH_DELAY, is_root=True)
        self._swing_amount.layer = Layer(encoder='swing_control')
        self._tempo = ValueComponent('tempo', self.song, display_label='Tempo:', display_format='%0.2f BPM', encoder_factor=128.0, encoder_touch_delay=TEMPO_SWING_TOUCH_DELAY, is_root=True)
        self._tempo.layer = Layer(encoder='tempo_control', shift_button='shift_button')
        self._master_vol = ParameterValueComponent(self.song.master_track.mixer_device.volume, display_label='Master Volume:', display_seg_start=3, name='Master_Volume_Display', is_root=True)
        self._master_vol.layer = Layer(encoder='master_volume_control')
        self._master_cue_vol = ParameterValueComponent(self.song.master_track.mixer_device.cue_volume, display_label='Cue Volume:', display_seg_start=3, name='Cue_Volume_Display', is_root=True)
        self._master_cue_vol.layer = Layer(encoder=self._with_shift('master_volume_control'))

    def _init_m4l_interface(self):
        self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard, priority=consts.M4L_PRIORITY, is_root=True)
        self.get_control_names = self._m4l_interface.get_control_names
        self.get_control = self._m4l_interface.get_control
        self.grab_control = self._m4l_interface.grab_control
        self.release_control = self._m4l_interface.release_control

    @listens('selected_mode')
    def __on_note_editor_layout_changed(self, mode):
        self.reset_controlled_track(mode)

    def reset_controlled_track(self, mode = None):
        if mode == None:
            mode = self._instrument.selected_mode
        if self._instrument.is_enabled() and mode == 'sequence':
            self.release_controlled_track()
        else:
            self.set_controlled_track(self.song.view.selected_track)

    @listens('selected_track.is_frozen')
    def __on_selected_track_is_frozen_changed(self):
        self._select_note_mode()

    def _on_selected_track_changed(self):
        self.reset_controlled_track()
        self._select_note_mode()
        self._note_repeat_enabler.selected_mode = 'disabled'

    def _send_midi(self, midi_event_bytes, optimized = True):
        if not self._suppress_sysex or not midi.is_sysex(midi_event_bytes):
            return super(PushBase, self)._send_midi(midi_event_bytes, optimized)

    def _update_full_velocity(self, accent_is_active):
        self._drum_step_sequencer.full_velocity = accent_is_active
        self._instrument.full_velocity = accent_is_active

    def _update_playhead_color(self, color):
        self._instrument.playhead_color = color
        self._drum_step_sequencer.playhead_color = color

    @listens('session_record')
    def __on_session_record_changed(self):
        status = self.song.session_record
        self._update_playhead_color('PlayheadRecord' if status else 'Playhead')
        feedback_color = int(to_midi_value(self._skin['Instrument.FeedbackRecord']) if status else to_midi_value(self._skin['Instrument.Feedback']))
        self._c_instance.set_feedback_velocity(feedback_color)

    @listens('selected_mode')
    def __on_accent_mode_changed(self, mode_name):
        accent_is_active = mode_name == 'enabled'
        self._update_full_velocity(accent_is_active)

    @listens('enabled')
    def __on_fixed_length_enabled_changed(self, enabled):
        self.preferences['fixed_length_enabled'] = enabled

    @listens('selected_index')
    def __on_fixed_length_selected_index_changed(self, index):
        self.preferences['fixed_length_option'] = index

    @listens('before_mode_sent')
    def __on_before_hardware_mode_sent(self, mode):
        self._suppress_sysex = False

    @listens('after_mode_sent')
    def __on_after_hardware_mode_sent(self, mode):
        if mode == sysex.USER_MODE:
            self._suppress_sysex = True

    @listens('mode')
    def __on_hardware_mode_changed(self, mode):
        if mode == sysex.USER_MODE:
            self._suppress_sysex = True
        self._update_auto_arm()

    @listens('selected_mode')
    def __on_matrix_mode_changed(self, mode):
        self._update_auto_arm(selected_mode=mode)

    def _update_auto_arm(self, selected_mode = None):
        self._auto_arm.set_enabled(self._user.mode == sysex.LIVE_MODE and (selected_mode or self._matrix_modes.selected_mode) == 'note')

    @listens('instrument')
    def __on_percussion_instrument_changed(self):
        self._select_note_mode()

    def _select_note_mode(self):
        """
        Selects which note mode to use depending on the kind of
        current selected track and its device chain...
        """
        track = self.song.view.selected_track
        drum_device, sliced_simpler = self._percussion_instruments_for_track(track)
        self._drum_component.set_drum_group_device(drum_device)
        self._slicing_component.set_simpler(sliced_simpler)
        if track == None or track.is_foldable or track in self.song.return_tracks or track == self.song.master_track or track.is_frozen:
            self._note_modes.selected_mode = 'disabled'
        elif track and track.has_audio_input:
            self._note_modes.selected_mode = 'looper'
        elif drum_device:
            self._note_modes.selected_mode = 'drums'
        elif sliced_simpler:
            self._note_modes.selected_mode = 'slicing'
        else:
            self._note_modes.selected_mode = 'instrument'
        self.reset_controlled_track()

    def _percussion_instruments_for_track(self, track):
        self._percussion_instrument_finder.device_parent = track
        drum_device = self._percussion_instrument_finder.drum_group
        sliced_simpler = self._percussion_instrument_finder.sliced_simpler
        return (drum_device, sliced_simpler)

    def _setup_accidental_touch_prevention(self):
        self._accidental_touch_prevention_layer = BackgroundLayer('tempo_control_tap', 'swing_control_tap', 'master_volume_control_tap', priority=consts.MOMENTARY_DIALOG_PRIORITY)
        self.__on_param_encoder_touched.replace_subjects(self.elements.global_param_touch_buttons_raw)

    @listens_group('value')
    def __on_param_encoder_touched(self, value, encoder):
        """
        When using the parameter encoders, other encoders around it are often accidentally
        touched and will take over the screen.
        By stealing the touch buttons from the encoders, we ensure they are not triggered
        while using any of the parameter encoders.
        """
        if any(imap(lambda e: e.is_pressed(), self.elements.global_param_touch_buttons_raw)):
            self._accidental_touch_prevention_layer.grab(self)
        else:
            self._accidental_touch_prevention_layer.release(self)

    def get_matrix_button(self, column, row):
        return self.elements.matrix_rows_raw[7 - row][column]

    def expect_dialog(self, message):
        self.schedule_message(1, partial(self._dialog.expect_dialog, message))

    def show_notification(self, message, blink_text = None, notification_time = None):
        return self._notification.show_notification(message, blink_text, notification_time)

    def process_midi_bytes(self, midi_bytes, midi_processor):
        if not midi.is_sysex(midi_bytes):
            recipient = self.get_recipient_for_nonsysex_midi_message(midi_bytes)
            if isinstance(recipient, ButtonElement) and midi.extract_value(midi_bytes) != 0 and self._notification is not None:
                self._notification.hide_notification()
        super(PushBase, self).process_midi_bytes(midi_bytes, midi_processor)