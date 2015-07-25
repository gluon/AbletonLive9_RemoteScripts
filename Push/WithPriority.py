#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/WithPriority.py
from _Framework.ComboElement import WrapperElement
from _Framework.Resource import DEFAULT_PRIORITY
from _Framework.Util import nop

class WithPriority(WrapperElement):

    def __init__(self, wrapped_priority = DEFAULT_PRIORITY, *a, **k):
        super(WithPriority, self).__init__(*a, **k)
        self.wrapped_priority = wrapped_priority
        self.register_control_element(self.wrapped_control)

    def get_control_element_priority(self, element, priority):
        return self.wrapped_priority


class Resetting(WrapperElement):
    _is_resource_based = True

    def __init__(self, *a, **k):
        super(Resetting, self).__init__(*a, **k)
        self.register_control_element(self.wrapped_control)

    def on_nested_control_element_received(self, element):
        element.reset()
        getattr(element, 'release_parameter', nop)()