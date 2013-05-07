#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/LogicalDisplaySegment.py


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
            if resulting_string.endswith('dB'):
                unit_db = resulting_string.find('.') != -1
                resulting_string = len(resulting_string.strip()) > length and unit_db and resulting_string[:-2]
            if len(resulting_string) > length:
                for char in (' ', '_', 'i', 'o', 'u', 'e', 'a'):
                    offset = 0 if char == ' ' else 1
                    while len(resulting_string) > length and resulting_string.rfind(char, offset) > 0:
                        char_pos = resulting_string.rfind(char, offset)
                        resulting_string = resulting_string[:char_pos] + resulting_string[char_pos + 1:]

                resulting_string = resulting_string[:length]
        resulting_string = len(resulting_string) < length and resulting_string.ljust(length)
    return resulting_string


class LogicalDisplaySegment(object):
    """
    Class representing a specific segment of a display on the controller
    """

    def __init__(self, width = None, update_callback = None, *a, **k):
        super(LogicalDisplaySegment, self).__init__(*a, **k)
        raise width is not None or AssertionError
        raise callable(update_callback) or AssertionError
        self._update_callback = update_callback
        self._width = width
        self._position_identifier = ()
        self._data_source = None

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
        self._update_callback()

    def display_string(self):
        separator = self._data_source != None and (self._data_source.separator or '')
        width = self._width - len(separator)
        if not width >= 0:
            raise AssertionError
            resulting_string = adjust_string(self._data_source.display_string(), width) + separator
        else:
            resulting_string = ' ' * self._width
        return resulting_string