#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_APC/DeviceBankButtonElement.py
from _Framework.ComboElement import ComboElement

class DeviceBankButtonElement(ComboElement):
    """
    ComboElement that will change the channel, while the control is grabbed
    """

    def on_nested_control_element_grabbed(self, control):
        super(DeviceBankButtonElement, self).on_nested_control_element_grabbed(control)
        self.wrapped_control.set_channel(1)

    def on_nested_control_element_released(self, control):
        super(DeviceBankButtonElement, self).on_nested_control_element_released(control)
        self.wrapped_control.set_channel(0)