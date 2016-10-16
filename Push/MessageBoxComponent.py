#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/MessageBoxComponent.py
from functools import partial
from _Framework.Dependency import dependency
from _Framework.CompoundComponent import CompoundComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import forward_property, const, nop, maybe
from _Framework import Task
from _Framework.ControlElement import ControlElement
from _Framework.Layer import Layer
from _Framework.BackgroundComponent import BackgroundComponent
from _Framework.CompoundElement import CompoundElement
from consts import MessageBoxText, DISPLAY_LENGTH, DISPLAY_BLOCK_LENGTH, MESSAGE_BOX_PRIORITY

class Messenger(object):
    """
    Externally provided interface for those components that provide
    global Push feedback.
    """
    expect_dialog = dependency(expect_dialog=const(nop))
    show_notification = dependency(show_notification=const(nop))


class MessageBoxComponent(BackgroundComponent):
    """
    Component showing a temporary message in the display
    """
    __subject_events__ = ('cancel',)
    _cancel_button_index = 7
    num_lines = 4

    def __init__(self, *a, **k):
        super(MessageBoxComponent, self).__init__(*a, **k)
        self._current_text = None
        self._can_cancel = False
        self._top_row_buttons = None
        self.data_sources = map(DisplayDataSource, ('',) * self.num_lines)
        self._notification_display = None

    def _set_display_line(self, n, display_line):
        if display_line:
            display_line.set_data_sources((self.data_sources[n],))

    def set_display_line1(self, display_line):
        self._set_display_line(0, display_line)

    def set_display_line2(self, display_line):
        self._set_display_line(1, display_line)

    def set_display_line3(self, display_line):
        self._set_display_line(2, display_line)

    def set_display_line4(self, display_line):
        self._set_display_line(3, display_line)

    def set_top_buttons(self, buttons):
        self._top_row_buttons = buttons
        if buttons:
            buttons.reset()
        self.set_cancel_button(buttons[self._cancel_button_index] if buttons else None)

    def set_cancel_button(self, button):
        self._on_cancel_button_value.subject = button
        self._update_cancel_button()

    def _update_cancel_button(self):
        if self.is_enabled():
            button = self._on_cancel_button_value.subject
            if self._top_row_buttons:
                self._top_row_buttons.reset()
            if self._can_cancel and button:
                button.set_light('MessageBox.Cancel')

    def _update_display(self):
        if self._current_text != None:
            lines = self._current_text.split('\n')
            for source_line, line in map(None, self.data_sources, lines):
                if source_line:
                    source_line.set_display_string(line or '')

            if self._can_cancel:
                self.data_sources[-1].set_display_string('[  Ok  ]'.rjust(DISPLAY_LENGTH - 1))

    @subject_slot('value')
    def _on_cancel_button_value(self, value):
        if self.is_enabled() and self._can_cancel and value:
            self.notify_cancel()

    def _get_text(self):
        return self._current_text

    def _set_text(self, text):
        self._current_text = text
        self._update_display()

    text = property(_get_text, _set_text)

    def _get_can_cancel(self):
        return self._can_cancel

    def _set_can_cancel(self, can_cancel):
        self._can_cancel = can_cancel
        self._update_cancel_button()
        self._update_display()

    can_cancel = property(_get_can_cancel, _set_can_cancel)

    def update(self):
        super(MessageBoxComponent, self).update()
        self._update_cancel_button()
        self._update_display()


class _CallbackControl(CompoundElement):
    _is_resource_based = True

    def __init__(self, token = None, callback = None, *a, **k):
        super(_CallbackControl, self).__init__(*a, **k)
        self._callback = callback
        self.register_control_element(token)

    def on_nested_control_element_received(self, control):
        self._callback()

    def on_nested_control_element_lost(self, control):
        pass


class _TokenControlElement(ControlElement):

    def reset(self):
        pass


BLANK_BLOCK = ' ' * DISPLAY_BLOCK_LENGTH

def align_none(width, text):
    return text


def align_left(width, text):
    while text.startswith(BLANK_BLOCK):
        text = text[DISPLAY_BLOCK_LENGTH:]

    return text


def align_right(width, text):
    text = text.ljust(width)
    while text.endswith(BLANK_BLOCK):
        text = BLANK_BLOCK + text[:1 - DISPLAY_BLOCK_LENGTH]

    return text


