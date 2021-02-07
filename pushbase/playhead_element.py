# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/playhead_element.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base import nop
from .proxy_element import ProxyElement

class NullPlayhead(object):
    notes = []
    start_time = 0.0
    step_length = 1.0
    velocity = 0.0
    wrap_around = False
    track = None
    clip = None
    set_feedback_channels = nop


class PlayheadElement(ProxyElement):

    def __init__(self, playhead=None, *a, **k):
        super(PlayheadElement, self).__init__(proxied_object=playhead, proxied_interface=NullPlayhead())

    def reset(self):
        self.track = None
        return