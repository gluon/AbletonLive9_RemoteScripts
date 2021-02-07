# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/sliced_simpler.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from pushbase.colors import Pulse
from pushbase.sliced_simpler_component import SlicedSimplerComponent
from .colors import IndexedColor
NEXT_SLICE_PULSE_SPEED = 48

def next_slice_color(track_color_index):
    return Pulse(color1=IndexedColor.from_live_index(track_color_index, shade_level=2), color2=IndexedColor.from_live_index(track_color_index, shade_level=1), speed=NEXT_SLICE_PULSE_SPEED)


class Push2SlicedSimplerComponent(SlicedSimplerComponent):

    def _next_slice_color(self):
        return next_slice_color(self.song.view.selected_track.color_index)