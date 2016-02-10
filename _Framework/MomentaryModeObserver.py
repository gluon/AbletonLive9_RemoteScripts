#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/MomentaryModeObserver.py
from __future__ import absolute_import
from . import Defaults

class MomentaryModeObserver(object):
    """ Listens to the changes of a given set of controls and decides which mode to use """

    def __init__(self):
        object.__init__(self)
        self._controls = None
        self._mode_callback = None
        self._reset()

    def disconnect(self):
        self._reset()

    def set_mode_details(self, base_mode, controls, mode_callback = None):
        if not isinstance(base_mode, int):
            raise AssertionError
            raise isinstance(controls, (type(None), tuple)) or AssertionError
            raise mode_callback == None or callable(mode_callback) or AssertionError
            self._reset()
            self._controls = controls != None and controls
            for control in self._controls:
                control.add_value_listener(self._control_changed)

        self._base_mode = base_mode
        self._mode_callback = mode_callback

    def is_mode_momentary(self):
        return self._controls_changed or self._timer_count >= Defaults.MOMENTARY_DELAY_TICKS

    def on_timer(self):
        self._timer_count += 1

    def _control_changed(self, value):
        if self._mode_callback == None or self._mode_callback() == self._base_mode:
            self._controls_changed = True

    def _release_controls(self):
        if self._controls != None:
            for control in self._controls:
                control.remove_value_listener(self._control_changed)

            self._controls = None

    def _reset(self):
        self._base_mode = -1
        self._controls_changed = False
        self._mode_callback = None
        self._timer_count = 0
        self._release_controls()