#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/OptionalElement.py
from ComboElement import WrapperElement
from _Framework.SubjectSlot import SlotManager, subject_slot

class ChoosingElement(WrapperElement, SlotManager):
    """
    An Element wrapper that enables one of the nested elements based on
    the value of the given setting.
    """

    def __init__(self, on_control = None, off_control = None, setting = None, *a, **k):
        super(ChoosingElement, self).__init__(*a, **k)
        self._on_control = on_control
        self._off_control = off_control
        self._on_setting_changed.subject = setting
        self._on_setting_changed(setting)

    @subject_slot('value')
    def _on_setting_changed(self, setting):
        if self.has_control_element(self._wrapped_control):
            self.unregister_control_element(self._wrapped_control)
        self._wrapped_control = self._on_control if setting.value else self._off_control
        if self._wrapped_control != None:
            self.register_control_element(self._wrapped_control)


class OptionalElement(ChoosingElement):
    """
    An Element wrapper that enables the nested element IFF some given
    setting is set to a specific value.
    """

    def __init__(self, control = None, setting = None, value = None, *a, **k):
        on_control = control if value else None
        off_control = None if value else control
        super(OptionalElement, self).__init__(on_control=on_control, off_control=off_control, setting=setting, *a, **k)