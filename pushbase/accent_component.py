# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/accent_component.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from ableton.v2.control_surface.mode import ModesComponent

class DummyFullVelocity(object):
    enabled = False


class AccentComponent(ModesComponent):

    def __init__(self, *a, **k):
        super(AccentComponent, self).__init__(*a, **k)
        self._full_velocity = None
        self.add_mode('disabled', None, 'Accent.Off')
        self.add_mode('enabled', (
         self._on_accent_on, self._on_accent_off), 'Accent.On')
        self.selected_mode = 'disabled'
        self.set_full_velocity(None)
        return

    def set_full_velocity(self, full_velocity):
        full_velocity = full_velocity or DummyFullVelocity()
        if self._full_velocity != None:
            self._full_velocity.enabled = False
        self._full_velocity = full_velocity
        self._full_velocity.enabled = self.selected_mode == 'enabled'
        return

    @property
    def activated(self):
        return self._full_velocity.enabled

    def _on_accent_off(self):
        self._full_velocity.enabled = False

    def _on_accent_on(self):
        self._full_velocity.enabled = True