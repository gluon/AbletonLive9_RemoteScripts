# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/setting.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from math import fabs
from ableton.v2.base import sign, clamp, EventObject, Event

class Setting(EventObject):
    """
    Setting interface for writing to the preferences and all
    information for changing and displaying it.
    """
    __events__ = (
     Event(name='value', doc=' Called when the value of the setting changes '),)

    def __init__(self, name='', values=None, default_value=None, preferences=None, *a, **k):
        super(Setting, self).__init__(*a, **k)
        self.name = name
        self.values = values or []
        self._preferences = preferences if preferences != None else {}
        if name in self._preferences and self._preferences[name] in values:
            default_value = self._preferences[name]
        self._preferences[name] = None
        self.value = default_value
        return

    def __str__(self):
        return self.value_to_string(self.value)

    def _set_value(self, value):
        assert value in self.values
        if self._preferences[self.name] != value:
            self._preferences[self.name] = value
            self.on_value_changed(value)
            self.notify_value(self.value)

    def _get_value(self):
        return self._preferences[self.name]

    value = property(_get_value, _set_value)

    def on_value_changed(self, value):
        pass

    def change_relative(self, value):
        """ Given a value between -1.0 and 1.0, this will decide on a new value. """
        raise NotImplementedError

    def value_to_string(self, value):
        raise NotImplementedError


class OnOffSetting(Setting):
    """ Simple on/off setting represented by a boolean value """
    THRESHOLD = 0.01

    def __init__(self, value_labels=[
 'On', 'Off'], *a, **k):
        super(OnOffSetting, self).__init__(values=[True, False], *a, **k)
        self._value_labels = value_labels

    def change_relative(self, value):
        if fabs(value) >= self.THRESHOLD:
            self.value = value > 0.0
            return True

    def value_to_string(self, value):
        return self._value_labels[int(not self.value)]


class EnumerableSetting(Setting):
    """ Setting to go through a list of values """
    STEP_SIZE = 0.1

    def __init__(self, value_formatter=str, *a, **k):
        super(EnumerableSetting, self).__init__(*a, **k)
        self._relative_value = 0.0
        self._value_formatter = value_formatter

    def change_relative(self, value):
        if sign(value) != sign(self._relative_value):
            self._relative_value = 0.0
        self._relative_value += value
        if fabs(self._relative_value) >= self.STEP_SIZE:
            relative_position = int(sign(self._relative_value))
            self._relative_value -= self.STEP_SIZE
            return self._jump_relative(relative_position) != None
        else:
            return None

    def _jump_relative(self, relative_position):
        current_position = self.values.index(self.value)
        new_position = clamp(current_position + relative_position, 0, len(self.values) - 1)
        self.value = self.values[new_position]
        if current_position != new_position:
            return new_position
        else:
            return None

    def on_value_changed(self, value):
        self._relative_value = 0.0

    def value_to_string(self, value):
        return self._value_formatter(value)