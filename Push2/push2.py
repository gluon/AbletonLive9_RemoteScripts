#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/push2.py
from __future__ import absolute_import, print_function
from contextlib import contextmanager
from functools import partial
import json
import logging
import weakref
import Live
import MidiRemoteScript
from ableton.v2.base import const, inject, listens, listens_group, task, Subject, NamedTuple
from ableton.v2.control_surface import BackgroundLayer, Component, IdentifiableControlSurface, Layer, get_element
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.elements import ButtonMatrixElement, ComboElement, SysexElement
from ableton.v2.control_surface.mode import EnablingModesComponent, ModesComponent, LayerMode, LazyComponentMode, ReenterBehaviour, SetAttributeMode
from pushbase.actions import select_clip_and_get_name_from_slot, select_scene_and_get_name
from pushbase.device_parameter_component import DeviceParameterComponentBase as DeviceParameterComponent
from pushbase.quantization_component import QUANTIZATION_NAMES_UNICODE, QuantizationComponent, QuantizationSettingsComponent
from pushbase.selection import PushSelection
from pushbase.percussion_instrument_finder_component import find_drum_group_device
from pushbase import consts
from pushbase.push_base import PushBase, NUM_TRACKS, NUM_SCENES
from pushbase.track_frozen_mode import TrackFrozenModesComponent
from . import sysex
from .actions import CaptureAndInsertSceneComponent
from .automation import AutomationComponent
from .elements import Elements
from .browser_component import BrowserComponent, NewTrackBrowserComponent
from .browser_modes import AddDeviceMode, AddTrackMode, BrowseMode, BrowserComponentMode, BrowserModeBehaviour
from .device_decoration import DeviceDecoratorFactory
from .skin_default import make_default_skin
from .mute_solo_stop import MuteSoloStopClipComponent
from .device_component import Push2DeviceProvider, DeviceComponent
from .device_view_component import DeviceViewComponent
from .device_navigation import is_empty_rack, DeviceNavigationComponent, MoveDeviceComponent
from .drum_group_component import DrumGroupComponent
from .drum_pad_parameter_component import DrumPadParameterComponent
from .chain_selection_component import ChainSelectionComponent
from .clip_control import AudioClipSettingsControllerComponent, ClipControlComponent, LoopSettingsControllerComponent
from .clip_decoration import ClipDecoratorFactory
from .colors import COLOR_TABLE
from .convert import ConvertComponent, ConvertEnabler
from .bank_selection_component import BankSelectionComponent
from .firmware import FirmwareUpdateComponent, FirmwareVersion
from .hardware_settings_component import HardwareSettingsComponent
from .master_track import MasterTrackComponent
from .mixer_control_component import MixerControlComponent
from .note_editor import Push2NoteEditorComponent
from .note_settings import NoteSettingsComponent
from .notification_component import NotificationComponent
from .pad_velocity_curve import PadVelocityCurveSender
from .scales_component import ScalesComponent, ScalesEnabler
from .session_component import SessionComponent
from .session_recording import SessionRecordingComponent
from .session_ring_selection_linking import SessionRingSelectionLinking
from .settings import create_settings
from .track_mixer_control_component import TrackMixerControlComponent
from .mode_collector import ModeCollector
from .real_time_channel import update_real_time_attachments
from .setup_component import SetupComponent, Settings
from .track_list import TrackListComponent
from .track_selection import SessionRingTrackProvider, ViewControlComponent
from .user_component import UserButtonBehavior, UserComponent
from .custom_bank_definitions import BANK_DEFINITIONS
logger = logging.getLogger(__name__)
VELOCITY_RANGE_THRESHOLDS = [120, 60, 0]

class QmlError(Exception):
    pass


def make_dialog_layer(priority = consts.DIALOG_PRIORITY, *a, **k):
    return (BackgroundLayer('global_param_controls', 'select_buttons', 'track_state_buttons', priority=priority), Layer(priority=priority, *a, **k))


def tracks_to_use_from_song(song):
    return tuple(song.visible_tracks) + tuple(song.return_tracks)


def wrap_button(select_buttons, modifier):
    return [ ComboElement(button, modifier=modifier) for button in get_element(select_buttons) ]


def make_freeze_aware(component, layer, default_mode_extras = [], frozen_mode_extras = []):
    return TrackFrozenModesComponent(default_mode=[component, LayerMode(component, layer)] + default_mode_extras, frozen_mode=[component, LayerMode(component, Layer())] + frozen_mode_extras, is_enabled=False)


class RealTimeClientModel(Subject):
    __events__ = ('clientId',)

    def __init__(self):
        self._client_id = ''

    def _get_client_id(self):
        return self._client_id

    def _set_client_id(self, client_id):
        self._client_id = client_id
        self.notify_clientId()

    clientId = property(_get_client_id, _set_client_id)


