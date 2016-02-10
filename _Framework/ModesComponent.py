#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/ModesComponent.py
"""
Mode handling components.
"""
from __future__ import absolute_import
from functools import partial
from itertools import imap
from . import Defaults
from . import Task
from .CompoundComponent import CompoundComponent
from .ControlSurfaceComponent import ControlSurfaceComponent
from .Dependency import depends
from .Layer import LayerBase
from .Resource import StackingResource
from .SubjectSlot import subject_slot
from .Util import is_iterable, is_contextmanager, lazy_attribute, infinite_context_manager, NamedTuple

def tomode(thing):
    if thing == None:
        return Mode()
    if isinstance(thing, Mode):
        return thing
    if isinstance(thing, ControlSurfaceComponent):
        return ComponentMode(thing)
    if isinstance(thing, tuple) and len(thing) == 2:
        if isinstance(thing[0], ControlSurfaceComponent) and isinstance(thing[1], LayerBase):
            return LayerMode(*thing)
        if callable(thing[0]) and callable(thing[1]):
            mode = Mode()
            mode.enter_mode, mode.leave_mode = thing
            return mode
    if callable(thing):
        mode = Mode()
        mode.enter_mode = thing
        return mode
    if is_iterable(thing):
        return CompoundMode(*thing)
    if is_contextmanager(thing):
        return ContextManagerMode(thing)
    return thing


class Mode(object):
    """
    Interface to be implemented by modes.  When a mode is enabled,
    enter_mode is called, and leave_mode when disabled.
    """

    def enter_mode(self):
        pass

    def leave_mode(self):
        pass

    def __enter__(self):
        self.enter_mode()

    def __exit__(self, *a):
        return self.leave_mode()


class ContextManagerMode(Mode):
    """
    Turns any context manager into a mode object.
    """

    def __init__(self, context_manager = None, *a, **k):
        super(ContextManagerMode, self).__init__(*a, **k)
        self._context_manager = context_manager

    def enter_mode(self):
        self._context_manager.__enter__()

    def leave_mode(self):
        self._context_manager.__exit__(None, None, None)

    def __exit__(self, exc_type, exc_value, traceback):
        return self._context_manager.__exit__(exc_type, exc_value, traceback)


def generator_mode(function):
    makecontext = infinite_context_manager(function)
    return lambda *a, **k: ContextManagerMode(makecontext(*a, **k))


class ComponentMode(Mode):
    """
    Enables a component while the mode is active.
    """

    def __init__(self, component = None, *a, **k):
        super(ComponentMode, self).__init__(*a, **k)
        raise component is not None or AssertionError
        self._component = component

    def enter_mode(self):
        self._component.set_enabled(True)

    def leave_mode(self):
        self._component.set_enabled(False)


class LazyComponentMode(Mode):
    """
    Creates the component the first time the mode is entered and
    enables it while the mode is active.
    """

    def __init__(self, component_creator = None, *a, **k):
        super(LazyComponentMode, self).__init__(*a, **k)
        self._component_creator = component_creator

    @lazy_attribute
    def component(self):
        return self._component_creator()

    def enter_mode(self):
        self.component.set_enabled(True)

    def leave_mode(self):
        self.component.set_enabled(False)


class DisableMode(Mode):
    """
    Disables a component while the mode is active.
    """

    def __init__(self, component = None, *a, **k):
        super(DisableMode, self).__init__(*a, **k)
        raise component is not None or AssertionError
        self._component = component

    def enter_mode(self):
        self._component.set_enabled(False)

    def leave_mode(self):
        self._component.set_enabled(True)


class LayerModeBase(Mode):

    def __init__(self, component = None, layer = None, *a, **k):
        super(LayerModeBase, self).__init__(*a, **k)
        raise component is not None or AssertionError
        self._component = component
        self._layer = layer

    def _get_component(self):
        if callable(self._component):
            return self._component()
        return self._component


class LayerMode(LayerModeBase):
    """
    Sets the layer of a component to a specific one.  When the mode is
    exited leaves the component without a layer.
    """

    def enter_mode(self):
        self._get_component().layer = self._layer

    def leave_mode(self):
        self._get_component().layer = None


