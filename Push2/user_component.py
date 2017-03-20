# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/user_component.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from contextlib import contextmanager
from ableton.v2.control_surface.mode import ModeButtonBehaviour
from pushbase.user_component import UserComponentBase
from . import sysex

class UserButtonBehavior(ModeButtonBehaviour):

    def __init__(self, user_component=None, *a, **k):
        assert user_component is not None
        super(UserButtonBehavior, self).__init__(*a, **k)
        self._previous_mode = None
        self._user_component = user_component
        return

    def press_immediate(self, component, mode):
        if component.selected_mode != 'user' and self._user_component.mode == sysex.LIVE_MODE:
            self._previous_mode = component.selected_mode
            component.selected_mode = 'user'
        else:
            self._leave_user_mode(component)

    def release_delayed(self, component, mode):
        self._leave_user_mode(component)

    def _leave_user_mode(self, component):
        if component.selected_mode == 'user' and self._user_component.mode == sysex.USER_MODE:
            assert self._previous_mode is not None
            component.selected_mode = self._previous_mode
            self._previous_mode = None
        return


class UserComponent(UserComponentBase):

    @contextmanager
    def _deferring_sysex(self):
        self.defer_sysex_sending = True
        yield
        self.defer_sysex_sending = False

    def _do_set_mode(self, mode):
        if mode == sysex.USER_MODE:
            with self._deferring_sysex():
                super(UserComponent, self)._do_set_mode(mode)
        else:
            super(UserComponent, self)._do_set_mode(mode)