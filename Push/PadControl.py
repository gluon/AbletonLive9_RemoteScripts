#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/PadControl.py
from _Framework.Control import PlayableControl

class PadControl(PlayableControl):

    class State(PlayableControl.State):

        def __init__(self, control = None, manager = None, *a, **k):
            super(PadControl.State, self).__init__(control, manager, *a, **k)
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

    def __init__(self, *a, **k):
        super(PadControl, self).__init__(*a, **k)