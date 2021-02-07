# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/mapped_control.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from ableton.v2.base import clamp, listens, liveobj_valid
from ableton.v2.control_surface.control import MappedControl as MappedControlBase
from ableton.v2.control_surface.control.encoder import ValueStepper
from pushbase.internal_parameter import InternalParameterBase

def is_internal_parameter(parameter):
    return isinstance(parameter, InternalParameterBase)


def is_zoom_parameter(parameter):
    """ Returns true for parameters, that provide a zoom method, i.e. Push 2's
        waveform zooming parameter.
    """
    return hasattr(parameter, 'zoom')


class MappedControl(MappedControlBase):

    class State(MappedControlBase.State):
        default_sensitivity = 1.0
        fine_sensitivity = 0.1

        def __init__(self, *a, **k):
            super(MappedControl.State, self).__init__(*a, **k)
            self._quantized_stepper = ValueStepper()

        def update_sensitivities(self, default, fine):
            self.default_sensitivity = default
            self.fine_sensitivity = fine
            if self._control_element:
                self._update_control_sensitivity()

        def _update_direct_connection(self):
            if self._control_element is None or is_internal_parameter(self.mapped_parameter):
                if self._control_element:
                    self._control_element.release_parameter()
                self._control_value.subject = self._control_element
            else:
                self._control_value.subject = None
                self._update_control_element()
            self._quantized_stepper.reset()
            return

        def _update_control_element(self):
            if liveobj_valid(self.mapped_parameter):
                self._control_element.connect_to(self.mapped_parameter)
            else:
                self._control_element.release_parameter()
            self._update_control_sensitivity()
            self._quantized_stepper.reset()

        def _update_control_sensitivity(self):
            if hasattr(self._control_element, 'set_sensitivities'):
                self._control_element.set_sensitivities(self.default_sensitivity, self.fine_sensitivity)
            else:
                self._control_element.mapping_sensitivity = self.default_sensitivity

        @listens('normalized_value')
        def _control_value(self, value):
            if is_zoom_parameter(self.mapped_parameter):
                self.mapped_parameter.zoom(value * self._control_element.mapping_sensitivity)
            if self.mapped_parameter.is_quantized:
                steps = self._quantized_stepper.advance(value)
                if steps != 0:
                    self.mapped_parameter.value = self._clamp_value_to_parameter_range(self.mapped_parameter.value + steps)
            else:
                value_offset = value * self._control_element.mapping_sensitivity
                self.mapped_parameter.linear_value = self._clamp_value_to_parameter_range(self.mapped_parameter.linear_value + value_offset)

        def _clamp_value_to_parameter_range(self, value):
            return clamp(value, self.mapped_parameter.min, self.mapped_parameter.max)