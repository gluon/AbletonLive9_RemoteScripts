#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_MxDCore/MxDCore.py
import Live.Base
from functools import partial, wraps
import _Framework
from _Framework.Disconnectable import Disconnectable
from _Framework.Debug import debug_print
from MxDUtils import TupleWrapper, StringHandler
from LomUtils import LomInformation, LomIntrospection, LomPathCalculator, LomPathResolver
from LomTypes import ENUM_TYPES, EXPOSED_TYPE_PROPERTIES, CONTROL_SURFACES, PROPERTY_TYPES, ROOT_KEYS, get_root_prop, is_lom_object, is_cplusplus_lom_object, is_object_iterable, LomNoteOperationWarning, LomNoteOperationError, LomAttributeError, LomObjectError, verify_object_property, is_property_hidden

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
PRIVATE_PROP_WARNING = 'Warning: Calling private property. This property might change or be removed in the future.'
HIDDEN_PROP_WARNING = 'Warning: Calling hidden property. This property might change or be removed in the future.'

def concatenate_strings(string_list, string_format = '%s %s'):
    return unicode(reduce(lambda s1, s2: string_format % (s1, s2), string_list) if len(string_list) > 0 else '')


def parameter_to_bool(parameter):
    bool_value = False
    if isinstance(parameter, (int, type(False))):
        bool_value = parameter
    elif unicode(parameter) in (u'True', u'False'):
        bool_value = unicode(parameter) == u'True'
    return bool_value


def note_from_parameters(parameters):
    new_note = [parameters[0], parameters[1], parameters[2]]
    new_note.append(int(parameters[3]) if len(parameters) > 3 and isinstance(parameters[3], (int, float)) else 100)
    new_note.append(len(parameters) > 4 and parameter_to_bool(parameters[4]))
    return tuple(new_note)


