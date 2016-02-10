#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/mode.py
"""
Mode handling components.
"""
from __future__ import absolute_import, print_function
from ..base import depends, infinite_context_manager, listens, is_contextmanager, is_iterable, lazy_attribute, listenable_property, NamedTuple, task
from . import defaults
from .layer import Layer, CompoundLayer
from .resource import StackingResource
from .compound_component import CompoundComponent
from .component import Component
from .control import control_color, ButtonControl, ButtonControlBase

def tomode(thing):
    if thing is None:
        return Mode()
    if isinstance(thing, Mode):
        return thing
    if isinstance(thing, Component):
        return ComponentMode(thing)
    if isinstance(thing, tuple) and len(thing) == 2:
        if isinstance(thing[0], Component) and isinstance(thing[1], (Layer, CompoundLayer)):
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
        delay = delay if delay is not None else defaults.MOMENTARY_DELAY
        self._mode = tomode(mode)
        self._mode_entered = False
        self._delay_task = parent_task_group.add(task.sequence(task.wait(delay), task.run(self._enter_mode_delayed)))
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


class ModeButtonControl(ButtonControlBase):
    """
    ButtonControl with special colors for the different mode states
    """

    class State(ButtonControlBase.State):
        mode_selected_color = control_color('DefaultButton.On')
        mode_unselected_color = control_color('DefaultButton.Off')
        mode_group_active_color = control_color('DefaultButton.On')

        def __init__(self, modes_component = None, mode_name = None, mode_selected_color = None, mode_unselected_color = None, mode_group_active_color = None, *a, **k):
            if not modes_component is not None:
                raise AssertionError
                if not mode_name is not None:
                    raise AssertionError
                    self._modes_component = modes_component
                    self._mode_name = mode_name
                    super(ModeButtonControl.State, self).__init__(*a, **k)
                    if mode_selected_color is not None:
                        self.mode_selected_color = mode_selected_color
                    self.mode_unselected_color = mode_unselected_color is not None and mode_unselected_color
                self.mode_group_active_color = mode_group_active_color is not None and mode_group_active_color
            self.__on_selected_mode_changed.subject = self._modes_component

        @property
        def mode_name(self):
            return self._mode_name

        @listens('selected_mode')
        def __on_selected_mode_changed(self, mode):
            self._send_current_color()

        def _send_button_color(self):
            selected_mode = self._modes_component.selected_mode
            groups = self._modes_component.get_mode_groups(self._mode_name)
            selected_groups = self._modes_component.get_mode_groups(selected_mode)
            if selected_mode == self._mode_name:
                self._control_element.set_light(self.mode_selected_color)
            elif bool(groups & selected_groups):
                self._control_element.set_light(self.mode_group_active_color)
            else:
                self._control_element.set_light(self.mode_unselected_color)


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
        pass


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


def make_mode_button_control(modes_component, mode_name, behaviour, **k):
    button_control = ModeButtonControl(modes_component=modes_component, mode_name=mode_name, **k)

    @button_control.pressed
    def button_control(modes_component, button):
        behaviour.press_immediate(modes_component, mode_name)

    @button_control.pressed_delayed
    def button_control(modes_component, button):
        behaviour.press_delayed(modes_component, mode_name)

    @button_control.released_immediately
    def button_control(modes_component, button):
        behaviour.release_immediate(modes_component, mode_name)

    @button_control.released_delayed
    def button_control(modes_component, button):
        behaviour.release_delayed(modes_component, mode_name)

    return button_control


class _ModeEntry(NamedTuple):
    """
    Used by ModesComponent to store information about modes.
    """
    mode = None
    groups = set()
    cycle_mode_button_color = None
    listens = None


