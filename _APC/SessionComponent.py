#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_APC/SessionComponent.py
from _Framework.SessionComponent import SessionComponent as SessionComponentBase

class SessionComponent(SessionComponentBase):
    """ Special SessionComponent for the APC controllers' combination mode """

    def link_with_track_offset(self, track_offset):
        if not track_offset >= 0:
            raise AssertionError
            self._is_linked() and self._unlink()
        self.set_offsets(track_offset, 0)
        self._link()

    def unlink(self):
        if self._is_linked():
            self._unlink()