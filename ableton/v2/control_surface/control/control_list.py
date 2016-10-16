#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/control/control_list.py
from __future__ import absolute_import, print_function
from functools import partial
from itertools import izip_longest
from ...base import clamp, first, second, mixin, product, flatten, is_matrix, find_if
from .control import Connectable, Control
from .radio_button import RadioButtonControl
_DYNAMIC_CONTROL_COUNT = None

class ControlList(Control):
    DYNAMIC_CONTROL_COUNT = _DYNAMIC_CONTROL_COUNT

    class State(Control.State):

        def __init__(self, control = None, manager = None, unavailable_color = None, extra_args = None, extra_kws = None, *a, **k):
            raise control is not None or AssertionError
            super(ControlList.State, self).__init__(manager=manager, control=control)
            self._control_elements = None
            self._control_type = control.control_type
            self._controls = []
            self._dynamic_create = False
            self._unavailable_color = unavailable_color if unavailable_color is not None else 'DefaultButton.Disabled'
            self._extra_args = a
            self._extra_kws = k
            self.control_count = control.control_count

        @property
        def control_count(self):
            return len(self._controls)

        @control_count.setter
        def control_count(self, count):
            dynamic_create = count == ControlList.DYNAMIC_CONTROL_COUNT
            if len(self._controls) != count and not dynamic_create or self._dynamic_create != dynamic_create:
                self._dynamic_create = count == ControlList.DYNAMIC_CONTROL_COUNT
                if self._dynamic_create:
                    count = len(self._control_elements) if self._control_elements else 0
                self._create_controls(count)
                self._update_controls()

        @property
        def unavailable_color(self):
            return self._unavailable_color

        @unavailable_color.setter
        def unavailable_color(self, value):
            self._unavailable_color = value
            control_elements = self._control_elements or []
            for control, element in izip_longest(self._controls, control_elements):
                if not control and element:
                    self._send_unavailable_color(element)

        def _create_controls(self, count):
            if count > len(self._controls):
                self._controls.extend([ self._make_control(i) for i in xrange(len(self._controls), count) ])
            elif count < len(self._controls):
                self._disconnect_controls(self._controls[count:])
                self._controls = self._controls[:count]

        def _disconnect_controls(self, controls):
            for control in controls:
                control._get_state(self._manager).disconnect()
                control._clear_state(self._manager)

        def _make_control(self, index):
            control = self._control_type(*self._extra_args, **self._extra_kws)
            control._event_listeners = self._event_listeners
            control_state = control._get_state(self._manager)
            if not hasattr(control_state, 'index'):
                control_state.index = index
            else:
                raise RuntimeError("Cannot set 'index' attribute. Attribute already set.")
            return control

        def set_control_element(self, control_elements):
            self._control_elements = control_elements
            if self._dynamic_create and len(control_elements or []) != len(self._control_element or []):
                self._create_controls(len(control_elements or []))
            self._update_controls()

        def _update_controls(self):
            control_elements = self._control_elements or []
            for control, element in izip_longest(self._controls, control_elements):
                if control:
                    control._get_state(self._manager).set_control_element(element)
                elif element:
                    element.reset_state()
                    self._send_unavailable_color(element)

        def _send_unavailable_color(self, element):
            if hasattr(element, 'set_light'):
                element.set_light(self._unavailable_color)

        def __getitem__(self, index):
            return self._controls[index]._get_state(self._manager)

        def _on_value(self, value, *a, **k):
            pass

        def _register_value_slot(self, manager, control):
            pass

    def __init__(self, control_type = None, control_count = _DYNAMIC_CONTROL_COUNT, *a, **k):
        super(ControlList, self).__init__(extra_args=a, extra_kws=k, *a, **k)
        self.control_type = control_type
        self.control_count = control_count


