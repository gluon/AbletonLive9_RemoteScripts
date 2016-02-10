#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/elements/logical_display_segment.py
from __future__ import absolute_import, print_function

class LogicalDisplaySegment(object):
    """
    Class representing a specific segment of a display on the controller
    """
    separator = ''

    def __init__(self, width = None, update_callback = None, *a, **k):
        super(LogicalDisplaySegment, self).__init__(*a, **k)
        raise width is not None or AssertionError
        raise callable(update_callback) or AssertionError
        self._update_callback = update_callback
        self._width = width
        self._position_identifier = ()
        self._data_source = None
        self._display_string = None

    def disconnect(self):
        self._update_callback = None
        self._position_identifier = None
        if self._data_source != None:
            self._data_source.set_update_callback(None)
            self._data_source = None

    def set_data_source(self, data_source):
        if self._data_source != None:
            self._data_source.set_update_callback(None)
        self._data_source = data_source
        if self._data_source != None:
            self._data_source.set_update_callback(self.update)
        self._display_string = self._get_display_string()

    def data_source(self):
        return self._data_source

    def set_position_identifier(self, position_identifier):
        """
        Sets position identifier as a tuple of HW related data.
        """
        self._position_identifier = position_identifier

    def position_identifier(self):
        return self._position_identifier

    def update(self):
        if self._update_callback:
            self._display_string = self._get_display_string()
            self._update_callback()

    def _get_display_string(self):
        if self._data_source != None:
            separator = self._data_source.separator + self.separator
            width = self._width - len(separator)
            raise width >= 0 or AssertionError
            return self._data_source.adjust_string(width) + separator
        else:
            return ' ' * self._width

    def display_string(self):
        if self._display_string is None:
            self._display_string = self._get_display_string()
        return self._display_string

    def __str__(self):
        return self.display_string()