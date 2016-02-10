#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/OptionalElement.py
from __future__ import absolute_import
from .ComboElement import ToggleElement
from .SubjectSlot import SlotManager, subject_slot

class ChoosingElement(ToggleElement, SlotManager):
    """
    An Element wrapper that enables one of the nested elements based on
    the value of the given flag.
    """

    def __init__(self, flag = None, *a, **k):
        super(ChoosingElement, self).__init__(*a, **k)
        self._on_flag_changed.subject = flag
        self._on_flag_changed(flag.value)

    @subject_slot('value')
    def _on_flag_changed(self, value):
        self.set_toggled(value)


class OptionalElement(ChoosingElement):
    """
    An Element wrapper that enables the nested element IFF some given
    flag is set to a specific value.
    """

    def __init__(self, control = None, flag = None, value = None, *a, **k):
        on_control = control if value else None
        off_control = None if value else control
        super(OptionalElement, self).__init__(on_control=on_control, off_control=off_control, flag=flag, *a, **k)