class RadioButtonGroup(ControlList, RadioButtonControl):

    class State(ControlList.State, Connectable):
        requires_listenable_connected_property = True

        def __init__(self, *a, **k):
            self._checked_index = -1
            super(RadioButtonGroup.State, self).__init__(*a, **k)

        @property
        def checked_index(self):
            return self._checked_index

        @checked_index.setter
        def checked_index(self, index):
            if not -1 <= index < self.control_count:
                raise AssertionError
                self[index].is_checked = index != -1 and True
            else:
                checked_control = find_if(lambda c: c.is_checked, self)
                if checked_control is not None:
                    checked_control.is_checked = False

        def connect_property(self, *a):
            super(RadioButtonGroup.State, self).connect_property(*a)
            self.checked_index = self.connected_property_value

        def on_connected_property_changed(self, value):
            self.checked_index = value

        def _create_controls(self, count):
            super(RadioButtonGroup.State, self)._create_controls(count)
            self.checked_index = clamp(self._checked_index, -1, count - 1)

        def _make_control(self, index):
            control = super(RadioButtonGroup.State, self)._make_control(index)
            control_state = control._get_state(self._manager)
            control_state._on_checked = partial(self._on_checked, control_state)
            control_state.is_checked = index == self._checked_index
            return control

        def _on_checked(self, checked_control):
            for control in self._controls:
                control = control._get_state(self._manager)
                control.is_checked = control == checked_control

            self._checked_index = checked_control.index
            self.connected_property_value = self._checked_index

    def __init__(self, *a, **k):
        super(RadioButtonGroup, self).__init__(RadioButtonControl, *a, **k)


_DYNAMIC_MATRIX_DIMENSIONS = (None, None)

class MatrixControl(ControlList):
    DYNAMIC_DIMENSIONS = _DYNAMIC_MATRIX_DIMENSIONS

    class State(ControlList.State):

        def __init__(self, control = None, manager = None, *a, **k):
            raise control is not None or AssertionError
            raise manager is not None or AssertionError
            self._dimensions = (None, None)
            super(MatrixControl.State, self).__init__(control, manager, *a, **k)

        @property
        def dimensions(self):
            return self._dimensions

        @dimensions.setter
        def dimensions(self, dimensions):
            if not first(dimensions):
                raise AssertionError
                raise second(dimensions) or AssertionError
                self._dynamic_create = dimensions == MatrixControl.DYNAMIC_DIMENSIONS
                count = self._dynamic_create and (len(self._control_elements) if self._control_elements else 0)
            self._dimensions = dimensions
            count = first(dimensions) * second(dimensions)
            self._create_controls(count)
            self._update_controls()

        def _create_controls(self, count):
            super(MatrixControl.State, self)._create_controls(count)
            self._update_coordinates()

        def _make_control(self, index):
            control = super(MatrixControl.State, self)._make_control(index)
            if hasattr(control._get_state(self._manager), 'coordinate'):
                raise RuntimeError("Cannot set 'coordinate' attribute. Attribute already set.")
            return control

        def _update_coordinates(self):
            for index, control in enumerate(self._controls):
                control_state = control._get_state(self._manager)
                control_state.coordinate = (int(index / self.width), index % self.width)

        def set_control_element(self, control_elements):
            dimensions = (None, None)
            if hasattr(control_elements, 'width') and hasattr(control_elements, 'height'):
                dimensions = (control_elements.height(), control_elements.width())
                if not self._dynamic_create:
                    control_elements = [ control_elements.get_button(col, row) for row, col in product(xrange(self.height), xrange(self.width)) ]
            elif is_matrix(control_elements):
                dimensions = (len(control_elements), len(first(control_elements)))
                if not self._dynamic_create:
                    control_elements = [ row[0:self.width] for row in control_elements ]
                control_elements = list(flatten(control_elements))
            elif control_elements is not None:
                raise RuntimeError('Control Elements must be a matrix')
            if self._dynamic_create and None not in dimensions:
                self._dimensions = dimensions
                self._create_controls(first(dimensions) * second(dimensions))
                self._update_controls()
            super(MatrixControl.State, self).set_control_element(control_elements)

        def get_control(self, row, column):
            index = row * self.width + column
            return self._controls[index]._get_state(self._manager)

        @property
        def width(self):
            return second(self._dimensions)

        @property
        def height(self):
            return first(self._dimensions)

    def __init__(self, *a, **k):
        super(MatrixControl, self).__init__(*a, **k)


_control_list_classes = dict()
_control_matrix_classes = dict()

def control_list(control_type, *a, **k):
    if control_type == RadioButtonControl:
        return RadioButtonGroup(*a, **k)
    c = _control_list_classes.get(control_type, None)
    if not c:
        c = mixin(ControlList, control_type)
        _control_list_classes[control_type] = c
    return c(control_type, *a, **k)


def control_matrix(control_type, *a, **k):
    m = _control_matrix_classes.get(control_type, None)
    if not m:
        m = mixin(MatrixControl, control_type)
        _control_matrix_classes[control_type] = m
    return m(control_type, *a, **k)