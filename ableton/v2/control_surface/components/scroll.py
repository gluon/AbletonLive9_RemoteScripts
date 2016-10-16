#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/scroll.py
from __future__ import absolute_import, print_function
from ...base import task
from .. import defaults
from ..control import ButtonControl
from ..component import Component

class Scrollable(object):
    """
    Abstract interface for an object that can be scrolled in discreet
    steps in one dimension.
    """

    def can_scroll_up(self):
        return False

    def can_scroll_down(self):
        return False

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass


class ScrollComponent(Component, Scrollable):
    """
    A component that handles scrolling behavior over a Scrollable
    with a pair of buttons.
    """
    is_private = True
    scrolling_delay = defaults.MOMENTARY_DELAY
    scrolling_step_delay = 0.1
    default_scrollable = Scrollable()
    default_pager = Scrollable()
    _scrollable = default_scrollable
    scroll_up_button = ButtonControl()
    scroll_down_button = ButtonControl()

    def __init__(self, scrollable = None, *a, **k):
        super(ScrollComponent, self).__init__(*a, **k)
        self._scroll_task_up = self._make_scroll_task(self._do_scroll_up)
        self._scroll_task_down = self._make_scroll_task(self._do_scroll_down)
        if scrollable != None:
            self.scrollable = scrollable

    def _make_scroll_task(self, scroll_step):
        t = self._tasks.add(task.sequence(task.wait(self.scrolling_delay), task.loop(task.wait(self.scrolling_step_delay), task.run(scroll_step))))
        t.kill()
        return t

    @property
    def scrollable(self):
        return self._scrollable

    @scrollable.setter
    def scrollable(self, scrollable):
        self._scrollable = scrollable
        self._update_scroll_buttons()

    def can_scroll_up(self):
        return self._scrollable.can_scroll_up()

    def can_scroll_down(self):
        return self._scrollable.can_scroll_down()

    def scroll_up(self):
        return self._scrollable.scroll_up()

    def scroll_down(self):
        return self._scrollable.scroll_down()

    def set_scroll_up_button(self, button):
        self.scroll_up_button.set_control_element(button)
        self._update_scroll_buttons()

    def set_scroll_down_button(self, button):
        self.scroll_down_button.set_control_element(button)
        self._update_scroll_buttons()

    def _update_scroll_buttons(self):
        self.scroll_up_button.enabled = self.can_scroll_up()
        self.scroll_down_button.enabled = self.can_scroll_down()

    @scroll_up_button.pressed
    def scroll_up_button(self, button):
        self._on_scroll_pressed(button, self._do_scroll_up, self._scroll_task_up)

    @scroll_up_button.released
    def scroll_up_button(self, button):
        self._on_scroll_released(self._scroll_task_up)

    @scroll_down_button.pressed
    def scroll_down_button(self, button):
        self._on_scroll_pressed(button, self._do_scroll_down, self._scroll_task_down)

    @scroll_down_button.released
    def scroll_down_button(self, button):
        self._on_scroll_released(self._scroll_task_down)

    def _do_scroll_up(self):
        self.scroll_up()
        self._update_scroll_buttons()

    def _do_scroll_down(self):
        self.scroll_down()
        self._update_scroll_buttons()

    def update(self):
        super(ScrollComponent, self).update()
        self._update_scroll_buttons()

    def _on_scroll_pressed(self, button, scroll_step, scroll_task):
        is_scrolling = not self._scroll_task_up.is_killed or not self._scroll_task_down.is_killed
        if not is_scrolling:
            scroll_step()
        if button.enabled:
            scroll_task.restart()
        self._ensure_scroll_one_direction()

    def _on_scroll_released(self, scroll_task):
        scroll_task.kill()
        self._ensure_scroll_one_direction()

    def _ensure_scroll_one_direction(self):
        if self.scroll_up_button.is_pressed and self.scroll_down_button.is_pressed:
            self._scroll_task_up.pause()
            self._scroll_task_down.pause()
        else:
            self._scroll_task_up.resume()
            self._scroll_task_down.resume()