class ModesComponent(CompoundComponent):
    """
    A ModesComponent handles the selection of different modes of the
    component. It improves the ModeSelectorComponent in several ways:
    
    - A mode is an object with two methods for entering and exiting
      the mode.  You do not need to know about all the modes
      registered.
    
    - Any object convertible by 'tomode' can be passed as mode.
    
    - Modes are identified by strings.
    
    - The component will dynamically generate controls of the form:
    
          [mode-name]_button = ModeButtonControl()
    
    The modes component behaves like a stack.  Several modes can be
    active at the same time, but the component will make sure that
    only the one at the top (aka 'selected_mode') will be entered at a
    given time.  This allows you to implement modes that can be
    'cancelled' or 'mode latch' (i.e. go to the previous mode under
    certain conditions).
    """
    cycle_mode_button = ButtonControl()
    default_behaviour = LatchingBehaviour()

    def __init__(self, *a, **k):
        super(ModesComponent, self).__init__(*a, **k)
        self._last_toggle_value = 0
        self._mode_toggle = None
        self._mode_list = []
        self._mode_map = {}
        self._last_selected_mode = None
        self._mode_stack = StackingResource(self._do_enter_mode, self._do_leave_mode)

    def disconnect(self):
        self._mode_stack.release_all()
        super(ModesComponent, self).disconnect()

    @listenable_property
    def selected_mode(self):
        """
        Mode that is currently the top of the mode stack. Setting the
        selected mode explictly will also cleanup the mode stack.
        """
        return self._mode_stack.owner or self._last_selected_mode

    @selected_mode.setter
    def selected_mode(self, mode):
        if not (mode in self._mode_map or mode is None):
            raise AssertionError
            if self.is_enabled():
                if self.selected_mode != mode:
                    mode is not None and self.push_mode(mode)
                    self.pop_unselected_modes()
                else:
                    self._mode_stack.release_all()
        else:
            self._last_selected_mode = mode

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

    def add_mode(self, name, mode_or_component, cycle_mode_button_color = None, groups = set(), behaviour = None):
        """
        Adds a mode of the given name into the component.  The mode
        object should be a Mode or Component instance.
        
        If 'group' is not None, the mode will be put in the group
        identified by the passed object.  When several modes are grouped:
        
          * Any of the group buttons will cancel the current mode when
            the current mode belongs to the group.
        """
        if not name not in self._mode_map.keys():
            raise AssertionError
            groups = isinstance(groups, set) or set(groups)
        mode = tomode(mode_or_component)
        behaviour = behaviour if behaviour is not None else self.default_behaviour
        self._mode_list.append(name)
        self._mode_map[name] = _ModeEntry(mode=mode, cycle_mode_button_color=cycle_mode_button_color, behaviour=behaviour, groups=groups)
        self.add_mode_button_control(name, behaviour)

    @property
    def modes(self):
        return self._mode_list

    def get_mode_groups(self, name):
        entry = self._mode_map.get(name, None)
        if entry:
            return entry.groups
        return set()

    def add_mode_button_control(self, mode_name, behaviour):
        button_control = make_mode_button_control(self, mode_name, behaviour)
        self.add_control('%s_button' % mode_name, button_control)
        self._update_mode_buttons(self.selected_mode)

    def _get_mode_behaviour(self, name):
        entry = self._mode_map.get(name, None)
        if entry is not None:
            return entry.behaviour
        return self.default_behaviour

    def get_mode(self, name):
        entry = self._mode_map.get(name, None)
        return entry and entry.mode

    def get_mode_button(self, name):
        return getattr(self, '%s_button' % name)

    def _update_mode_buttons(self, selected):
        if self.is_enabled():
            for name, entry in self._mode_map.iteritems():
                self._get_mode_behaviour(name).update_button(self, name, selected)

    @cycle_mode_button.pressed
    def cycle_mode_button(self, button):
        if len(self._mode_list):
            self.cycle_mode(1)

    @cycle_mode_button.released_delayed
    def cycle_mode_button(self, button):
        if len(self._mode_list) and self.selected_mode != self._mode_list[0]:
            self.cycle_mode(-1)

    def _update_cycle_mode_button(self, selected):
        entry = self._mode_map.get(selected)
        color = entry.cycle_mode_button_color if entry else None
        if color is not None:
            self.cycle_mode_button.color = color

    def cycle_mode(self, delta = 1):
        current_index = self._mode_list.index(self.selected_mode) if self.selected_mode else -delta
        current_index = (current_index + delta) % len(self._mode_list)
        self.selected_mode = self._mode_list[current_index]

    def _do_enter_mode(self, name):
        entry = self._mode_map[name]
        entry.mode.enter_mode()
        self._update_mode_buttons(name)
        self._update_cycle_mode_button(name)
        self.notify_selected_mode(name)

    def _do_leave_mode(self, name):
        self._mode_map[name].mode.leave_mode()
        if self._mode_stack.stack_size == 0:
            self._update_mode_buttons(None)
            self._update_cycle_mode_button(None)
            self.notify_selected_mode(None)

    def on_enabled_changed(self):
        super(ModesComponent, self).on_enabled_changed()
        if not self.is_enabled():
            self._last_selected_mode = self.selected_mode
            self._mode_stack.release_all()
        elif self._last_selected_mode:
            self.push_mode(self._last_selected_mode)


class EnablingModesComponent(ModesComponent):
    """
    Adds the two modes 'enabled' and 'disabled'. The provided component will be
    enabled while the 'enabled' mode is active.
    """

    def __init__(self, component = None, enabled_color = 'DefaultButton.On', disabled_color = 'DefaultButton.Off', *a, **k):
        super(EnablingModesComponent, self).__init__(*a, **k)
        component.set_enabled(False)
        self.add_mode('disabled', None, disabled_color)
        self.add_mode('enabled', component, enabled_color)
        self.selected_mode = 'disabled'