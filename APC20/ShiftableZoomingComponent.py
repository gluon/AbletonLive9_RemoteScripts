#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC20/ShiftableZoomingComponent.py
import Live
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.ButtonElement import ButtonElement

class ShiftableZoomingComponent(SessionZoomingComponent):
    """ Special ZoomingComponent that uses clip stop buttons for stop all when zoomed """

    def __init__(self, session, stop_buttons):
        SessionZoomingComponent.__init__(self, session)
        self._stop_buttons = stop_buttons
        self._ignore_buttons = False
        for button in self._stop_buttons:
            raise isinstance(button, ButtonElement) or AssertionError
            button.add_value_listener(self._stop_value, identify_sender=True)

    def disconnect(self):
        SessionZoomingComponent.disconnect(self)
        for button in self._stop_buttons:
            button.remove_value_listener(self._stop_value)

    def set_ignore_buttons(self, ignore):
        if not isinstance(ignore, type(False)):
            raise AssertionError
            if self._ignore_buttons != ignore:
                self._ignore_buttons = ignore
                self._is_zoomed_out or self._session.set_enabled(not ignore)
            self.update()

    def update(self):
        if not self._ignore_buttons:
            SessionZoomingComponent.update(self)
        elif self.is_enabled():
            if self._scene_bank_buttons != None:
                for button in self._scene_bank_buttons:
                    button.turn_off()

    def _stop_value(self, value, sender):
        if not value in range(128):
            raise AssertionError
            if not sender != None:
                raise AssertionError
                self.is_enabled() and not self._ignore_buttons and self._is_zoomed_out and (value != 0 or not sender.is_momentary()) and self.song().stop_all_clips()

    def _zoom_value(self, value):
        if not self._zoom_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled():
                    if self._zoom_button.is_momentary():
                        self._is_zoomed_out = value > 0
                    else:
                        self._is_zoomed_out = not self._is_zoomed_out
                    if not self._ignore_buttons:
                        self._scene_bank_index = self._is_zoomed_out and int(self._session.scene_offset() / self._session.height() / self._buttons.height())
                    else:
                        self._scene_bank_index = 0
                    self._session.set_enabled(not self._is_zoomed_out)
                    self._is_zoomed_out and self.update()

    def _matrix_value(self, value, x, y, is_momentary):
        if not self._ignore_buttons:
            SessionZoomingComponent._matrix_value(self, value, x, y, is_momentary)

    def _nav_up_value(self, value):
        if not self._ignore_buttons:
            SessionZoomingComponent._nav_up_value(self, value)

    def _nav_down_value(self, value):
        if not self._ignore_buttons:
            SessionZoomingComponent._nav_down_value(self, value)

    def _nav_left_value(self, value):
        if not self._ignore_buttons:
            SessionZoomingComponent._nav_left_value(self, value)

    def _nav_right_value(self, value):
        if not self._ignore_buttons:
            SessionZoomingComponent._nav_right_value(self, value)

    def _scene_bank_value(self, value, sender):
        if not self._ignore_buttons:
            SessionZoomingComponent._scene_bank_value(self, value, sender)