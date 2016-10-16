#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_MxDCore/LomTypes.py
import types
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ControlElement import ControlElement
from _Framework.Util import is_iterable
_DEVICE_BASE_PROPS = ['canonical_parent',
 'parameters',
 'view',
 'can_have_chains',
 'can_have_drum_pads',
 'class_display_name',
 'class_name',
 'is_active',
 'name',
 'type',
 'store_chosen_bank']
_DEVICE_VIEW_BASE_PROPS = ['canonical_parent', 'is_collapsed']
EXPOSED_TYPE_PROPERTIES = {Live.Application.Application: ('view', 'current_dialog_button_count', 'current_dialog_message', 'open_dialog_count', 'get_bugfix_version', 'get_document', 'get_major_version', 'get_minor_version', 'press_current_dialog_button'),
 Live.Application.Application.View: ('canonical_parent', 'browse_mode', 'available_main_views', 'focus_view', 'hide_view', 'is_view_visible', 'scroll_view', 'show_view', 'toggle_browse', 'zoom_view'),
 Live.Chain.Chain: ('canonical_parent', 'name', 'devices', 'delete_device', 'mute', 'solo', 'muted_via_solo', 'mixer_device', 'color', 'color_index', 'is_auto_colored', 'has_audio_input', 'has_audio_output', 'has_midi_input', 'has_midi_output'),
 Live.ChainMixerDevice.ChainMixerDevice: ('canonical_parent', 'volume', 'panning', 'sends', 'chain_activator'),
 Live.Clip.Clip: ('canonical_parent', 'view', 'color', 'color_index', 'end_marker', 'has_envelopes', 'is_arrangement_clip', 'is_audio_clip', 'is_midi_clip', 'is_overdubbing', 'is_playing', 'is_recording', 'is_triggered', 'length', 'loop_end', 'loop_start', 'looping', 'muted', 'name', 'playing_position', 'position', 'signature_denominator', 'signature_numerator', 'start_marker', 'start_time', 'will_record_on_start', 'clear_all_envelopes', 'clear_envelope', 'deselect_all_notes', 'duplicate_loop', 'fire', 'get_notes', 'get_selected_notes', 'move_playing_pos', 'quantize', 'quantize_pitch', 'remove_notes', 'replace_selected_notes', 'scrub', 'select_all_notes', 'set_fire_button_state', 'set_notes', 'stop', 'stop_scrub', 'available_warp_modes', 'file_path', 'gain', 'gain_display_string', 'pitch_coarse', 'pitch_fine', 'ram_mode', 'warp_mode', 'warping'),
 Live.Clip.Clip.View: ('canonical_parent', 'grid_is_triplet', 'grid_quantization', 'hide_envelope', 'select_envelope_parameter', 'show_envelope', 'show_loop'),
 Live.ClipSlot.ClipSlot: ('canonical_parent', 'clip', 'color', 'color_index', 'controls_other_clips', 'has_clip', 'has_stop_button', 'is_playing', 'is_recording', 'is_triggered', 'playing_status', 'will_record_on_start', 'create_clip', 'delete_clip', 'fire', 'set_fire_button_state', 'stop'),
 Live.Device.Device: tuple(_DEVICE_BASE_PROPS),
 Live.Device.Device.View: tuple(_DEVICE_VIEW_BASE_PROPS),
 Live.DeviceParameter.DeviceParameter: ('canonical_parent', 'automation_state', 'is_enabled', 'is_quantized', 'max', 'min', 'name', 'original_name', 'state', 'value', 'value_items', 're_enable_automation', 'str_for_value', '__str__'),
 Live.DrumPad.DrumPad: ('canonical_parent', 'chains', 'mute', 'name', 'note', 'solo', 'delete_all_chains'),
 Live.MaxDevice.MaxDevice: tuple(_DEVICE_BASE_PROPS + ['get_bank_count', 'get_bank_name', 'get_bank_parameters']),
 Live.MixerDevice.MixerDevice: ('canonical_parent', 'sends', 'panning', 'track_activator', 'volume', 'crossfade_assign'),
 Live.PluginDevice.PluginDevice: tuple(_DEVICE_BASE_PROPS + ['presets', 'selected_preset_index']),
 Live.RackDevice.RackDevice: tuple(_DEVICE_BASE_PROPS + ['chains',
                              'drum_pads',
                              'return_chains',
                              'visible_drum_pads',
                              'has_macro_mappings',
                              'copy_pad',
                              'has_drum_pads']),
 Live.RackDevice.RackDevice.View: tuple(_DEVICE_VIEW_BASE_PROPS + ['selected_chain',
                                   'is_showing_chain_devices',
                                   'selected_drum_pad',
                                   'drum_pads_scroll_position']),
 Live.Sample.Sample: ('canonical_parent', 'beats_granulation_resolution', 'beats_transient_envelope', 'beats_transient_loop_mode', 'complex_pro_envelope', 'complex_pro_formants', 'end_marker', 'file_path', 'gain', 'length', 'slicing_sensitivity', 'start_marker', 'texture_flux', 'texture_grain_size', 'tones_grain_size', 'warp_mode', 'warping', 'gain_display_string', 'insert_slice', 'move_slice', 'remove_slice'),
 Live.Scene.Scene: ('canonical_parent', 'clip_slots', 'color', 'color_index', 'is_empty', 'is_triggered', 'name', 'tempo', 'fire', 'fire_as_selected', 'set_fire_button_state'),
 Live.SimplerDevice.SimplerDevice: tuple(_DEVICE_BASE_PROPS + ['sample',
                                    'can_warp_as',
                                    'can_warp_double',
                                    'can_warp_half',
                                    'multi_sample_mode',
                                    'pad_slicing',
                                    'playback_mode',
                                    'playing_position',
                                    'playing_position_enabled',
                                    'retrigger',
                                    'slicing_playback_mode',
                                    'voices',
                                    'crop',
                                    'guess_playback_length',
                                    'reverse',
                                    'warp_as',
                                    'warp_double',
                                    'warp_half']),
 Live.SimplerDevice.SimplerDevice.View: tuple(_DEVICE_VIEW_BASE_PROPS + ['selected_slice']),
 Live.Song.Song: ('cue_points', 'return_tracks', 'scenes', 'tracks', 'visible_tracks', 'master_track', 'view', 'appointed_device', 'arrangement_overdub', 'back_to_arranger', 'can_jump_to_next_cue', 'can_jump_to_prev_cue', 'can_redo', 'can_undo', 'clip_trigger_quantization', 'current_song_time', 'exclusive_arm', 'exclusive_solo', 'groove_amount', 'is_playing', 'last_event_time', 'loop', 'loop_length', 'loop_start', 'metronome', 'midi_recording_quantization', 'nudge_down', 'overdub', 'punch_in', 'punch_out', 'nudge_up', 're_enable_automation_enabled', 'record_mode', 'root_note', 'scale_name', 'select_on_launch', 'session_automation_record', 'session_record', 'session_record_status', 'signature_denominator', 'signature_numerator', 'song_length', 'swing_amount', 'tempo', 'capture_and_insert_scene', 'continue_playing', 'create_audio_track', 'create_midi_track', 'create_return_track', 'create_scene', 'delete_scene', 'delete_track', 'duplicate_scene', 'duplicate_track', 'find_device_position', 'get_beats_loop_length', 'get_beats_loop_start', 'get_current_beats_song_time', 'get_current_smpte_song_time', 'is_cue_point_selected', 'jump_by', 'jump_to_next_cue', 'jump_to_prev_cue', 'move_device', 'play_selection', 're_enable_automation', 'redo', 'scrub_by', 'set_or_delete_cue', 'start_playing', 'stop_all_clips', 'stop_playing', 'tap_tempo', 'trigger_session_record', 'undo'),
 Live.Song.Song.View: ('canonical_parent', 'detail_clip', 'highlighted_clip_slot', 'selected_chain', 'selected_parameter', 'selected_scene', 'selected_track', 'draw_mode', 'follow_song', 'select_device'),
 Live.Song.CuePoint: ('canonical_parent', 'name', 'time', 'jump'),
 Live.Track.Track: ('clip_slots', 'devices', 'canonical_parent', 'mixer_device', 'view', 'arm', 'can_be_armed', 'can_be_frozen', 'can_show_chains', 'color', 'color_index', 'current_input_routing', 'current_input_sub_routing', 'current_monitoring_state', 'current_output_routing', 'current_output_sub_routing', 'fired_slot_index', 'has_audio_input', 'has_audio_output', 'has_midi_input', 'has_midi_output', 'implicit_arm', 'input_meter_level', 'input_routings', 'input_sub_routings', 'input_meter_left', 'input_meter_right', 'is_foldable', 'is_frozen', 'is_grouped', 'is_part_of_selection', 'is_showing_chains', 'is_visible', 'mute', 'muted_via_solo', 'name', 'output_meter_left', 'output_meter_level', 'output_meter_right', 'output_routings', 'output_sub_routings', 'playing_slot_index', 'solo', 'delete_device', 'duplicate_clip_slot', 'jump_in_running_session_clip', 'stop_all_clips'),
 Live.Track.Track.View: ('canonical_parent', 'selected_device', 'device_insert_mode', 'is_collapsed', 'select_instrument')}
