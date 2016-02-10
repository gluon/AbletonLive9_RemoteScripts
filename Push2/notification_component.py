#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/notification_component.py
from __future__ import absolute_import, print_function
from weakref import ref
import time
from ableton.v2.base import nop, task, listenable_property
from ableton.v2.control_surface import ControlElement, Component
from pushbase.message_box_component import Notification
from .model.repr import strip_formatted_string

class NotificationComponent(Component):

    def __init__(self, default_notification_time = 2.5, *a, **k):
        super(NotificationComponent, self).__init__(*a, **k)
        self._visible = False
        self._message = ''
        self._shown_at = None
        self._duration = None
        self.show_notification = self._show_notification
        self._notification_timeout_task = None
        self._default_notification_time = default_notification_time
        self._dummy_control_element = ControlElement()
        self._dummy_control_element.reset = nop

    def disconnect(self):
        self.hide_notification()
        self.show_notification = nop
        super(NotificationComponent, self).disconnect()

    @listenable_property
    def visible(self):
        return self._visible

    @listenable_property
    def message(self):
        return self._message

    def _create_notification_timeout_task(self, duration):
        self._notification_timeout_task = self._tasks.add(task.sequence(task.wait(duration), task.run(self.hide_notification)))

    def _show_notification(self, text, blink_text = None, notification_time = None):
        self._message = strip_formatted_string(text)
        self._duration = notification_time if notification_time is not None else self._default_notification_time
        self._create_notification_timeout_task(self._duration)
        if not self._visible:
            self._visible = True
            self._shown_at = time.clock()
            self.notify_visible()
            self.notify_message()
        self._current_notification = Notification(self)
        self._current_notification.reschedule_after_slow_operation = self._reschedule_after_slow_operation
        return ref(self._current_notification)

    def _reschedule_after_slow_operation(self):
        time_remaining = self._duration - (time.clock() - self._shown_at)
        if time_remaining > 0:
            if self._notification_timeout_task:
                self._notification_timeout_task.kill()
            self._create_notification_timeout_task(time_remaining)
        else:
            self.hide_notification()

    def hide_notification(self):
        if self._notification_timeout_task:
            self._notification_timeout_task.kill()
        if self._visible:
            self._visible = False
            self.notify_visible()

    def use_single_line(self, *a):
        """
        Only for Push 1 compatibility
        """
        return self._dummy_control_element

    def use_full_display(self, *a):
        """
        Only for Push 1 compatibility
        """
        return self._dummy_control_element