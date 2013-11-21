#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/NotifyingControlElement.py
from SubjectSlot import Subject, SubjectEvent
from ControlElement import ControlElement

class NotifyingControlElement(Subject, ControlElement):
    """
    Class representing control elements that can send values
    """
    __subject_events__ = (SubjectEvent(name='value', doc=' Called when the control element receives a MIDI value\n                             from the hardware '),)