HIDDEN_TYPE_PROPERTIES = {Live.Sample.Sample: ('slices',)}
ENUM_TYPES = (Live.Song.Quantization,
 Live.Song.RecordingQuantization,
 Live.Song.CaptureMode,
 Live.Clip.GridQuantization,
 Live.DeviceParameter.AutomationState)
TUPLE_TYPES = {'tracks': Live.Track.Track,
 'visible_tracks': Live.Track.Track,
 'return_tracks': Live.Track.Track,
 'clip_slots': Live.ClipSlot.ClipSlot,
 'scenes': Live.Scene.Scene,
 'parameters': Live.DeviceParameter.DeviceParameter,
 'sends': Live.DeviceParameter.DeviceParameter,
 'devices': Live.Device.Device,
 'cue_points': Live.Song.CuePoint,
 'chains': Live.Chain.Chain,
 'return_chains': Live.Chain.Chain,
 'drum_pads': Live.DrumPad.DrumPad,
 'visible_drum_pads': Live.DrumPad.DrumPad,
 'control_surfaces': ControlSurface,
 'components': ControlSurfaceComponent,
 'controls': ControlElement}
PROPERTY_TYPES = {'master_track': Live.Track.Track,
 'selected_track': Live.Track.Track,
 'selected_scene': Live.Scene.Scene,
 'volume': Live.DeviceParameter.DeviceParameter,
 'panning': Live.DeviceParameter.DeviceParameter,
 'crossfader': Live.DeviceParameter.DeviceParameter,
 'song_tempo': Live.DeviceParameter.DeviceParameter,
 'cue_volume': Live.DeviceParameter.DeviceParameter,
 'track_activator': Live.DeviceParameter.DeviceParameter,
 'chain_activator': Live.DeviceParameter.DeviceParameter,
 'clip': Live.Clip.Clip,
 'detail_clip': Live.Clip.Clip,
 'highlighted_clip_slot': Live.ClipSlot.ClipSlot,
 'selected_device': Live.Device.Device,
 'selected_parameter': Live.DeviceParameter.DeviceParameter,
 'selected_chain': Live.Chain.Chain,
 'selected_drum_pad': Live.DrumPad.DrumPad,
 'sample': Live.Sample.Sample,
 'mixer_device': (Live.MixerDevice.MixerDevice, Live.ChainMixerDevice.ChainMixerDevice),
 'view': (Live.Application.Application.View,
          Live.Song.Song.View,
          Live.Track.Track.View,
          Live.Device.Device.View,
          Live.RackDevice.RackDevice.View,
          Live.Clip.Clip.View)}
