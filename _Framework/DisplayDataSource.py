#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/DisplayDataSource.py


class DisplayDataSource(object):
    """
    Data object that is fed with a specific string and notifies a
    observer via its update_callback.
    """

    def __init__(self, display_string = '', separator = None, *a, **k):
        super(DisplayDataSource, self).__init__(*a, **k)
        self._display_string = display_string
        self._separator = separator
        self._update_callback = None
        self._represented_data_source = None
        self._in_update = False

    def _get_separator(self):
        return self._separator

    def _set_separator(self, separator):
        if separator != self._separator:
            self._separator = separator
            self.update()

    separator = property(_get_separator, _set_separator)

    def set_update_callback(self, update_callback):
        if not (not update_callback or callable(update_callback)):
            raise AssertionError
            self._update_callback = update_callback
            update_callback and self.update()

    def set_display_string(self, new_string):
        if not new_string != None:
            raise AssertionError
            raise isinstance(new_string, str) or isinstance(new_string, unicode) or AssertionError
            self._display_string = self._display_string != new_string and new_string
            self.update()

    def clear(self):
        self.set_display_string('')
        self.separator = None

    def connect_to(self, data_source):
        if self._represented_data_source != None:
            self._represented_data_source.set_update_callback(None)
        self._represented_data_source = data_source
        if self._represented_data_source != None:
            self._represented_data_source.set_update_callback(self.update)
        self.update()

    def disconnect_from(self, data_source):
        raise data_source != None or AssertionError
        raise data_source == self._represented_data_source or AssertionError
        self.connect_to(None)

    def update(self):
        if not not self._in_update:
            raise AssertionError
            self._in_update = True
            self._update_callback != None and self._update_callback()
        self._in_update = False

    def display_string(self):
        return self._display_string if self._represented_data_source == None else self._represented_data_source.display_string()