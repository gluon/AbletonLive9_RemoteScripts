#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/elements/display_data_source.py
from __future__ import absolute_import, print_function
from functools import partial

def adjust_string_crop(original, length):
    return original[:length].ljust(length)


def adjust_string(original, length):
    """
    Brings the string to the given length by either removing
    characters or adding spaces. The algorithm is adopted from ede's
    old implementation for the Mackie.
    """
    if not length > 0:
        raise AssertionError
        resulting_string = original
        if len(resulting_string) > length:
            unit_db = resulting_string.endswith('dB') and resulting_string.find('.') != -1
            if len(resulting_string.strip()) > length and unit_db:
                resulting_string = resulting_string[:-2]
            if len(resulting_string) > length:
                for char in (' ', '_', 'i', 'o', 'u', 'e', 'a'):
                    offset = 0 if char == ' ' else 1
                    while len(resulting_string) > length and resulting_string.rfind(char, offset) > 0:
                        char_pos = resulting_string.rfind(char, offset)
                        resulting_string = resulting_string[:char_pos] + resulting_string[char_pos + 1:]

                resulting_string = resulting_string[:length]
        resulting_string = len(resulting_string) < length and resulting_string.ljust(length)
    return resulting_string


class DisplayDataSource(object):
    """
    Data object that is fed with a specific string and notifies a
    observer via its update_callback.
    """
    _separator = ''
    _adjust_string_fn = partial(adjust_string)

    def __init__(self, display_string = '', separator = None, adjust_string_fn = adjust_string, *a, **k):
        super(DisplayDataSource, self).__init__(*a, **k)
        if adjust_string_fn is not None:
            self._adjust_string_fn = partial(adjust_string_fn)
        if separator is not None:
            self._separator = separator
        self._display_string = display_string
        self._update_callback = None
        self._in_update = False

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, separator):
        if separator != self._separator:
            self._separator = separator
            self.update()

    def set_update_callback(self, update_callback):
        if not (not update_callback or callable(update_callback)):
            raise AssertionError
            self._update_callback = update_callback
            update_callback and self.update()

    def set_display_string(self, new_string):
        if self._display_string != new_string:
            self._display_string = new_string
            self.update()

    def clear(self):
        self.set_display_string('')
        self.separator = ''

    def update(self):
        if not not self._in_update:
            raise AssertionError
            self._in_update = True
            self._update_callback != None and self._update_callback()
        self._in_update = False

    def display_string(self):
        return self._display_string

    def adjust_string(self, width):
        return self._adjust_string_fn(self.display_string(), width)