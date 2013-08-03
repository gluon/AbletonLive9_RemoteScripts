#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/WithPriority.py
from _Framework.Resource import PrioritizedResource
from ComboElement import WrapperElement

class WithPriority(WrapperElement):

    def __init__(self, wrapped_priority = PrioritizedResource.default_priority, *a, **k):
        super(WithPriority, self).__init__(*a, **k)
        self.wrapped_priority = wrapped_priority
        self.register_control_element(self.wrapped_control)

    def get_control_element_priority(self, element):
        return self.wrapped_priority