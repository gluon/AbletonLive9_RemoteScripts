#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/elements/combo.py
from __future__ import absolute_import, print_function
from itertools import imap
from contextlib import contextmanager
from ...base import const, depends, find_if, is_iterable, lazy_attribute, nop, ProxyBase, SlotManager, Subject, listens, task
from .. import defaults
from ..compound_element import CompoundElement
from ..input_control_element import ParameterSlot
from ..control_element import NotifyingControlElement, get_element
from ..resource import DEFAULT_PRIORITY
from .button import ButtonElementMixin

class WrapperElement(CompoundElement, ProxyBase):
    """
    Helper class for implementing a wrapper for a specific control,
    forwarding most basic operations to it.
    
    Note that the wrapped control element is not registered to allow
    this flexibly specific implementations.
    """

    class ProxiedInterface(CompoundElement.ProxiedInterface):

        def __getattr__(self, name):
            wrapped = self.outer.__dict__['_wrapped_control']
            return getattr(wrapped.proxied_interface, name)

    def __init__(self, wrapped_control = None, *a, **k):
        super(WrapperElement, self).__init__(*a, **k)
        self._wrapped_control = get_element(wrapped_control)
        self._parameter_slot = ParameterSlot()

    @property
    def proxied_object(self):
        if self._is_initialized() and self.owns_control_element(self._wrapped_control):
            return self._wrapped_control

    def _is_initialized(self):
        return '_wrapped_control' in self.__dict__

    def register_wrapped(self):
        self.register_control_element(self._wrapped_control)

    def unregister_wrapped(self):
        self.unregister_control_element(self._wrapped_control)

    @property
    def wrapped_control(self):
        return self._wrapped_control

    def __nonzero__(self):
        return self.owns_control_element(self._wrapped_control)

    def on_nested_control_element_received(self, control):
        if control == self._wrapped_control:
            self._parameter_slot.control = control

    def on_nested_control_element_lost(self, control):
        if control == self._wrapped_control:
            self._parameter_slot.control = None

    def on_nested_control_element_value(self, value, control):
        if control == self._wrapped_control:
            self.notify_value(value)

    def connect_to(self, parameter):
        if self._parameter_slot.parameter == None:
            self.request_listen_nested_control_elements()
        self._parameter_slot.parameter = parameter

    def release_parameter(self):
        if self._parameter_slot.parameter != None:
            self.unrequest_listen_nested_control_elements()
        self._parameter_slot.parameter = None


class ComboElement(WrapperElement):
    """
    An element representing a combination of buttons.  It will forward
    the button values when all the modifiers have the specified state,
    and silently discard them when they are not. If no state is provided
    for the modifiers, being pressed is assumed as the target state.
    
    When using resources, this element:
      - Grabs the modifiers at all times.
      - Grabs the action button only when all modifiers have the right state.
    
    This means that the action button can be used at the same time in
    the same Layer in a combined and un-combined fashion.  The setters
    of the layer buttons will be called properly so the button gets
    the right light updated when the modifiers are pressed.  For
    example see how the SessionRecording takes the automation_button
    in a combo and raw.
    """
    priority_increment = 0.5

    def __init__(self, control = None, modifier = [], *a, **k):
        super(ComboElement, self).__init__(wrapped_control=control, *a, **k)
        self._combo_modifiers = map(get_element, modifier) if not isinstance(modifier, basestring) and is_iterable(modifier) else [get_element(modifier)]
        raise all(imap(lambda x: x.is_momentary(), self._combo_modifiers)) or AssertionError
        self.register_control_elements(*self._combo_modifiers)
        self.request_listen_nested_control_elements()

    def reset(self):
        if self.owns_control_element(self._wrapped_control):
            self._wrapped_control.reset()

    def get_control_element_priority(self, element, priority):
        if element == self._wrapped_control:
            raise priority is None or 1 - priority + int(priority) > self.priority_increment or AssertionError('Attempting to increase the priority over a whole unit. ' + 'Make sure the combo element is not inside another combo element')
            priority = DEFAULT_PRIORITY if priority is None else priority
            return priority + self.priority_increment
        return priority

    def on_nested_control_element_received(self, control):
        if control != self._wrapped_control:
            self._enforce_control_invariant()
        else:
            super(ComboElement, self).on_nested_control_element_received(control)

    def on_nested_control_element_lost(self, control):
        if control != self._wrapped_control:
            self._enforce_control_invariant()
        else:
            super(ComboElement, self).on_nested_control_element_lost(control)

    def on_nested_control_element_value(self, value, control):
        if control != self._wrapped_control:
            self._enforce_control_invariant()
        else:
            super(ComboElement, self).on_nested_control_element_value(value, control)

    def _enforce_control_invariant(self):
        if self._combo_is_on():
            if not self.has_control_element(self._wrapped_control):
                self.register_control_element(self._wrapped_control)
        elif self.has_control_element(self._wrapped_control):
            self.unregister_control_element(self._wrapped_control)

    def _combo_is_on(self):
        return all(imap(self._modifier_is_valid, self._combo_modifiers))

    def _modifier_is_valid(self, mod):
        return self.owns_control_element(mod) and mod.is_pressed()


