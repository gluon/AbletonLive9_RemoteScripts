#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/message_box_component.py
from __future__ import absolute_import, print_function
from itertools import izip_longest
from ableton.v2.base import forward_property, const, nop, listens, listenable_property
from ableton.v2.base.dependency import dependency
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.elements import DisplayDataSource
from ableton.v2.control_surface.components import BackgroundComponent
from .consts import DISPLAY_LENGTH, MessageBoxText

class Notification(object):

    def __init__(self, parent, *a, **k):
        super(Notification, self).__init__(*a, **k)
        self.hide = parent.hide_notification


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
    __events__ = ('cancel',)
    num_lines = 4

    def __init__(self, *a, **k):
        super(MessageBoxComponent, self).__init__(*a, **k)
        self._current_text = None
        self._can_cancel = False
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

    def set_cancel_button(self, button):
        self._on_cancel_button_value.subject = button
        self._update_cancel_button()

    def _update_cancel_button(self):
        if self.is_enabled():
            button = self._on_cancel_button_value.subject
            if button is not None:
                button.reset()
            if self._can_cancel and button:
                button.set_light('MessageBox.Cancel')

    def _update_display(self):
        if self._current_text != None:
            lines = self._current_text.split('\n')
            for source_line, line in izip_longest(self.data_sources, lines):
                if source_line:
                    source_line.set_display_string(line or '')

            if self._can_cancel:
                self.data_sources[-1].set_display_string('[  Ok  ]'.rjust(DISPLAY_LENGTH - 1))

    @listens('value')
    def _on_cancel_button_value(self, value):
        if self.is_enabled() and self._can_cancel and value:
            self.notify_cancel()

    @listenable_property
    def text(self):
        return self._current_text

    @text.setter
    def text(self, text):
        if self._current_text != text:
            self._current_text = text
            self._update_display()
            self.notify_text()

    @listenable_property
    def can_cancel(self):
        return self._can_cancel

    @can_cancel.setter
    def can_cancel(self, can_cancel):
        if self._can_cancel != can_cancel:
            self._can_cancel = can_cancel
            self._update_cancel_button()
            self._update_display()
            self.notify_can_cancel()

    def update(self):
        super(MessageBoxComponent, self).update()
        self._update_cancel_button()
        self._update_display()


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

    @listens('open_dialog_count')
    def _on_open_dialog_count(self):
        self._update_dialog(open_dialog_changed=True)
        self._next_message = None

    @listens('cancel')
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