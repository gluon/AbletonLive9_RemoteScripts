#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_MxDCore/MxDCore.py
import Live.Base
from _Tools import types
import sys
import _Framework
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ControlElement import ControlElement
from _Framework.Debug import debug_print
from _Framework.Util import is_iterable
from MxDUtils import TupleWrapper, StringHandler

def get_control_surfaces():
    result = []
    cs_list_key = 'control_surfaces'
    if isinstance(__builtins__, dict):
        if cs_list_key in __builtins__.keys():
            result = __builtins__[cs_list_key]
    elif hasattr(__builtins__, cs_list_key):
        result = getattr(__builtins__, cs_list_key)
    return tuple(result)


def get_current_max_device(device_id):
    raise MxDCore.instance != None and MxDCore.instance.manager != None or AssertionError
    return MxDCore.instance.manager.get_max_device(device_id)


PATH_KEY = 'CURRENT_PATH'
ID_KEY = 'CURRENT_LOM_ID'
TYPE_KEY = 'CURRENT_TYPE'
PROP_KEY = 'CURRENT_PROPERTY'
PROP_LISTENER_KEY = 'PROPERTY_LISTENER'
PATH_LISTENER_KEY = 'PATH_LISTENERS'
OPEN_OPERATIONS_KEY = 'OPEN_OPERATION'
NOTE_BUFFER_KEY = 'NOTE_BUFFER'
NOTE_OPERATION_KEY = 'NOTE_OPERATION'
NOTE_COUNT_KEY = 'NOTE_COUNT'
NOTE_REPLACE_KEY = 'NOTE_REPLACE'
NOTE_SET_KEY = 'NOTE_SET'
CONTAINS_CS_ID_KEY = 'CONTAINS_CS_ID_KEY'
LAST_SENT_ID_KEY = 'LAST_SENT_ID'
LIVE_APP = 'live_app'
LIVE_SET = 'live_set'
CONTROL_SURFACES = 'control_surfaces'
THIS_DEVICE = 'this_device'
LISTENABLE_PATH_COMPONENTS = ('tracks', 'return_tracks', 'visible_tracks', 'clip_slots', 'cue_points', 'scenes', 'selected_track', 'selected_scene', 'detail_clip', 'devices', 'selected_device', 'selected_parameter', 'parameters', 'clip', 'chains', 'return_chains', 'drum_pads', 'visible_drum_pads', 'selected_drum_pad')
HIDDEN_TYPES = Live.Browser.Browser
HIDDEN_PROPERTIES = ('begin_undo_step', 'end_undo_step')
ENUM_TYPES = (Live.Song.Quantization, Live.Song.RecordingQuantization)
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
 'selected_drum_pad': Live.DrumPad.DrumPad,
 'mixer_device': (Live.MixerDevice.MixerDevice, Live.ChainMixerDevice.ChainMixerDevice),
 'view': (Live.Application.Application.View,
          Live.Song.Song.View,
          Live.Track.Track.View,
          Live.Device.Device.View)}
ROOT_PROPERTIES = {LIVE_APP: Live.Application.get_application,
 LIVE_SET: lambda : Live.Application.get_application().get_document(),
 CONTROL_SURFACES: get_control_surfaces,
 THIS_DEVICE: get_current_max_device}

