#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_static/midi-remote-scripts/_Framework/SwitchModeSelectorComponent.py
from ModeSelectorComponent import ModeSelectorComponent
from ControlSurfaceComponent import ControlSurfaceComponent
from ButtonElement import ButtonElement

class SwitchModeSelectorComponent(ModeSelectorComponent):
    """ Class that handles modes by enabling and disabling components """

    def __init__(self):
        ModeSelectorComponent.__init__(self)
        self._components_per_mode = []

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._components_per_mode = None

    def add_mode(self, components, button):
        if not components != None:
            raise AssertionError
            if not isinstance(components, tuple):
                raise AssertionError
                raise button == None or isinstance(button, ButtonElement) or AssertionError
                self._mode_index = len(self._modes_buttons) == 0 and 0
            for component in components:
                raise isinstance(component, ControlSurfaceComponent) or AssertionError

            identify_sender = button != None and True
            button.add_value_listener(self._mode_value, identify_sender)
            self._modes_buttons.append(button)
        self._components_per_mode.append(components)
        self.update()

    def number_of_modes(self):
        return len(self._components_per_mode)

    def update(self):
        super(SwitchModeSelectorComponent, self).update()
        raise len(self._modes_buttons) == 0 or len(self._modes_buttons) == len(self._components_per_mode) or AssertionError
        if not len(self._components_per_mode) > self._mode_index:
            raise AssertionError
            index = 0
            active_components = None
            if self.is_enabled():
                active_components = self._components_per_mode[self._mode_index]
            for index in range(len(self._components_per_mode)):
                if self._components_per_mode[index] != active_components:
                    if len(self._modes_buttons) == len(self._components_per_mode):
                        self._modes_buttons[index].turn_off()
                    for component in self._components_per_mode[index]:
                        component.set_enabled(False)

            if active_components != None:
                for component in active_components:
                    component.set_enabled(True)

                len(self._modes_buttons) == len(self._components_per_mode) and self._modes_buttons[self._mode_index].turn_on()