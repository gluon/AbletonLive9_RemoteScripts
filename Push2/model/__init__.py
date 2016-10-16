#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/model/__init__.py
from __future__ import absolute_import, print_function
from .declaration import Binding, custom_property, id_property, listmodel, listof, view_property, ViewModel, ModelVisitor
from .repr import BrowserItemAdapter, BrowserListWrapper, ClipAdapter, DeviceAdapter, DeviceParameterAdapter, EditModeOptionAdapter, ItemListAdapter, ItemSlotAdapter, LiveDialogAdapter, OptionsListAdapter, SimplerDeviceAdapter, TrackAdapter, TrackControlAdapter, TrackListAdapter, VisibleAdapter
__all__ = (ModelVisitor,)

class VisibleModel(ViewModel):
    visible = view_property(bool, False)


class Track(Binding):
    ADAPTER = TrackAdapter
    name = view_property(unicode, '')
    colorIndex = view_property(int, -1)
    isFoldable = view_property(bool, False)
    containsDrumRack = view_property(bool, False)
    canShowChains = view_property(bool, False)
    nestingLevel = view_property(int, 0)
    activated = view_property(bool, True)
    isFrozen = view_property(bool, True)
    parentColorIndex = view_property(int, -1)
    arm = view_property(bool, False)
    isMaster = view_property(bool, False)
    isAudio = view_property(bool, False)
    id = id_property()


class TrackListModel(Binding):
    ADAPTER = TrackListAdapter
    visible = view_property(bool, False)
    tracks = view_property(listof(Track))
    selectedTrack = view_property(Track)
    absolute_selected_track_index = view_property(int, -1)


class Device(Binding):
    ADAPTER = DeviceAdapter
    name = view_property(unicode, '')
    nestingLevel = view_property(int, 0)
    is_active = view_property(bool, False)
    id = id_property()
    class_name = view_property(unicode, '')
    icon = view_property(unicode, '')


class DeviceListModel(Binding):
    ADAPTER = ItemListAdapter
    visible = view_property(bool, False)
    items = view_property(listof(Device))
    selectedItem = view_property(Device)
    moving = view_property(bool, False)


class ItemSlotModel(Binding):
    ADAPTER = ItemSlotAdapter
    name = view_property(unicode, '')
    icon = view_property(unicode, '')


class ParameterBankListModel(Binding):
    ADAPTER = ItemListAdapter
    visible = view_property(bool, False)
    items = view_property(listof(ItemSlotModel))
    selectedItem = view_property(ItemSlotModel)


class EditModeOption(Binding):
    ADAPTER = EditModeOptionAdapter
    firstChoice = view_property(unicode, '')
    secondChoice = view_property(unicode, '')
    activeIndex = view_property(int, 0)
    active = view_property(bool, False)


class EditModeOptionsModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    device = view_property(unicode, '')
    options = view_property(listof(EditModeOption))


class Chain(Binding):
    ADAPTER = ItemSlotAdapter
    name = view_property(unicode, '')
    id = id_property()
    icon = view_property(unicode, '')


class ChainListModel(Binding):
    ADAPTER = ItemListAdapter
    visible = view_property(bool, False)
    items = view_property(listof(Chain))
    selectedItem = view_property(Chain)


class MixerSelectionListModel(Binding):
    ADAPTER = OptionsListAdapter
    visible = view_property(bool, False)
    items = view_property(listof(ItemSlotModel))
    selectedItem = view_property(unicode, '')


class TrackMixerSelectionListModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    items = view_property(listof(ItemSlotModel))


class DeviceParameter(Binding):
    ADAPTER = DeviceParameterAdapter
    name = view_property(unicode, '')
    original_name = view_property(unicode, '')
    min = view_property(float, 0.0)
    max = view_property(float, 0.0)
    value = view_property(float, 0.0)
    valueItems = view_property(listof(unicode))
    displayValue = view_property(unicode, '')
    unit = view_property(unicode, '')
    id = id_property()
    is_enabled = view_property(bool, True)
    hasAutomation = view_property(bool, False)
    automationActive = view_property(bool, False)
    isActive = view_property(bool, True)


class Encoder(Binding):
    id = id_property()
    touched = view_property(bool, False)


class Controls(ViewModel):
    encoders = view_property(listof(Encoder))


