#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Push/SlideComponent.py
"""
Component that navigates a series of pages.
"""
from math import ceil
from itertools import imap
from _Framework.SubjectSlot import subject_slot, Subject
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ScrollComponent import ScrollComponent, Scrollable
from _Framework.Util import clamp
from TouchStripElement import TouchStripElement, TouchStripHandle, DraggingBehaviour, SelectingBehaviour, MAX_PITCHBEND

class Slideable(Subject):
    """
    Models of an entity that has a position in a 1-D discrete axis,
    and that has some natural steps (called pages) of this axis.
    """
    __subject_events__ = ('page_offset', 'page_length', 'position', 'position_count', 'contents')

    def contents_range(self, pmin, pmax):
        """
        Tells whether there are any contents in the (min, max) range,
        wheren min and max are floats in the (0, position_count)
        range. Can be left unimplemented.
        """
        pos_count = self.position_count
        first_pos = max(int(pmin), 0)
        last_pos = min(int(pmax), pos_count)
        return xrange(first_pos, last_pos)

    def contents(self, position):
        return False

    @property
    def position_count(self):
        raise NotImplementedError

    @property
    def position(self):
        raise NotImplementedError

    @property
    def page_offset(self):
        raise NotImplementedError

    @property
    def page_length(self):
        raise NotImplementedError