class AddLayerMode(LayerModeBase):
    """
    Adds an extra layer to a component, independently of the layer
    associated to the component.
    """

    def enter_mode(self):
        self._layer.grab(self._get_component())

    def leave_mode(self):
        self._layer.release(self._get_component())


class CompoundMode(Mode):
    """
    A compound mode wraps any number of modes into one. They are
    entered in the given order and left in reversed order.
    """

    def __init__(self, *modes, **k):
        super(CompoundMode, self).__init__(**k)
        self._modes = map(tomode, modes)

    def enter_mode(self):
        for mode in self._modes:
            mode.enter_mode()

    def leave_mode(self):
        for mode in reversed(self._modes):
            mode.leave_mode()


class MultiEntryMode(Mode):
    """
    Mode wrapper that allows registration in multiple modes
    components.  This wrapper can be entered multiple times and the
    enter method will be called only once.  It will be left when the
    number of times leave_mode is called matches the number of calls
    to enter_mode.
    """

    def __init__(self, mode = None, *a, **k):
        super(MultiEntryMode, self).__init__(*a, **k)
        self._mode = tomode(mode)
        self._entry_count = 0

    def enter_mode(self):
        if self._entry_count == 0:
            self._mode.enter_mode()
        self._entry_count += 1

    def leave_mode(self):
        if not self._entry_count > 0:
            raise AssertionError
            self._entry_count == 1 and self._mode.leave_mode()
        self._entry_count -= 1

    @property
    def is_entered(self):
        return self._entry_count > 0


class SetAttributeMode(Mode):
    """
    Changes an attribute of an object to a given value.  Restores it
    to the original value, unless the value has changed while the mode
    was active.
    """

    def __init__(self, obj = None, attribute = None, value = None, *a, **k):
        super(SetAttributeMode, self).__init__(*a, **k)
        self._obj = obj
        self._attribute = attribute
        self._old_value = None
        self._value = value

    def _get_object(self):
        if callable(self._obj):
            return self._obj()
        return self._obj

    def enter_mode(self):
        self._old_value = getattr(self._get_object(), self._attribute, None)
        setattr(self._get_object(), self._attribute, self._value)

    def leave_mode(self):
        if getattr(self._get_object(), self._attribute) == self._value:
            setattr(self._get_object(), self._attribute, self._old_value)


class DelayMode(Mode):
    """
    Decorates a mode by delaying it.
    """

    @depends(parent_task_group=None)
    def __init__(self, mode = None, delay = None, parent_task_group = None, *a, **k):
        super(DelayMode, self).__init__(*a, **k)
        raise mode is not None or AssertionError
        raise parent_task_group is not None or AssertionError
        delay = delay if delay is not None else Defaults.MOMENTARY_DELAY
        self._mode = tomode(mode)
        self._mode_entered = False
        self._delay_task = parent_task_group.add(Task.sequence(Task.wait(delay), Task.run(self._enter_mode_delayed)))
        self._delay_task.kill()

    def _enter_mode_delayed(self):
        self._mode_entered = True
        self._mode.enter_mode()

    def enter_mode(self):
        self._delay_task.restart()

    def leave_mode(self):
        if self._mode_entered:
            self._mode.leave_mode()
            self._mode_entered = False
        self._delay_task.kill()


class ModeButtonBehaviour(object):
    """
    Strategy that determines how the mode button of a specific mode
    behaves. The protocol is a follows:
    
    1. When the button is pressed, the press_immediate is called.
    
    2. If the button is released shortly, the release_immediate is
       called.
    
    3. However, if MOMENTARY_DELAY is elapsed before release,
       press_delayed is called and release_immediate will never be
       called.
    
    4. release_delayed will be called when the button is released and
       more than MOMENTARY_DELAY time has passed since press.
    """

    def press_immediate(self, component, mode):
        pass

    def release_immediate(self, component, mode):
        pass

    def press_delayed(self, component, mode):
        pass

    def release_delayed(self, component, mode):
        pass

    def update_button(self, component, mode, selected_mode):
        """
        Updates the button light for 'mode'.
        """
        button = component.get_mode_button(mode)
        groups = component.get_mode_groups(mode)
        selected_groups = component.get_mode_groups(selected_mode)
        button.set_light(mode == selected_mode or bool(groups & selected_groups))


