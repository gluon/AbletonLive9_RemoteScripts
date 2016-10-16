#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/Control.py
from __future__ import absolute_import, with_statement
from functools import partial
from itertools import izip_longest
from . import Task
from .Defaults import MOMENTARY_DELAY
from .SubjectSlot import SlotManager
from .Util import clamp, lazy_attribute, mixin, nop, first, second, is_matrix, flatten, product

class ControlManager(SlotManager):

    def __init__(self, *a, **k):
        super(ControlManager, self).__init__(*a, **k)
        self._control_states = dict()

    @lazy_attribute
    def _tasks(self):
        return Task.TaskGroup()

    def control_notifications_enabled(self):
        return True

    def update(self):
        for control_state in self._control_states.values():
            control_state.update()


def control_event(event_name):

    def event_decorator(self):

        def event_listener_decorator(event_listener):
            raise event_listener not in self._event_listeners or AssertionError
            self._event_listeners[event_name] = event_listener
            return self

        return event_listener_decorator

    return property(event_decorator)


class Control(object):
    value = control_event('value')

    class State(SlotManager):
        enabled = True

        def __init__(self, control = None, manager = None, channel = None, identifier = None, *a, **k):
            super(Control.State, self).__init__(*a, **k)
            raise control is not None or AssertionError
            raise manager is not None or AssertionError
            self._manager = manager
            self._value_listener = control._event_listeners.get('value', None)
            self._event_listeners = control._event_listeners
            self._control_element = None
            self._value_slot = None
            self._channel = channel
            self._identifier = identifier
            self._register_value_slot(manager, control)
            manager.register_slot_manager(self)

        def set_control_element(self, control_element):
            self._control_element = control_element
            if self._control_element:
                self._control_element.reset_state()
                if self._channel is not None:
                    self._control_element.set_channel(self._channel)
                if self._identifier is not None:
                    self._control_element.set_identifier(self._identifier)
            if self._value_slot:
                self._value_slot.subject = control_element

        def _register_value_slot(self, manager, control):
            if self._event_listener_required():
                self._value_slot = self.register_slot(None, self._on_value, 'value')

        def _event_listener_required(self):
            return len(self._event_listeners) > 0

        def _on_value(self, value, *a, **k):
            if self._value_listener and self._notifications_enabled():
                self._value_listener(self._manager, value, self, *a, **k)

        def _notifications_enabled(self):
            return self.enabled and self._manager.control_notifications_enabled()

        def update(self):
            pass

        def _get_channel(self):
            return self._channel

        def _set_channel(self, channel):
            self._channel = channel
            if self._control_element:
                self._control_element.set_channel(self._channel)

        channel = property(_get_channel, _set_channel)

        def _get_identifier(self):
            return self._identifier

        def _set_identifier(self, value):
            self._identifier = value
            if self._control_element:
                self._control_element.set_identifier(self._identifier)

        identifier = property(_get_identifier, _set_identifier)

    _extra_kws = {}
    _extra_args = []

    def __init__(self, extra_args = None, extra_kws = None, *a, **k):
        super(Control, self).__init__(*a, **k)
        self._event_listeners = {}
        if extra_args is not None:
            self._extra_args = extra_args
        if extra_kws is not None:
            self._extra_kws = extra_kws

    def __get__(self, manager, owner):
        return self._get_state(manager)

    def __set__(self, manager, owner):
        raise RuntimeError('Cannot change control.')

    def _get_state(self, manager):
        if self not in manager._control_states:
            manager._control_states[self] = None
            manager._control_states[self] = self.State(self, manager, *self._extra_args, **self._extra_kws)
        if manager._control_states[self] is None:
            raise RuntimeError('Cannot fetch state during construction of controls.')
        return manager._control_states[self]

    def _clear_state(self, manager):
        if self in manager._control_states:
            del manager._control_states[self]


