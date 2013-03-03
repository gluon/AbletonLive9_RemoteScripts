#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/ComboElement.py
from itertools import imap
from _Framework.CompoundElement import CompoundElement
from _Framework.ButtonElement import ButtonElementMixin
from _Framework.InputControlElement import ParameterSlot

class WrapperElement(CompoundElement, ButtonElementMixin):
    """
    Helper class for implementing a wrapper for a specific control,
    forwarding most basic operations to it.
    
    Note that the wrapped control element is not registered to allow
    this flexibly specific implementations.
    """

    def __init__(self, wrapped_control = None, *a, **k):
        super(WrapperElement, self).__init__(*a, **k)
        self._wrapped_control = wrapped_control
        self._parameter_slot = ParameterSlot()

    @property
    def wrapped_control(self):
        return self._wrapped_control

    def __nonzero__(self):
        return self.owns_control_element(self._wrapped_control)

    def is_momentary(self):
        return self._wrapped_control.is_momentary()

    def is_pressed(self):
        return self.owns_control_element(self._wrapped_control) and self._wrapped_control.is_pressed()

    def set_light(self, *a, **k):
        if self.owns_control_element(self._wrapped_control):
            self._wrapped_control.set_light(*a, **k)

    def send_value(self, *a, **k):
        if self.owns_control_element(self._wrapped_control):
            self._wrapped_control.send_value(*a, **k)

    def on_nested_control_element_grabbed(self, control):
        if control == self._wrapped_control:
            self._parameter_slot.control = control

    def on_nested_control_element_released(self, control):
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
    the button values when all the modifiers are pressed, and silently
    discard them when they are not.
    
    When using resources, this element:
      - Grabs the modifiers at all times.
      - Grabs the action button only when all modifiers are pressed.
    
    This means that the action button can be used at the same time in
    the same Layer in a combined and un-combined fashion.  The setters
    of the layer buttons will be called properly so the button gets
    the right light updated when the modifiers are pressed.  For
    example see how the SessionRecording takes the automation_button
    in a combo and raw.
    """

    def __init__(self, modifiers = tuple(), control = None, *a, **k):
        super(ComboElement, self).__init__(wrapped_control=control, *a, **k)
        raise all(imap(lambda x: x.is_momentary(), modifiers)) or AssertionError
        self._combo_modifiers = modifiers
        self.register_control_elements(*modifiers)

    def on_nested_control_element_grabbed(self, control):
        if control != self._wrapped_control:
            self._enforce_control_invariant()
        else:
            super(ComboElement, self).on_nested_control_element_grabbed(control)

    def on_nested_control_element_released(self, control):
        if control != self._wrapped_control:
            self._enforce_control_invariant()
        else:
            super(ComboElement, self).on_nested_control_element_released(control)

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
        return all(imap(self._modifier_is_pressed, self._combo_modifiers))

    def _modifier_is_pressed(self, mod):
        return self.owns_control_element(mod) and mod.is_pressed()