class LatchingBehaviour(ModeButtonBehaviour):
    """
    Behaviour that will jump back to the previous mode when the button
    is released after having been hold for some time.  If the button
    is quickly pressed, the selected mode will stay.
    """

    def press_immediate(self, component, mode):
        component.push_mode(mode)

    def release_immediate(self, component, mode):
        component.pop_unselected_modes()

    def release_delayed(self, component, mode):
        if len(component.active_modes) > 1:
            component.pop_mode(mode)


class ReenterBehaviour(LatchingBehaviour):
    """
    Like latching, but calls a callback when the mode is-reentered.
    """

    def __init__(self, on_reenter = None, *a, **k):
        super(ReenterBehaviour, self).__init__(*a, **k)
        if on_reenter is not None:
            self.on_reenter = on_reenter

    def press_immediate(self, component, mode):
        was_active = component.selected_mode == mode
        super(ReenterBehaviour, self).press_immediate(component, mode)
        if was_active:
            self.on_reenter()

    def on_reenter(self):
        pass


class CancellableBehaviour(ModeButtonBehaviour):
    """
    Acts a toggle for the mode -- when the button is pressed a second
    time, every mode in this mode group will be exited, going back to
    the last selected mode.  It also does mode latching.
    """
    _previous_mode = None

    def press_immediate(self, component, mode):
        active_modes = component.active_modes
        groups = component.get_mode_groups(mode)
        can_cancel_mode = mode in active_modes or any(imap(lambda other: groups & component.get_mode_groups(other), active_modes))
        if can_cancel_mode:
            if groups:
                component.pop_groups(groups)
            else:
                component.pop_mode(mode)
            self.restore_previous_mode(component)
        else:
            self.remember_previous_mode(component)
            component.push_mode(mode)

    def remember_previous_mode(self, component):
        self._previous_mode = component.active_modes[0] if component.active_modes else None

    def restore_previous_mode(self, component):
        if len(component.active_modes) == 0 and self._previous_mode != None:
            component.push_mode(self._previous_mode)


class ImmediateBehaviour(ModeButtonBehaviour):
    """
    Just goes to the pressed mode immediatley.
    No latching or magic.
    """

    def press_immediate(self, component, mode):
        component.selected_mode = mode


class AlternativeBehaviour(CancellableBehaviour):
    """
    Relies in the alternative to be in the same group for cancellation
    to work properly. Also shows cancellable behaviour and the
    alternative is latched.
    """

    def __init__(self, alternative_mode = None, *a, **k):
        super(AlternativeBehaviour, self).__init__(*a, **k)
        self._alternative_mode = alternative_mode

    def _check_mode_groups(self, component, mode):
        mode_groups = component.get_mode_groups(mode)
        alt_group = component.get_mode_groups(self._alternative_mode)
        return mode_groups and mode_groups & alt_group

    def release_delayed(self, component, mode):
        raise self._check_mode_groups(component, mode) or AssertionError
        component.pop_groups(component.get_mode_groups(mode))
        self.restore_previous_mode(component)

    def press_delayed(self, component, mode):
        raise self._check_mode_groups(component, mode) or AssertionError
        self.remember_previous_mode(component)
        component.push_mode(self._alternative_mode)

    def release_immediate(self, component, mode):
        raise self._check_mode_groups(component, mode) or AssertionError
        super(AlternativeBehaviour, self).press_immediate(component, mode)

    def press_immediate(self, component, mode):
        raise self._check_mode_groups(component, mode) or AssertionError