class MappedControl(Control):

    class State(Control.State):

        def __init__(self, control = None, manager = None, *a, **k):
            raise control is not None or AssertionError
            raise manager is not None or AssertionError
            super(MappedControl.State, self).__init__(control, manager, *a, **k)
            self._direct_mapping = None

        def set_control_element(self, control_element):
            if self._control_element:
                self._control_element.release_parameter()
            super(MappedControl.State, self).set_control_element(control_element)
            self._update_direct_connection()

        def _get_direct_mapping(self):
            return self._direct_mapping

        def _set_direct_mapping(self, direct_mapping):
            self._direct_mapping = direct_mapping
            self._update_direct_connection()

        mapped_parameter = property(_get_direct_mapping, _set_direct_mapping)

        def _update_direct_connection(self):
            if self._control_element:
                self._control_element.connect_to(self._direct_mapping)

        def _notifications_enabled(self):
            return super(MappedControl.State, self)._notifications_enabled() and self._direct_mapping is None

    def __init__(self, *a, **k):
        super(MappedControl, self).__init__(extra_args=a, extra_kws=k)


class ButtonControl(Control):
    DELAY_TIME = MOMENTARY_DELAY
    REPEAT_RATE = 0.1
    pressed = control_event('pressed')
    released = control_event('released')
    pressed_delayed = control_event('pressed_delayed')
    released_delayed = control_event('released_delayed')
    released_immediately = control_event('released_immediately')

    class State(Control.State):

        def __init__(self, control = None, manager = None, color = None, pressed_color = None, disabled_color = None, repeat = False, enabled = True, *a, **k):
            raise control is not None or AssertionError
            raise manager is not None or AssertionError
            super(ButtonControl.State, self).__init__(control, manager, *a, **k)
            self._pressed_listener = control._event_listeners.get('pressed', None)
            self._released_listener = control._event_listeners.get('released', None)
            self._pressed_delayed_listener = control._event_listeners.get('pressed_delayed', None)
            self._released_delayed_listener = control._event_listeners.get('released_delayed', None)
            self._released_immediately_listener = control._event_listeners.get('released_immediately', None)
            self._repeat = repeat
            self._is_pressed = False
            self._enabled = enabled
            self._color = color if color is not None else 'DefaultButton.On'
            self._disabled_color = disabled_color if disabled_color is not None else 'DefaultButton.Disabled'
            self._pressed_color = pressed_color

        def _get_color(self):
            return self._color

        def _set_color(self, value):
            self._color = value
            self._send_current_color()

        color = property(_get_color, _set_color)

        def _get_pressed_color(self):
            return self._pressed_color

        def _set_pressed_color(self, value):
            self._pressed_color = value
            self._send_current_color()

        pressed_color = property(_get_pressed_color, _set_pressed_color)

        def _get_disabled_color(self):
            return self._disabled_color

        def _set_disabled_color(self, value):
            self._disabled_color = value
            self._send_current_color()

        disabled_color = property(_get_disabled_color, _set_disabled_color)

        def _get_enabled(self):
            return self._enabled

        def _set_enabled(self, enabled):
            if self._enabled != enabled:
                if not enabled:
                    self._release_button()
                self._enabled = enabled
                self._send_current_color()

        enabled = property(_get_enabled, _set_enabled)

        @property
        def is_momentary(self):
            return self._control_element and self._control_element.is_momentary()

        @property
        def is_pressed(self):
            return self._is_pressed

        def _event_listener_required(self):
            return True

        def set_control_element(self, control_element):
            if self._control_element != control_element:
                self._release_button()
            super(ButtonControl.State, self).set_control_element(control_element)
            self._send_current_color()

        def _send_current_color(self):
            if self._control_element:
                if not self._enabled:
                    self._control_element.set_light(self._disabled_color)
                elif self._pressed_color and self.is_pressed:
                    self._control_element.set_light(self._pressed_color)
                else:
                    self._control_element.set_light(self._color)

        def _on_value(self, value, *a, **k):
            if self._notifications_enabled():
                if not self.is_momentary:
                    self._press_button()
                    self._release_button()
                elif value:
                    self._press_button()
                else:
                    self._release_button()
                super(ButtonControl.State, self)._on_value(value, *a, **k)
            self._send_current_color()

        def _press_button(self):
            is_pressed = self._is_pressed
            self._is_pressed = True
            if self._notifications_enabled() and not is_pressed:
                if self._pressed_listener is not None:
                    if self._repeat:
                        self._repeat_task.restart()
                    self._pressed_listener(self._manager, self)
                if self._has_delayed_event():
                    self._delay_task.restart()

        def _release_button(self):
            is_pressed = self._is_pressed
            self._is_pressed = False
            if self._notifications_enabled() and is_pressed:
                if self._released_listener is not None:
                    self._released_listener(self._manager, self)
                if self._repeat:
                    self._repeat_task.kill()
                if self._has_delayed_event():
                    if self._delay_task.is_running:
                        self._released_immediately_listener(self._manager, self)
                        self._delay_task.kill()
                    else:
                        self._released_delayed_listener(self._manager, self)

        @lazy_attribute
        def _delay_task(self):
            return self._manager._tasks.add(Task.sequence(Task.wait(ButtonControl.DELAY_TIME), Task.run(self._on_pressed_delayed)))

        @lazy_attribute
        def _repeat_task(self):
            notify_pressed = partial(self._pressed_listener, self._manager, self)
            return self._manager._tasks.add(Task.sequence(Task.wait(ButtonControl.DELAY_TIME), Task.loop(Task.wait(ButtonControl.REPEAT_RATE), Task.run(notify_pressed))))

        def _has_delayed_event(self):
            return self._pressed_delayed_listener is not None or self._released_delayed_listener is not None or self._released_immediately_listener is not None

        def _on_pressed_delayed(self):
            if self._notifications_enabled() and self._is_pressed:
                self._pressed_delayed_listener(self._manager, self)

        def update(self):
            self._send_current_color()

    def __init__(self, *a, **k):
        super(ButtonControl, self).__init__(extra_args=a, extra_kws=k)


