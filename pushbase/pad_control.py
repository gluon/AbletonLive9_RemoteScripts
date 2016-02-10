#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/pad_control.py
from __future__ import absolute_import, print_function
from ableton.v2.control_surface.control import PlayableControl

class PadControl(PlayableControl):

    class State(PlayableControl.State):

        def __init__(self, *a, **k):
            super(PadControl.State, self).__init__(*a, **k)
            self._sensitivity_profile = None

        def _get_sensitivity_profile(self):
            return self._sensitivity_profile

        def _set_sensitivity_profile(self, value):
            self._sensitivity_profile = value
            self._update_sensitivity()

        sensitivity_profile = property(_get_sensitivity_profile, _set_sensitivity_profile)

        def set_control_element(self, control_element):
            super(PadControl.State, self).set_control_element(control_element)
            self._update_sensitivity()

        def _update_sensitivity(self):
            if self._control_element and self._sensitivity_profile:
                self._control_element.sensitivity_profile = self._sensitivity_profile