class Push2(IdentifiableControlSurface, PushBase):
    session_component_type = SessionComponent
    drum_group_note_editor_skin = 'DrumGroupNoteEditor'
    input_target_name_for_auto_arm = 'Push2 Input'
    note_editor_velocity_range_thresholds = VELOCITY_RANGE_THRESHOLDS
    device_component_class = DeviceComponent
    device_provider_class = Push2DeviceProvider
    bank_definitions = BANK_DEFINITIONS
    note_editor_class = Push2NoteEditorComponent
    RESEND_MODEL_DATA_TIMEOUT = 5.0
    DEFUNCT_EXTERNAL_PROCESS_RELAUNCH_TIMEOUT = 2.0

    def __init__(self, c_instance = None, model = None, bank_definitions = None, *a, **k):
        if not model is not None:
            raise AssertionError
            self._model = model
            self._real_time_mapper = c_instance.real_time_mapper
            self._clip_decorator_factory = ClipDecoratorFactory()
            self._real_time_data_list = []
            self.bank_definitions = bank_definitions is not None and bank_definitions
        super(Push2, self).__init__(c_instance=c_instance, product_id_bytes=sysex.IDENTITY_RESPONSE_PRODUCT_ID_BYTES, *a, **k)
        self._board_revision = 0
        self._firmware_version = FirmwareVersion(0, 0, 0)
        self._real_time_client = RealTimeClientModel()
        self._connected = False
        self._identified = False
        self._initialized = False
        self.register_disconnectable(model)
        self.register_disconnectable(self._clip_decorator_factory)
        with self.component_guard():
            self._model.realTimeClient = self._real_time_client
            self._real_time_client.clientId = self._real_time_mapper.client_id
        logger.info('Push 2 script loaded')

    def initialize(self):
        if not self._initialized:
            self._initialized = True
            self._init_hardware_settings()
            self._init_pad_curve()
            self._hardware_settings.fade_in_led_brightness(self._setup_settings.hardware.led_brightness)
            self._pad_curve_sender.send()
            self._send_color_palette()
            super(Push2, self).initialize()
            self.__on_selected_track_frozen_changed.subject = self.song.view
            self.__on_selected_track_frozen_changed()
            self._switch_to_live_mode()
            self.update()
        if self._firmware_update.provided_version > self._firmware_version and self._board_revision > 0 and self._identified:
            self._firmware_update.start()

    def _try_initialize(self):
        if self._connected and self._identified:
            self.initialize()

    def on_process_state_changed(self, state):
        StateEnum = MidiRemoteScript.Push2ProcessState
        self._connected = state == StateEnum.connected
        if state == StateEnum.died:
            self._c_instance.launch_external_process()
        elif state == StateEnum.connected:
            with self.component_guard():
                self._try_initialize()
            self._model.commit_changes(send_all=True)
        elif state in (StateEnum.defunct_process_terminated, StateEnum.defunct_process_killed):
            self._tasks.add(task.sequence(task.wait(self.DEFUNCT_EXTERNAL_PROCESS_RELAUNCH_TIMEOUT), task.run(self._c_instance.launch_external_process)))

    def on_user_data_arrived(self, message):
        if self._initialized:
            data = json.loads(message)
            self._process_qml_errors(data)
            self._firmware_update.process_firmware_response(data)

    def _process_qml_errors(self, data):
        qmlerrors = [ entry['description'] for entry in data if entry['type'] == 'qmlerror' ]
        if qmlerrors:
            raise QmlError('\n'.join(qmlerrors))

    def disconnect(self):
        super(Push2, self).disconnect()
        self.__dict__.clear()
        logger.info('Push 2 script unloaded')

    def register_real_time_data(self, real_time_data):
        self._real_time_data_list.append(real_time_data)

    def _commit_real_time_data_changes(self):
        update_real_time_attachments(self._real_time_data_list)

    def _create_device_decorator_factory(self):
        return DeviceDecoratorFactory()

    def _create_skin(self):
        return self.register_disconnectable(make_default_skin())

    def _create_injector(self):
        return inject(double_press_context=const(self._double_press_context), expect_dialog=const(self.expect_dialog), show_notification=const(self.show_notification), commit_model_changes=const(self._model.commit_changes), register_real_time_data=const(self.register_real_time_data), selection=lambda : PushSelection(application=self.application(), device_component=self._device_component, navigation_component=self._device_navigation))

    def _create_components(self):
        self._init_dialog_modes()
        super(Push2, self)._create_components()
        self._init_browser()
        self._init_session_ring_selection_linking()
        self._init_setup_component()
        self._init_firmware_update()
        self._init_convert_enabler()
        self._init_mute_solo_stop()

    @contextmanager
    def _component_guard(self):
        with super(Push2, self)._component_guard():
            with inject(real_time_mapper=const(self._c_instance.real_time_mapper)).everywhere():
                yield
                self._commit_real_time_data_changes()
                self._model.commit_changes()

    def _create_notification_component(self):
        notification = NotificationComponent(is_root=True)
        self._model.notificationView = notification
        return notification

    def _create_background_layer(self):
        return super(Push2, self)._create_background_layer() + Layer(mix_button='mix_button', page_left_button='page_left_button', page_right_button='page_right_button', mute_button='global_mute_button', solo_button='global_solo_button', track_stop_button='global_track_stop_button', convert_button='convert_button', layout_button='layout_button', setup_button='setup_button')

    def _create_message_box_background_layer(self):
        return super(Push2, self)._create_message_box_background_layer() + BackgroundLayer('mix_button', 'page_left_button', 'page_right_button', 'convert_button', 'layout_button', 'setup_button')

    def _create_message_box_layer(self):
        return Layer(cancel_button='track_state_buttons_raw[0]', priority=consts.MESSAGE_BOX_PRIORITY)

    def _init_message_box(self):
        super(Push2, self)._init_message_box()
        self._model.liveDialogView = self._dialog._message_box

    def _create_convert(self):
        convert = ConvertComponent(decorator_factory=self._device_decorator_factory, name='Convert', tracks_provider=self._session_ring, is_enabled=False, layer=make_dialog_layer(action_buttons='select_buttons', cancel_button='track_state_buttons_raw[0]'))
        self.__on_convert_closed.subject = convert
        self.__on_convert_suceeded.subject = convert
        self._model.convertView = convert
        return convert

    def _init_note_settings_component(self):
        self._note_settings_component = NoteSettingsComponent(grid_resolution=self._grid_resolution, is_enabled=False, layer=Layer(full_velocity_button='accent_button', priority=consts.MOMENTARY_DIALOG_PRIORITY))
        self._model.noteSettingsView = self._note_settings_component

    def _init_note_editor_settings_component(self):
        super(Push2, self)._init_note_editor_settings_component()
        self._model.stepSettingsView = self._note_editor_settings_component.step_settings

    def _init_automation_component(self):
        self._automation_component = AutomationComponent()
        self._model.stepAutomationSettingsView = self._automation_component

    def _init_convert_enabler(self):
        self._convert_enabler = ConvertEnabler(is_root=True, is_enabled=True, enter_dialog_mode=self._enter_dialog_mode, exit_dialog_mode=self._exit_dialog_mode)
        self._convert_enabler.layer = Layer(convert_toggle_button='convert_button')

    @listens('cancel')
    def __on_convert_closed(self):
        self._dialog_modes.selected_mode = None

    @listens('success')
    def __on_convert_suceeded(self, action_name):
        if action_name == 'audio_clip_to_simpler':
            self._main_modes.selected_mode = 'device'

    def _init_main_modes(self):
        super(Push2, self)._init_main_modes()
        self._main_modes.add_mode('user', [self._user_mode_ui_blocker, SetAttributeMode(obj=self._user, attribute='mode', value=sysex.USER_MODE)], behaviour=UserButtonBehavior(user_component=self._user))
        self._model.modeState = self.register_disconnectable(ModeCollector(main_modes=self._main_modes, mix_modes=self._mix_modes, global_mix_modes=self._mixer_control, device_modes=self._device_navigation.modes))
        self.__on_main_mode_button_value.replace_subjects([self.elements.vol_mix_mode_button,
         self.elements.pan_send_mix_mode_button,
         self.elements.single_track_mix_mode_button,
         self.elements.clip_mode_button,
         self.elements.device_mode_button,
         self.elements.browse_mode_button,
         self.elements.create_device_button,
         self.elements.create_track_button])

    @listens_group('value')
    def __on_main_mode_button_value(self, value, sender):
        if not value:
            self._exit_modal_modes()

    def _exit_modal_modes(self):
        self._dialog_modes.selected_mode = None
        self._setup_enabler.selected_mode = 'disabled'

    def _create_capture_and_insert_scene_component(self):
        return CaptureAndInsertSceneComponent(name='Capture_And_Insert_Scene', decorator_factory=self._clip_decorator_factory, is_root=True)

    def _init_mute_solo_stop(self):
        self._mute_solo_stop = MuteSoloStopClipComponent(is_root=True, item_provider=self._session_ring, track_list_component=self._track_list_component, cancellation_action_performers=[self._device_navigation, self._drum_component] + self._note_editor_settings_component.editors, solo_track_button='global_solo_button', mute_track_button='global_mute_button', stop_clips_button='global_track_stop_button')
        self._mute_solo_stop.layer = Layer(stop_all_clips_button=self._with_shift('global_track_stop_button'))
        self._master_selector = MasterTrackComponent(tracks_provider=self._session_ring, is_enabled=False, layer=Layer(toggle_button='master_select_button'))
        self._master_selector.set_enabled(True)

    def _create_instrument_layer(self):
        return super(Push2, self)._create_instrument_layer() + Layer(prev_loop_page_button='page_left_button', next_loop_page_button='page_right_button')

    def _create_step_sequencer_layer(self):
        return super(Push2, self)._create_step_sequencer_layer() + Layer(prev_loop_page_button='page_left_button', next_loop_page_button='page_right_button')

    def _create_session(self):
        session = super(Push2, self)._create_session()
        for scene_ix in xrange(8):
            scene = session.scene(scene_ix)
            for track_ix in xrange(8):
                clip_slot = scene.clip_slot(track_ix)
                clip_slot.set_decorator_factory(self._clip_decorator_factory)

        return session

    def _create_session_navigation_layer(self):
        return Layer(left_button='nav_left_button', right_button='nav_right_button', up_button='nav_up_button', down_button='nav_down_button', page_left_button='page_left_button', page_right_button='page_right_button', page_up_button='octave_up_button', page_down_button='octave_down_button')

    def on_select_clip_slot(self, clip_slot):
        self.show_notification('Clip Selected: ' + select_clip_and_get_name_from_slot(clip_slot, self.song))

    def on_select_scene(self, scene):
        self.show_notification('Scene Selected: ' + select_scene_and_get_name(scene, self.song))

    def _create_session_mode(self):
        session_modes = ModesComponent(is_enabled=False)
        session_modes.add_mode('session', self._session_mode)
        session_modes.add_mode('overview', self._session_overview_mode)
        session_modes.layer = Layer(cycle_mode_button='layout_button')
        session_modes.selected_mode = 'session'
        return [session_modes, self._session_navigation]

    def _create_session_overview_layer(self):
        return Layer(button_matrix='matrix')

    def _create_drum_component(self):
        return DrumGroupComponent(name='Drum_Group', is_enabled=False, notification_formatter=self._drum_pad_notification_formatter(), tracks_provider=self._session_ring, device_decorator_factory=self._device_decorator_factory, quantizer=self._quantize)

    def _create_device_mode(self):
        self._drum_pad_parameter_component = DrumPadParameterComponent(view_model=self._model, is_enabled=False, layer=Layer(choke_encoder='parameter_controls_raw[0]'))
        self._device_or_pad_parameter_chooser = ModesComponent()
        self._device_or_pad_parameter_chooser.add_mode('device', [make_freeze_aware(self._device_parameter_component, self._device_parameter_component.layer), self._device_view])
        self._device_or_pad_parameter_chooser.add_mode('drum_pad', [make_freeze_aware(self._drum_pad_parameter_component, self._drum_pad_parameter_component.layer)])
        self._device_or_pad_parameter_chooser.selected_mode = 'device'
        return [partial(self._view_control.show_view, 'Detail/DeviceChain'),
         self._device_or_pad_parameter_chooser,
         self._setup_freeze_aware_device_navigation(),
         self._device_note_editor_mode,
         SetAttributeMode(obj=self._note_editor_settings_component, attribute='parameter_provider', value=self._device_component)]

    def _setup_freeze_aware_device_navigation(self):

        def create_layer_setter(layer_name, layer):
            return SetAttributeMode(obj=self._device_navigation, attribute=layer_name, value=layer)

        return make_freeze_aware(self._device_navigation, self._device_navigation.layer, default_mode_extras=[create_layer_setter('scroll_right_layer', Layer(button=self.elements.track_state_buttons_raw[-1])), create_layer_setter('scroll_left_layer', Layer(button=self.elements.track_state_buttons_raw[0]))], frozen_mode_extras=[lambda : setattr(self._device_navigation.modes, 'selected_mode', 'default'), create_layer_setter('scroll_right_layer', Layer()), create_layer_setter('scroll_left_layer', Layer())])

    @listens('drum_pad_selection')
    def __on_drum_pad_selection_changed(self):
        show_pad_parameters = self._device_navigation.is_drum_pad_selected and self._device_navigation.is_drum_pad_unfolded
        new_mode = 'drum_pad' if show_pad_parameters else 'device'
        if show_pad_parameters:
            selected_pad = self._device_navigation.item_provider.selected_item
            self._drum_pad_parameter_component.drum_pad = selected_pad
        self._device_or_pad_parameter_chooser.selected_mode = new_mode
        self._automation_component.set_drum_pad_selected(self._device_navigation.is_drum_pad_selected)

    def _init_browser(self):
        self._browser_component_mode = BrowserComponentMode(weakref.ref(self._model), self._create_browser)
        self._new_track_browser_component_mode = BrowserComponentMode(weakref.ref(self._model), self._create_new_track_browser)

    def _init_browse_mode(self):
        application = Live.Application.get_application()
        browser = application.browser
        self._main_modes.add_mode('browse', [BrowseMode(application=application, song=self.song, browser=browser, component_mode=self._browser_component_mode)], behaviour=BrowserModeBehaviour())
        self._main_modes.add_mode('add_device', [AddDeviceMode(application=application, song=self.song, browser=browser, component_mode=self._browser_component_mode)], behaviour=BrowserModeBehaviour())
        self._main_modes.add_mode('add_track', [AddTrackMode(browser=browser, component_mode=self._new_track_browser_component_mode)], behaviour=BrowserModeBehaviour())

    def _create_browser_layer(self):
        return (BackgroundLayer('select_buttons', 'track_state_buttons', priority=consts.DIALOG_PRIORITY), Layer(up_button='nav_up_button', down_button='nav_down_button', right_button='nav_right_button', left_button='nav_left_button', back_button='track_state_buttons_raw[-2]', open_button='track_state_buttons_raw[-1]', load_button='select_buttons_raw[-1]', scroll_encoders=self.elements.global_param_controls.submatrix[:-1, :], scroll_focused_encoder='parameter_controls_raw[-1]', close_button='track_state_buttons_raw[0]', prehear_button='track_state_buttons_raw[1]', priority=consts.DIALOG_PRIORITY))

    def _create_browser(self):
        browser = BrowserComponent(name='Browser', is_enabled=False, preferences=self.preferences, main_modes_ref=weakref.ref(self._main_modes), layer=self._create_browser_layer())
        self._on_browser_loaded.add_subject(browser)
        self._on_browser_closed.add_subject(browser)
        return browser

    def _create_new_track_browser(self):
        browser = NewTrackBrowserComponent(name='NewTrackBrowser', is_enabled=False, preferences=self.preferences, layer=self._create_browser_layer())
        self._on_browser_loaded.add_subject(browser)
        self._on_browser_closed.add_subject(browser)
        return browser

    @listens_group('loaded')
    def _on_browser_loaded(self, sender):
        if sender.browse_for_audio_clip:
            self._main_modes.selected_mode = 'clip'
        else:
            browser = Live.Application.get_application().browser
            if browser.hotswap_target is None:
                self._main_modes.selected_mode = 'device'
            drum_rack = find_drum_group_device(self.song.view.selected_track)
            if drum_rack and is_empty_rack(drum_rack):
                self._device_navigation.request_drum_pad_selection()
            if drum_rack and self._device_navigation.is_drum_pad_selected:
                if not self._device_navigation.is_drum_pad_unfolded:
                    self._device_navigation.unfold_current_drum_pad()
                self._device_navigation.sync_selection_to_selected_device()

    @listens_group('close')
    def _on_browser_closed(self, sender):
        if sender.browse_for_audio_clip:
            self._main_modes.selected_mode = 'clip'
        elif self._main_modes.selected_mode == 'add_track':
            self._main_modes.selected_mode = self._main_modes.active_modes[0]
        else:
            self._main_modes.selected_mode = 'device'

    def _is_on_master(self):
        return self.song.view.selected_track == self.song.master_track

    def _determine_mix_mode(self):
        selected_mode = self._main_modes.selected_mode
        mix_mode = self._mix_modes.selected_mode
        if selected_mode == 'mix':
            if self._is_on_master():
                if mix_mode == 'global':
                    self._mix_modes.push_mode('track')
            elif mix_mode == 'track' and 'global' in self._mix_modes.active_modes:
                self._mix_modes.pop_mode('track')

    def _on_selected_track_changed(self):
        if self._initialized:
            super(Push2, self)._on_selected_track_changed()
            self._close_browse_mode()
            self._determine_mix_mode()

    def _close_browse_mode(self):
        selected_mode = self._main_modes.selected_mode
        if selected_mode in ('browse', 'add_device', 'add_track'):
            self._main_modes.pop_mode(selected_mode)

    @listens('selected_track.is_frozen')
    def __on_selected_track_frozen_changed(self):
        frozen = self.song.view.selected_track.is_frozen
        self._main_modes.browse_button.enabled = self._main_modes.add_track_button.enabled = self._main_modes.add_device_button.enabled = not frozen
        self._close_browse_mode()

    def _create_device_parameter_component(self):
        return DeviceParameterComponent(parameter_provider=self._device_component, is_enabled=False, layer=Layer(parameter_controls='fine_grain_param_controls'))

    def _create_device_navigation(self):
        self._chain_selection = ChainSelectionComponent(is_enabled=False, layer=Layer(select_buttons='select_buttons', priority=consts.DIALOG_PRIORITY))
        self._chain_selection.scroll_left_layer = Layer(button='select_buttons_raw[0]', priority=consts.DIALOG_PRIORITY)
        self._chain_selection.scroll_right_layer = Layer(button='select_buttons_raw[-1]', priority=consts.DIALOG_PRIORITY)
        self._bank_selection = BankSelectionComponent(bank_registry=self._device_bank_registry, banking_info=self._banking_info, device_options_provider=self._device_component, is_enabled=False, layer=Layer(option_buttons='track_state_buttons', select_buttons='select_buttons', priority=consts.DIALOG_PRIORITY))
        self._bank_selection.scroll_left_layer = Layer(button='select_buttons_raw[0]', priority=consts.DIALOG_PRIORITY)
        self._bank_selection.scroll_right_layer = Layer(button='select_buttons_raw[-1]', priority=consts.DIALOG_PRIORITY)
        move_device = MoveDeviceComponent(is_enabled=False, layer=Layer(move_encoders='global_param_controls'))
        device_navigation = DeviceNavigationComponent(name='DeviceNavigation', device_bank_registry=self._device_bank_registry, banking_info=self._banking_info, device_component=self._device_component, delete_handler=self._delete_component, chain_selection=self._chain_selection, bank_selection=self._bank_selection, move_device=move_device, track_list_component=self._track_list_component, is_enabled=False, layer=Layer(select_buttons='track_state_buttons'))
        device_navigation.scroll_left_layer = Layer(button='track_state_buttons_raw[0]')
        device_navigation.scroll_right_layer = Layer(button='track_state_buttons_raw[-1]')
        self.__on_drum_pad_selection_changed.subject = device_navigation
        self.device_provider.allow_update_callback = lambda : device_navigation.device_selection_update_allowed
        return device_navigation

    def _init_device(self):
        super(Push2, self)._init_device()
        self._device_component.layer = Layer(parameter_touch_buttons=ButtonMatrixElement(rows=[self.elements.global_param_touch_buttons_raw]))
        self._device_view = DeviceViewComponent(name='DeviceView', device_component=self._device_component, view_model=self._model, is_enabled=False)
        self._model.devicelistView = self._device_navigation
        self._model.chainListView = self._chain_selection
        self._model.parameterBankListView = self._bank_selection
        self._model.editModeOptionsView = self._bank_selection.options

    def _drum_pad_notification_formatter(self):
        return None

    def _create_view_control_component(self):
        return ViewControlComponent(name='View_Control', tracks_provider=self._session_ring)

    def _create_session_recording(self):
        return SessionRecordingComponent(fixed_length_setting=self._fixed_length_setting, clip_creator=self._clip_creator, view_controller=self._view_control, name='Session_Recording', is_root=True)

    def _init_session_ring(self):
        self._session_ring = SessionRingTrackProvider(name='Session_Ring', num_tracks=NUM_TRACKS, num_scenes=NUM_SCENES, tracks_to_use=partial(tracks_to_use_from_song, self.song), is_enabled=True, is_root=True)

    def _init_session_ring_selection_linking(self):
        self._sessionring_link = self.register_disconnectable(SessionRingSelectionLinking(session_ring=self._session_ring, selection_changed_notifier=self._view_control))

    def _init_track_list(self):
        self._track_list_component = TrackListComponent(tracks_provider=self._session_ring, trigger_recording_on_release_callback=self._session_recording.set_trigger_recording_on_release, is_enabled=False, is_root=True, layer=Layer(track_action_buttons='select_buttons', lock_override_button='select_button', delete_button='delete_button', duplicate_button='duplicate_button', arm_button='record_button'))
        self._track_list_component.set_enabled(True)
        self._model.tracklistView = self._track_list_component

    def _create_main_mixer_modes(self):
        self._mixer_control = MixerControlComponent(name='Global_Mix_Component', view_model=self._model.mixerView, tracks_provider=self._session_ring, is_enabled=False, layer=Layer(controls='fine_grain_param_controls', volume_button='track_state_buttons_raw[0]', panning_button='track_state_buttons_raw[1]', send_slot_one_button='track_state_buttons_raw[2]', send_slot_two_button='track_state_buttons_raw[3]', send_slot_three_button='track_state_buttons_raw[4]', send_slot_four_button='track_state_buttons_raw[5]', send_slot_five_button='track_state_buttons_raw[6]', cycle_sends_button='track_state_buttons_raw[7]'))
        self._model.mixerView.realtimeMeterData = self._mixer_control.real_time_meter_handlers
        track_mixer_control = TrackMixerControlComponent(name='Track_Mix_Component', is_enabled=False, tracks_provider=self._session_ring, layer=Layer(controls='fine_grain_param_controls', scroll_left_button='track_state_buttons_raw[6]', scroll_right_button='track_state_buttons_raw[7]'))
        self._model.mixerView.trackControlView = track_mixer_control
        self._mix_modes = ModesComponent(is_enabled=False)
        self._mix_modes.add_mode('global', self._mixer_control)
        self._mix_modes.add_mode('track', track_mixer_control)
        self._mix_modes.selected_mode = 'global'
        self._model.mixerSelectView = self._mixer_control
        self._model.trackMixerSelectView = track_mixer_control

        class MixModeBehaviour(ReenterBehaviour):

            def press_immediate(behaviour_self, component, mode):
                if self._is_on_master() and self._mix_modes.selected_mode != 'track':
                    self._mix_modes.selected_mode = 'track'
                super(MixModeBehaviour, behaviour_self).press_immediate(component, mode)

            def on_reenter(behaviour_self):
                if not self._is_on_master():
                    self._mix_modes.cycle_mode()

        self._main_modes.add_mode('mix', [self._mix_modes, SetAttributeMode(obj=self._note_editor_settings_component, attribute='parameter_provider', value=self._track_parameter_provider)], behaviour=MixModeBehaviour())

    def _init_dialog_modes(self):
        self._dialog_modes = ModesComponent(is_root=True)
        self._dialog_modes.add_mode('convert', LazyComponentMode(self._create_convert))
        self.__dialog_mode_button_value.replace_subjects([self.elements.scale_presets_button, self.elements.convert_button])

    @listens_group('value')
    def __dialog_mode_button_value(self, value, sender):
        if not value:
            self._setup_enabler.selected_mode = 'disabled'

    def _enter_dialog_mode(self, mode_name):
        self._dialog_modes.selected_mode = None if self._dialog_modes.selected_mode == mode_name else mode_name

    def _exit_dialog_mode(self, mode_name):
        if self._dialog_modes.selected_mode == mode_name:
            self._dialog_modes.selected_mode = None

    def _create_scales(self):
        root_note_buttons = ButtonMatrixElement(rows=[self.elements.track_state_buttons_raw[1:-1], self.elements.select_buttons_raw[1:-1]])
        scales = ScalesComponent(note_layout=self._note_layout, is_enabled=False, layer=make_dialog_layer(root_note_buttons=root_note_buttons, in_key_toggle_button='select_buttons_raw[0]', fixed_toggle_button='select_buttons_raw[-1]', scale_encoders=self.elements.global_param_controls.submatrix[1:-1, :], close_button='track_state_buttons_raw[0]', up_button='nav_up_button', down_button='nav_down_button', right_button='nav_right_button', left_button='nav_left_button'))
        self.__on_scales_closed.subject = scales
        self._model.scalesView = scales
        return scales

    def _init_scales(self):
        self._dialog_modes.add_mode('scales', self._create_scales())
        super(Push2, self)._init_scales()

    def _create_scales_enabler(self):
        return ScalesEnabler(enter_dialog_mode=self._enter_dialog_mode, exit_dialog_mode=self._exit_dialog_mode, is_enabled=False, is_root=True, layer=Layer(toggle_button='scale_presets_button'))

    @listens('close')
    def __on_scales_closed(self):
        self._dialog_modes.selected_mode = None

    def _create_clip_mode(self):
        base_loop_layer = Layer(shift_button='shift_button', loop_button='track_state_buttons_raw[1]', zoom_encoder='fine_grain_param_controls_raw[0]', encoders=self.elements.global_param_controls.submatrix[1:4, :])
        self._loop_controller = LoopSettingsControllerComponent(is_enabled=False)
        self._model.loopSettingsView = self._loop_controller
        audio_clip_layer = Layer(warp_mode_encoder='parameter_controls_raw[5]', transpose_encoder='parameter_controls_raw[6]', detune_encoder=self._with_shift('parameter_controls_raw[6]'), gain_encoder='parameter_controls_raw[7]', shift_button='shift_button')
        audio_clip_controller = AudioClipSettingsControllerComponent(is_enabled=False)
        self._model.audioClipSettingsView = audio_clip_controller
        clip_control_mode_selector = ModesComponent(is_enabled=False)
        clip_control_mode_selector.add_mode('midi', [make_freeze_aware(self._loop_controller, base_loop_layer + Layer(encoders=self.elements.global_param_controls.submatrix[:3, :]))])
        clip_control_mode_selector.add_mode('audio', [make_freeze_aware(self._loop_controller, base_loop_layer + Layer(encoders=self.elements.global_param_controls.submatrix[1:4, :])), make_freeze_aware(audio_clip_controller, audio_clip_layer)])
        clip_control_mode_selector.add_mode('no_clip', [])
        clip_control_mode_selector.selected_mode = 'no_clip'
        clip_control = ClipControlComponent(loop_controller=self._loop_controller, audio_clip_controller=audio_clip_controller, mode_selector=clip_control_mode_selector, decorator_factory=self._clip_decorator_factory, is_enabled=False)
        self._model.clipView = clip_control
        return [clip_control_mode_selector,
         make_freeze_aware(self._loop_controller, base_loop_layer),
         make_freeze_aware(audio_clip_controller, audio_clip_layer),
         clip_control]

    def _init_quantize_actions(self):
        self._quantize_settings = QuantizationSettingsComponent(name='Quantization_Settings', quantization_names=QUANTIZATION_NAMES_UNICODE, is_enabled=False, layer=make_dialog_layer(swing_amount_encoder='parameter_controls_raw[0]', quantize_to_encoder='parameter_controls_raw[1]', quantize_amount_encoder='parameter_controls_raw[2]', record_quantization_encoder='parameter_controls_raw[4]', record_quantization_toggle_button='track_state_buttons_raw[4]', priority=consts.MOMENTARY_DIALOG_PRIORITY))
        self._model.quantizeSettingsView = self._quantize_settings
        self._quantize = self._for_non_frozen_tracks(QuantizationComponent(name='Selected_Clip_Quantize', settings=self._quantize_settings, is_enabled=False, layer=Layer(action_button='quantize_button')), is_root=True)

    def _init_fixed_length(self):
        super(Push2, self)._init_fixed_length()
        self._fixed_length_settings_component.layer = make_dialog_layer(length_option_buttons='select_buttons', fixed_length_toggle_button='track_state_buttons_raw[0]', priority=consts.MOMENTARY_DIALOG_PRIORITY)
        self._model.fixedLengthSelectorView = self._fixed_length_settings_component
        self._model.fixedLengthSettings = self._fixed_length_setting

    def _init_value_components(self):
        super(Push2, self)._init_value_components()
        self._model.importantGlobals.swing = self._swing_amount.display
        self._model.importantGlobals.tempo = self._tempo.display
        self._model.importantGlobals.masterVolume = self._master_vol.display
        self._model.importantGlobals.cueVolume = self._master_cue_vol.display

    def _create_main_modes_layer(self):
        return Layer(mix_button='mix_button', clip_button='clip_mode_button', device_button='device_mode_button', browse_button='browse_mode_button', add_device_button='create_device_button', add_track_button='create_track_button') + Layer(user_button='user_button', priority=consts.USER_BUTTON_PRIORITY)

    def _should_send_palette(self):
        return self._firmware_version <= FirmwareVersion(0, 5, 28)

    def _send_color_palette(self):
        if self._should_send_palette():
            with self.component_guard():
                palette_entry = SysexElement(sysex.make_rgb_palette_entry_message)
                finalize_palette = SysexElement(sysex.make_reapply_palette_message)
                for index, hex_color, white_balance in COLOR_TABLE:
                    palette_entry.send_value(index, hex_color, white_balance)

                finalize_palette.send_value()

    def _init_pad_curve(self):
        self._pad_curve_sender = PadVelocityCurveSender(curve_sysex_element=SysexElement(sysex.make_pad_velocity_curve_message), threshold_sysex_element=SysexElement(sysex.make_pad_threshold_message), settings=self._setup_settings.pad_settings, chunk_size=sysex.PAD_VELOCITY_CURVE_CHUNK_SIZE)

    def _create_user_component(self):
        self._user_mode_ui_blocker = Component(is_enabled=False, layer=self._create_message_box_background_layer())
        sysex_control = SysexElement(send_message_generator=sysex.make_mode_switch_messsage, sysex_identifier=sysex.make_message_identifier(sysex.MODE_SWITCH_MESSAGE_ID))
        user = UserComponent(value_control=sysex_control, is_enabled=True, is_root=True)
        return user

    def _create_settings(self):
        return create_settings(preferences=self.preferences)

    def _init_hardware_settings(self):
        self._setup_settings = self.register_disconnectable(Settings(preferences=self.preferences))
        self._hardware_settings = HardwareSettingsComponent(led_brightness_element=SysexElement(sysex.make_led_brightness_message), display_brightness_element=SysexElement(sysex.make_display_brightness_message), settings=self._setup_settings.hardware)

    def _init_setup_component(self):
        self._setup_settings.general.workflow = 'scene' if self._settings['workflow'].value else 'clip'
        self.__on_workflow_setting_changed.subject = self._setup_settings.general
        self.__on_new_waveform_navigation_setting_changed.subject = self._setup_settings.experimental
        self.__on_new_waveform_navigation_setting_changed(self._setup_settings.experimental.new_waveform_navigation)
        setup = SetupComponent(name='Setup', settings=self._setup_settings, pad_curve_sender=self._pad_curve_sender, in_developer_mode=self._c_instance.in_developer_mode, is_enabled=False, layer=make_dialog_layer(category_radio_buttons='select_buttons', priority=consts.SETUP_DIALOG_PRIORITY))
        setup.general.layer = Layer(workflow_encoder='parameter_controls_raw[0]', display_brightness_encoder='parameter_controls_raw[1]', led_brightness_encoder='parameter_controls_raw[2]', priority=consts.SETUP_DIALOG_PRIORITY)
        setup.pad_settings.layer = Layer(sensitivity_encoder='parameter_controls_raw[4]', gain_encoder='parameter_controls_raw[5]', dynamics_encoder='parameter_controls_raw[6]', priority=consts.SETUP_DIALOG_PRIORITY)
        setup.display_debug.layer = Layer(show_row_spaces_button='track_state_buttons_raw[0]', show_row_margins_button='track_state_buttons_raw[1]', show_row_middle_button='track_state_buttons_raw[2]', show_button_spaces_button='track_state_buttons_raw[3]', show_unlit_button_button='track_state_buttons_raw[4]', show_lit_button_button='track_state_buttons_raw[5]', priority=consts.SETUP_DIALOG_PRIORITY)
        setup.profiling.layer = Layer(show_qml_stats_button='track_state_buttons_raw[0]', show_usb_stats_button='track_state_buttons_raw[1]', show_realtime_ipc_stats_button='track_state_buttons_raw[2]', priority=consts.SETUP_DIALOG_PRIORITY)
        setup.experimental.layer = Layer(new_waveform_navigation_button='track_state_buttons_raw[0]', priority=consts.SETUP_DIALOG_PRIORITY)
        self._model.setupView = setup
        self._setup_enabler = EnablingModesComponent(component=setup, enabled_color='DefaultButton.On', disabled_color='DefaultButton.On')
        self._setup_enabler.layer = Layer(cycle_mode_button='setup_button')

    def _init_firmware_update(self):
        self._firmware_update = FirmwareUpdateComponent(layer=self._create_message_box_background_layer())
        self._model.firmwareUpdate = self._firmware_update

    @listens('workflow')
    def __on_workflow_setting_changed(self, value):
        self._settings['workflow'].value = value == 'scene'

    @listens('new_waveform_navigation')
    def __on_new_waveform_navigation_setting_changed(self, value):
        self._device_component.use_waveform_navigation = value

    def _create_note_mode(self):

        class NoteLayoutSwitcher(Component):
            cycle_button = ButtonControl()

            def __init__(self, switch_note_mode_layout = None, *a, **k):
                raise switch_note_mode_layout is not None or AssertionError
                super(NoteLayoutSwitcher, self).__init__(*a, **k)
                self._switch_note_mode_layout = switch_note_mode_layout

            @cycle_button.pressed
            def cycle_button(self, button):
                self._switch_note_mode_layout()

        note_layout_switcher = NoteLayoutSwitcher(switch_note_mode_layout=self._switch_note_mode_layout, is_enabled=False, layer=Layer(cycle_button='layout_button'))
        return super(Push2, self)._create_note_mode() + [note_layout_switcher]

    def _create_note_mode_behaviour(self):
        return self._auto_arm.auto_arm_restore_behaviour()

    def _create_controls(self):

        class Deleter(object):

            @property
            def is_deleting(_):
                return self._delete_default_component.is_deleting

            def delete_clip_envelope(_, param):
                return self._delete_default_component.delete_clip_envelope(param)

        self.elements = Elements(deleter=Deleter(), undo_handler=self.song, playhead=self._c_instance.playhead, model=self._model)
        self.__on_param_encoder_touched.replace_subjects(self.elements.global_param_touch_buttons_raw)
        self._update_encoder_model()

    def _update_full_velocity(self, accent_is_active):
        super(Push2, self)._update_full_velocity(accent_is_active)
        self._slice_step_sequencer.full_velocity = accent_is_active

    def _update_playhead_color(self, color):
        super(Push2, self)._update_playhead_color(color)
        self._slice_step_sequencer.playhead_color = color

    @listens_group('value')
    def __on_param_encoder_touched(self, value, encoder):
        self._update_encoder_model()

    def _update_encoder_model(self):
        self._model.controls.encoders = [ NamedTuple(__id__='encoder_%i' % i, touched=e.is_pressed()) for i, e in enumerate(self.elements.global_param_touch_buttons_raw) ]

    def _with_firmware_version(self, major_version, minor_version, control_element):
        """
        We consider all features to be available for Push 2
        """
        return control_element

    def _send_hardware_settings(self):
        self._hardware_settings.send()
        self._pad_curve_sender.send()
        self._send_color_palette()

    def port_settings_changed(self):
        super(Push2, self).port_settings_changed()
        if self._initialized:
            self._send_hardware_settings()
            self.update()

    def on_identified(self, response_bytes):
        try:
            major, minor, build, sn, board_revision = sysex.extract_identity_response_info(response_bytes)
            self._model.firmwareInfo.major = major
            self._model.firmwareInfo.minor = minor
            self._model.firmwareInfo.build = build
            self._model.firmwareInfo.serialNumber = sn
            logger.info('Push 2 identified')
            logger.info('Firmware %i.%i Build %i' % (major, minor, build))
            logger.info('Serial number %i' % sn)
            logger.info('Board Revision %i' % board_revision)
            self._firmware_version = FirmwareVersion(major, minor, build)
            self._board_revision = board_revision
            self._identified = True
            self._try_initialize()
        except IndexError:
            logger.warning("Couldn't identify Push 2 unit")

    def update(self):
        if self._initialized:
            super(Push2, self).update()

    def request_zoom(self, zoom_factor):
        mode = self._main_modes.selected_mode
        if mode == 'device':
            self._device_component.request_zoom(zoom_factor)
        elif mode == 'clip':
            self._loop_controller.request_zoom(zoom_factor)