class ToggleButtonControl(Control):
    toggled = control_event('toggled')

    class State(Control.State):

        def __init__(self, control = None, manager = None, untoggled_color = None, toggled_color = None, *a, **k):
            super(ToggleButtonControl.State, self).__init__(control, manager, *a, **k)
            self._untoggled_color = untoggled_color or 'DefaultButton.Off'
            self._toggled_color = toggled_color or 'DefaultButton.On'
            self._is_toggled = False
            self._toggled_listener = control._event_listeners.get('toggled', None)

        def _get_is_toggled(self):
            return self._is_toggled

        def _set_is_toggled(self, toggled):
            if self._is_toggled != toggled:
                self._is_toggled = toggled
                if self._toggled_listener and self._notifications_enabled():
                    self._toggled_listener(self._manager, self._is_toggled, self)
                self._send_current_color()

        is_toggled = property(_get_is_toggled, _set_is_toggled)

        def _get_untoggled_color(self):
            return self._untoggled_color

        def _set_untoggled_color(self, value):
            self._untoggled_color = value
            self._send_current_color()

        untoggled_color = property(_get_untoggled_color, _set_untoggled_color)

        def _get_toggled_color(self):
            return self._toggled_color

        def _set_toggled_color(self, value):
            self._toggled_color = value
            self._send_current_color()

        toggled_color = property(_get_toggled_color, _set_toggled_color)

        def set_control_element(self, control_element):
            super(ToggleButtonControl.State, self).set_control_element(control_element)
            self._send_current_color()

        def _send_current_color(self):
            if self._control_element:
                self._control_element.set_light(self._toggled_color if self._is_toggled else self._untoggled_color)

        def _is_momentary(self):
            return self._control_element and self._control_element.is_momentary()

        def _on_value(self, value, *a, **k):
            if self._notifications_enabled():
                if value or not self._is_momentary():
                    self._is_toggled = not self._is_toggled
                    if self._toggled_listener:
                        self._toggled_listener(self._manager, self._is_toggled, self)
                    self._send_current_color()
                super(ToggleButtonControl.State, self)._on_value(value, *a, **k)

        def update(self):
            self._send_current_color()

    def __init__(self, *a, **k):
        super(ToggleButtonControl, self).__init__(extra_args=a, extra_kws=k)


