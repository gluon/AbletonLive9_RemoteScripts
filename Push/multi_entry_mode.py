#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/multi_entry_mode.py
from __future__ import absolute_import, print_function
from ableton.v2.control_surface.mode import tomode, Mode

class MultiEntryMode(Mode):
    """
    Mode wrapper that allows registration in multiple modes
    components.  This wrapper can be entered multiple times and the
    enter method will be called only once.  It will be left when the
    number of times leave_mode is called matches the number of calls
    to enter_mode.
    """

    def __init__(self, mode = None, *a, **k):
        super(MultiEntryMode, self).__init__(*a, **k)
        self._mode = tomode(mode)
        self._entry_count = 0

    def enter_mode(self):
        if self._entry_count == 0:
            self._mode.enter_mode()
        self._entry_count += 1

    def leave_mode(self):
        if not self._entry_count > 0:
            raise AssertionError
            self._entry_count == 1 and self._mode.leave_mode()
        self._entry_count -= 1

    @property
    def is_entered(self):
        return self._entry_count > 0