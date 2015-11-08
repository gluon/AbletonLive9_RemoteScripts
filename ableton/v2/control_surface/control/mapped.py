#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/ableton/v2/control_surface/control/mapped.py
from __future__ import absolute_import
from .control import InputControl

class MappedControl(InputControl):

    class State(InputControl.State):

        def __init__(self, control = None, manager = None, *a, **k):
            raise control is not None or AssertionError
            raise manager is not None or AssertionError
            super(MappedControl.State, self).__init__(control=control, manager=manager, *a, **k)
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