class EventElement(NotifyingControlElement, SlotManager, ProxyBase, ButtonElementMixin):
    """
    Translate an arbitrary subject event into a notifying control
    element interface.
    """
    event_value = 1
    _subject = None

    def __init__(self, subject = None, event = None, *a, **k):
        raise subject is not None or AssertionError
        raise event is not None or AssertionError
        super(EventElement, self).__init__(*a, **k)
        self._subject = subject
        self.register_slot(subject, self._on_event, event)

    @property
    def proxied_object(self):
        return self._subject

    @property
    def proxied_interface(self):
        return getattr(self._subject, 'proxied_interface', self._subject)

    def _on_event(self, *a, **k):
        self.notify_value(self.event_value)

    def is_momentary(self):
        return False

    def reset(self):
        getattr(self._subject, 'reset', nop)()

    def send_value(self, *a, **k):
        try:
            send_value = super(EventElement, self).__getattr__('send_value')
        except AttributeError:
            send_value = nop

        send_value(*a, **k)

    def set_light(self, *a, **k):
        try:
            set_light = super(EventElement, self).__getattr__('set_light')
        except AttributeError:
            set_light = nop

        set_light(*a, **k)


class DoublePressContext(Subject):
    """
    Determines the context of double press.  Every double press element
    in the same scope can not be interleaved -- i.e. let buttons B1
    and B2, the sequence press(B1), press(B2), press(B1) does not
    trigger a double press event regardless of how fast it happens.
    """
    __events__ = ('break_double_press',)

    @contextmanager
    def breaking_double_press(self):
        self._broke_double_press = False
        yield
        if not self._broke_double_press:
            self.break_double_press()

    def break_double_press(self):
        self.notify_break_double_press()
        self._broke_double_press = True


GLOBAL_DOUBLE_PRESS_CONTEXT_PROVIDER = const(DoublePressContext())

class DoublePressElement(WrapperElement):
    """
    Element wrapper that provides a facade with two events,
    single_press and double_press.
    
    The single_press() and double_press() methods create non-momentary
    button-like controls that represent these events.  Note that these
    controls are individual and have their own ownership, put the
    original DoublePressElement as a hidden element of the layer where
    these are used if ownership is to be taken into account.
    """
    __events__ = ('single_press', 'double_press')
    DOUBLE_PRESS_MAX_DELAY = defaults.MOMENTARY_DELAY

    @depends(double_press_context=GLOBAL_DOUBLE_PRESS_CONTEXT_PROVIDER)
    def __init__(self, wrapped_control = None, double_press_context = None, *a, **k):
        super(DoublePressElement, self).__init__(wrapped_control=wrapped_control, *a, **k)
        self.register_control_element(self._wrapped_control)
        self._double_press_context = double_press_context
        self._double_press_task = self._tasks.add(task.sequence(task.wait(self.DOUBLE_PRESS_MAX_DELAY), task.run(self.finish_single_press))).kill()
        self.request_listen_nested_control_elements()

    def on_nested_control_element_value(self, value, control):
        if not control.is_momentary() or value:
            if self._double_press_task.is_killed:
                self._double_press_context.break_double_press()
                self.__on_break_double_press.subject = self._double_press_context
                self._double_press_task.restart()
            else:
                self.finish_double_press()
                self._double_press_task.kill()
        super(DoublePressElement, self).on_nested_control_element_value(value, control)

    @listens('break_double_press')
    def __on_break_double_press(self):
        if not self._double_press_task.is_killed:
            self._double_press_task.kill()
            self.finish_single_press()

    def finish_single_press(self):
        self.__on_break_double_press.subject = None
        self.notify_single_press()

    def finish_double_press(self):
        self.__on_break_double_press.subject = None
        self.notify_double_press()

    @lazy_attribute
    def single_press(self):
        return EventElement(self, 'single_press')

    @lazy_attribute
    def double_press(self):
        return EventElement(self, 'double_press')


class MultiElement(CompoundElement, ButtonElementMixin):
    """
    Makes several elements behave as single one. Useful when it is
    desired to map several buttons to single one.
    """

    class ProxiedInterface(CompoundElement.ProxiedInterface):

        def __getattr__(self, name):
            found = find_if(lambda x: x is not None, imap(lambda c: getattr(c.proxied_interface, name, None), self.outer.nested_control_elements()))
            if found is not None:
                return found
            raise AttributeError

    def __init__(self, *controls, **k):
        super(MultiElement, self).__init__(**k)
        self.register_control_elements(*map(get_element, controls))

    def send_value(self, value):
        for control in self.owned_control_elements():
            control.send_value(value)

    def set_light(self, value):
        for control in self.owned_control_elements():
            control.set_light(value)

    def on_nested_control_element_value(self, value, control):
        if not self.is_pressed() or value:
            self.notify_value(value)

    def is_pressed(self):
        return find_if(lambda c: getattr(c, 'is_pressed', const(False))(), self.owned_control_elements()) != None

    def is_momentary(self):
        return find_if(lambda c: getattr(c, 'is_momentary', const(False))(), self.nested_control_elements()) != None

    def on_nested_control_element_received(self, control):
        pass

    def on_nested_control_element_lost(self, control):
        pass


class ToggleElement(WrapperElement):
    """
    An Element wrapper that enables one of the nested elements based on
    a toggle state.
    """

    def __init__(self, on_control = None, off_control = None, *a, **k):
        super(ToggleElement, self).__init__(*a, **k)
        self._on_control = get_element(on_control)
        self._off_control = get_element(off_control)
        self._toggled = False
        self._update_toggled()

    def set_toggled(self, value):
        self._toggled = value
        self._update_toggled()

    def _update_toggled(self):
        if self.has_control_element(self._wrapped_control):
            self.unregister_control_element(self._wrapped_control)
        self._wrapped_control = self._on_control if self._toggled else self._off_control
        if self._wrapped_control != None:
            self.register_control_element(self._wrapped_control)