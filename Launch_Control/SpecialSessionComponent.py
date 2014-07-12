#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_static/midi-remote-scripts/Launch_Control/SpecialSessionComponent.py
from _Framework.SessionComponent import SessionComponent

class SpecialSessionComponent(SessionComponent):

    def set_clip_launch_buttons(self, buttons):
        for i, button in map(None, xrange(self._num_tracks), buttons or []):
            scene = self.selected_scene()
            slot = scene.clip_slot(i)
            slot.set_launch_button(button)