class Slice(Binding):
    id = id_property()
    time = view_property(int, -1)


class Sample(Binding):
    start_marker = view_property(int, 0)
    end_marker = view_property(int, 0)
    length = view_property(int, 0)


class SimplerView(Binding):
    sample_start = view_property(int, 0)
    sample_end = view_property(int, 0)
    sample_loop_start = view_property(int, 0)
    sample_loop_end = view_property(int, 0)
    sample_loop_fade = view_property(int, 0)
    sample_env_fade_in = view_property(int, 0)
    sample_env_fade_out = view_property(int, 0)


class WaveformNavigationFocusMarker(Binding):
    name = view_property(unicode, u'')
    position = view_property(int, -1)


class WaveformNavigation(Binding):
    animate_visible_region = view_property(bool, False)
    visible_start = view_property(float, 0.0, depends=animate_visible_region)
    visible_end = view_property(float, 0.0, depends=animate_visible_region)
    show_focus = view_property(bool, False)
    focus_marker = view_property(WaveformNavigationFocusMarker)


class SimplerProperties(Binding):
    ADAPTER = SimplerDeviceAdapter
    sample_start = view_property(DeviceParameter)
    sample_length = view_property(DeviceParameter)
    loop_length = view_property(DeviceParameter)
    loop_on = view_property(DeviceParameter)
    zoom = view_property(DeviceParameter)
    gain = view_property(float, 0.0)
    start_marker = view_property(int, 0)
    end_marker = view_property(int, 0)
    multi_sample_mode = view_property(bool, False)
    current_playback_mode = view_property(int, 0)
    slices = view_property(listmodel(Slice))
    selected_slice = view_property(Slice)
    playhead_real_time_channel_id = view_property(unicode, '')
    waveform_real_time_channel_id = view_property(unicode, '')
    sample = view_property(Sample)
    view = view_property(SimplerView)
    waveform_navigation = view_property(WaveformNavigation)


class DeviceParameterListModel(ViewModel):
    visible = view_property(bool, False)
    deviceType = view_property(unicode, '')
    parameters = view_property(listof(DeviceParameter))


class SimplerDeviceViewModel(ViewModel):
    visible = view_property(bool, False)
    deviceType = view_property(unicode, '')
    simpler = view_property(Device)
    parameters = view_property(listof(DeviceParameter))
    properties = view_property(SimplerProperties)
    wants_waveform_shown = view_property(bool, False)
    processed_zoom_requests = view_property(int, 0)


class RealTimeChannel(Binding):
    channel_id = view_property(unicode, '')
    object_id = view_property(unicode, '')


class TrackControlModel(Binding):
    ADAPTER = TrackControlAdapter
    visible = view_property(bool, False)
    parameters = view_property(listof(DeviceParameter))
    scrollOffset = view_property(int, 0)
    real_time_meter_channel = view_property(RealTimeChannel)


class BrowserListView(Binding):
    id = id_property()
    selected_index = view_property(int, -1)


class BrowserItem(Binding):
    ADAPTER = BrowserItemAdapter
    id = id_property()
    name = view_property(unicode, '')
    icon = view_property(unicode, '')
    is_loadable = view_property(bool, False)


class BrowserModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    lists = view_property(listmodel(BrowserListView))
    scrolling = view_property(bool, False)
    horizontal_navigation = view_property(bool, False)
    focused_list_index = view_property(int, -1)
    focused_item = view_property(BrowserItem)
    list_offset = view_property(int, 0)
    can_enter = view_property(bool, False)
    can_exit = view_property(bool, False)
    expanded = view_property(bool, False)
    load_text = view_property(unicode, u'')
    prehear_enabled = view_property(bool, False)
    context_text = view_property(unicode, u'')
    context_color_index = view_property(int, -1)


class BrowserList(Binding):
    id = id_property()
    items = custom_property(listmodel(BrowserItem), wrapper_class=BrowserListWrapper)


class BrowserData(Binding):
    lists = view_property(listmodel(BrowserList))


class Notification(Binding):
    visible = view_property(bool, False)
    message = view_property(unicode, '')


class RealTimeClient(Binding):
    clientId = view_property(unicode, '')


