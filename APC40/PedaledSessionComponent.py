#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC40/PedaledSessionComponent.py
import Live
from APCSessionComponent import APCSessionComponent
from _Framework.ButtonElement import ButtonElement

class PedaledSessionComponent(APCSessionComponent):
    """ Special SessionComponent with a button (pedal) to fire the selected clip slot """

    def __init__(self, num_tracks, num_scenes):
        APCSessionComponent.__init__(self, num_tracks, num_scenes)
        self._slot_launch_button = None

    def disconnect(self):
        APCSessionComponent.disconnect(self)
        if self._slot_launch_button != None:
            self._slot_launch_button.remove_value_listener(self._slot_launch_value)
            self._slot_launch_button = None

    def set_slot_launch_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._slot_launch_button != button:
                if self._slot_launch_button != None:
                    self._slot_launch_button.remove_value_listener(self._slot_launch_value)
                self._slot_launch_button = button
                self._slot_launch_button != None and self._slot_launch_button.add_value_listener(self._slot_launch_value)
            self.update()

    def _slot_launch_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._slot_launch_button != None:
                raise AssertionError
                if self.is_enabled():
                    (value != 0 or not self._slot_launch_button.is_momentary()) and self.song().view.highlighted_clip_slot != None and self.song().view.highlighted_clip_slot.fire()