class MxDCore(object):
    """ Central class for the Max-integration """
    instance = None

    def __init__(self):
        object.__init__(self)
        self.device_contexts = {}
        self.manager = None
        self.lom_classes = []
        self._call_handler = {'get_notes': self._object_get_notes_handler,
         'set_notes': self._object_set_notes_handler,
         'get_selected_notes': self._object_selected_notes_handler,
         'replace_selected_notes': self._object_replace_selected_notes_handler,
         'notes': self._object_notes_handler,
         'note': self._object_note_handler,
         'done': self._object_done_handler,
         'get_control_names': self._object_get_control_names_handler}
        self._create_introspection_for_dir(Live, exclude=[Live.Base])
        self._create_introspection_for_dir(_Framework)
        self.lom_classes.remove(Live.Song.BeatTime)
        self.lom_classes.remove(Live.Song.SmptTime)
        self.appointed_lom_ids = {0: None}

    def disconnect(self):
        for dev_id in self.device_contexts.keys():
            device_context = self.device_contexts[dev_id]
            if device_context[CONTAINS_CS_ID_KEY]:
                self.release_device_context(dev_id, -1, '')

        TupleWrapper.forget_tuple_wrapper_instances()
        self.manager.set_manager_callbacks(None, None, None, None)
        self.manager = None
        del self.appointed_lom_ids
        del self.lom_classes

    def _is_iterable(self, obj):
        return not isinstance(obj, basestring) and is_iterable(obj) and not isinstance(obj, self._cs_base_classes())

    def set_manager(self, manager):
        self.manager = manager
        manager.set_manager_callbacks(self.update_observer_listener, self.install_observer_listener, self.uninstall_observer_listener, self.update_remote_timeable)

    def _get_lom_object_by_lom_id(self, referring_device_id, lom_id):
        if lom_id > 0:
            return self.manager.get_lom_object(referring_device_id, lom_id)
        return self.appointed_lom_ids[lom_id]

    def _lom_id_exists(self, referring_device_id, lom_id):
        if lom_id > 0:
            return self.manager.lom_id_exists(referring_device_id, lom_id)
        return lom_id in self.appointed_lom_ids

    def _is_cplusplus_lom_object(self, lom_object):
        return isinstance(lom_object, Live.LomObject.LomObject)

    def _get_lom_id_by_lom_object(self, lom_object):
        if self._is_cplusplus_lom_object(lom_object):
            return self.manager.get_lom_id(lom_object)
        for id, object in self.appointed_lom_ids.iteritems():
            if object == lom_object:
                return id

        id = -len(self.appointed_lom_ids)
        self.appointed_lom_ids[id] = lom_object
        return id

    def _get_lom_id_observers_and_remotes(self, lom_id):
        """returns a list of (device_id, object_id) tuples that observe the given lom_id"""
        raise lom_id != 0 or AssertionError
        observers = []
        remotes = []
        for device_id, device_context in self.device_contexts.iteritems():
            for object_id, _ in device_context.iteritems():
                if not isinstance(object_id, int):
                    continue
                type = self._get_current_type(device_id, object_id)
                if type == 'obs':
                    if self._get_current_lom_id(device_id, object_id) == int(lom_id):
                        observers.append((device_id, object_id))
                elif type == 'rmt':
                    if self._get_current_lom_id(device_id, object_id) == int(lom_id):
                        remotes.append((device_id, object_id))

        return (observers, remotes)

    def _get_object_path(self, device_id, lom_object):
        path = ''
        current_object = lom_object
        while current_object != None:
            found_property = False
            parent = current_object.canonical_parent
            if parent != None:
                for key in PROPERTY_TYPES.keys():
                    if isinstance(current_object, PROPERTY_TYPES[key]):
                        if hasattr(parent, key):
                            path = current_object == getattr(parent, key) and unicode(key) + ' ' + path
                            found_property = True
                            break

                if not found_property:
                    for key in sorted(list(TUPLE_TYPES.keys())):
                        if hasattr(parent, key):
                            property = getattr(parent, key)
                            if current_object in property:
                                index = list(property).index(current_object)
                                path = unicode(key) + ' ' + unicode(index) + ' ' + path
                                found_property = True
                                break

            else:
                for key in ROOT_PROPERTIES.keys():
                    root_prop = self._get_root_prop(device_id, key)
                    if not self._is_iterable(root_prop):
                        if current_object == root_prop:
                            path = unicode(key) + ' ' + path
                            found_property = True
                    elif current_object in root_prop:
                        index = list(root_prop).index(current_object)
                        path = unicode(key) + ' ' + unicode(index) + ' ' + path
                        found_property = True
                    if found_property:
                        break

            if not found_property:
                path = ''
                break
            current_object = parent

        return path

    def _is_integer(self, s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    def _set_current_lom_id(self, device_id, object_id, lom_id, type):
        """set the CURRENT_LOM_ID of obj/obs/rmt objects"""
        if not self.manager.set_current_lom_id(device_id, object_id, lom_id):
            self.device_contexts[device_id][object_id][ID_KEY] = lom_id
            self._set_current_type(device_id, object_id, type)
            if type == 'obs':
                self._observer_update_listener(device_id, object_id)
            elif type == 'rmt':
                self._remote_update_timeable(device_id, object_id, True)

    def _get_current_lom_id(self, device_id, object_id):
        """get the CURRENT_LOM_ID of obj/obs/rmt objects"""
        current_id = self.manager.get_current_lom_id(device_id, object_id)
        if current_id != 0:
            return current_id
        return self.device_contexts[device_id][object_id][ID_KEY]

    def _set_current_type(self, device_id, object_id, type):
        """set the CURRENT_TYPE of obj/obs/rmt objects"""
        if type == 'obj':
            old_type = self.device_contexts[device_id][object_id][TYPE_KEY]
            if old_type is None:
                self.device_contexts[device_id][object_id][TYPE_KEY] = type
        else:
            self.device_contexts[device_id][object_id][TYPE_KEY] = type

    def _get_current_type(self, device_id, object_id):
        """get the CURRENT_TYPE of obj/obs/rmt objects"""
        current_type = self.manager.get_type(device_id, object_id)
        if current_type != -1:
            return {0: 'obs',
             1: None,
             2: 'obj',
             3: 'obs',
             4: 'rmt'}[current_type]
        return self.device_contexts[device_id][object_id][TYPE_KEY]

    def _set_current_property(self, device_id, object_id, property_name):
        """set the name of the observed property"""
        if not self.manager.set_current_property(device_id, object_id, property_name):
            self.device_contexts[device_id][object_id][PROP_KEY] = property_name
            self._set_current_type(device_id, object_id, 'obs')
            self._observer_update_listener(device_id, object_id)

    def _get_current_property(self, device_id, object_id):
        """get the name of the observed property, or an empty string"""
        property_name = self.manager.get_current_property(device_id, object_id)
        if property_name != '':
            return property_name
        return self.device_contexts[device_id][object_id][PROP_KEY]

    def update_device_context(self, device_id, object_id):
        if device_id not in self.device_contexts.keys():
            self.device_contexts[device_id] = {CONTAINS_CS_ID_KEY: False}
        if object_id not in self.device_contexts[device_id].keys():
            self.device_contexts[device_id][object_id] = {PATH_KEY: [],
             ID_KEY: 0,
             TYPE_KEY: None,
             PROP_KEY: '',
             PROP_LISTENER_KEY: (None, None, None),
             PATH_LISTENER_KEY: {},
             OPEN_OPERATIONS_KEY: {},
             LAST_SENT_ID_KEY: None}

    def release_device_context(self, device_id, object_id, parameters):
        device_context = self.device_contexts[device_id]
        for key in device_context.keys():
            if isinstance(key, int):
                object_context = device_context[key]
                self._observer_uninstall_listener(device_id, key)
                if len(object_context[PATH_KEY]) > 0:
                    object_context[PATH_KEY] = []
                    self._install_path_listeners(device_id, key, self._path_listener_callback)

        del self.device_contexts[device_id]

    def prepare_control_surface_update(self, device_id, object_id, parameters):
        found_cs_references = False
        for dev_id in self.device_contexts.keys():
            device_context = self.device_contexts[dev_id]
            if device_context[CONTAINS_CS_ID_KEY]:
                found_cs_references = True
                self.release_device_context(dev_id, -1, parameters)
                self.manager.refresh_max_device(dev_id)

        if found_cs_references:
            TupleWrapper.forget_tuple_wrapper_instances()
            self.appointed_lom_ids = {0: None}

    def path_set_path(self, device_id, object_id, parameters):
        if not isinstance(parameters, (str, unicode)):
            raise AssertionError
            pure_path = parameters.strip().strip('"')
            path_components = pure_path.split(' ')
            len(pure_path) > 0 and path_components[0] not in ROOT_PROPERTIES.keys() and self._raise(device_id, object_id, 'set path: invalid path')
        else:
            self.device_contexts[device_id][object_id][PATH_KEY] = []
            self.path_goto(device_id, object_id, parameters)

    def path_goto(self, device_id, object_id, parameters):
        raise isinstance(parameters, (str, unicode)) or AssertionError
        self._goto_path(device_id, object_id, parameters)
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        resulting_path = ''
        resulting_object = self._object_from_path(device_id, object_id, object_context[PATH_KEY], must_exist=False)
        resulting_id = self._get_lom_id_by_lom_object(resulting_object)
        device_context[CONTAINS_CS_ID_KEY] |= CONTROL_SURFACES in object_context[PATH_KEY]
        for component in object_context[PATH_KEY]:
            resulting_path += component + ' '

        self.manager.send_message(device_id, object_id, 'path_curr_path', unicode(resulting_path))
        self.manager.send_message(device_id, object_id, 'path_orig_id', unicode(resulting_id))
        self.manager.send_message(device_id, object_id, 'path_curr_id', unicode(resulting_id))
        self._install_path_listeners(device_id, object_id, self._path_listener_callback)

    def path_get_id(self, device_id, object_id, parameters):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        resulting_id = self._get_lom_id_by_lom_object(self._object_from_path(device_id, object_id, object_context[PATH_KEY], must_exist=False))
        self.manager.send_message(device_id, object_id, 'path_orig_id', unicode(resulting_id))
        self.manager.send_message(device_id, object_id, 'path_curr_id', unicode(resulting_id))

    def path_bang(self, device_id, object_id, parameters):
        self.path_get_id(device_id, object_id, parameters)

    def path_get_props(self, device_id, object_id, parameters):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        current_path = object_context[PATH_KEY]
        current_object = self._object_from_path(device_id, object_id, current_path, must_exist=True)
        result = ''
        if len(current_path) == 0:
            for property in ROOT_PROPERTIES.keys():
                result += property + ' '

        elif current_object != None:
            current_object = self._disambiguate_object(current_object)
            if self._is_iterable(current_object):
                result = '%d list elements, no properties' % len(current_object)
            else:
                for property in dir(current_object):
                    if not unicode(property).startswith('_'):
                        if hasattr(current_object, property):
                            try:
                                if property in TUPLE_TYPES.keys() + PROPERTY_TYPES.keys() + ['canonical_parent']:
                                    real_property = getattr(current_object, property)
                                    if real_property != None and self._is_lom_object(real_property):
                                        result += property + ' '
                            except:
                                pass

                    if len(result) == 0:
                        result = 'No path properties'

        if len(result) > 0:
            self.manager.send_message(device_id, object_id, 'path_props', result)

    def path_get_children(self, device_id, object_id, parameters):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        current_path = object_context[PATH_KEY]
        current_object = self._object_from_path(device_id, object_id, current_path, must_exist=True)
        result = ''
        if len(current_path) == 0:
            for property in ROOT_PROPERTIES.keys():
                result += property + ' '

        elif current_object != None:
            current_object = self._disambiguate_object(current_object)
            if self._is_iterable(current_object):
                result = '%d list elements, no children' % len(current_object)
            else:
                for property in dir(current_object):
                    if not unicode(property).startswith('_'):
                        if hasattr(current_object, property):
                            try:
                                if property in TUPLE_TYPES.keys() + PROPERTY_TYPES.keys() + ['canonical_parent']:
                                    real_property = getattr(current_object, property)
                                    if real_property != None and self._is_lom_object(real_property):
                                        result += property + ' '
                            except:
                                pass

                if len(result) == 0:
                    result = 'No children'
        if len(result) > 0:
            self.manager.send_message(device_id, object_id, 'path_children', result)

    def path_get_count(self, device_id, object_id, parameters):
        if not isinstance(parameters, (str, unicode)):
            raise AssertionError
            device_context = self.device_contexts[device_id]
            object_context = device_context[object_id]
            current_path = object_context[PATH_KEY]
            current_object = self._object_from_path(device_id, object_id, current_path, must_exist=True)
            property = None
            if len(current_path) == 0:
                if parameters in ROOT_PROPERTIES.keys():
                    property = self._get_root_prop(device_id, parameters)
            elif current_object != None:
                if hasattr(current_object, parameters):
                    property = getattr(current_object, parameters)
            if property != None:
                count = -1
                count = self._is_iterable(property) and len(property)
            self.manager.send_message(device_id, object_id, 'path_count', unicode(parameters) + ' ' + unicode(count))
        else:
            self._raise(device_id, object_id, 'getcount: invalid property name')

    def obj_set_id(self, device_id, object_id, parameter):
        if self._is_integer(parameter) and self._lom_id_exists(device_id, int(parameter)):
            self._set_current_lom_id(device_id, object_id, int(parameter), 'obj')
        else:
            self._raise(device_id, object_id, 'set id: invalid id')

    def obj_get_id(self, device_id, object_id, parameter):
        self.manager.send_message(device_id, object_id, 'obj_id', unicode(self._get_current_lom_id(device_id, object_id)))

    def obj_get_path(self, device_id, object_id, parameters):
        lom_object = self._get_current_lom_object(device_id, object_id)
        path = self._get_object_path(device_id, lom_object)
        if len(path) == 0 and lom_object != None:
            self._raise(device_id, object_id, 'get path: error calculating the path')
        else:
            self.manager.send_message(device_id, object_id, 'obj_path', unicode(path).strip())

    def obj_get_type(self, device_id, object_id, parameters):
        current_object = self._get_current_lom_object(device_id, object_id)
        object_type = 'unknown'
        if current_object != None:
            current_object = self._disambiguate_object(current_object)
            object_type = current_object.__class__.__name__
        self.manager.send_message(device_id, object_id, 'obj_type', unicode(object_type))

    def obj_get_info(self, device_id, object_id, parameters):
        current_object = self._get_current_lom_object(device_id, object_id)
        object_info = 'No object'
        if current_object != None:
            object_info = 'id ' + unicode(self._get_lom_id_by_lom_object(current_object)) + '\n'
            current_object = self._disambiguate_object(current_object)
            object_info += 'type ' + unicode(current_object.__class__.__name__) + '\n'
            if hasattr(current_object, '__doc__') and isinstance(current_object.__doc__, (str, unicode)) and current_object.__doc__ != '':
                description = current_object.__doc__
                description = description.replace('\n', ' ')
                description = description.replace(',', '\\,')
                object_info += 'description ' + unicode(description) + '\n'
            children_info = ''
            child_info = ''
            prop_info = ''
            func_info = ''
            if not self._is_iterable(current_object):
                for property in dir(current_object):
                    try:
                        if not property.startswith('_'):
                            real_property = getattr(current_object, property)
                            if property in TUPLE_TYPES.keys():
                                children_info += 'children ' + property + ' ' + TUPLE_TYPES[property].__name__ + '\n'
                            elif property in HIDDEN_PROPERTIES or isinstance(real_property, HIDDEN_TYPES):
                                pass
                            elif (property in PROPERTY_TYPES.keys() or self._is_lom_object(real_property)) and real_property == None:
                                if not not self.is_iterable(PROPERTY_TYPES[property]):
                                    raise AssertionError
                                    class_name = PROPERTY_TYPES[property].__name__
                                else:
                                    class_name = real_property.__class__.__name__
                                child_info += 'child ' + property + ' ' + class_name + '\n'
                            elif dir(real_property).count('im_func') is 1:
                                if not unicode(property).endswith('_listener'):
                                    func_info += 'function ' + property + '\n'
                            elif real_property.__class__.__name__ not in ('class', 'type'):
                                prop_info += 'property ' + property + ' '
                                if isinstance(real_property, ENUM_TYPES):
                                    prop_info += 'int\n'
                                else:
                                    prop_info += real_property.__class__.__name__ + '\n'
                    except:
                        pass

            if len(children_info) > 0:
                object_info += children_info
            if len(child_info) > 0:
                object_info += child_info
            if len(prop_info) > 0:
                object_info += prop_info
            if len(func_info) > 0:
                object_info += func_info
            object_info += 'done'
        self.manager.send_message(device_id, object_id, 'obj_info', unicode(object_info))

    def obj_set_val(self, device_id, object_id, parameters):
        self.obj_set(device_id, object_id, parameters)

    def obj_set(self, device_id, object_id, parameters):
        raise isinstance(parameters, (str, unicode)) or AssertionError
        current_object = self._get_current_lom_object(device_id, object_id)
        if current_object != None:
            parsed_params = self._parse(device_id, object_id, parameters)
            property_name = parsed_params[0]
            property_values = parsed_params[1:]
            property = getattr(current_object, property_name)
            value = property_values[0]
            if property_name in PROPERTY_TYPES.keys():
                if self._is_lom_object(value):
                    if isinstance(value, PROPERTY_TYPES[property_name]):
                        setattr(current_object, property_name, value)
                    else:
                        self._raise(device_id, object_id, 'set: type mismatch')
                else:
                    self._raise(device_id, object_id, 'set: no valid object id')
            elif isinstance(property, (int, bool)):
                if unicode(value) in (u'True', u'False'):
                    bool_value = unicode(value) == u'True'
                    setattr(current_object, property_name, int(bool_value))
                elif isinstance(value, int):
                    setattr(current_object, property_name, value)
                else:
                    self._raise(device_id, object_id, 'set: invalid value')
            elif not (isinstance(property, float) and isinstance(value, (int, float))):
                raise AssertionError
                setattr(current_object, property_name, float(value))
            elif not (isinstance(property, (str, unicode)) and isinstance(value, (str, unicode))):
                if not isinstance(value, (int, float)):
                    raise AssertionError
                    value = unicode(value)
                setattr(current_object, property_name, value)
            else:
                self._raise(device_id, object_id, 'set: unsupported property type')

    def obj_get_val(self, device_id, object_id, parameters):
        self.obj_get(device_id, object_id, parameters)

    def obj_get(self, device_id, object_id, parameters):
        if not isinstance(parameters, (str, unicode)):
            raise AssertionError
            current_object = self._get_current_lom_object(device_id, object_id)
            result_value = None
            param_valid = current_object != None and True
            if not (parameters.isdigit() and self._is_iterable(current_object)):
                raise AssertionError
                if not int(parameters) in range(len(current_object)):
                    raise AssertionError
                    result_value = current_object[int(parameters)]
                elif hasattr(current_object, parameters):
                    result_value = getattr(current_object, parameters)
                    if isinstance(result_value, ENUM_TYPES):
                        result_value = int(result_value)
                else:
                    param_valid = False
                if param_valid:
                    result = self._str_representation_for_object(device_id, result_value)
                    result = isinstance(result_value, (str, unicode)) and StringHandler.prepare_outgoing(result)
                self.manager.send_message(device_id, object_id, 'obj_prop_val', result)
            else:
                self._warn(device_id, object_id, "get: no property called '" + parameters + "'")
        else:
            self._warn(device_id, object_id, 'get: no valid object set')

    def obj_call(self, device_id, object_id, parameters):
        raise isinstance(parameters, (str, unicode)) or AssertionError
        current_object = self._get_current_lom_object(device_id, object_id)
        if current_object != None:
            try:
                param_comps = self._parse(device_id, object_id, parameters)
                func_name = str(param_comps[0])
                if func_name in HIDDEN_PROPERTIES:
                    raise AttributeError("'%s' object has no attribute '%s'" % (current_object.__class__.__name__, func_name))
                handler = self._call_handler[func_name] if func_name in self._call_handler.keys() else self._object_default_call_handler
                handler(device_id, object_id, current_object, param_comps)
            except:
                error = sys.exc_info()[0].__name__
                reason = unicode(sys.exc_info()[1])
                if error == 'AttributeError':
                    error_message = reason
                else:
                    if error != 'RuntimeError':
                        reason = 'Invalid arguments' if error == 'ArgumentError' else 'Invalid syntax'
                    error_message = "%s: '%s'" % (reason, unicode(parameters))
                self._raise(device_id, object_id, error_message)

        else:
            self._warn(device_id, object_id, 'call ' + unicode(parameters) + ': no valid object set')

    def obs_set_id(self, device_id, object_id, parameter):
        if self._is_integer(parameter) and self._lom_id_exists(device_id, int(parameter)):
            self.device_contexts[device_id][object_id][LAST_SENT_ID_KEY] = None
            self._set_current_lom_id(device_id, object_id, int(parameter), 'obs')
        else:
            self._raise(device_id, object_id, 'set id: invalid id')

    def obs_get_id(self, device_id, object_id, parameter):
        self.manager.send_message(device_id, object_id, 'obs_id', unicode(self._get_current_lom_id(device_id, object_id)))

    def obs_set_prop(self, device_id, object_id, parameter):
        raise isinstance(parameter, (str, unicode)) or AssertionError
        self._set_current_property(device_id, object_id, parameter)

    def obs_get_prop(self, device_id, object_id, parameter):
        self.manager.send_message(device_id, object_id, 'obs_prop', unicode(self._get_current_property(device_id, object_id)))

    def obs_get_type(self, device_id, object_id, parameter):
        current_object = self._get_current_lom_object(device_id, object_id)
        property_name = self._get_current_property(device_id, object_id)
        result = 'unknown'
        if current_object != None and property_name != '':
            if hasattr(current_object, property_name):
                result = getattr(current_object, property_name).__class__.__name__
            else:
                self._warn(device_id, object_id, 'gettype: no property with the name ' + property_name)
        self.manager.send_message(device_id, object_id, 'obs_type', unicode(result))

    def obs_bang(self, device_id, object_id, parameter):
        self._observer_property_callback(device_id, object_id, None, None, None, None)

    def rmt_set_id(self, device_id, object_id, parameter):
        if self._is_integer(parameter) and self._lom_id_exists(device_id, int(parameter)):
            new_id = int(parameter)
            lom_object = self._get_lom_object_by_lom_id(device_id, new_id)
            if isinstance(lom_object, (Live.DeviceParameter.DeviceParameter, type(None))):
                self._set_current_lom_id(device_id, object_id, new_id, 'rmt')
            else:
                self._raise(device_id, object_id, 'set id: only accepts objects of type DeviceParameter')
        else:
            self._raise(device_id, object_id, 'set id: invalid id')

    def _get_root_prop(self, device_id, prop_key):
        if not prop_key in ROOT_PROPERTIES.keys():
            raise AssertionError
            result = None
            result = prop_key == 'this_device' and ROOT_PROPERTIES[prop_key](device_id)
        else:
            result = ROOT_PROPERTIES[prop_key]()
        return result

    def _object_attr_path_iter(self, device_id, object_id, path_components):
        """Returns a generator of (object, attribute) tuples along the given path.
        It won't pack objects into a TupleWrapper."""
        if len(path_components) == 0:
            return
        raise path_components[0] in ROOT_PROPERTIES.keys() or AssertionError
        cur_object = self._get_root_prop(device_id, path_components[0])
        for component in path_components[1:]:
            if cur_object == None:
                return
            yield (cur_object, component)
            if not (component.isdigit() and self._is_iterable(cur_object)):
                raise AssertionError
                index = int(component)
                if index >= 0 and index < len(cur_object):
                    cur_object = cur_object[index]
                else:
                    return
            else:
                try:
                    cur_object = getattr(cur_object, component)
                except Exception:
                    return

    def _object_from_path(self, device_id, object_id, path_components, must_exist):
        resulting_object = None
        raise len(path_components) > 0 and (path_components[0] in ROOT_PROPERTIES.keys() or AssertionError)
        if path_components[-1] in TUPLE_TYPES.keys():
            parent = None
            attribute = path_components[-1]
            if len(path_components) > 1:
                parent = self._object_from_path(device_id, object_id, path_components[:-1], must_exist)
            if attribute in ('cs', 'control_surfaces'):
                if not parent == None:
                    raise AssertionError
                    resulting_object = TupleWrapper.get_tuple_wrapper(parent, 'control_surfaces')
                elif parent != None and hasattr(parent, attribute):
                    if self._is_cplusplus_lom_object(parent):
                        resulting_object = self.manager.get_list_wrapper(parent, attribute)
                    else:
                        resulting_object = TupleWrapper.get_tuple_wrapper(parent, attribute)
            else:
                prev_component = path_components[0]
                resulting_object = self._get_root_prop(device_id, path_components[0])
                for component in path_components[1:]:
                    raise component.isdigit() and (self._is_iterable(resulting_object) or AssertionError)
                    if not prev_component in TUPLE_TYPES.keys():
                        raise AssertionError
                        index = int(component)
                        if index >= 0 and index < len(resulting_object):
                            resulting_object = resulting_object[index]
                        else:
                            if must_exist:
                                self._raise(device_id, object_id, "invalid index of component '" + prev_component + "'")
                            resulting_object = None
                            break
                    else:
                        try:
                            resulting_object = getattr(resulting_object, component)
                            if isinstance(resulting_object, HIDDEN_TYPES):
                                raise Exception
                        except Exception:
                            if must_exist:
                                self._raise(device_id, object_id, "invalid path component '" + component + "'")
                            return

                    prev_component = component

                if not self._is_lom_object(resulting_object):
                    self._raise(device_id, object_id, "component '" + prev_component + "' is not an object")
                    resulting_object = None
        return resulting_object

    def _get_current_lom_object(self, device_id, object_id):
        """retrieving current lom object for object_ids of type obj/obs/rmt"""
        return self._get_lom_object_by_lom_id(device_id, self._get_current_lom_id(device_id, object_id))

    def _object_for_id(self, device_id):
        lom_object = None
        try:
            lom_object = lambda lom_id: self._get_lom_object_by_lom_id(device_id, lom_id)
        except:
            pass

        return lom_object

    def _str_representation_for_object(self, device_id, lom_object):
        result = ''
        lom_object = self._disambiguate_object(lom_object)
        if self._is_lom_object(lom_object) and not self._is_iterable(lom_object):
            result = 'id ' + unicode(self._get_lom_id_by_lom_object(lom_object))
        elif isinstance(lom_object, type(False)):
            result = unicode(int(lom_object))
        elif self._is_iterable(lom_object):
            result = ''
            for element in lom_object:
                result += self._str_representation_for_object(device_id, element) + ' '

            result = result[:-1]
        else:
            result = unicode(lom_object)
        return result

    def _is_lom_object(self, lom_object):
        return isinstance(lom_object, tuple(self.lom_classes) + (type(None),)) or isinstance(lom_object, self._cs_base_classes()) or isinstance(lom_object, Live.Base.Vector)

    def _cs_base_classes(self):
        from _Framework.ControlSurface import ControlSurface
        from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
        from _Framework.ControlElement import ControlElement
        return (ControlSurface, ControlSurfaceComponent, ControlElement)

    def _is_class(self, class_object):
        return isinstance(class_object, types.ClassType) or hasattr(class_object, '__bases__')

    def _is_relevant_class(self, class_object, relevant_modules):
        return self._is_class(class_object) and self.lom_classes.count(class_object) == 0 and hasattr(class_object, '__module__') and sys.modules.get(class_object.__module__) in relevant_modules and class_object not in ENUM_TYPES

    def _create_introspection_for_dir(self, directory, exclude = []):
        present_modules = []
        for attr_name in list(dir(directory)):
            try:
                attribute = getattr(directory, attr_name)
                is_module = isinstance(attribute, types.ModuleType)
                if attribute in exclude:
                    continue
                if self._is_class(attribute) and self.lom_classes.count(attribute) == 0:
                    self.lom_classes.append(attribute)
                if is_module and present_modules.count(attribute) == 0:
                    present_modules.append(attribute)
                if self._is_class(attribute) or is_module:
                    for sub_attr_name in dir(attribute):
                        try:
                            sub_attribute = getattr(attribute, sub_attr_name)
                            if self._is_relevant_class(sub_attribute, present_modules):
                                self.lom_classes.append(sub_attribute)
                                for sub_sub_attr_name in dir(sub_attribute):
                                    try:
                                        sub_sub_attribute = getattr(sub_attribute, sub_sub_attr_name)
                                        if self._is_relevant_class(sub_sub_attribute, present_modules):
                                            self.lom_classes.append(sub_sub_attribute)
                                    except:
                                        pass

                        except:
                            pass

            except:
                pass

    def _install_path_listeners(self, device_id, object_id, listener_callback):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        path_components = object_context[PATH_KEY]
        new_listeners = {}
        self._uninstall_path_listeners(device_id, object_id)
        listener = lambda device_id = device_id, object_id = object_id: listener_callback(device_id, object_id)
        obj_attr_iter = self._object_attr_path_iter(device_id, object_id, path_components)
        for lom_object, attribute in obj_attr_iter:
            if lom_object != None and attribute in LISTENABLE_PATH_COMPONENTS:
                attribute = attribute == 'clip' and 'has_clip'
            raise hasattr(lom_object, attribute + '_has_listener') or AssertionError, 'Object %s: property %s not listenable' % (str(lom_object), attribute)
            if not not getattr(lom_object, attribute + '_has_listener')(listener):
                raise AssertionError
                getattr(lom_object, 'add_' + attribute + '_listener')(listener)
                new_listeners[lom_object, attribute] = listener

        object_context[PATH_LISTENER_KEY] = new_listeners

    def _uninstall_path_listeners(self, device_id, object_id):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        old_listeners = object_context[PATH_LISTENER_KEY]
        for (lom_object, attribute), listener in old_listeners.iteritems():
            if lom_object != None and getattr(lom_object, attribute + '_has_listener')(listener):
                getattr(lom_object, 'remove_' + attribute + '_listener')(listener)

    def _path_listener_callback(self, device_id, object_id):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        resulting_id = self._get_lom_id_by_lom_object(self._object_from_path(device_id, object_id, object_context[PATH_KEY], must_exist=False))
        self.manager.send_message(device_id, object_id, 'path_curr_id', unicode(resulting_id))
        self._install_path_listeners(device_id, object_id, self._path_listener_callback)

    def _goto_path(self, device_id, object_id, parameters):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        try:
            pure_path = parameters.strip().strip('"')
            path_components = []
            if len(pure_path) > 0:
                path_components = pure_path.strip().split(' ')
            for parameter in path_components:
                if parameter == 'up':
                    del object_context[PATH_KEY][-1]
                elif parameter in ROOT_PROPERTIES.keys():
                    object_context[PATH_KEY] = [parameter]
                else:
                    object_context[PATH_KEY].append(parameter)

        except:
            self._raise(device_id, object_id, 'goto: invalid path')
            return

    def _object_default_call_handler(self, device_id, object_id, lom_object, parameters):
        function = getattr(lom_object, parameters[0])
        result = function(*parameters[1:])
        result_str = self._str_representation_for_object(device_id, result)
        if isinstance(result, (str, unicode)):
            result_str = unicode(StringHandler.prepare_outgoing(result_str))
        self.manager.send_message(device_id, object_id, 'obj_call_result', result_str)

    def _object_get_notes_handler(self, device_id, object_id, lom_object, parameters):
        raise isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip or AssertionError
        raise parameters[0] == 'get_notes' or AssertionError
        notes = getattr(lom_object, 'get_notes')(parameters[1], parameters[2], parameters[3], parameters[4])
        self.manager.send_message(device_id, object_id, 'obj_call_result', self._create_notes_output(notes))

    def _object_selected_notes_handler(self, device_id, object_id, lom_object, parameters):
        raise isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip or AssertionError
        notes = getattr(lom_object, 'get_selected_notes')()
        self.manager.send_message(device_id, object_id, 'obj_call_result', self._create_notes_output(notes))

    def _object_set_notes_handler(self, device_id, object_id, lom_object, parameters):
        self._start_note_operation(device_id, object_id, lom_object, parameters, NOTE_SET_KEY)

    def _object_replace_selected_notes_handler(self, device_id, object_id, lom_object, parameters):
        self._start_note_operation(device_id, object_id, lom_object, parameters, NOTE_REPLACE_KEY)

    def _object_notes_handler(self, device_id, object_id, lom_object, parameters):
        if not (isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip):
            raise AssertionError
            raise isinstance(parameters[1], int) or AssertionError
            device_context = self.device_contexts[device_id][object_id]
            device_context[OPEN_OPERATIONS_KEY][NOTE_COUNT_KEY] = NOTE_OPERATION_KEY in device_context[OPEN_OPERATIONS_KEY].keys() and parameters[1]
        else:
            self._raise(device_id, object_id, 'no operation in progress')

    def _object_note_handler(self, device_id, object_id, lom_object, parameters):
        raise isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip or AssertionError
        raise isinstance(parameters[1], (int, float)) and isinstance(parameters[2], float) and isinstance(parameters[3], float) or AssertionError
        device_context = self.device_contexts[device_id][object_id]
        raise NOTE_OPERATION_KEY in device_context[OPEN_OPERATIONS_KEY].keys() and (NOTE_BUFFER_KEY in device_context[OPEN_OPERATIONS_KEY].keys() or AssertionError)
        if not NOTE_COUNT_KEY in device_context[OPEN_OPERATIONS_KEY].keys():
            raise AssertionError
            if len(device_context[OPEN_OPERATIONS_KEY][NOTE_BUFFER_KEY]) < device_context[OPEN_OPERATIONS_KEY][NOTE_COUNT_KEY]:
                new_note = [parameters[1], parameters[2], parameters[3]]
                new_velocity = 100
                if len(parameters) > 4 and isinstance(parameters[4], (int, float)):
                    new_velocity = int(parameters[4])
                new_note.append(new_velocity)
                new_mute_state = False
                if len(parameters) > 5:
                    if isinstance(parameters[5], (int, type(False))):
                        new_mute_state = parameters[5]
                    elif unicode(parameters[5]) in (u'True', u'False'):
                        new_mute_state = unicode(parameters[5]) == u'True'
                new_note.append(new_mute_state)
                device_context[OPEN_OPERATIONS_KEY][NOTE_BUFFER_KEY].append(tuple(new_note))
            else:
                self._raise(device_id, object_id, 'too many notes')
                self._stop_note_operation(device_id, object_id)
        else:
            self._raise(device_id, object_id, 'no operation in progress')

    def _object_done_handler(self, device_id, object_id, lom_object, parameters):
        raise isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip or AssertionError
        device_context = self.device_contexts[device_id][object_id]
        if not (NOTE_OPERATION_KEY in device_context[OPEN_OPERATIONS_KEY].keys() and NOTE_COUNT_KEY in device_context[OPEN_OPERATIONS_KEY].keys() and NOTE_BUFFER_KEY in device_context[OPEN_OPERATIONS_KEY].keys()):
            raise AssertionError
            notes = tuple(device_context[OPEN_OPERATIONS_KEY][NOTE_BUFFER_KEY])
            if len(notes) == device_context[OPEN_OPERATIONS_KEY][NOTE_COUNT_KEY]:
                if device_context[OPEN_OPERATIONS_KEY][NOTE_OPERATION_KEY] == NOTE_REPLACE_KEY:
                    lom_object.replace_selected_notes(notes)
                elif device_context[OPEN_OPERATIONS_KEY][NOTE_OPERATION_KEY] == NOTE_SET_KEY:
                    lom_object.set_notes(notes)
                else:
                    self._warn(device_id, object_id, 'invalid note operation')
            else:
                self._warn(device_id, object_id, 'wrong note count')
            self._stop_note_operation(device_id, object_id)
        else:
            self._raise(device_id, object_id, 'no operation in progress')

    def _object_get_control_names_handler(self, device_id, object_id, lom_object, parameters):
        control_names = getattr(lom_object, 'get_control_names')()
        result = 'control_names %d\n' % len(control_names)
        for name in control_names:
            result += 'control %s\n' % name

        result += 'done'
        self.manager.send_message(device_id, object_id, 'obj_call_result', result)

    def _create_notes_output(self, notes):
        result = 'notes ' + unicode(len(notes)) + '\n'
        for note in notes:
            raise isinstance(note, tuple) and len(note) > 0 or AssertionError
            note_result = 'note '
            for index in range(len(note)):
                if isinstance(note[index], type(False)):
                    note_result += unicode(int(note[index]))
                else:
                    note_result += unicode(note[index])
                if index + 1 < len(note):
                    note_result += ' '

            result += unicode(note_result) + '\n'

        result += 'done'
        return result

    def _start_note_operation(self, device_id, object_id, lom_object, parameters, operation):
        if not (isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip):
            raise AssertionError
            device_context = self.device_contexts[device_id][object_id]
            raise NOTE_OPERATION_KEY not in device_context[OPEN_OPERATIONS_KEY].keys() and (NOTE_BUFFER_KEY not in device_context[OPEN_OPERATIONS_KEY].keys() or AssertionError)
            raise NOTE_BUFFER_KEY not in device_context[OPEN_OPERATIONS_KEY].keys() or AssertionError
            device_context[OPEN_OPERATIONS_KEY][NOTE_BUFFER_KEY] = []
            device_context[OPEN_OPERATIONS_KEY][NOTE_OPERATION_KEY] = operation
        else:
            self._raise(device_id, object_id, 'an operation is already in progress')

    def _stop_note_operation(self, device_id, object_id):
        device_context = self.device_contexts[device_id][object_id]
        del device_context[OPEN_OPERATIONS_KEY][NOTE_OPERATION_KEY]
        del device_context[OPEN_OPERATIONS_KEY][NOTE_BUFFER_KEY]
        del device_context[OPEN_OPERATIONS_KEY][NOTE_COUNT_KEY]

    def update_observer_listener(self, device_id, object_id):
        self.update_device_context(device_id, object_id)
        self._observer_update_listener(device_id, object_id)

    def install_observer_listener(self, device_id, object_id):
        self.update_device_context(device_id, object_id)
        self._observer_install_listener(device_id, object_id)

    def uninstall_observer_listener(self, device_id, object_id):
        self.update_device_context(device_id, object_id)
        self._observer_uninstall_listener(device_id, object_id)

    def update_lom_id_observers_and_remotes(self, lom_id):
        """updates observer and remote~ links for the given lom_id"""
        observers, remotes = self._get_lom_id_observers_and_remotes(lom_id)
        for device_id, object_id in observers:
            self._observer_update_listener(device_id, object_id)

        for device_id, object_id in remotes:
            self._remote_update_timeable(device_id, object_id, False)

    def _observer_update_listener(self, device_id, object_id):
        self._observer_uninstall_listener(device_id, object_id)
        self._observer_install_listener(device_id, object_id)

    def _observer_install_listener(self, device_id, object_id):
        if not self.device_contexts[device_id][object_id][PROP_LISTENER_KEY] == (None, None, None):
            raise AssertionError
            current_object = self._get_current_lom_object(device_id, object_id)
            property_name = self._get_current_property(device_id, object_id)
            property_name == u'id' and self._observer_id_callback(device_id, object_id)
        else:
            if current_object != None and property_name != '':
                object_context = self.device_contexts[device_id][object_id]
                listener_callback = lambda arg1 = None, arg2 = None, arg3 = None, arg4 = None: self._observer_property_callback(device_id, object_id, arg1, arg2, arg3, arg4)
                transl_prop_name = property_name
                transl_prop_name = property_name == 'clip' and 'has_clip'
            if hasattr(current_object, transl_prop_name + '_has_listener'):
                if not not getattr(current_object, transl_prop_name + '_has_listener')(listener_callback):
                    raise AssertionError
                    getattr(current_object, 'add_' + transl_prop_name + '_listener')(listener_callback)
                    object_context[PROP_LISTENER_KEY] = (listener_callback, current_object, property_name)
                    listener_callback()
                elif hasattr(current_object, transl_prop_name):
                    self._warn(device_id, object_id, 'property cannot be listened to')

    def _observer_uninstall_listener(self, device_id, object_id):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        self._uninstall_path_listeners(device_id, object_id)
        listener_callback, current_object, property_name = object_context[PROP_LISTENER_KEY]
        raise current_object != None and listener_callback != None and (property_name != '' or AssertionError)
        if not not isinstance(current_object, TupleWrapper):
            raise AssertionError
            transl_prop_name = property_name
            transl_prop_name = property_name == 'clip' and 'has_clip'
        if not hasattr(current_object, transl_prop_name + '_has_listener'):
            raise AssertionError
            if getattr(current_object, transl_prop_name + '_has_listener')(listener_callback):
                getattr(current_object, 'remove_' + transl_prop_name + '_listener')(listener_callback)
        object_context[PROP_LISTENER_KEY] = (None, None, None)

    def _observer_property_callback(self, device_id, object_id, arg1, arg2, arg3, arg4):
        current_object = self._get_current_lom_object(device_id, object_id)
        property_name = self._get_current_property(device_id, object_id)
        arguments = (arg1,
         arg2,
         arg3,
         arg4)
        if list(arguments).count(None) < len(arguments):
            result = ''
            for argument in arguments:
                if argument != None:
                    if isinstance(argument, type(False)):
                        argument = int(argument)
                    result += unicode(argument) + ' '

            self.manager.send_message(device_id, object_id, 'obs_list_val', result)
        elif not (current_object != None and property_name != '' and not isinstance(current_object, TupleWrapper)):
            raise AssertionError
            if hasattr(current_object, property_name):
                property = getattr(current_object, property_name)
                if isinstance(property, (str, unicode)):
                    self.manager.send_message(device_id, object_id, 'obs_string_val', unicode(StringHandler.prepare_outgoing(property)))
                elif isinstance(property, (int, type(False))):
                    self.manager.send_message(device_id, object_id, 'obs_int_val', unicode(int(property)))
                elif isinstance(property, float):
                    self.manager.send_message(device_id, object_id, 'obs_float_val', unicode(property))
                elif self._is_iterable(property):
                    self.manager.send_message(device_id, object_id, 'obs_list_val', self._str_representation_for_object(device_id, property))
                elif self._is_lom_object(property):
                    self.manager.send_message(device_id, object_id, 'obs_id_val', unicode(self._get_lom_id_by_lom_object(property)))
                else:
                    self._warn(device_id, object_id, 'unsupported property type')
            elif hasattr(current_object, property_name + '_has_listener'):
                self.manager.send_message(device_id, object_id, 'obs_string_val', 'bang')
            else:
                self._warn(device_id, object_id, 'property should be listenable')

    def _observer_id_callback(self, device_id, object_id):
        if not self._get_current_property(device_id, object_id) == u'id':
            raise AssertionError
            object_context = self.device_contexts[device_id][object_id]
            current_object = self._get_current_lom_object(device_id, object_id)
            self._goto_path(device_id, object_id, self._get_object_path(device_id, current_object))
            self._install_path_listeners(device_id, object_id, self._observer_id_callback)
            current_id = 0 if current_object == None else self._get_current_lom_id(device_id, object_id)
            object_context[LAST_SENT_ID_KEY] = current_id != object_context[LAST_SENT_ID_KEY] and current_id
            self.manager.send_message(device_id, object_id, 'obs_id_val', unicode(current_id))

    def update_remote_timeable(self, device_id, object_id):
        self.update_device_context(device_id, object_id)
        self._remote_update_timeable(device_id, object_id, False)

    def reset_all_current_lom_ids(self, device_id):
        if device_id in self.device_contexts:
            device_context = self.device_contexts[device_id]
            for object_id, _ in device_context.iteritems():
                if isinstance(object_id, int):
                    type = self._get_current_type(device_id, object_id)
                    if type in ('obs', 'obj', 'rmt'):
                        self._set_current_lom_id(device_id, object_id, 0, type)

    def _remote_update_timeable(self, device_id, object_id, validate_change_allowed):
        current_object = self._get_current_lom_object(device_id, object_id)
        if isinstance(current_object, Live.DeviceParameter.DeviceParameter):
            self.manager.register_remote_timeable(device_id, object_id, current_object, validate_change_allowed)
        else:
            self.manager.unregister_remote_timeable(device_id, object_id, validate_change_allowed)

    def _disambiguate_object(self, object):
        result = object
        if object.__class__.__name__ in ('ListWrapper', 'TupleWrapper'):
            result = object.get_list()
        return result

    def _parse(self, device_id, object_id, string):
        return StringHandler.parse(string, self._object_for_id(device_id))

    def _raise(self, device_id, object_id, message):
        debug_print('Error: ' + unicode(message))
        self.manager.print_message(device_id, object_id, 'error', unicode(message))

    def _warn(self, device_id, object_id, message):
        debug_print('Warning: ' + unicode(message))
        self.manager.print_message(device_id, object_id, 'warning', unicode(message))