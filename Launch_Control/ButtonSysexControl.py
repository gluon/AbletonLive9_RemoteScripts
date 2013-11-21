#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Launch_Control/ButtonSysexControl.py
from _Framework.SysexValueControl import SysexValueControl

class ButtonSysexControl(SysexValueControl):
    """
    A SysexValueControl that behaves like a button so it can be used as a mode button of
    the ModesComponent.
    """

    def set_light(self, value):
        pass

    def is_momentary(self):
        return False