class RadioButtonControl(Control):
    checked = control_event('checked')

    class State(Control.State):

        def __init__(self, control, manager = None, unchecked_color = None, checked_color = None, *a, **k):
            super(RadioButtonControl.State, self).__init__(control, manager, *a, **k)
            self._unchecked_color = unchecked_color or 'DefaultButton.Off'
            self._checked_color = checked_color or 'DefaultButton.On'
            self._checked = False
            self._checked_listener = control._event_listeners.get('checked', None)
            self._on_checked = nop

        def _get_is_checked(self):
            return self._checked

        def _set_is_checked(self, value):
            if self._checked != value:
                self._checked = value
                self._notify_checked()
                self._send_current_color()

        is_checked = property(_get_is_checked, _set_is_checked)

        def _get_unchecked_color(self):
            return self._unchecked_color

        def _set_unchecked_color(self, value):
            self._unchecked_color = value
            self._send_current_color()

        unchecked_color = property(_get_unchecked_color, _set_unchecked_color)

        def _get_checked_color(self):
            return self._checked_color

        def _set_checked_color(self, value):
            self._checked_color = value
            self._send_current_color()

        checked_color = property(_get_checked_color, _set_checked_color)

        def set_control_element(self, control_element):
            super(RadioButtonControl.State, self).set_control_element(control_element)
            self._send_current_color()

        def _send_current_color(self):
            if self._control_element:
                self._control_element.set_light(self._checked_color if self._checked else self._unchecked_color)

        def _is_momentary(self):
            return self._control_element and self._control_element.is_momentary()

        def _on_value(self, value, *a, **k):
            if self._notifications_enabled():
                checked = value or self._is_momentary()
                if checked and not self._checked:
                    self.is_checked = True
                super(RadioButtonControl.State, self)._on_value(value, *a, **k)

        def _notify_checked(self):
            if self._checked:
                if self._checked_listener and self._notifications_enabled():
                    self._checked_listener(self._manager, self)
                self._on_checked()

        def update(self):
            self._send_current_color()

    def __init__(self, *a, **k):
        super(RadioButtonControl, self).__init__(extra_args=a, extra_kws=k)


class EncoderControl(Control):
    TOUCH_TIME = 0.5
    touched = control_event('touched')
    released = control_event('released')

    class State(Control.State):

        def __init__(self, control = None, manager = None, *a, **k):
            if not control is not None:
                raise AssertionError
                raise manager is not None or AssertionError
                super(EncoderControl.State, self).__init__(control, manager, *a, **k)
                self._is_touched = False
                self._touched_listener = control._event_listeners.get('touched', None)
                self._released_listener = control._event_listeners.get('released', None)
                self._touch_value_slot = None
                self._timer_based = False
                self._touch_value_slot = (self._touched_listener or self._released_listener) and self.register_slot(None, self._on_touch_value, 'touch_value')

        @lazy_attribute
        def _release_task(self):
            return self._manager._tasks.add(Task.sequence(Task.wait(EncoderControl.TOUCH_TIME), Task.run(self._release_encoder)))

        @property
        def is_touched(self):
            return self._is_touched

        def set_control_element(self, control_element):
            if self._control_element != control_element:
                self._release_encoder()
            super(EncoderControl.State, self).set_control_element(control_element)
            if self._touch_value_slot:
                self._touch_value_slot.subject = control_element
            if control_element and hasattr(control_element, 'is_pressed') and control_element.is_pressed():
                self._touch_encoder()

        def _touch_encoder(self):
            is_touched = self._is_touched
            self._is_touched = True
            if self._notifications_enabled() and self._touched_listener and not is_touched:
                self._touched_listener(self._manager, self)

        def _release_encoder(self):
            is_touched = self._is_touched
            self._is_touched = False
            self._timer_based = False
            if self._notifications_enabled() and self._released_listener and is_touched:
                self._released_listener(self._manager, self)

        def _on_value(self, value, *a, **k):
            if self._notifications_enabled():
                if not self._is_touched:
                    self._timer_based = True
                    self._touch_encoder()
                    self._release_task.restart()
                elif self._timer_based:
                    self._release_task.restart()
                if self._value_listener and self._control_element:
                    normalized_value = self._control_element.normalize_value(value)
                    self._value_listener(self._manager, normalized_value, self, *a, **k)

        def _on_touch_value(self, value, *a, **k):
            if self._notifications_enabled():
                if value:
                    self._touch_encoder()
                else:
                    self._release_encoder()


