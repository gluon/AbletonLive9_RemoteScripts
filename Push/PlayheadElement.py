#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/PlayheadElement.py
from _Framework.ControlElement import ControlElement
from _Framework.Proxy import Proxy

class NullPlayhead(object):
    notes = []
    start_time = 0.0
    step_length = 1.0
    clip_start_time = 0.0
    clip_start_marker = 0.0
    clip_loop = (0.0, 0.0)
    velocity = 0.0
    enabled = False
    wrap_around = False


class ProxyElement(Proxy, ControlElement):

    def reset(self):
        try:
            super(ProxyElement, self).__getattr__('reset')()
        except AttributeError:
            pass


class PlayheadElement(ProxyElement):

    def __init__(self, playhead = None, *a, **k):
        super(PlayheadElement, self).__init__(proxied_object=playhead, proxied_interface=NullPlayhead())

    def reset(self):
        self.enabled = False