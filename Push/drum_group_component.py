#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/drum_group_component.py
from pushbase.drum_group_component import DrumGroupComponent as DrumGroupComponentBase

class DrumGroupComponent(DrumGroupComponentBase):

    def __init__(self, selector = None, *a, **k):
        super(DrumGroupComponent, self).__init__(*a, **k)
        self._selector = selector

    def select_drum_pad(self, drum_pad):
        self._selector.on_select_drum_pad(drum_pad)