class PlayableControl(ButtonControl):
    """
    Control that will make the elements MIDI go into Live, to make it playable.
    """

    class State(ButtonControl.State):

        def __init__(self, *a, **k):
            super(PlayableControl.State, self).__init__(*a, **k)
            self._enabled = True
            self._playable = True

        def set_control_element(self, control_element):
            super(PlayableControl.State, self).set_control_element(control_element)
            self._update_script_forwarding()
            self._send_current_color()

        def _update_script_forwarding(self):
            if self._control_element and self._enabled:
                self._control_element.suppress_script_forwarding = self._playable

        def _get_enabled(self):
            return self._enabled

        def _set_enabled(self, enabled):
            super(PlayableControl.State, self)._set_enabled(enabled)
            if not enabled and self._control_element:
                self._control_element.reset_state()
                self._send_current_color()
            else:
                self.set_control_element(self._control_element)

        enabled = property(_get_enabled, _set_enabled)

        def set_playable(self, value):
            self._playable = value
            self._update_script_forwarding()

        def _notifications_enabled(self):
            return super(PlayableControl.State, self)._notifications_enabled() and not self._playable


_DYNAMIC_CONTROL_COUNT = None

class ControlList(Control):
    DYNAMIC_CONTROL_COUNT = _DYNAMIC_CONTROL_COUNT

    class State(Control.State):
        _extra_kws = {}
        _extra_args = []

        def __init__(self, control = None, manager = None, extra_args = None, extra_kws = None, unavailable_color = None, *a, **k):
            if not control is not None:
                raise AssertionError
                super(ControlList.State, self).__init__(manager=manager, control=control, *a, **k)
                self._control_elements = None
                self._control_type = control.control_type
                self._controls = []
                self._dynamic_create = False
                self._unavailable_color = unavailable_color if unavailable_color is not None else 'DefaultButton.Disabled'
                if extra_args is not None:
                    self._extra_args = extra_args
                self._extra_kws = extra_kws is not None and extra_kws
            self.control_count = control.control_count

        def _get_control_count(self):
            return len(self._controls)

        def _set_control_count(self, count):
            self._dynamic_create = count == ControlList.DYNAMIC_CONTROL_COUNT
            if self._dynamic_create:
                count = len(self._control_elements) if self._control_elements else 0
            self._create_controls(count)
            self._update_controls()

        control_count = property(_get_control_count, _set_control_count)

        def _get_unavailable_color(self):
            return self._unavailable_color

        def _set_unavailable_color(self, value):
            self._unavailable_color = value
            control_elements = self._control_elements or []
            for control, element in izip_longest(self._controls, control_elements):
                if not control and element:
                    self._send_unavailable_color(element)

        unavailable_color = property(_get_unavailable_color, _set_unavailable_color)

        def _create_controls(self, count):
            self._disconnect_controls()
            self._controls = [ self._make_control(i) for i in xrange(count) ]

        def _disconnect_controls(self):
            for control in self._controls:
                control._get_state(self._manager).disconnect()
                control._clear_state(self._manager)

        def _make_control(self, index):
            control = self._control_type(*self._extra_args, **self._extra_kws)
            control._event_listeners = self._event_listeners
            control_state = control._get_state(self._manager)
            if not hasattr(control_state, 'index'):
                control_state.index = index
            else:
                raise RuntimeError("Cannot set 'index' attribute. Attribute already set.")
            return control

        def set_control_element(self, control_elements):
            self._control_elements = control_elements
            if self._dynamic_create and len(control_elements or []) != len(self._control_element or []):
                self._create_controls(len(control_elements or []))
            self._update_controls()

        def _update_controls(self):
            control_elements = self._control_elements or []
            for control, element in izip_longest(self._controls, control_elements):
                if control:
                    control._get_state(self._manager).set_control_element(element)
                elif element:
                    element.reset_state()
                    self._send_unavailable_color(element)

        def _send_unavailable_color(self, element):
            if hasattr(element, 'set_light'):
                element.set_light(self._unavailable_color)

        def __getitem__(self, index):
            return self._controls[index]._get_state(self._manager)

        def _on_value(self, value, *a, **k):
            pass

        def _register_value_slot(self, manager, control):
            pass

    def __init__(self, control_type = None, control_count = _DYNAMIC_CONTROL_COUNT, *a, **k):
        super(ControlList, self).__init__(extra_args=a, extra_kws=k, *a, **k)
        self.control_type = control_type
        self.control_count = control_count


