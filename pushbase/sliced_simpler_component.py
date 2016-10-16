#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/sliced_simpler_component.py
from __future__ import absolute_import, print_function
from ableton.v2.control_surface.components import PlayableComponent
from ableton.v2.control_surface.components import Slideable, SlideComponent
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.base import liveobj_valid, listens, listenable_property
from .slideable_touch_strip_component import SlideableTouchStripComponent
from .matrix_maps import PAD_FEEDBACK_CHANNEL
BASE_SLICING_NOTE = 36

class SlicedSimplerComponent(PlayableComponent, SlideableTouchStripComponent, SlideComponent, Slideable):
    delete_button = ButtonControl()
    position_count = 16
    page_length = 4
    page_offset = 1

    def __init__(self, *a, **k):
        self._position = 0
        super(SlicedSimplerComponent, self).__init__(touch_slideable=self, dragging_enabled=True, *a, **k)
        self._simpler = None

    def _get_position(self):
        return self._position

    def _set_position(self, index):
        raise 0 <= index <= 12 or AssertionError
        self._position = index
        self.notify_position()
        self._update_led_feedback()
        self._update_note_translations()

    position = property(_get_position, _set_position)

    def set_simpler(self, simpler):
        self._simpler = simpler
        self.__on_selected_slice_changed.subject = simpler
        self.__on_file_changed.subject = simpler
        self.__on_slices_changed.subject = simpler.sample if liveobj_valid(simpler) else None
        self._update_led_feedback()
        self.update()

    @listens('slices')
    def __on_slices_changed(self):
        self._update_led_feedback()

    @listens('view.selected_slice')
    def __on_selected_slice_changed(self):
        self._update_led_feedback()
        self.notify_selected_note()

    def _slices(self):
        if liveobj_valid(self._simpler) and liveobj_valid(self._simpler.sample):
            return self._simpler.sample.slices
        return []

    @listenable_property
    def selected_note(self):
        slices = list(self._slices())
        selected_slice = self._selected_slice()
        index = slices.index(selected_slice) if selected_slice in slices else 0
        return BASE_SLICING_NOTE + index

    def _selected_slice(self):
        if liveobj_valid(self._simpler):
            return self._simpler.view.selected_slice
        return -1

    @listens('sample')
    def __on_file_changed(self):
        self.__on_slices_changed.subject = self._simpler.sample if liveobj_valid(self._simpler) else None
        self._update_led_feedback()

    def _button_coordinate_to_slice_index(self, button):
        y, x = button.coordinate
        y = self.height - y - 1
        y += self._position
        y += self.height if x >= 4 else 0
        return x % 4 + y * 4

    def _update_button_color(self, button):
        index = self._button_coordinate_to_slice_index(button)
        slices = self._slices()
        if index < len(slices):
            button.color = 'SlicedSimpler.SliceSelected' if slices[index] == self._selected_slice() else 'SlicedSimpler.SliceUnselected'
        else:
            button.color = 'SlicedSimpler.NoSlice'

    def _note_translation_for_button(self, button):
        identifier = BASE_SLICING_NOTE + self._button_coordinate_to_slice_index(button)
        return (identifier, PAD_FEEDBACK_CHANNEL)

    @delete_button.value
    def delete_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    def _try_delete_slice_at_index(self, index):
        if liveobj_valid(self._simpler) and liveobj_valid(self._simpler.sample):
            slices = self._slices()
            if len(slices) > index:
                self._simpler.sample.remove_slice(slices[index])

    def set_select_button(self, button):
        self.select_button.set_control_element(button)

    def _try_select_slice_at_index(self, index):
        slices = self._slices()
        if len(slices) > index:
            self._simpler.view.selected_slice = slices[index]

    def _on_matrix_pressed(self, button):
        slice_index = self._button_coordinate_to_slice_index(button)
        if self.delete_button.is_pressed:
            self._try_delete_slice_at_index(slice_index)
        elif self.select_button.is_pressed:
            self._try_select_slice_at_index(slice_index)
        super(SlicedSimplerComponent, self)._on_matrix_pressed(button)