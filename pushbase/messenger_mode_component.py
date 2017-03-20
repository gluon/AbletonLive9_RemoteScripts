# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/messenger_mode_component.py
# Compiled at: 2016-06-08 13:13:04
from __future__ import absolute_import, print_function
from ableton.v2.base import BooleanContext
from ableton.v2.control_surface.mode import ModesComponent
from .message_box_component import Messenger

class MessengerModesComponent(ModesComponent, Messenger):
    notify_when_enabled = False

    def __init__(self, *a, **k):
        super(MessengerModesComponent, self).__init__(*a, **k)
        self._mode_message_map = {}
        self._is_being_enabled = BooleanContext()

    def add_mode(self, name, mode_or_component, message=None, **k):
        super(MessengerModesComponent, self).add_mode(name, mode_or_component, **k)
        self._mode_message_map[name] = message

    def on_enabled_changed(self):
        with self._is_being_enabled():
            super(MessengerModesComponent, self).on_enabled_changed()

    def _do_enter_mode(self, name):
        super(MessengerModesComponent, self)._do_enter_mode(name)
        if not self._is_being_enabled or self.notify_when_enabled:
            message = self._mode_message_map.get(name, None)
            if message:
                self.show_notification(message)
        return