class ConvertModel(Binding):
    ADAPTER = VisibleAdapter
    source_color_index = view_property(int, -1)
    source_name = view_property(unicode, '')
    visible = view_property(bool, False)
    available_conversions = view_property(listof(unicode))


class NoteLayout(Binding):
    is_in_key = view_property(bool, False)
    is_fixed = view_property(bool, False)


class ScalesModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    scale_names = view_property(listof(unicode), '')
    selected_scale_index = view_property(int, -1)
    root_note_names = view_property(listof(unicode), '')
    selected_root_note_index = view_property(int, -1)
    note_layout = view_property(NoteLayout)
    horizontal_navigation = view_property(bool, False)


class QuantizeSettingsModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    swing_amount = view_property(float, 0.0)
    quantize_to_index = view_property(int, -1)
    quantize_amount = view_property(float, 0.0)
    record_quantization_index = view_property(int, -1)
    record_quantization_enabled = view_property(bool, False)
    quantization_option_names = view_property(listof(unicode))


class StepSettingsModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)


class StepAutomationSettingsModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    deviceType = view_property(unicode, '')
    parameters = view_property(listof(DeviceParameter))
    can_automate_parameters = view_property(bool, False)


class NoteSettingModel(Binding):
    min = view_property(float, 0.0)
    max = view_property(float, 0.0)


class NoteSettingsModel(Binding):
    ADAPTER = VisibleAdapter
    nudge = view_property(NoteSettingModel)
    coarse = view_property(NoteSettingModel)
    fine = view_property(NoteSettingModel)
    velocity = view_property(NoteSettingModel)
    color_index = view_property(int, -1)
    visible = view_property(bool, False)


class FixedLengthSettingsModel(Binding):
    option_names = view_property(listof(unicode))
    selected_index = view_property(int, -1)
    enabled = view_property(bool, False)


class FixedLengthSelectorModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)


class LoopSettingsModel(Binding):
    looping = view_property(bool, False)
    loop_parameters = view_property(listof(DeviceParameter))
    zoom = view_property(DeviceParameter)
    processed_zoom_requests = view_property(int, 0)
    waveform_navigation = view_property(WaveformNavigation)


class AudioClipSettingsModel(Binding):
    warping = view_property(bool, False)
    gain = view_property(float, 0.0)
    audio_parameters = view_property(listof(DeviceParameter))
    waveform_real_time_channel_id = view_property(unicode, '')
    playhead_real_time_channel_id = view_property(unicode, '')


class ClipViewModel(Binding):
    sample_length = view_property(int, -1)
    sample_start_marker = view_property(int, -1)
    sample_end_marker = view_property(int, -1)
    sample_loop_start = view_property(int, -1)
    sample_loop_end = view_property(int, -1)


class ClipModel(Binding):
    ADAPTER = ClipAdapter
    id = id_property()
    name = view_property(unicode, '')
    color_index = view_property(int, -1)
    is_recording = view_property(bool, False)
    view = view_property(ClipViewModel)


class ClipControlModel(Binding):
    clip = view_property(ClipModel)


class ModeState(Binding):
    main_mode = view_property(unicode, '')
    mix_mode = view_property(unicode, '')
    global_mix_mode = view_property(unicode, '')
    device_mode = view_property(unicode, '')


class MixerRealTimeMeterModel(Binding):
    real_time_meter_channel_ids = view_property(listof(unicode), '')


class MixerViewModel(ViewModel):
    volumeControlListView = view_property(DeviceParameterListModel)
    panControlListView = view_property(DeviceParameterListModel)
    trackControlView = view_property(TrackControlModel)
    sendControlListView = view_property(DeviceParameterListModel)
    realtimeMeterData = view_property(listof(RealTimeChannel))


class GeneralSettingsModel(Binding):
    workflow = view_property(unicode, 'scene')


class PadSettingsModel(Binding):
    sensitivity = view_property(int, 0)
    min_sensitivity = view_property(int, 0)
    max_sensitivity = view_property(int, 0)
    gain = view_property(int, 0)
    min_gain = view_property(int, 0)
    max_gain = view_property(int, 0)
    dynamics = view_property(int, 0)
    min_dynamics = view_property(int, 0)
    max_dynamics = view_property(int, 0)


