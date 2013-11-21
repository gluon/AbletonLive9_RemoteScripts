#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/ScrollComponent.py
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import subject_slot
from _Framework import Task
from _Framework import Defaults

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


class ScrollComponent(ControlSurfaceComponent, Scrollable):
    """
    A component that handles scrolling behavior over a Scrollable
    with a pair of buttons.
    """
    is_private = True
    scrolling_delay = Defaults.MOMENTARY_DELAY
    scrolling_step_delay = 0.1
    default_scrollable = Scrollable()
    default_pager = Scrollable()
    _scrollable = default_scrollable

    def __init__(self, scrollable = None, *a, **k):
        super(ScrollComponent, self).__init__(*a, **k)
        self._scroll_task_up = self._make_scroll_task(self._do_scroll_up)
        self._scroll_task_down = self._make_scroll_task(self._do_scroll_down)
        if scrollable != None:
            self.scrollable = scrollable

    def _make_scroll_task(self, scroll_step):
        task = self._tasks.add(Task.sequence(Task.wait(self.scrolling_delay), Task.loop(Task.wait(self.scrolling_step_delay), Task.run(scroll_step))))
        task.kill()
        return task

    def _get_scrollable(self):
        return self._scrollable

    def _set_scrollable(self, scrollable):
        self._scrollable = scrollable
        self.update()

    scrollable = property(_get_scrollable, _set_scrollable)

    def can_scroll_up(self):
        return self._scrollable.can_scroll_up()

    def can_scroll_down(self):
        return self._scrollable.can_scroll_down()

    def scroll_up(self):
        return self._scrollable.scroll_up()

    def scroll_down(self):
        return self._scrollable.scroll_down()

    def set_scroll_up_button(self, button):
        if button:
            button.reset()
        self._on_scroll_up_value.subject = button
        if not button or not button.is_pressed():
            self._scroll_task_up.kill()
        self._update_scroll_up_button()

    def set_scroll_down_button(self, button):
        if button:
            button.reset()
        self._on_scroll_down_value.subject = button
        if not button or not button.is_pressed():
            self._scroll_task_down.kill()
        self._update_scroll_down_button()

    def update(self):
        self._update_scroll_down_button()
        self._update_scroll_up_button()

    def _update_scroll_up_button(self):
        button = self._on_scroll_up_value.subject
        if self.is_enabled() and button:
            if button.is_momentary():
                is_pressed = button.is_pressed()
                can_scroll_up = self.can_scroll_up()
                can_scroll_up and button.set_light('Pressed' if is_pressed else 'Enabled')
            else:
                button.turn_off()

    def _update_scroll_down_button(self):
        button = self._on_scroll_down_value.subject
        if self.is_enabled() and button:
            if button.is_momentary():
                is_pressed = button.is_pressed()
                can_scroll_down = self.can_scroll_down()
                can_scroll_down and button.set_light('Pressed' if is_pressed else 'Enabled')
            else:
                button.turn_off()

    @subject_slot('value')
    def _on_scroll_up_value(self, value):
        self._on_scroll_value(value, self._on_scroll_up_value.subject, self._do_scroll_up, self._scroll_task_up)

    @subject_slot('value')
    def _on_scroll_down_value(self, value):
        self._on_scroll_value(value, self._on_scroll_down_value.subject, self._do_scroll_down, self._scroll_task_down)

    def _do_scroll_up(self):
        self.scroll_up()
        self._update_scroll_up_button()
        self._update_scroll_down_button()

    def _do_scroll_down(self):
        self.scroll_down()
        self._update_scroll_up_button()
        self._update_scroll_down_button()

    def _on_scroll_value(self, value, button, scroll_step, scroll_task):
        if self.is_enabled():
            is_momentary = button.is_momentary()
            if not not self._scroll_task_up.is_killed:
                is_scrolling = not self._scroll_task_down.is_killed
                if not is_scrolling or not is_momentary:
                    scroll_step()
                scroll_task.kill()
                is_momentary and value and scroll_task.restart()
            self._ensure_scroll_one_direction()
            self.update()

    def _ensure_scroll_one_direction(self):
        scroll_up_button = self._on_scroll_up_value.subject
        scroll_down_button = self._on_scroll_down_value.subject
        if scroll_up_button and scroll_up_button.is_pressed() and scroll_down_button and scroll_down_button.is_pressed():
            self._scroll_task_up.pause()
            self._scroll_task_down.pause()
        else:
            self._scroll_task_up.resume()
            self._scroll_task_down.resume()