class DynamicBehaviourMixin(ModeButtonBehaviour):
    """
    Chooses the mode to uses dynamically when the button is pressed.
    If no mode is returned, the default one is used instead.
    
    It can be safely used as a mixin in front of every other behviour.
    """

    def __init__(self, mode_chooser = None, *a, **k):
        super(DynamicBehaviourMixin, self).__init__(*a, **k)
        self._mode_chooser = mode_chooser
        self._chosen_mode = None

    def press_immediate(self, component, mode):
        self._chosen_mode = self._mode_chooser() or mode
        super(DynamicBehaviourMixin, self).press_immediate(component, self._chosen_mode)

    def release_delayed(self, component, mode):
        super(DynamicBehaviourMixin, self).release_delayed(component, self._chosen_mode)

    def press_delayed(self, component, mode):
        super(DynamicBehaviourMixin, self).press_delayed(component, self._chosen_mode)

    def release_immediate(self, component, mode):
        super(DynamicBehaviourMixin, self).release_immediate(component, self._chosen_mode)


class ExcludingBehaviourMixin(ModeButtonBehaviour):
    """
    Button behaviour that excludes the mode/s when the currently
    selected mode is in any of the excluded groups.
    """

    def __init__(self, excluded_groups = set(), *a, **k):
        super(ExcludingBehaviourMixin, self).__init__(*a, **k)
        self._excluded_groups = set(excluded_groups)

    def is_excluded(self, component, selected):
        return bool(component.get_mode_groups(selected) & self._excluded_groups)

    def press_immediate(self, component, mode):
        if not self.is_excluded(component, component.selected_mode):
            super(ExcludingBehaviourMixin, self).press_immediate(component, mode)

    def release_delayed(self, component, mode):
        if not self.is_excluded(component, component.selected_mode):
            super(ExcludingBehaviourMixin, self).release_delayed(component, mode)

    def press_delayed(self, component, mode):
        if not self.is_excluded(component, component.selected_mode):
            super(ExcludingBehaviourMixin, self).press_delayed(component, mode)

    def release_immediate(self, component, mode):
        if not self.is_excluded(component, component.selected_mode):
            super(ExcludingBehaviourMixin, self).release_immediate(component, mode)

    def update_button(self, component, mode, selected_mode):
        if not self.is_excluded(component, selected_mode):
            super(ExcludingBehaviourMixin, self).update_button(component, mode, selected_mode)
        else:
            component.get_mode_button(mode).set_light('DefaultButton.Disabled')


class _ModeEntry(NamedTuple):
    """
    Used by ModesComponent to store information about modes.
    """
    mode = None
    groups = set()
    toggle_value = False
    subject_slot = None
    momentary_task = None