class HardwareSettingsModel(Binding):
    min_led_brightness = view_property(int, 0)
    max_led_brightness = view_property(int, 0)
    led_brightness = view_property(int, 0)
    min_display_brightness = view_property(int, 0)
    max_display_brightness = view_property(int, 0)
    display_brightness = view_property(int, 0)


class DisplayDebugSettingsModel(Binding):
    show_row_spaces = view_property(bool, False)
    show_row_margins = view_property(bool, False)
    show_row_middle = view_property(bool, False)
    show_button_spaces = view_property(bool, False)
    show_unlit_button = view_property(bool, False)
    show_lit_button = view_property(bool, False)


class ProfilingSettingsModel(Binding):
    show_qml_stats = view_property(bool, False)
    show_usb_stats = view_property(bool, False)
    show_realtime_ipc_stats = view_property(bool, False)


class ExperimentalSettingsModel(Binding):
    new_waveform_navigation = view_property(bool, False)


class SettingsModel(Binding):
    general = view_property(GeneralSettingsModel)
    pad_settings = view_property(PadSettingsModel)
    hardware = view_property(HardwareSettingsModel)
    display_debug = view_property(DisplayDebugSettingsModel)
    profiling = view_property(ProfilingSettingsModel)
    experimental = view_property(ExperimentalSettingsModel)


class VelocityCurveModel(Binding):
    curve_points = view_property(listof(int))


class SetupModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    settings = view_property(SettingsModel)
    selected_mode = view_property(unicode, '')
    modes = view_property(listof(unicode))
    velocity_curve = view_property(VelocityCurveModel)


class ValueModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    value_string = view_property(unicode, '')


class ImportantGlobals(ViewModel):
    masterVolume = view_property(ValueModel)
    cueVolume = view_property(ValueModel)
    swing = view_property(ValueModel)
    tempo = view_property(ValueModel)


class FirmwareInfo(ViewModel):
    major = view_property(int, 0)
    minor = view_property(int, 0)
    build = view_property(int, 0)
    serialNumber = view_property(int, 0)


class FirmwareUpdateModel(Binding):
    ADAPTER = VisibleAdapter
    visible = view_property(bool, False)
    firmware_file = view_property(unicode, u'')
    data_file = view_property(unicode, u'')
    state = view_property(unicode, u'')


class LiveDialogViewModel(Binding):
    ADAPTER = LiveDialogAdapter
    visible = view_property(bool, False)
    text = view_property(unicode, u'')
    can_cancel = view_property(bool, False)


class RootModel(ViewModel):
    notificationView = view_property(Notification)
    realTimeClient = view_property(RealTimeClient)
    modeState = view_property(ModeState)
    controls = view_property(Controls)
    liveDialogView = view_property(LiveDialogViewModel)
    mixerSelectView = view_property(MixerSelectionListModel)
    trackMixerSelectView = view_property(TrackMixerSelectionListModel)
    devicelistView = view_property(DeviceListModel)
    editModeOptionsView = view_property(EditModeOptionsModel)
    deviceParameterView = view_property(DeviceParameterListModel)
    simplerDeviceView = view_property(SimplerDeviceViewModel)
    mixerView = view_property(MixerViewModel)
    tracklistView = view_property(TrackListModel)
    chainListView = view_property(ChainListModel)
    parameterBankListView = view_property(ParameterBankListModel)
    browserView = view_property(BrowserModel)
    browserData = view_property(BrowserData)
    convertView = view_property(ConvertModel)
    scalesView = view_property(ScalesModel)
    quantizeSettingsView = view_property(QuantizeSettingsModel)
    fixedLengthSelectorView = view_property(FixedLengthSelectorModel)
    fixedLengthSettings = view_property(FixedLengthSettingsModel)
    noteSettingsView = view_property(NoteSettingsModel)
    stepSettingsView = view_property(StepSettingsModel)
    stepAutomationSettingsView = view_property(StepAutomationSettingsModel)
    audioClipSettingsView = view_property(AudioClipSettingsModel)
    loopSettingsView = view_property(LoopSettingsModel)
    clipView = view_property(ClipControlModel)
    setupView = view_property(SetupModel)
    importantGlobals = view_property(ImportantGlobals)
    firmwareInfo = view_property(FirmwareInfo)
    firmwareUpdate = view_property(FirmwareUpdateModel)