class NotificationComponent(CompoundComponent):
    """
    Displays notifications to the user for a given amount of time. A notification time
    of -1 creates an infinite duration notification.
    
    To adjust the way notifications are shown in special cases, assign a generated
    control using use_single_line or use_full_display to a layer. If the layer is on
    top, it will set the preferred view.
    This will show the notification on line 1 if my_component is enabled and
    the priority premise of the layer is met:
    
        my_component.layer = Layer(
            _notification = notification_component.use_single_line(1))
    """
    _default_align_text_fn = partial(maybe(partial(align_none, DISPLAY_LENGTH)))

    def __init__(self, notification_time = 2.5, blinking_time = 0.3, display_lines = [], *a, **k):
        super(NotificationComponent, self).__init__(*a, **k)
        self._display_lines = display_lines
        self._token_control = _TokenControlElement()
        self._align_text_fn = self._default_align_text_fn
        self._message_box = self.register_component(MessageBoxComponent())
        self._message_box.set_enabled(False)
        self._notification_timeout_task = self._tasks.add(Task.sequence(Task.wait(notification_time), Task.run(self.hide_notification))).kill() if notification_time != -1 else self._tasks.add(Task.Task())
        self._blink_text_task = self._tasks.add(Task.loop(Task.sequence(Task.run(lambda : self._message_box.__setattr__('text', self._original_text)), Task.wait(blinking_time), Task.run(lambda : self._message_box.__setattr__('text', self._blink_text)), Task.wait(blinking_time)))).kill()
        self._original_text = None
        self._blink_text = None

    message_box_layer = forward_property('_message_box')('layer')

    def show_notification(self, text, blink_text = None):
        """
        Triggers a notification with the given text.
        """
        text = self._align_text_fn(text)
        blink_text = self._align_text_fn(blink_text)
        if blink_text is not None:
            self._original_text = text
            self._blink_text = blink_text
            self._blink_text_task.restart()
        self._message_box.text = text
        self._message_box.set_enabled(True)
        self._notification_timeout_task.restart()

    def hide_notification(self):
        """
        Hides the current notification, if any existing.
        """
        self._blink_text_task.kill()
        self._message_box.set_enabled(False)

    def use_single_line(self, line_index, line_slice = None, align = align_none):
        """
        Returns a control, that will change the notification to a single line view,
        if it is grabbed.
        """
        if not (line_index >= 0 and line_index < len(self._display_lines)):
            raise AssertionError
            display = self._display_lines[line_index]
            display = line_slice is not None and display.subdisplay[line_slice]
        layer = Layer(priority=MESSAGE_BOX_PRIORITY, display_line1=display)
        return _CallbackControl(self._token_control, partial(self._set_message_box_layout, layer, maybe(partial(align, display.width))))

    def use_full_display(self, message_line_index = 2):
        """
        Returns a control, that will change the notification to use the whole display,
        if it is grabbed.
        """
        layer = Layer(priority=MESSAGE_BOX_PRIORITY, **dict([ ('display_line1' if i == message_line_index else 'bg%d' % i, line) for i, line in enumerate(self._display_lines) ]))
        return _CallbackControl(self._token_control, partial(self._set_message_box_layout, layer))

    def _set_message_box_layout(self, layer, align_text_fn = None):
        self._message_box.layer = layer
        self._align_text_fn = partial(align_text_fn or self._default_align_text_fn)


class DialogComponent(CompoundComponent):
    """
    Handles representing modal dialogs from the application.  The
    script can also request dialogs.
    """

    def __init__(self, *a, **k):
        super(DialogComponent, self).__init__(*a, **k)
        self._message_box = self.register_component(MessageBoxComponent())
        self._message_box.set_enabled(False)
        self._next_message = None
        self._on_open_dialog_count.subject = self.application()
        self._on_message_cancel.subject = self._message_box

    message_box_layer = forward_property('_message_box')('layer')

    def expect_dialog(self, message):
        """
        Expects a dialog from Live to appear soon.  The dialog will be
        shown on the controller with the given message regardless of
        wether a dialog actually appears.  This dialog can be
        cancelled.
        """
        self._next_message = message
        self._update_dialog()

    @subject_slot('open_dialog_count')
    def _on_open_dialog_count(self):
        self._update_dialog(open_dialog_changed=True)
        self._next_message = None

    @subject_slot('cancel')
    def _on_message_cancel(self):
        self._next_message = None
        try:
            self.application().press_current_dialog_button(0)
        except RuntimeError:
            pass

        self._update_dialog()

    def _update_dialog(self, open_dialog_changed = False):
        message = self._next_message or MessageBoxText.LIVE_DIALOG
        can_cancel = self._next_message != None
        self._message_box.text = message
        self._message_box.can_cancel = can_cancel
        self._message_box.set_enabled(self.application().open_dialog_count > 0 or not open_dialog_changed and self._next_message)


class InfoComponent(BackgroundComponent):
    """
    Component that will show an info text and grab all components that should be unusable.
    """

    def __init__(self, info_text = '', *a, **k):
        super(InfoComponent, self).__init__(*a, **k)
        self._data_source = DisplayDataSource()
        self._data_source.set_display_string(info_text)

    def set_display(self, display):
        if display:
            display.set_data_sources([self._data_source])