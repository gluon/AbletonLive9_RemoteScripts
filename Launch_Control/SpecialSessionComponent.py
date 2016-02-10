#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control/SpecialSessionComponent.py
from itertools import izip_longest
from _Framework.SessionComponent import SessionComponent

class SpecialSessionComponent(SessionComponent):

    def set_clip_launch_buttons(self, buttons):
        for i, button in izip_longest(xrange(self._num_tracks), buttons or []):
            scene = self.selected_scene()
            slot = scene.clip_slot(i)
            slot.set_launch_button(button)