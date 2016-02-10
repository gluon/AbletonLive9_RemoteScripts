#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/device_options.py
from __future__ import absolute_import, print_function
from ableton.v2.base import liveobj_valid, listenable_property, listens, const, Subject, Slot, SlotManager

class DeviceTriggerOption(Subject):
    __events__ = ('default_label',)

    def __init__(self, name = None, default_label = None, callback = None, is_active = None):
        raise callback or AssertionError
        self.trigger = callback
        self._name = name or 'Option'
        self._default_label = default_label or self._name
        self._is_active_callback = is_active or const(True)

    @property
    def name(self):
        return self._name

    @listenable_property
    def active(self):
        return self._is_active()

    def _is_active(self):
        return self._is_active_callback()

    def _get_default_label(self):
        return self._default_label

    def _set_default_label(self, label):
        self._default_label = label
        self.notify_default_label()

    default_label = property(_get_default_label, _set_default_label)


class DeviceSwitchOption(SlotManager, DeviceTriggerOption):

    def __init__(self, second_label = None, parameter = None, *a, **k):
        super(DeviceSwitchOption, self).__init__(callback=self.cycle_index, *a, **k)
        self._second_label = second_label or ''
        self.set_parameter(parameter)

    def set_parameter(self, parameter):
        self._parameter = parameter
        self.__on_value_changed.subject = parameter
        self.notify_active_index()
        self.notify_active()

    def _is_active(self):
        return super(DeviceSwitchOption, self)._is_active() and liveobj_valid(self._parameter)

    @listenable_property
    def active_index(self):
        if liveobj_valid(self._parameter):
            return int(bool(self._parameter.value))
        return 0

    @listens('value')
    def __on_value_changed(self):
        self.notify_active_index()

    @property
    def second_label(self):
        return self._second_label

    def cycle_index(self):
        if liveobj_valid(self._parameter):
            self._parameter.value = float((self.active_index + 1.0) % 2)


class DeviceOnOffOption(SlotManager, DeviceTriggerOption):
    ON_LABEL = 'ON'
    OFF_LABEL = 'OFF'

    def __init__(self, name = None, property_host = None, property_name = '', *a, **k):
        super(DeviceOnOffOption, self).__init__(callback=self.cycle_index, name=name, *a, **k)
        self._property_host = property_host
        self._property_name = property_name

        def notify_index_and_default_label():
            self.notify_active_index()
            self.notify_default_label()

        self._property_slot = self.register_slot(Slot(subject=property_host, event=property_name, listener=notify_index_and_default_label))

    def _property_value(self):
        if liveobj_valid(self._property_host):
            return getattr(self._property_host, self._property_name, False)
        return False

    def _is_active(self):
        return super(DeviceOnOffOption, self)._is_active() and liveobj_valid(self._property_host)

    @listenable_property
    def active_index(self):
        return int(not self._property_value())

    def cycle_index(self):
        if liveobj_valid(self._property_host):
            value_type = type(self._property_value())
            new_value = not bool((self.active_index + 1) % 2)
            setattr(self._property_host, self._property_name, value_type(new_value))

    @property
    def default_label(self):
        return '%s %s' % (self._default_label, self.ON_LABEL if self._property_value() else self.OFF_LABEL)