class MxDCore(object):
    """ Central class for the Max-integration """
    instance = None

    def __init__(self, *a, **k):
        super(MxDCore, self).__init__(*a, **k)
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
        self.lom_classes = EXPOSED_TYPE_PROPERTIES.keys()
        self.lom_classes += LomIntrospection(_Framework).lom_classes
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

    def _get_lom_id_by_lom_object(self, lom_object):
        if is_cplusplus_lom_object(lom_object):
            return self.manager.get_lom_id(lom_object)
        for id, object in self.appointed_lom_ids.iteritems():
            if object == lom_object:
                return id

        id = -len(self.appointed_lom_ids)
        self.appointed_lom_ids[id] = lom_object
        if isinstance(lom_object, Disconnectable):

            def unregister_lom_object(f):

                @wraps(f)
                def wrapper(*a, **k):
                    try:
                        del self.appointed_lom_ids[id]
                    except KeyError:
                        pass

                    return f(*a, **k)

                return wrapper

            lom_object.disconnect = unregister_lom_object(lom_object.disconnect)
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
        resolver = LomPathCalculator(lom_object, get_current_max_device(device_id))
        return concatenate_strings(resolver.path_components)

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
            len(pure_path) > 0 and path_components[0] not in ROOT_KEYS and self._raise(device_id, object_id, 'set path: invalid path')
        else:
            self.device_contexts[device_id][object_id][PATH_KEY] = []
            self.path_goto(device_id, object_id, parameters)

    def path_goto(self, device_id, object_id, parameters):
        raise isinstance(parameters, (str, unicode)) or AssertionError
        self._goto_path(device_id, object_id, parameters)
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        result_object = self._object_from_path(device_id, object_id, object_context[PATH_KEY], must_exist=False)
        result_id = unicode(self._get_lom_id_by_lom_object(result_object))
        device_context[CONTAINS_CS_ID_KEY] |= CONTROL_SURFACES in object_context[PATH_KEY]
        result_path = unicode(concatenate_strings(object_context[PATH_KEY]))
        for msg_type, value in (('path_curr_path', result_path), ('path_orig_id', result_id), ('path_curr_id', result_id)):
            self.manager.send_message(device_id, object_id, msg_type, value)

        self._install_path_listeners(device_id, object_id, self._path_listener_callback)

    def path_get_id(self, device_id, object_id, parameters):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        lom_object = self._object_from_path(device_id, object_id, object_context[PATH_KEY], must_exist=False)
        result_id = unicode(self._get_lom_id_by_lom_object(lom_object))
        for msg_type, value in (('path_orig_id', result_id), ('path_curr_id', result_id)):
            self.manager.send_message(device_id, object_id, msg_type, value)

    def path_bang(self, device_id, object_id, parameters):
        self.path_get_id(device_id, object_id, parameters)

    def _get_path_and_object(self, device_id, object_id):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        current_path = object_context[PATH_KEY]
        current_object = self._object_from_path(device_id, object_id, current_path, must_exist=True)
        return (current_path, current_object)

    def _get_lom_object_properties(self, device_id, object_id, looking_for):
        current_path, current_object = self._get_path_and_object(device_id, object_id)
        if len(current_path) == 0:
            result = concatenate_strings(ROOT_KEYS)
        elif current_object != None:
            current_object = self._disambiguate_object(current_object)
            if is_object_iterable(current_object):
                result = '%d list elements, no %s' % (len(current_object), looking_for)
            else:
                lom_info = LomInformation(current_object)
                path_props = map(lambda info: info[0], lom_info.lists_of_children + lom_info.children)
                result = concatenate_strings(sorted(path_props))
        return result

    def path_get_props(self, device_id, object_id, parameters):
        result = self._get_lom_object_properties(device_id, object_id, 'properties') or 'No path properties'
        self.manager.send_message(device_id, object_id, 'path_props', result)

    def path_get_children(self, device_id, object_id, parameters):
        result = self._get_lom_object_properties(device_id, object_id, 'children') or 'No children'
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
                if parameters in ROOT_KEYS:
                    property = get_root_prop(get_current_max_device(device_id), parameters)
            elif current_object != None:
                if hasattr(current_object, parameters):
                    property = getattr(current_object, parameters)
            count = property != None and unicode(len(property) if is_object_iterable(property) else -1)
            self.manager.send_message(device_id, object_id, 'path_count', concatenate_strings((parameters, count)))
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
            object_info = 'id %s\n' % unicode(self._get_lom_id_by_lom_object(current_object))
            current_object = self._disambiguate_object(current_object)
            lom_info = LomInformation(current_object)
            object_info += 'type %s\n' % unicode(current_object.__class__.__name__)
            object_info += '%s\n' % lom_info.description
            if not is_object_iterable(current_object):

                def accumulate_info(info_list, label):
                    result = ''
                    if len(info_list) > 0:
                        str_format = '%s %s %s\n' if len(info_list[0]) > 1 else '%s %s\n'
                        formatter = lambda info: str_format % ((label,) + info)
                        result = concatenate_strings(map(formatter, info_list), string_format='%s%s')
                    return result

                object_info += accumulate_info(lom_info.lists_of_children, 'children') + accumulate_info(lom_info.children, 'child') + accumulate_info(lom_info.properties, 'property') + accumulate_info(lom_info.functions, 'function')
            object_info += 'done'
        self.manager.send_message(device_id, object_id, 'obj_info', unicode(object_info))

    def obj_set_val(self, device_id, object_id, parameters):
        self.obj_set(device_id, object_id, parameters)

    def _set_property_value(self, lom_object, property_name, value):
        verify_object_property(lom_object, property_name)
        prop = getattr(lom_object, property_name)
        if property_name in PROPERTY_TYPES.keys():
            if not is_lom_object(value, self.lom_classes):
                raise LomAttributeError('set: no valid object id')
            if not isinstance(value, PROPERTY_TYPES[property_name]):
                raise LomAttributeError('set: type mismatch')
        elif isinstance(prop, (int, bool)):
            if unicode(value) in (u'True', u'False'):
                value = int(unicode(value) == u'True')
            elif not isinstance(value, int):
                raise LomAttributeError('set: invalid value')
        elif isinstance(prop, float):
            if not isinstance(value, (int, float)):
                raise LomAttributeError('set: type mismatch')
            value = float(value)
        elif isinstance(prop, (str, unicode)):
            if not isinstance(value, (str,
             unicode,
             int,
             float)):
                raise LomAttributeError('set: type mismatch')
            value = unicode(value)
        else:
            raise LomAttributeError('set: unsupported property type')
        setattr(lom_object, property_name, value)

    def _warn_if_using_private_property(self, device_id, object_id, property_name):
        if property_name.startswith('_'):
            self._warn(device_id, object_id, PRIVATE_PROP_WARNING)
        lom_object = self._get_current_lom_object(device_id, object_id)
        if is_property_hidden(lom_object, property_name):
            self._warn(device_id, object_id, HIDDEN_PROP_WARNING)

    def obj_set(self, device_id, object_id, parameters):
        if not isinstance(parameters, (str, unicode)):
            raise AssertionError
            current_object = self._get_current_lom_object(device_id, object_id)
            parsed_params = current_object != None and self._parse(device_id, object_id, parameters)
            property_name = parsed_params[0]
            property_values = parsed_params[1:]
            value = property_values[0]
            try:
                self._set_property_value(current_object, property_name, value)
                self._warn_if_using_private_property(device_id, object_id, property_name)
            except LomAttributeError as e:
                self._raise(device_id, object_id, e.message)

    def obj_get_val(self, device_id, object_id, parameters):
        self.obj_get(device_id, object_id, parameters)

    def obj_get(self, device_id, object_id, parameters):
        raise isinstance(parameters, (str, unicode)) or AssertionError
        current_object = self._get_current_lom_object(device_id, object_id)
        result_value = None
        if current_object != None:
            try:
                raise parameters.isdigit() and (is_object_iterable(current_object) or AssertionError)
                if not int(parameters) in range(len(current_object)):
                    raise AssertionError
                    result_value = current_object[int(parameters)]
                else:
                    verify_object_property(current_object, parameters)
                    self._warn_if_using_private_property(device_id, object_id, parameters)
                    result_value = getattr(current_object, parameters)
                    if isinstance(result_value, ENUM_TYPES):
                        result_value = int(result_value)
                result = self._str_representation_for_object(result_value)
                self.manager.send_message(device_id, object_id, 'obj_prop_val', result)
            except LomAttributeError as e:
                self._warn(device_id, object_id, e.message)

        else:
            self._warn(device_id, object_id, 'get: no valid object set')

    def obj_call(self, device_id, object_id, parameters):
        raise isinstance(parameters, (str, unicode)) or AssertionError
        current_object = self._get_current_lom_object(device_id, object_id)
        if current_object != None:
            try:
                param_comps = self._parse(device_id, object_id, parameters)
                func_name = str(param_comps[0])
                handler = self._call_handler[func_name] if func_name in self._call_handler.keys() else self._object_default_call_handler
                handler(device_id, object_id, current_object, param_comps)
            except AttributeError as e:
                self._raise(device_id, object_id, e.message)
            except RuntimeError as e:
                self._raise(device_id, object_id, u"%s: '%s'" % (e.message, parameters))
            except Exception as e:
                reason = 'Invalid ' + ('arguments' if isinstance(e, TypeError) else 'syntax')
                self._raise(device_id, object_id, u"%s: '%s'" % (reason, parameters))

        else:
            self._warn(device_id, object_id, u'call %s: no valid object set' % parameters)

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
        self._observer_property_callback(device_id, object_id)

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

    def _object_attr_path_iter(self, device_id, object_id, path_components):
        """Returns a generator of (object, attribute) tuples along the given path.
        It won't pack objects into a TupleWrapper."""
        if len(path_components) == 0:
            return
        raise path_components[0] in ROOT_KEYS or AssertionError
        cur_object = get_root_prop(get_current_max_device(device_id), path_components[0])
        for component in path_components[1:]:
            if cur_object == None:
                return
            yield (cur_object, component)
            if not (component.isdigit() and is_object_iterable(cur_object)):
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
        lom_object = None
        try:
            resolver = LomPathResolver(path_components, get_current_max_device(device_id), self.lom_classes, self.manager)
            lom_object = resolver.lom_object
        except (LomAttributeError, LomObjectError) as e:
            if must_exist or isinstance(e, LomObjectError):
                self._raise(device_id, object_id, e.message)

        return lom_object

    def _get_current_lom_object(self, device_id, object_id):
        """retrieving current lom object for object_ids of type obj/obs/rmt"""
        return self._get_lom_object_by_lom_id(device_id, self._get_current_lom_id(device_id, object_id))

    def _object_for_id(self, device_id):
        lom_object = None
        try:
            lom_object = partial(self._get_lom_object_by_lom_id, device_id)
        except:
            pass

        return lom_object

    def _str_representation_for_object(self, lom_object, mark_ids = True):
        result = ''
        lom_object = self._disambiguate_object(lom_object)
        if is_object_iterable(lom_object):
            result = concatenate_strings(map(self._str_representation_for_object, lom_object))
        elif is_lom_object(lom_object, self.lom_classes):
            result = ('id ' if mark_ids else '') + unicode(self._get_lom_id_by_lom_object(lom_object))
        elif isinstance(lom_object, (int, bool)):
            result = unicode(int(lom_object))
        else:
            result = StringHandler.prepare_outgoing(unicode(lom_object))
        return result

    def _install_path_listeners(self, device_id, object_id, listener_callback):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        path_components = object_context[PATH_KEY]
        new_listeners = {}
        self._uninstall_path_listeners(device_id, object_id)
        listener = partial(listener_callback, device_id, object_id)
        obj_attr_iter = self._object_attr_path_iter(device_id, object_id, path_components)
        for lom_object, attribute in obj_attr_iter:
            attribute = self._listenable_property_for(attribute)
            if not (lom_object != None and hasattr(lom_object, attribute + '_has_listener') and not getattr(lom_object, attribute + '_has_listener')(listener)):
                raise AssertionError
                getattr(lom_object, 'add_%s_listener' % attribute)(listener)
                new_listeners[lom_object, attribute] = listener

        object_context[PATH_LISTENER_KEY] = new_listeners

    def _uninstall_path_listeners(self, device_id, object_id):
        device_context = self.device_contexts[device_id]
        object_context = device_context[object_id]
        old_listeners = object_context[PATH_LISTENER_KEY]
        for (lom_object, attribute), listener in old_listeners.iteritems():
            if lom_object != None and getattr(lom_object, attribute + '_has_listener')(listener):
                getattr(lom_object, 'remove_%s_listener' % attribute)(listener)

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
                else:
                    if parameter in ROOT_KEYS:
                        object_context[PATH_KEY] = []
                    object_context[PATH_KEY].append(parameter)

        except:
            self._raise(device_id, object_id, 'goto: invalid path')
            return

    def _object_default_call_handler(self, device_id, object_id, lom_object, parameters):
        verify_object_property(lom_object, parameters[0])
        self._warn_if_using_private_property(device_id, object_id, parameters[0])
        function = getattr(lom_object, parameters[0])
        result = function(*parameters[1:])
        result_str = self._str_representation_for_object(result)
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
        raise isinstance(parameters[1], (int, float)) or AssertionError
        raise isinstance(parameters[2], float) or AssertionError
        raise isinstance(parameters[3], float) or AssertionError
        device_context = self.device_contexts[device_id][object_id]
        operations = device_context[OPEN_OPERATIONS_KEY]
        try:
            if NOTE_OPERATION_KEY not in operations:
                raise LomNoteOperationError('no operation in progress')
            if NOTE_COUNT_KEY not in operations:
                raise LomNoteOperationError('no note count given')
            if not NOTE_BUFFER_KEY in operations:
                raise AssertionError
                raise len(operations[NOTE_BUFFER_KEY]) >= operations[NOTE_COUNT_KEY] and LomNoteOperationError('too many notes')
            operations[NOTE_BUFFER_KEY].append(note_from_parameters(parameters[1:]))
        except LomNoteOperationError as e:
            self._raise(device_id, object_id, e.message)
            self._stop_note_operation(device_id, object_id)

    def _selector_for_note_operation(self, note_operation):
        if note_operation not in (NOTE_REPLACE_KEY, NOTE_SET_KEY):
            raise LomNoteOperationWarning('invalid note operation')
        if note_operation == NOTE_SET_KEY:
            return 'set_notes'
        return 'replace_selected_notes'

    def _object_done_handler(self, device_id, object_id, lom_object, parameters):
        if not (isinstance(lom_object, Live.Clip.Clip) and lom_object.is_midi_clip):
            raise AssertionError
            device_context = self.device_contexts[device_id][object_id]
            open_operations = device_context[OPEN_OPERATIONS_KEY]
            raise NOTE_OPERATION_KEY in open_operations and NOTE_COUNT_KEY in open_operations and (NOTE_BUFFER_KEY in open_operations or AssertionError)
            try:
                notes = tuple(open_operations[NOTE_BUFFER_KEY])
                if len(notes) != open_operations[NOTE_COUNT_KEY]:
                    raise LomNoteOperationWarning('wrong note count')
                operation = open_operations[NOTE_OPERATION_KEY]
                selector = self._selector_for_note_operation(operation)
                getattr(lom_object, selector)(notes)
            except LomNoteOperationWarning as w:
                self._warn(device_id, object_id, w.message)

            self._stop_note_operation(device_id, object_id)
        else:
            self._raise(device_id, object_id, 'no operation in progress')

    def _object_get_control_names_handler(self, device_id, object_id, lom_object, parameters):
        control_names = getattr(lom_object, 'get_control_names')()
        formatter = lambda name: 'control %s\n' % name
        result = 'control_names %d\n' % len(control_names) + concatenate_strings(map(formatter, control_names), string_format='%s%s') + 'done'
        self.manager.send_message(device_id, object_id, 'obj_call_result', result)

    def _create_notes_output(self, notes):
        element_format = lambda el: unicode(int(el) if isinstance(el, bool) else el)
        note_format = lambda note: u'note %s\n' % concatenate_strings(map(element_format, note))
        result = 'notes %d\n%sdone' % (len(notes), concatenate_strings(map(note_format, notes), string_format='%s%s'))
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
        for key in (NOTE_OPERATION_KEY, NOTE_BUFFER_KEY, NOTE_COUNT_KEY):
            try:
                del device_context[OPEN_OPERATIONS_KEY][key]
            except KeyError:
                pass

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
            self._warn_if_using_private_property(device_id, object_id, property_name)
            property_name == u'id' and self._observer_id_callback(device_id, object_id)
        else:
            object_context = current_object != None and property_name != '' and self.device_contexts[device_id][object_id]
            listener_callback = partial(self._observer_property_callback, device_id, object_id)
            transl_prop_name = self._listenable_property_for(property_name)
            if hasattr(current_object, transl_prop_name + '_has_listener'):
                if not not getattr(current_object, transl_prop_name + '_has_listener')(listener_callback):
                    raise AssertionError
                    getattr(current_object, 'add_%s_listener' % transl_prop_name)(listener_callback)
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
        raise not isinstance(current_object, TupleWrapper) or AssertionError
        transl_prop_name = self._listenable_property_for(property_name)
        if not hasattr(current_object, transl_prop_name + '_has_listener'):
            raise AssertionError
            if getattr(current_object, transl_prop_name + '_has_listener')(listener_callback):
                getattr(current_object, 'remove_%s_listener' % transl_prop_name)(listener_callback)
        object_context[PROP_LISTENER_KEY] = (None, None, None)

    def _observer_property_message_type(self, prop):
        prop_type = None
        if isinstance(prop, (str, unicode)):
            prop_type = 'obs_string_val'
        elif isinstance(prop, (int, bool)):
            prop_type = 'obs_int_val'
        elif isinstance(prop, float):
            prop_type = 'obs_float_val'
        elif is_object_iterable(prop):
            prop_type = 'obs_list_val'
        elif is_lom_object(prop, self.lom_classes):
            prop_type = 'obs_id_val'
        return prop_type

    def _observer_property_callback(self, device_id, object_id, *args):
        current_object = self._get_current_lom_object(device_id, object_id)
        property_name = self._get_current_property(device_id, object_id)
        if len(args) > 0:
            formatter = lambda arg: unicode(int(arg) if isinstance(arg, bool) else arg)
            args_type = self._observer_property_message_type(args if len(args) > 1 else args[0])
            result = concatenate_strings(map(formatter, args))
            self.manager.send_message(device_id, object_id, args_type, result)
        elif not (current_object != None and property_name != '' and not isinstance(current_object, TupleWrapper)):
            raise AssertionError
            if hasattr(current_object, property_name):
                prop = getattr(current_object, property_name)
                prop_type = self._observer_property_message_type(prop)
                if prop_type == None:
                    self._warn(device_id, object_id, 'unsupported property type')
                else:
                    prop_value = self._str_representation_for_object(prop, mark_ids=False)
                    self.manager.send_message(device_id, object_id, prop_type, prop_value)
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

    def _listenable_property_for(self, prop_name):
        if prop_name == 'clip':
            return 'has_clip'
        return prop_name

    def _parse(self, device_id, object_id, string):
        return StringHandler.parse(string, self._object_for_id(device_id))

    def _raise(self, device_id, object_id, message):
        debug_print('Error: ' + unicode(message))
        self.manager.print_message(device_id, object_id, 'error', unicode(message))

    def _warn(self, device_id, object_id, message):
        debug_print('Warning: ' + unicode(message))
        self.manager.print_message(device_id, object_id, 'warning', unicode(message))