class RadioButtonGroup(ControlList, RadioButtonControl):

    class State(ControlList.State):

        def __init__(self, *a, **k):
            self._checked_index = 0
            super(RadioButtonGroup.State, self).__init__(*a, **k)

        def _create_controls(self, count):
            self._checked_index = clamp(self._checked_index, 0, count - 1)
            super(RadioButtonGroup.State, self)._create_controls(count)

        def _make_control(self, index):
            control = super(RadioButtonGroup.State, self)._make_control(index)
            control_state = control._get_state(self._manager)
            control_state._on_checked = partial(self._on_checked, control_state)
            control_state.is_checked = index == self._checked_index
            return control

        def _on_checked(self, checked_control):
            for control in self._controls:
                control = control._get_state(self._manager)
                control.is_checked = control == checked_control

            self._checked_index = checked_control.index

    def __init__(self, *a, **k):
        super(RadioButtonGroup, self).__init__(RadioButtonControl, *a, **k)


_DYNAMIC_MATRIX_DIMENSIONS = (None, None)

class MatrixControl(ControlList):
    DYNAMIC_DIMENSIONS = _DYNAMIC_MATRIX_DIMENSIONS

    class State(ControlList.State):

        def __init__(self, control = None, manager = None, *a, **k):
            raise control is not None or AssertionError
            raise manager is not None or AssertionError
            self._dimensions = (None, None)
            super(MatrixControl.State, self).__init__(control, manager, *a, **k)

        def _get_dimensions(self):
            return self._dimensions

        def _set_dimensions(self, dimensions):
            if not first(dimensions):
                raise AssertionError
                raise second(dimensions) or AssertionError
                self._dynamic_create = dimensions == MatrixControl.DYNAMIC_DIMENSIONS
                count = self._dynamic_create and (len(self._control_elements) if self._control_elements else 0)
            self._dimensions = dimensions
            count = first(dimensions) * second(dimensions)
            self._create_controls(count)
            self._update_controls()

        dimensions = property(_get_dimensions, _set_dimensions)

        def _make_control(self, index):
            control = super(MatrixControl.State, self)._make_control(index)
            control_state = control._get_state(self._manager)
            if not hasattr(control_state, 'coordinate'):
                control_state.coordinate = (int(index / self.width), index % self.width)
            else:
                raise RuntimeError("Cannot set 'coordinate' attribute. Attribute already set.")
            return control

        def set_control_element(self, control_elements):
            dimensions = (None, None)
            if hasattr(control_elements, 'width') and hasattr(control_elements, 'height'):
                dimensions = (control_elements.height(), control_elements.width())
                if not self._dynamic_create:
                    control_elements = [ control_elements.get_button(col, row) for row, col in product(xrange(self.height), xrange(self.width)) ]
            elif is_matrix(control_elements):
                dimensions = (len(control_elements), len(first(control_elements)))
                if not self._dynamic_create:
                    control_elements = [ row[0:self.width] for row in control_elements ]
                control_elements = [ _ for _ in flatten(control_elements) ]
            elif control_elements is not None:
                raise RuntimeError('Control Elements must be a matrix')
            if self._dynamic_create and None not in dimensions:
                self._dimensions = dimensions
                self._create_controls(first(dimensions) * second(dimensions))
                self._update_controls()
            super(MatrixControl.State, self).set_control_element(control_elements)

        def get_control(self, row, column):
            index = row * self.width + column
            return self._controls[index]._get_state(self._manager)

        @property
        def width(self):
            return second(self._dimensions)

        @property
        def height(self):
            return first(self._dimensions)

    def __init__(self, *a, **k):
        super(MatrixControl, self).__init__(*a, **k)


_control_list_classes = dict()
_control_matrix_classes = dict()

def control_list(control_type, *a, **k):
    if control_type == RadioButtonControl:
        return RadioButtonGroup(*a, **k)
    c = _control_list_classes.get(control_type, None)
    if not c:
        c = mixin(ControlList, control_type)
        c.State = mixin(ControlList.State, control_type.State)
        _control_list_classes[control_type] = c
    return c(control_type, *a, **k)


def control_matrix(control_type, *a, **k):
    m = _control_matrix_classes.get(control_type, None)
    if not m:
        m = mixin(MatrixControl, control_type)
        m.State = mixin(MatrixControl.State, control_type.State)
        _control_matrix_classes[control_type] = m
    return m(control_type, *a, **k)