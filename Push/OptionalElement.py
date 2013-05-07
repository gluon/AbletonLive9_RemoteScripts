#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/OptionalElement.py
from ComboElement import WrapperElement
from _Framework.SubjectSlot import SlotManager, subject_slot

class OptionalElement(WrapperElement, SlotManager):
    """
    An Element wrapper that enables the nested element IFF some given
    setting is set to a specific value.
    """

    def __init__(self, control = None, setting = None, value = None, *a, **k):
        super(OptionalElement, self).__init__(wrapped_control=control, *a, **k)
        self._optional_value = value
        self._control_registered = False
        self._on_setting_changed.subject = setting
        self._on_setting_changed(setting)

    @subject_slot('value')
    def _on_setting_changed(self, setting):
        if self._control_registered:
            if setting.value != self._optional_value:
                self.unregister_control_element(self._wrapped_control)
                self._control_registered = False
        elif setting.value == self._optional_value:
            self.register_control_element(self._wrapped_control)
            self._control_registered = True