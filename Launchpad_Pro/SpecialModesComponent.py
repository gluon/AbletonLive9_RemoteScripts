#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/SpecialModesComponent.py
from _Framework.ModesComponent import ReenterBehaviour, ModesComponent

class SpecialModesComponent(ModesComponent):

    def on_enabled_changed(self):
        super(SpecialModesComponent, self).on_enabled_changed()
        if not self.is_enabled():
            self._last_selected_mode = None


class SpecialReenterBehaviour(ReenterBehaviour):
    """
    When a mode with this behaviour is reentered, enters on_reenter_mode instead
    """

    def __init__(self, mode_name = None, *a, **k):
        super(ReenterBehaviour, self).__init__(*a, **k)
        self._mode_name = mode_name

    def press_immediate(self, component, mode):
        was_active = component.selected_mode == mode
        super(ReenterBehaviour, self).press_immediate(component, mode)
        if was_active:
            if self._mode_name is not None and component.get_mode(self._mode_name):
                component.push_mode(self._mode_name)
                component.pop_unselected_modes()


class CancelingReenterBehaviour(SpecialReenterBehaviour):

    def __init__(self, *a, **k):
        super(CancelingReenterBehaviour, self).__init__(*a, **k)
        self._reenter_mode_active = False

    def press_immediate(self, component, mode):
        was_active = component.selected_mode == mode
        super(CancelingReenterBehaviour, self).press_immediate(component, mode)
        if was_active:
            self._reenter_mode_active = True

    def release_immediate(self, component, mode):
        super(CancelingReenterBehaviour, self).release_immediate(component, mode)
        self._return(component, mode)

    def release_delayed(self, component, mode):
        super(CancelingReenterBehaviour, self).release_delayed(component, mode)
        self._return(component, mode)

    def _return(self, component, mode):
        if self._reenter_mode_active:
            component.push_mode(mode)
            component.pop_unselected_modes()
            self._reenter_mode_active = False