LIVE_APP = 'live_app'
LIVE_SET = 'live_set'
CONTROL_SURFACES = 'control_surfaces'
THIS_DEVICE = 'this_device'
ROOT_KEYS = (THIS_DEVICE,
 CONTROL_SURFACES,
 LIVE_APP,
 LIVE_SET)

class LomAttributeError(AttributeError):
    pass


class LomObjectError(AttributeError):
    pass


class LomNoteOperationWarning(Exception):
    pass


class LomNoteOperationError(AttributeError):
    pass


def is_class(class_object):
    return isinstance(class_object, types.ClassType) or hasattr(class_object, '__bases__')


def get_control_surfaces():
    result = []
    cs_list_key = 'control_surfaces'
    if isinstance(__builtins__, dict):
        if cs_list_key in __builtins__.keys():
            result = __builtins__[cs_list_key]
    elif hasattr(__builtins__, cs_list_key):
        result = getattr(__builtins__, cs_list_key)
    return tuple(result)


def get_root_prop(external_device, prop_key):
    root_properties = {LIVE_APP: Live.Application.get_application,
     LIVE_SET: lambda : Live.Application.get_application().get_document(),
     CONTROL_SURFACES: get_control_surfaces}
    if not prop_key in ROOT_KEYS:
        raise AssertionError
        return prop_key == THIS_DEVICE and external_device
    return root_properties[prop_key]()


def cs_base_classes():
    from _Framework.ControlSurface import ControlSurface
    from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
    from _Framework.ControlElement import ControlElement
    from ableton.v2.control_surface import ControlElement as ControlElement2
    from ableton.v2.control_surface import ControlSurface as ControlSurface2
    from ableton.v2.control_surface import Component as ControlSurfaceComponent2
    return (ControlSurface,
     ControlSurfaceComponent,
     ControlElement,
     ControlSurface2,
     ControlSurfaceComponent2,
     ControlElement2)


def is_lom_object(lom_object, lom_classes):
    return isinstance(lom_object, tuple(lom_classes) + (type(None),)) or isinstance(lom_object, cs_base_classes()) or isinstance(lom_object, Live.Base.Vector)


def is_cplusplus_lom_object(lom_object):
    return isinstance(lom_object, Live.LomObject.LomObject)


def is_object_iterable(obj):
    return not isinstance(obj, basestring) and is_iterable(obj) and not isinstance(obj, cs_base_classes())


def is_property_exposed(lom_object, property_name):
    return property_name in EXPOSED_TYPE_PROPERTIES.get(type(lom_object), [])


def is_property_hidden(lom_object, property_name):
    return property_name in HIDDEN_TYPE_PROPERTIES.get(type(lom_object), [])


def verify_object_property(lom_object, property_name):
    raise_error = False
    if isinstance(lom_object, cs_base_classes()):
        if not hasattr(lom_object, property_name):
            raise_error = True
    elif not (is_property_exposed(lom_object, property_name) or is_property_hidden(lom_object, property_name)):
        raise_error = True
    if raise_error:
        raise LomAttributeError("'%s' object has no attribute '%s'" % (lom_object.__class__.__name__, property_name))