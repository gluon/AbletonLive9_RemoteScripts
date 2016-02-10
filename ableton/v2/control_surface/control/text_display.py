#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/control/text_display.py
from __future__ import absolute_import, print_function
from ..elements import DisplayDataSource
from .control import Control

class TextDisplayControl(Control):

    class State(Control.State):

        def __init__(self, segments = None, *a, **k):
            raise segments is not None or AssertionError
            super(TextDisplayControl.State, self).__init__(*a, **k)
            self._data_sources = [ DisplayDataSource(segment) for segment in segments ]

        def set_control_element(self, control_element):
            super(TextDisplayControl.State, self).set_control_element(control_element)
            if control_element:
                control_element.set_data_sources(self._data_sources)

        def __getitem__(self, index):
            return self._data_sources[index].display_string()

        def __setitem__(self, index, value):
            return self._data_sources[index].set_display_string(value)

    def __init__(self, *a, **k):
        super(TextDisplayControl, self).__init__(extra_args=a, extra_kws=k)