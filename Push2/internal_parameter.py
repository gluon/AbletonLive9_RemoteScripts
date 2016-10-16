#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/internal_parameter.py
from __future__ import absolute_import
from Live import DeviceParameter
from ableton.v2.base import listenable_property, liveobj_valid, nop, Slot, SlotManager, Subject, SlotError

def identity(value, _parent):
    return value


def to_percentage_display(value):
    percentage = 100.0 * value
    percentage_str = '100'
    if percentage < 100.0:
        precision = 2 if percentage < 10.0 else 1
        format_str = '%.' + str(precision) + 'f'
        percentage_str = format_str % percentage
    return unicode(percentage_str + ' %')


class InternalParameterBase(Subject):
    is_enabled = True
    is_quantized = False

    def __init__(self, name = None, *a, **k):
        raise name is not None or AssertionError
        super(InternalParameterBase, self).__init__(*a, **k)
        self._name = name

    def _has_valid_parent(self):
        return liveobj_valid(self._parent)

    @property
    def canonical_parent(self):
        raise NotImplementedError

    @property
    def display_value(self):
        raise NotImplementedError

    @property
    def min(self):
        raise NotImplementedError

    @property
    def max(self):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError

    @property
    def name(self):
        return self._name

    @property
    def original_name(self):
        return self._name

    @property
    def default_value(self):
        return self.min

    @listenable_property
    def automation_state(self):
        return DeviceParameter.AutomationState.none

    @listenable_property
    def state(self):
        return DeviceParameter.ParameterState.enabled

    @property
    def _live_ptr(self):
        return id(self)

    def __str__(self):
        return self.display_value


class InternalParameter(InternalParameterBase):
    """
    Class implementing the DeviceParameter interface. Using instances of this class,
    we can mix script-internal values with DeviceParameter instances.
    """
    __events__ = ('value',)

    def __init__(self, parent = None, display_value_conversion = None, *a, **k):
        super(InternalParameter, self).__init__(*a, **k)
        self._value = 0.0
        self._parent = parent
        self.set_display_value_conversion(display_value_conversion)
        self.set_scaling_functions(None, None)

    def set_display_value_conversion(self, display_value_conversion):
        self._display_value_conversion = display_value_conversion or to_percentage_display
        self.notify_value()

    def set_scaling_functions(self, to_internal, from_internal):
        self._to_internal = to_internal or identity
        self._from_internal = from_internal or identity

    @property
    def canonical_parent(self):
        return self._parent

    def _get_value(self):
        return self._from_internal(self.linear_value, self._parent) if self._has_valid_parent() else self.min

    def _set_value(self, new_value):
        raise self.min <= new_value <= self.max or AssertionError, 'Invalid value %f' % new_value
        self.linear_value = self._to_internal(new_value, self._parent)

    value = property(_get_value, _set_value)

    def _get_linear_value(self):
        return self._value

    def _set_linear_value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self.notify_value()

    linear_value = property(_get_linear_value, _set_linear_value)

    @property
    def min(self):
        return 0.0

    @property
    def max(self):
        return 1.0

    @property
    def display_value(self):
        return self._display_value_conversion(self.value)


class WrappingParameter(InternalParameter, SlotManager):

    def __init__(self, source_property = None, from_property_value = None, to_property_value = None, display_value_conversion = nop, value_items = [], *a, **k):
        raise source_property is not None or AssertionError
        super(WrappingParameter, self).__init__(display_value_conversion=display_value_conversion, *a, **k)
        raise hasattr(self._parent, source_property) or source_property in dir(self._parent) or AssertionError
        self._source_property = source_property
        self._value_items = value_items
        self.set_scaling_functions(to_property_value, from_property_value)
        self._property_slot = self.register_slot(Slot(listener=self.notify_value, event=source_property))
        self.connect()

    def connect(self):
        self._property_slot.subject = None
        self._property_slot.subject = self._parent

    def _get_property_value(self):
        return getattr(self._parent, self._source_property) if self._has_valid_parent() else self.min

    def _get_value(self):
        try:
            return self._from_internal(self._get_property_value(), self._parent) if self._has_valid_parent() else self.min
        except RuntimeError:
            return self.min

    def _set_value(self, new_value):
        raise self.min <= new_value <= self.max or AssertionError, 'Invalid value %f' % new_value
        try:
            setattr(self._parent, self._source_property, self._to_internal(new_value, self._parent))
        except RuntimeError:
            pass

    linear_value = property(_get_value, _set_value)
    value = property(_get_value, _set_value)

    @property
    def display_value(self):
        try:
            value = self._get_property_value()
            return unicode(self._display_value_conversion(value))
        except RuntimeError:
            return unicode()

    @property
    def is_quantized(self):
        return len(self._value_items) > 0

    @property
    def value_items(self):
        return self._value_items


class EnumWrappingParameter(InternalParameterBase, SlotManager):
    is_enabled = True
    is_quantized = True

    def __init__(self, parent = None, values_property = None, index_property = None, value_type = int, to_index_conversion = None, from_index_conversion = None, *a, **k):
        raise parent is not None or AssertionError
        raise values_property is not None or AssertionError
        raise index_property is not None or AssertionError
        super(EnumWrappingParameter, self).__init__(*a, **k)
        self._parent = parent
        self._values_property = values_property
        self._index_property = index_property
        self._to_index = to_index_conversion or (lambda x: x)
        self._from_index = from_index_conversion or (lambda x: x)
        self.value_type = value_type
        self._index_property_slot = self.register_slot(self._parent, self.notify_value, index_property)
        try:
            self.register_slot(self._parent, self.notify_value_items, values_property)
        except SlotError:
            pass

    def connect(self):
        self._index_property_slot.subject = None
        self._index_property_slot.subject = self._parent

    @property
    def display_value(self):
        index = self._get_index()
        values = self._get_values()
        if index < len(values):
            return unicode(values[index])
        else:
            return unicode()

    @listenable_property
    def value_items(self):
        return self._get_values()

    @listenable_property
    def value(self):
        return self._get_index()

    @value.setter
    def value(self, new_value):
        self._set_index(new_value)

    def _get_values(self):
        return getattr(self._parent, self._values_property) if self._has_valid_parent() else []

    def _get_index(self):
        return self._from_index(int(getattr(self._parent, self._index_property)) if self._has_valid_parent() else 0)

    def _set_index(self, index):
        index = self._to_index(index)
        setattr(self._parent, self._index_property, self.value_type(index))

    @property
    def canonical_parent(self):
        self._parent

    @property
    def max(self):
        return len(self.value_items) - 1

    @property
    def min(self):
        return 0


class RelativeInternalParameter(InternalParameter):
    __events__ = ('delta',)

    @property
    def default_value(self):
        return 0.5

    def _get_value(self):
        return self.default_value

    def _set_value(self, new_value):
        delta = new_value - self.value
        if delta != 0.0:
            self.notify_value()
            self.notify_delta(delta)

    value = property(_get_value, _set_value)
    linear_value = property(_get_value, _set_value)