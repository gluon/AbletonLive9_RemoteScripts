#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/mode_behaviours.py
from __future__ import absolute_import, print_function
from itertools import imap
from ableton.v2.control_surface.mode import ModeButtonBehaviour

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
        if len(component.active_modes) == 0 and self._previous_mode is not None:
            component.push_mode(self._previous_mode)


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
        component.get_mode_button(mode).enabled = not self.is_excluded(component, selected_mode)