class SlideComponent(CompoundComponent, Scrollable):

    def __init__(self, slideable = None, dragging_enabled = False, *a, **k):
        super(SlideComponent, self).__init__(*a, **k)
        slideable = slideable or self
        self._behaviour = DraggingBehaviour() if dragging_enabled else SelectingBehaviour()
        self._touch_strip_array = []
        self._slideable = slideable
        self._position_scroll, self._page_scroll = self.register_components(ScrollComponent(), ScrollComponent())
        self._position_scroll.scrollable = self
        self._page_scroll.can_scroll_up = self.can_scroll_page_up
        self._page_scroll.can_scroll_down = self.can_scroll_page_down
        self._page_scroll.scroll_down = self.scroll_page_down
        self._page_scroll.scroll_up = self.scroll_page_up
        self._on_page_length_changed.subject = slideable
        self._on_page_offset_changed.subject = slideable
        self._on_position_count_changed.subject = slideable
        self._on_position_changed.subject = slideable
        self._on_contents_changed.subject = slideable

    def set_page_strip(self, strip):
        self._on_page_touch_strip_value.subject = strip
        self._update_touch_strip_state(strip)

    def set_scroll_strip(self, strip):
        self._on_touch_strip_value.subject = strip
        self._update_touch_strip_state(strip)

    def set_scroll_up_button(self, button):
        self._position_scroll.set_scroll_up_button(button)

    def set_scroll_down_button(self, button):
        self._position_scroll.set_scroll_down_button(button)

    def set_scroll_page_up_button(self, button):
        self._page_scroll.set_scroll_up_button(button)

    def set_scroll_page_down_button(self, button):
        self._page_scroll.set_scroll_down_button(button)

    def scroll_page_up(self):
        self._scroll_page(1)

    def scroll_page_down(self):
        self._scroll_page(-1)

    def scroll_up(self):
        self._scroll_position(1)

    def scroll_down(self):
        self._scroll_position(-1)

    def can_scroll_page_up(self):
        model = self._slideable
        return model.position < model.position_count - model.page_length

    def can_scroll_page_down(self):
        return self._slideable.position > 0

    def can_scroll_up(self):
        return self.can_scroll_page_up()

    def can_scroll_down(self):
        return self.can_scroll_page_down()

    def update(self):
        super(SlideComponent, self).update()
        self._touch_strip_array = []
        self._update_touch_strips()

    def _scroll_position(self, delta):
        if self.is_enabled():
            model = self._slideable
            model.position = clamp(model.position + delta, 0, model.position_count - model.page_length)

    def _scroll_page(self, sign):
        if self.is_enabled():
            model = self._slideable
            remainder = (model.position - model.page_offset) % model.page_length
            if sign > 0:
                delta = model.page_length - remainder
            elif remainder == 0:
                delta = -model.page_length
            else:
                delta = -remainder
            self._scroll_position(delta)

    def _update_touch_strips(self):
        self._update_touch_strip_state(self._on_touch_strip_value.subject)
        self._update_touch_strip_state(self._on_page_touch_strip_value.subject)

    def _scroll_to_led_position(self, scroll_pos, num_leds):
        scroll_pos += 1
        pos_count = self._slideable.position_count
        return min(int(float(scroll_pos) / pos_count * num_leds), num_leds)

    def _touch_strip_to_scroll_position(self, value):
        bank_size = self._slideable.page_length
        num_pad_rows = self._slideable.position_count
        max_pad_row = num_pad_rows - bank_size
        return min(int(float(value) / MAX_PITCHBEND * num_pad_rows), max_pad_row)

    def _touch_strip_to_page_position(self, value):
        bank_size = self._slideable.page_length
        num_pad_rows = self._slideable.position_count
        max_pad_row = num_pad_rows - bank_size
        offset = bank_size - self._slideable.page_offset
        return clamp(int(int(value / MAX_PITCHBEND * num_pad_rows + offset) / float(bank_size)) * bank_size - offset, 0, max_pad_row)

    def _scroll_to_touch_strip_position(self, scroll_pos):
        num_pad_rows = self._slideable.position_count
        return min(int(float(scroll_pos) / num_pad_rows * MAX_PITCHBEND), int(MAX_PITCHBEND))

    def _touch_strip_led_page_length(self, num_leds):
        return int(ceil(float(self._slideable.page_length) / self._slideable.position_count * num_leds))

    def _update_touch_strip_state(self, strip):
        if strip and self.is_enabled():
            strip.behaviour = self._behaviour
            if len(self._touch_strip_array) != strip.STATE_COUNT:
                self._update_touch_strip_array(strip.STATE_COUNT)
            model_pos = self._slideable.position
            led_pos = self._scroll_to_led_position(model_pos, strip.STATE_COUNT)
            strip_pos = self._scroll_to_touch_strip_position(model_pos)
            array = list(self._touch_strip_array)
            led_page_length = self._touch_strip_led_page_length(strip.STATE_COUNT)
            array[led_pos:led_pos + led_page_length] = [strip.STATE_FULL] * led_page_length
            led_size = MAX_PITCHBEND / strip.STATE_COUNT
            self._behaviour.handle = TouchStripHandle(range=(-led_size, led_size * led_page_length), position=strip_pos)
            strip.send_state(array[:strip.STATE_COUNT])

    def _update_touch_strip_array(self, num_leds):
        if self.is_enabled():
            model = self._slideable

            def led_contents(i):
                pmin = float(i) / num_leds * model.position_count
                pmax = pmin + float(model.position_count) / num_leds
                return any(imap(model.contents, model.contents_range(pmin, pmax)))

            array = [ (TouchStripElement.STATE_HALF if led_contents(i) else TouchStripElement.STATE_OFF) for i in xrange(num_leds) ]
            self._touch_strip_array = array

    @subject_slot('value')
    def _on_touch_strip_value(self, value):
        if self.is_enabled():
            position = self._touch_strip_to_scroll_position(value)
            self._slideable.position = position

    @subject_slot('value')
    def _on_page_touch_strip_value(self, value):
        if self.is_enabled():
            position = self._touch_strip_to_page_position(value)
            self._slideable.position = position

    @subject_slot('page_length')
    def _on_page_length_changed(self):
        self._update_touch_strips()

    @subject_slot('page_offset')
    def _on_page_offset_changed(self):
        pass

    @subject_slot('position')
    def _on_position_changed(self):
        self._update_touch_strips()
        self._position_scroll.update()
        self._page_scroll.update()

    @subject_slot('position_count')
    def _on_position_count_changed(self):
        pass

    @subject_slot('contents')
    def _on_contents_changed(self):
        self.update()