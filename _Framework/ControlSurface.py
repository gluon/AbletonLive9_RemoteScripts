#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/ControlSurface.py
from __future__ import absolute_import, with_statement
from functools import partial, wraps
from itertools import chain, ifilter, imap
from contextlib import contextmanager
import traceback
import Live
from . import Defaults
from . import Task
from .ControlElement import OptimizedOwnershipHandler
from .Debug import debug_print
from .Dependency import inject
from .InputControlElement import InputControlElement, MIDI_CC_TYPE, MIDI_PB_TYPE, MIDI_NOTE_TYPE, MIDI_SYSEX_TYPE, MIDI_PB_STATUS
from .PhysicalDisplayElement import PhysicalDisplayElement
from .Profile import profile
from .SubjectSlot import SlotManager
from .Util import BooleanContext, first, find_if, const, in_range

def _scheduled_method(method):
    """
    Methods from two control surfaces that use the component_guard can
    not live in the stack at the same time. Use this for methods that
    can be called implicitly by other control surfaces to delay
    execution.
    """

    @wraps(method)
    def wrapper(self, *a, **k):

        def doit():
            return method(self, *a, **k)

        self.schedule_message(1, doit)

    return wrapper


CS_LIST_KEY = 'control_surfaces'

def publish_control_surface(control_surface):
    get_control_surfaces().append(control_surface)


def get_control_surfaces():
    if isinstance(__builtins__, dict):
        if CS_LIST_KEY not in __builtins__.keys():
            __builtins__[CS_LIST_KEY] = []
        return __builtins__[CS_LIST_KEY]
    else:
        if not hasattr(__builtins__, CS_LIST_KEY):
            setattr(__builtins__, CS_LIST_KEY, [])
        return getattr(__builtins__, CS_LIST_KEY)


