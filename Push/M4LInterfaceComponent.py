#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/M4LInterfaceComponent.py
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
import consts

class M4LInterfaceComponent(ControlSurfaceComponent):
    """
    Simplified API for interaction from M4L as a high priority layer
    superposed on top of any L9C functionality.
    """

    def __init__(self, controls, *a, **k):
        super(M4LInterfaceComponent, self).__init__(self, *a, **k)
        self._controls = dict(map(lambda x: (x.name, x), controls))
        self._grabbed_controls = []

    def disconnect(self):
        for control in self._grabbed_controls[:]:
            self.release_control(control)

        super(M4LInterfaceComponent, self).disconnect()

    def set_control_element(self, control, grabbed):
        if hasattr(control, 'release_parameter'):
            control.release_parameter()
        control.reset()

    def get_control_names(self):
        return self._controls.keys()

    def get_control(self, control_name):
        return self._controls[control_name] if control_name in self._controls else None

    def grab_control(self, control):
        if not control in self._controls.values():
            raise AssertionError
            control not in self._grabbed_controls and control.resource.grab(self, priority=consts.M4L_PRIORITY)
            self._grabbed_controls.append(control)

    def release_control(self, control):
        if not control in self._controls.values():
            raise AssertionError
            control in self._grabbed_controls and self._grabbed_controls.remove(control)
            control.resource.release(self)

    def update(self):
        pass