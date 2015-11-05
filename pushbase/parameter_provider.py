#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/pushbase/parameter_provider.py
from __future__ import absolute_import
from ableton.v2.base import liveobj_valid, NamedTuple, Subject
from . import consts
DISCRETE_PARAMETERS_DICT = {'GlueCompressor': ('Ratio', 'Attack', 'Release', 'Peak Clip In')}

def is_parameter_quantized(parameter, parent_device):
    is_quantized = False
    if liveobj_valid(parameter):
        device_class = getattr(parent_device, 'class_name', None)
        is_quantized = parameter.is_quantized or device_class in DISCRETE_PARAMETERS_DICT and parameter.name in DISCRETE_PARAMETERS_DICT[device_class]
    return is_quantized


def parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    return consts.QUANTIZED_MAPPING_SENSITIVITY if is_quantized else consts.CONTINUOUS_MAPPING_SENSITIVITY


def fine_grain_parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    return consts.QUANTIZED_MAPPING_SENSITIVITY if is_quantized else consts.FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY


class ParameterInfo(NamedTuple):
    parameter = None
    name = None
    default_encoder_sensitivity = consts.CONTINUOUS_MAPPING_SENSITIVITY
    fine_grain_encoder_sensitivity = consts.FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY


def generate_info(parameter, name = None, default_sens_factory = parameter_mapping_sensitivity, fine_sens_factory = fine_grain_parameter_mapping_sensitivity):
    if name is None:
        name = parameter.name if parameter else ''
    return ParameterInfo(name=name, parameter=parameter, default_encoder_sensitivity=default_sens_factory(parameter), fine_grain_encoder_sensitivity=fine_sens_factory(parameter))


class ParameterProvider(Subject):
    __events__ = ('parameters',)

    @property
    def parameters(self):
        return []