class ModesComponent(CompoundComponent):
    """
    A ModesComponent handles the selection of different modes of the
    component. It improves the ModeSelectorComponent in several ways:
    
    - A mode is an object with two methods for entering and exiting
      the mode.  You do not need to know about all the modes
      registered.
    
    - Any object convertible by 'tomode' can be passed as mode.
    
    - Modes are identified by strings.
    
    - The component will dynamically generate methods of the form:
    
          set_[mode-name]_button(button)
    
      for setting the mode button.  Thanks to this, you can pass the mode
      buttons in a layer.
    
    The modes component behaves like a stack.  Several modes can be
    active at the same time, but the component will make sure that
    only the one at the top (aka 'selected_mode') will be entered at a
    given time.  This allows you to implement modes that can be
    'cancelled' or 'mode latch' (i.e. go to the previous mode under
    certain conditions).
    """
    __subject_events__ = ('selected_mode',)
    momentary_toggle = False
    default_behaviour = LatchingBehaviour()

    def __init__(self, *a, **k):
        super(ModesComponent, self).__init__(*a, **k)
        self._last_toggle_value = 0
        self._mode_toggle = None
        self._mode_toggle_task = self._tasks.add(Task.wait(Defaults.MOMENTARY_DELAY))
        self._mode_toggle_task.kill()
        self._mode_list = []
        self._mode_map = {}
        self._last_selected_mode = None
        self._mode_stack = StackingResource(self._do_enter_mode, self._do_leave_mode)
        self._shift_button = None

    def disconnect(self):
        self._mode_stack.release_all()
        super(ModesComponent, self).disconnect()

    def set_shift_button(self, button):
        raise not button or button.is_momentary() or AssertionError
        self._shift_button = button

    def _do_enter_mode(self, name):
        entry = self._mode_map[name]
        entry.mode.enter_mode()
        self._update_buttons(name)
        self.notify_selected_mode(name)

    def _do_leave_mode(self, name):
        self._mode_map[name].mode.leave_mode()
        if self._mode_stack.stack_size == 0:
            self._update_buttons(None)
            self.notify_selected_mode(None)

    def _get_selected_mode(self):
        """
        Mode that is currently the top of the mode stack. Setting the
        selected mode explictly will also cleanup the mode stack.
        """
        return self._mode_stack.owner or self._last_selected_mode

    def _set_selected_mode(self, mode):
        if not (mode in self._mode_map or mode is None):
            raise AssertionError
            if self.is_enabled():
                mode != None and self.push_mode(mode)
                self.pop_unselected_modes()
            else:
                self._mode_stack.release_all()
        else:
            self._last_selected_mode = mode

    selected_mode = property(_get_selected_mode, _set_selected_mode)

    @property
    def selected_groups(self):
        entry = self._mode_map.get(self.selected_mode, None)
        if entry:
            return entry.groups
        return set()

    @property
    def active_modes(self):
        return self._mode_stack.clients

    def push_mode(self, mode):
        """
        Selects the current 'mode', leaving the rest of the modes in
        the mode stack.
        """
        self._mode_stack.grab(mode)

    def pop_mode(self, mode):
        """
        Takes 'mode' away from the mode stack.  If the mode was the
        currently selected one, the last pushed mode will be selected.
        """
        self._mode_stack.release(mode)

    def pop_groups(self, groups):
        """
        Pops every mode in groups.
        """
        if not isinstance(groups, set):
            groups = set(groups)
        for client in self._mode_stack.clients:
            if self.get_mode_groups(client) & groups:
                self._mode_stack.release(client)

    def pop_unselected_modes(self):
        """
        Pops from the mode stack all the modes that are not the
        currently selected one.
        """
        self._mode_stack.release_stacked()

    def on_enabled_changed(self):
        super(ModesComponent, self).on_enabled_changed()
        if not self.is_enabled():
            self._last_selected_mode = self.selected_mode
            self._mode_stack.release_all()
        elif self._last_selected_mode:
            self.push_mode(self._last_selected_mode)

    def update(self):
        super(ModesComponent, self).update()
        self._update_buttons(self.selected_mode)

    def add_mode(self, name, mode_or_component, toggle_value = False, groups = set(), behaviour = None):
        """
        Adds a mode of the given name into the component.  The mode
        object should be a Mode or ControlSurfaceComponent instance.
        
        The 'toggle_value' is the light value the toggle_botton will
        be set to when the component is on this mode.
        
        If 'group' is not None, the mode will be put in the group
        identified by the passed object.  When several modes are grouped:
        
          * All the buttons in the group will light up when any of the
            modes withing the group is selected.
        
          * Any of the group buttons will cancel the current mode when
            the current mode belongs to the group.
        """
        if not name not in self._mode_map.keys():
            raise AssertionError
            if not isinstance(groups, set):
                groups = set(groups)
            mode = tomode(mode_or_component)
            task = self._tasks.add(Task.sequence(Task.wait(Defaults.MOMENTARY_DELAY), Task.run(lambda : self._get_mode_behaviour(name).press_delayed(self, name))))
            task.kill()
            slot = self.register_slot(listener=partial(self._on_mode_button_value, name), event='value', extra_kws=dict(identify_sender=True))
            self._mode_list.append(name)
            self._mode_map[name] = _ModeEntry(mode=mode, toggle_value=toggle_value, behaviour=behaviour, subject_slot=slot, momentary_task=task, groups=groups)
            button_setter = 'set_' + name + '_button'
            hasattr(self, button_setter) or setattr(self, button_setter, partial(self.set_mode_button, name))

    def _get_mode_behaviour(self, name):
        entry = self._mode_map.get(name, None)
        return entry and entry.behaviour or self.default_behaviour

    def get_mode(self, name):
        entry = self._mode_map.get(name, None)
        return entry and entry.mode

    def get_mode_groups(self, name):
        entry = self._mode_map.get(name, None)
        if entry:
            return entry.groups
        return set()

    def set_toggle_button(self, button):
        if button and self.is_enabled():
            button.reset()
        self._mode_toggle = button
        self._on_toggle_value.subject = button
        self._update_buttons(self.selected_mode)

    def set_mode_button(self, name, button):
        if button and self.is_enabled():
            button.reset()
        self._mode_map[name].subject_slot.subject = button
        self._update_buttons(self.selected_mode)

    def get_mode_button(self, name):
        return self._mode_map[name].subject_slot.subject

    def _update_buttons(self, selected):
        if self.is_enabled():
            for name, entry in self._mode_map.iteritems():
                if entry.subject_slot.subject != None:
                    self._get_mode_behaviour(name).update_button(self, name, selected)

            if self._mode_toggle:
                entry = self._mode_map.get(selected)
                value = entry and entry.toggle_value
                self._mode_toggle.set_light(value)

    def _on_mode_button_value(self, name, value, sender):
        shift = self._shift_button and self._shift_button.is_pressed()
        if not shift and self.is_enabled():
            behaviour = self._get_mode_behaviour(name)
            if sender.is_momentary():
                entry = self._mode_map[name]
                task = entry.momentary_task
                if value:
                    behaviour.press_immediate(self, name)
                    task.restart()
                elif task.is_killed:
                    behaviour.release_delayed(self, name)
                else:
                    behaviour.release_immediate(self, name)
                    task.kill()
            else:
                behaviour.press_immediate(self, name)
                behaviour.release_immediate(self, name)

    @subject_slot('value')
    def _on_toggle_value(self, value):
        shift = self._shift_button and self._shift_button.is_pressed()
        if not shift and self.is_enabled() and len(self._mode_list):
            is_press = value and not self._last_toggle_value
            is_release = not value and self._last_toggle_value
            can_latch = self._mode_toggle_task.is_killed and self.selected_mode != self._mode_list[0]
            if not self._mode_toggle.is_momentary() or is_press:
                self.cycle_mode(1)
                self._mode_toggle_task.restart()
            elif is_release and (self.momentary_toggle or can_latch):
                self.cycle_mode(-1)
            self._last_toggle_value = value

    def cycle_mode(self, delta = 1):
        current_index = self._mode_list.index(self.selected_mode) if self.selected_mode else -delta
        current_index = (current_index + delta) % len(self._mode_list)
        self.selected_mode = self._mode_list[current_index]