class ControlSurface(SlotManager):
    """
    Central base class for scripts based on the new Framework. New
    scripts need to subclass this class and add special behavior.
    """

    def __init__(self, c_instance = None, publish_self = True, *a, **k):
        """ Define and Initialize standard behavior """
        super(ControlSurface, self).__init__(*a, **k)
        if not c_instance:
            raise AssertionError
            self.canonical_parent = None
            publish_self and publish_control_surface(self)
        self._c_instance = c_instance
        self.log_message('Initialising...')
        self._pad_translations = None
        self._suggested_input_port = str('')
        self._suggested_output_port = str('')
        self._components = []
        self._displays = []
        self.controls = []
        self._highlighting_session_component = None
        self._device_component = None
        self._device_selection_follows_track_selection = False
        self._forwarding_long_identifier_registry = {}
        self._forwarding_registry = {}
        self._is_sending_scheduled_messages = BooleanContext()
        self._remaining_scheduled_messages = []
        self._task_group = Task.TaskGroup(auto_kill=False)
        self._in_build_midi_map = BooleanContext()
        self._suppress_requests_counter = 0
        self._rebuild_requests_during_suppression = 0
        self._enabled = True
        self._in_component_guard = BooleanContext()
        self._accumulate_midi_messages = BooleanContext()
        self._midi_message_dict = {}
        self._midi_message_list = []
        self._midi_message_count = 0
        self._control_surface_injector = inject(parent_task_group=const(self._task_group), show_message=const(self.show_message), log_message=const(self.log_message), register_component=const(self._register_component), register_control=const(self._register_control), request_rebuild_midi_map=const(self.request_rebuild_midi_map), set_pad_translations=const(self.set_pad_translations), send_midi=const(self._send_midi), song=self.song).everywhere()
        self.register_slot(self.song(), self._on_track_list_changed, 'visible_tracks')
        self.register_slot(self.song(), self._on_scene_list_changed, 'scenes')
        self.register_slot(self.song().view, self._on_selected_track_changed, 'selected_track')
        self.register_slot(self.song().view, self._on_selected_scene_changed, 'selected_scene')

    @property
    def components(self):
        return tuple(filter(lambda comp: not comp.is_private, self._components))

    @property
    def root_components(self):
        return tuple(filter(lambda comp: comp.is_root and not comp.is_private, self._components))

    def _get_tasks(self):
        return self._task_group

    _tasks = property(_get_tasks)

    def application(self):
        """ Returns a reference to the application that we are running in """
        return Live.Application.get_application()

    def song(self):
        """ Returns a reference to the Live song instance that we control """
        return self._c_instance.song()

    def disconnect(self):
        """
        Live -> Script: Called right before we get disconnected from Live
        """
        self._disconnect_and_unregister_all_components()
        with self.component_guard():
            for control in self.controls:
                control.disconnect()
                control.canonical_parent = None

        self._forwarding_registry = None
        self.controls = None
        self._displays = None
        self._device_component = None
        self._pad_translations = None
        cs_list = self._control_surfaces()
        if self in cs_list:
            cs_list.remove(self)
        self._task_group.clear()
        super(ControlSurface, self).disconnect()

    def _control_surfaces(self):
        """ Returns list of registered control surfaces """
        return get_control_surfaces()

    def can_lock_to_devices(self):
        """
        Live -> Script
        """
        return self._device_component != None

    @_scheduled_method
    def lock_to_device(self, device):
        """
        Live -> Script
        Live tells the script which device to control
        """
        raise self._device_component != None or AssertionError
        with self.component_guard():
            self._device_component.set_lock_to_device(True, device)

    @_scheduled_method
    def unlock_from_device(self, device):
        """
        Live -> Script
        Live tells the script to unlock from a certain device
        """
        raise self._device_component != None or AssertionError
        with self.component_guard():
            self._device_component.set_lock_to_device(False, device)

    @_scheduled_method
    def restore_bank(self, bank_index):
        """
        Live -> Script
        Live tells the script which bank to use.
        """
        raise self._device_component != None or AssertionError
        with self.component_guard():
            self._device_component.restore_bank(bank_index)

    def suggest_input_port(self):
        """ Live -> Script: Live can ask for the name of the script's
        prefered input port"""
        return self._suggested_input_port

    def suggest_output_port(self):
        """ Live -> Script: Live can ask for the name of the script's
        prefered output port"""
        return self._suggested_output_port

    def suggest_map_mode(self, cc_no, channel):
        """ Live -> Script: Live can ask for a suitable mapping mode
        for a given CC"""
        raise in_range(cc_no, 0, 128) or AssertionError
        raise in_range(channel, 0, 16) or AssertionError
        suggested_map_mode = -1
        for control in self.controls:
            if isinstance(control, InputControlElement) and control.message_type() == MIDI_CC_TYPE and control.message_identifier() == cc_no and control.message_channel() == channel:
                suggested_map_mode = control.message_map_mode()
                break

        return suggested_map_mode

    def suggest_needs_takeover(self, cc_no, channel):
        """ Live -> Script: Live can ask whether a given CC needs takeover """
        raise in_range(cc_no, 0, 128) or AssertionError
        raise in_range(channel, 0, 16) or AssertionError
        needs_takeover = True
        for control in self._controls:
            if isinstance(control, InputControlElement) and control.message_type() == MIDI_CC_TYPE and control.message_identifier() == cc_no and control.message_channel() == channel:
                needs_takeover = control.needs_takeover()
                break

        return needs_takeover

    def supports_pad_translation(self):
        return self._pad_translations != None

    def set_highlighting_session_component(self, session_component):
        if self._highlighting_session_component is not None:
            self._set_session_highlight(-1, -1, -1, -1, False)
            self._highlighting_session_component.set_highlighting_callback(None)
        if session_component is not None:
            session_component.set_highlighting_callback(self._set_session_highlight)
        self._highlighting_session_component = session_component

    def highlighting_session_component(self):
        """ Return the session component showing the ring in Live session """
        return self._highlighting_session_component

    def show_message(self, message):
        """ Displays the given message in Live's status bar """
        raise isinstance(message, (str, unicode)) or AssertionError
        self._c_instance.show_message(message)

    def log_message(self, *message):
        """ Writes the given message into Live's main log file """
        message = '(%s) %s' % (self.__class__.__name__, ' '.join(map(str, message)))
        console_message = 'LOG: ' + message
        if debug_print != None:
            debug_print(console_message)
        else:
            print console_message
        if self._c_instance:
            self._c_instance.log_message(message)

    def instance_identifier(self):
        return self._c_instance.instance_identifier()

    def connect_script_instances(self, instanciated_scripts):
        """ Called by the Application as soon as all scripts are initialized.
            You can connect yourself to other running scripts here, as we do it
            connect the extension modules (MackieControlXTs).
        """
        pass

    def request_rebuild_midi_map(self):
        """ Script -> Live.
            When the internal MIDI controller has changed in a way that
            you need to rebuild the MIDI mappings, request a rebuild
            by calling this function This is processed as a request,
            to be sure that its not too often called, because its
            time-critical.
        """
        if not not self._in_build_midi_map:
            raise AssertionError
            self._suppress_requests_counter > 0 and self._rebuild_requests_during_suppression += 1
        else:
            self._c_instance.request_rebuild_midi_map()

    def build_midi_map(self, midi_map_handle):
        """ Live -> Script
            Build DeviceParameter Mappings, that are processed in Audio time, or
            forward MIDI messages explicitly to our receive_midi_functions.
            Which means that when you are not forwarding MIDI, nor mapping parameters,
            you will never get any MIDI messages at all.
        """
        with self._in_build_midi_map():
            self._forwarding_registry.clear()
            self._forwarding_long_identifier_registry.clear()
            for control in self.controls:
                if isinstance(control, InputControlElement):
                    control.install_connections(self._translate_message, partial(self._install_mapping, midi_map_handle), partial(self._install_forwarding, midi_map_handle))

            if self._pad_translations != None:
                self._c_instance.set_pad_translation(self._pad_translations)

    def toggle_lock(self):
        """ Script -> Live
            Use this function to toggle the script's lock on devices
        """
        self._c_instance.toggle_lock()

    def port_settings_changed(self):
        """ Live -> Script
            Is called when either the user changes the MIDI ports that are assigned
            to the script, or the ports state changes due to unplugging/replugging the
            device.
            Will always be called initially when setting up the script.
        """
        self.refresh_state()

    def refresh_state(self):
        """ Live -> Script
            Send out MIDI to completely update the attached MIDI controller.
            Will be called when exiting MIDI map mode
        """
        self.update()

    def update(self):
        with self.component_guard():
            for control in self.controls:
                control.clear_send_cache()

            for component in self._components:
                component.update()

    @profile
    def update_display(self):
        """ Live -> Script
            Aka on_timer. Called every 100 ms and should be used to update display relevant
            parts of the controller
        """
        with self.component_guard():
            with self._is_sending_scheduled_messages():
                self._task_group.update(Defaults.TIMER_DELAY)

    @profile
    def receive_midi(self, midi_bytes):
        """ Live -> Script
            MIDI messages are only received through this function, when explicitly
            forwarded in 'build_midi_map'.
        """
        with self.component_guard():
            self._do_receive_midi(midi_bytes)

    def is_sysex_message(self, midi_bytes):
        return len(midi_bytes) != 3

    def _do_receive_midi(self, midi_bytes):
        if not self.is_sysex_message(midi_bytes):
            self.handle_nonsysex(midi_bytes)
        else:
            self.handle_sysex(midi_bytes)

    def get_recipient_for_nonsysex_midi_message(self, midi_bytes):
        is_pitchbend = midi_bytes[0] & 240 == MIDI_PB_STATUS
        forwarding_key = midi_bytes[:1 if is_pitchbend else 2]
        if forwarding_key in self._forwarding_registry:
            return self._forwarding_registry[forwarding_key]

    def handle_nonsysex(self, midi_bytes):
        is_pitchbend = midi_bytes[0] & 240 == MIDI_PB_STATUS
        value = midi_bytes[1] + (midi_bytes[2] << 7) if is_pitchbend else midi_bytes[2]
        recipient = self.get_recipient_for_nonsysex_midi_message(midi_bytes)
        if recipient is not None:
            recipient.receive_value(value)
        else:
            self.log_message('Got unknown message: ' + str(midi_bytes))

    def handle_sysex(self, midi_bytes):
        result = find_if(lambda (id, _): midi_bytes[:len(id)] == id, self._forwarding_long_identifier_registry.iteritems())
        if result != None:
            id, control = result
            control.receive_value(midi_bytes[len(id):-1])
        else:
            self.log_message('Got unknown sysex message: ', midi_bytes)

    def set_device_component(self, device_component):
        if self._device_component is not None:
            self._device_component.set_lock_callback(None)
        self._device_component = device_component
        self._c_instance.update_locks()
        if device_component is not None:
            device_component.set_lock_callback(self._toggle_lock)
            if self._device_selection_follows_track_selection:
                self.schedule_message(1, self._update_device_selection)

    @contextmanager
    def suppressing_rebuild_requests(self):
        """
        Delays requesting a MIDI map rebuild, if any, until the scope
        of the context manager is exited.
        """
        try:
            self._set_suppress_rebuild_requests(True)
            yield
        finally:
            self._set_suppress_rebuild_requests(False)

    def _set_suppress_rebuild_requests(self, suppress_requests):
        if not not self._in_build_midi_map:
            raise AssertionError
            suppress_requests and self._suppress_requests_counter += 1
        elif not self._suppress_requests_counter > 0:
            raise AssertionError
            self._suppress_requests_counter -= 1
            self._suppress_requests_counter == 0 and self._rebuild_requests_during_suppression > 0 and self.request_rebuild_midi_map()
            self._rebuild_requests_during_suppression = 0

    def set_pad_translations(self, pad_translations):

        def check_translation(translation):
            raise len(translation) == 4 or AssertionError
            raise in_range(translation[0], 0, 4) or AssertionError
            raise in_range(translation[1], 0, 4) or AssertionError
            raise in_range(translation[2], -1, 128) or AssertionError
            raise in_range(translation[3], -1, 16) or AssertionError
            return True

        raise pad_translations is None or all(imap(check_translation, pad_translations)) and len(pad_translations) <= 16 or AssertionError
        self._pad_translations = pad_translations

    def set_enabled(self, enable):
        bool_enable = bool(enable)
        if self._enabled != bool_enable:
            with self.component_guard():
                self._enabled = bool_enable
                root_components = self.root_components
                components = root_components if len(root_components) > 0 else self._components
                for component in components:
                    component._set_enabled_recursive(bool_enable)

    def schedule_message(self, delay_in_ticks, callback, parameter = None):
        """ Schedule a callback to be called after a specified time """
        if not delay_in_ticks > 0:
            raise AssertionError
            if not callable(callback):
                raise AssertionError
                self._is_sending_scheduled_messages or delay_in_ticks -= 1
            message_reference = [None]

            def message(delta):
                if parameter:
                    callback(parameter)
                else:
                    callback()
                self._remaining_scheduled_messages.remove(message_reference)

            message_reference[0] = message
            self._remaining_scheduled_messages.append(message_reference)
            delay_in_ticks and self._task_group.add(Task.sequence(Task.delay(delay_in_ticks), message))
        else:
            self._task_group.add(message)

    def _process_remaining_scheduled_messages(self):
        current_scheduled_messages = tuple(self._remaining_scheduled_messages)
        for message, in current_scheduled_messages:
            message(None)

    def set_feedback_channels(self, channels):
        self._c_instance.set_feedback_channels(channels)

    def set_controlled_track(self, track):
        """ Sets the track that will send its feedback to the control surface """
        raise track == None or isinstance(track, Live.Track.Track) or AssertionError
        self._c_instance.set_controlled_track(track)

    def release_controlled_track(self):
        """ Sets that no track will send its feedback to the control surface """
        self._c_instance.release_controlled_track()

    def _register_control(self, control):
        """ puts control into the list of controls for triggering updates """
        if not control != None:
            raise AssertionError
            raise control not in self.controls or AssertionError('Control registered twice')
            self.controls.append(control)
            control.canonical_parent = self
            isinstance(control, PhysicalDisplayElement) and self._displays.append(control)

    def _register_component(self, component):
        """ puts component into the list of controls for triggering updates """
        raise component != None or AssertionError
        raise component not in self._components or AssertionError('Component registered twice')
        self._components.append(component)
        component.canonical_parent = self

    def _disconnect_and_unregister_all_components(self):
        with self.component_guard():
            for component in self._components:
                component.canonical_parent = None
                component.disconnect()

        self._components = []
        self.set_highlighting_session_component(None)
        self.set_device_component(None)

    @contextmanager
    def component_guard(self):
        """
        Context manager that guards user code.  This prevents
        unnecesary updating and enables several optimisations.  Should
        be used to guard calls to components or control elements.
        """
        if not self._in_component_guard:
            with self._in_component_guard():
                with self._component_guard():
                    yield
        else:
            yield

    @property
    def in_component_guard(self):
        return bool(self._in_component_guard)

    @contextmanager
    def _component_guard(self):
        with self._control_surface_injector:
            with self.suppressing_rebuild_requests():
                with self.accumulating_midi_messages():
                    yield

    @profile
    def call_listeners(self, listeners):
        with self.component_guard():
            for listener in ifilter(lambda l: l != None, listeners):
                listener()

    @contextmanager
    def accumulating_midi_messages(self):
        with self._accumulate_midi_messages():
            try:
                yield
            finally:
                self._flush_midi_messages()

    def get_control_by_name(self, control_name):
        return find_if(lambda c: c.name == control_name, self.controls)

    def _send_midi(self, midi_event_bytes, optimized = True):
        """
        Script -> Live
        Use this function to send MIDI events through Live to the
        _real_ MIDI devices that this script is assigned to.
        
        When optimized=True it is assumed that messages can be
        dropped -- only the last message within an update for a
        given (channel, key) has visible effects.
        """
        if self._accumulate_midi_messages:
            sysex_status_byte = 240
            entry = (self._midi_message_count, midi_event_bytes)
            if optimized and midi_event_bytes[0] != sysex_status_byte:
                self._midi_message_dict[midi_event_bytes[0], midi_event_bytes[1]] = entry
            else:
                self._midi_message_list.append(entry)
            self._midi_message_count += 1
        else:
            self._do_send_midi(midi_event_bytes)
        return True

    def _flush_midi_messages(self):
        raise self._accumulate_midi_messages or AssertionError
        for _, message in sorted(chain(self._midi_message_list, self._midi_message_dict.itervalues()), key=first):
            self._do_send_midi(message)

        self._midi_message_dict.clear()
        self._midi_message_list[:] = []
        self._midi_message_count = 0

    def _do_send_midi(self, midi_event_bytes):
        try:
            self._c_instance.send_midi(midi_event_bytes)
        except:
            self.log_message('Error while sending midi message', midi_event_bytes)
            traceback.print_exc()
            return False

        return True

    def _install_mapping(self, midi_map_handle, control, parameter, feedback_delay, feedback_map):
        if not self._in_build_midi_map:
            raise AssertionError
            raise control != None and parameter != None or AssertionError
            raise isinstance(parameter, Live.DeviceParameter.DeviceParameter) or AssertionError
            raise isinstance(control, InputControlElement) or AssertionError
            raise isinstance(feedback_delay, int) or AssertionError
            if not isinstance(feedback_map, tuple):
                raise AssertionError
                success = False
                feedback_rule = None
                feedback_rule = control.message_type() is MIDI_NOTE_TYPE and Live.MidiMap.NoteFeedbackRule()
                feedback_rule.note_no = control.message_identifier()
                feedback_rule.vel_map = feedback_map
            elif control.message_type() is MIDI_CC_TYPE:
                feedback_rule = Live.MidiMap.CCFeedbackRule()
                feedback_rule.cc_no = control.message_identifier()
                feedback_rule.cc_value_map = feedback_map
            elif control.message_type() is MIDI_PB_TYPE:
                feedback_rule = Live.MidiMap.PitchBendFeedbackRule()
                feedback_rule.value_pair_map = feedback_map
            if not feedback_rule != None:
                raise AssertionError
                feedback_rule.channel = control.message_channel()
                feedback_rule.delay_in_ms = feedback_delay
                success = control.message_type() is MIDI_NOTE_TYPE and Live.MidiMap.map_midi_note_with_feedback_map(midi_map_handle, parameter, control.message_channel(), control.message_identifier(), feedback_rule)
            elif control.message_type() is MIDI_CC_TYPE:
                success = Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, control.message_channel(), control.message_identifier(), control.message_map_mode(), feedback_rule, not control.needs_takeover(), control.mapping_sensitivity)
            elif control.message_type() is MIDI_PB_TYPE:
                success = Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, parameter, control.message_channel(), feedback_rule, not control.needs_takeover())
            success and Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter)
        return success

    def _install_forwarding(self, midi_map_handle, control):
        if not self._in_build_midi_map:
            raise AssertionError
            raise control != None or AssertionError
            if not isinstance(control, InputControlElement):
                raise AssertionError
                success = False
                success = control.message_type() is MIDI_NOTE_TYPE and Live.MidiMap.forward_midi_note(self._c_instance.handle(), midi_map_handle, control.message_channel(), control.message_identifier())
            elif control.message_type() is MIDI_CC_TYPE:
                success = Live.MidiMap.forward_midi_cc(self._c_instance.handle(), midi_map_handle, control.message_channel(), control.message_identifier())
            elif control.message_type() is MIDI_PB_TYPE:
                success = Live.MidiMap.forward_midi_pitchbend(self._c_instance.handle(), midi_map_handle, control.message_channel())
            else:
                raise control.message_type() == MIDI_SYSEX_TYPE or AssertionError
                success = True
            forwarding_keys = success and control.identifier_bytes()
            for key in forwarding_keys:
                registry = self._forwarding_registry if control.message_type() != MIDI_SYSEX_TYPE else self._forwarding_long_identifier_registry
                raise key not in registry.keys() or AssertionError('Registry key %s registered twice. Check Midi messages!' % str(key))
                registry[key] = control

        return success

    def _translate_message(self, type, from_identifier, from_channel, to_identifier, to_channel):
        if not type in (MIDI_CC_TYPE, MIDI_NOTE_TYPE):
            raise AssertionError
            raise from_identifier in range(128) or AssertionError
            raise from_channel in range(16) or AssertionError
            raise to_identifier in range(128) or AssertionError
            raise to_channel in range(16) or AssertionError
            type == MIDI_CC_TYPE and self._c_instance.set_cc_translation(from_identifier, from_channel, to_identifier, to_channel)
        elif type == MIDI_NOTE_TYPE:
            self._c_instance.set_note_translation(from_identifier, from_channel, to_identifier, to_channel)
        else:
            raise False or AssertionError

    def _set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
        raise list((track_offset,
         scene_offset,
         width,
         height)).count(-1) != 4 and (width > 0 or AssertionError)
        if not height > 0:
            raise AssertionError
        self._c_instance.set_session_highlight(track_offset, scene_offset, width, height, include_return_tracks)

    def _on_track_list_changed(self):
        for component in self._components:
            component.on_track_list_changed()

        self.schedule_message(1, self._on_selected_track_changed)

    def _on_scene_list_changed(self):
        for component in self._components:
            component.on_scene_list_changed()

    def _on_selected_track_changed(self):
        for component in self._components:
            component.on_selected_track_changed()

        if self._device_component is not None and self._device_selection_follows_track_selection:
            self._update_device_selection()

    def _on_selected_scene_changed(self):
        for component in self._components:
            component.on_selected_scene_changed()

    def _toggle_lock(self):
        raise self._device_component != None or AssertionError
        self._c_instance.toggle_lock()

    def _refresh_displays(self):
        """
        Make sure the displays of the control surface display current
        data.
        """
        for display in self._displays:
            display.update()
            display._tasks.update(Defaults.TIMER_DELAY)

    def _update_device_selection(self):
        track = self.song().view.selected_track
        device_to_select = track.view.selected_device
        if device_to_select == None and len(track.devices) > 0:
            device_to_select = track.devices[0]
        if device_to_select != None:
            self.song().view.select_device(device_to_select)
            self._device_component.set_device(self.song().appointed_device)
        else:
            self._device_component.set_device(None)


class OptimizedControlSurface(ControlSurface):
    """
    Control Surface that makes use of the optimized ownership handler for controls.
    """

    def __init__(self, *a, **k):
        super(OptimizedControlSurface, self).__init__(*a, **k)
        self._optimized_ownership_handler = OptimizedOwnershipHandler()
        injecting = inject(element_ownership_handler=const(self._optimized_ownership_handler))
        self._ownership_handler_injector = injecting.everywhere()

    @contextmanager
    def _component_guard(self):
        with super(OptimizedControlSurface, self)._component_guard():
            with self._ownership_handler_injector:
                yield
                self._optimized_ownership_handler.commit_ownership_changes()

    def _register_control(self, control):
        super(OptimizedControlSurface, self)._register_control(control)
        if hasattr(control, '_is_resource_based'):
            control._is_resource_based = True