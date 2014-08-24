#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_MxDCore/LomTypes.py
import Live
from _Tools import types
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ControlElement import ControlElement
from _Framework.Util import is_iterable
HIDDEN_TYPES = (Live.Browser.Browser, Live.Clip.AutomationEnvelope)
HIDDEN_PROPERTIES = ('begin_undo_step', 'end_undo_step', 'begin_gesture', 'end_gesture', 'automation_envelope')
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
 'mixer_device': (Live.MixerDevice.MixerDevice, Live.ChainMixerDevice.ChainMixerDevice),
 'view': (Live.Application.Application.View,
          Live.Song.Song.View,
          Live.Track.Track.View,
          Live.Device.Device.View,
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
    raise prop_key in ROOT_KEYS or AssertionError
    return external_device if prop_key == THIS_DEVICE else root_properties[prop_key]()


def cs_base_classes():
    from _Framework.ControlSurface import ControlSurface
    from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
    from _Framework.ControlElement import ControlElement
    return (ControlSurface, ControlSurfaceComponent, ControlElement)


def is_lom_object(lom_object, lom_classes):
    return isinstance(lom_object, tuple(lom_classes) + (type(None),)) or isinstance(lom_object, cs_base_classes()) or isinstance(lom_object, Live.Base.Vector)


def is_cplusplus_lom_object(lom_object):
    return isinstance(lom_object, Live.LomObject.LomObject)


def is_object_iterable(obj):
    return not isinstance(obj, basestring) and is_iterable(obj) and not isinstance(obj, cs_base_classes())


def verify_object_property(lom_object, property_name):
    if not hasattr(lom_object, property_name) or property_name in HIDDEN_PROPERTIES:
        raise LomAttributeError("'%s' object has no attribute '%s'" % (lom_object.__class__.__name__, property_name))