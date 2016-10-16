#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/CompoundComponent.py
from __future__ import absolute_import
from .ControlSurfaceComponent import ControlSurfaceComponent

class CompoundComponent(ControlSurfaceComponent):
    """ Base class for classes encompasing other components to form complex components """

    def __init__(self, *a, **k):
        super(CompoundComponent, self).__init__(*a, **k)
        self._sub_components = []

    def update_all(self):
        self.update()
        for component in self._sub_components:
            component.update_all()

    def register_component(self, component):
        raise component != None or AssertionError
        raise component not in self._sub_components or AssertionError
        component._set_enabled_recursive(self.is_enabled())
        self._sub_components.append(component)
        return component

    def register_components(self, *a):
        return map(self.register_component, a)

    def has_component(self, component):
        return component in self._sub_components

    def set_enabled(self, enable):
        """
        When disabling a compound component, its children are disabled. When
        enabled, these children are restored to whatever state they were
        explicitly set to.
        """
        super(CompoundComponent, self).set_enabled(enable)
        for component in self._sub_components:
            component._set_enabled_recursive(self.is_enabled())

    def _set_enabled_recursive(self, enable):
        super(CompoundComponent, self)._set_enabled_recursive(enable)
        for component in self._sub_components:
            component._set_enabled_recursive(self.is_enabled())

    def set_allow_update(self, allow_updates):
        allow = bool(allow_updates)
        if self._allow_updates != allow:
            for component in self._sub_components:
                component.set_allow_update(allow)

            super(CompoundComponent, self).set_allow_update(allow)