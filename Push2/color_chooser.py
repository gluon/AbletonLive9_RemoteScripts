# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/color_chooser.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base import liveobj_changed, liveobj_valid, nop
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import ButtonControl, control_matrix
from pushbase.colors import Pulse
from pushbase.message_box_component import Messenger
from .colors import IndexedColor, Rgb, inverse_translate_color_index, translate_color_index
from .skin_default import SELECTION_PULSE_SPEED
COLOR_CHOOSER_LAYOUT = (
 (13, 12, 14, 15, 17, 16, 18, 19),
 (11, None, None, None, None, None, None, 20),
 (9, None, None, None, None, None, None, 21),
 (8, None, None, None, None, None, None, 26),
 (10, None, None, None, None, None, None, 22),
 (7, None, None, None, None, None, None, 25),
 (5, None, None, None, None, None, None, 24),
 (4, 6, 3, None, None, 1, 23, 2))

class ColorChooserComponent(Component, Messenger):
    matrix = control_matrix(ButtonControl, dimensions=(8, 8))

    def __init__(self, *a, **k):
        super(ColorChooserComponent, self).__init__(is_enabled=False, *a, **k)
        self._object = None
        self._notification_ref = nop
        for button in self.matrix:
            row, column = button.coordinate
            button.color_index = COLOR_CHOOSER_LAYOUT[row][column]

        return

    @property
    def object(self):
        return self._object

    @object.setter
    def object(self, obj):
        if liveobj_changed(self._object, obj):
            self._object = obj
            if obj is None:
                notification = self._notification_ref()
                if notification:
                    notification.hide()
                self.set_enabled(False)
            else:
                self._render_color_palette(translate_color_index(obj.color_index))
                self.set_enabled(True)
                self._notification_ref = self.show_notification('Select a color for: %s' % obj.name, notification_time=-1)
        return

    @matrix.pressed
    def matrix(self, button):
        if liveobj_valid(self.object):
            if button.color_index is None:
                if hasattr(self.object, 'is_auto_colored'):
                    self.object.is_auto_colored = True
                    self.show_notification('Color automatically enabled for: %s' % self.object.name)
            else:
                self.object.color_index = inverse_translate_color_index(button.color_index)
            self.object = None
        return

    def _render_color_palette(self, selected_color_index):
        for button in self.matrix:
            color_index = button.color_index
            if color_index is not None:
                if color_index == selected_color_index:
                    button.color = Pulse(IndexedColor.from_push_index(color_index, shade_level=2), IndexedColor.from_push_index(color_index), SELECTION_PULSE_SPEED)
                else:
                    button.color = IndexedColor.from_push_index(color_index)
            else:
                button.color = Rgb.BLACK

        return