class DisplayingModesComponent(ModesComponent):
    """
    A modes component that displays the selected option.
    """

    def __init__(self, *a, **k):
        super(DisplayingModesComponent, self).__init__(*a, **k)
        self._mode_data_sources = {}

    def add_mode(self, name, mode_or_component, data_source):
        """
        Adds a mode.  The mode will be displayed in the given data
        source. The display name of the data source is its value when
        added.
        """
        super(DisplayingModesComponent, self).add_mode(name, mode_or_component)
        self._mode_data_sources[name] = (data_source, data_source.display_string())

    def update(self):
        super(DisplayingModesComponent, self).update()
        self._update_data_sources(self.selected_mode)

    def _do_enter_mode(self, name):
        super(DisplayingModesComponent, self)._do_enter_mode(name)
        self._update_data_sources(name)

    def _update_data_sources(self, selected):
        if self.is_enabled():
            for name, (source, string) in self._mode_data_sources.iteritems():
                source.set_display_string('*' + string if name == selected else string)


class EnablingModesComponent(ModesComponent):
    """
    Adds the two modes 'enabled' and 'disabled'. The provided component will be
    enabled while the 'enabled' mode is active.
    """

    def __init__(self, component = None, toggle_value = False, disabled_value = False, *a, **k):
        super(EnablingModesComponent, self).__init__(*a, **k)
        component.set_enabled(False)
        self.add_mode('disabled', None, disabled_value)
        self.add_mode('enabled', component, toggle_value)
        self.selected_mode = 'disabled'