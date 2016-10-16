#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/drum_pad_parameter_component.py
from __future__ import absolute_import, print_function
from ableton.v2.base import clamp, listenable_property, listens, liveobj_valid, SlotManager
from ableton.v2.control_surface import CompoundComponent
from ableton.v2.control_surface.control import StepEncoderControl
from pushbase.internal_parameter import InternalParameterBase
from pushbase.parameter_provider import generate_info, ParameterProvider
from .device_view_component import DeviceViewConnector
NO_CHOKE_GROUP = u'None'
MAX_CHOKE_GROUP = 16
NUM_CHOKE_GROUPS = MAX_CHOKE_GROUP + 1

class ChokeParameter(SlotManager, InternalParameterBase):
    is_quantized = True
    value_items = [NO_CHOKE_GROUP] + map(unicode, range(1, NUM_CHOKE_GROUPS))
    min = 0
    max = MAX_CHOKE_GROUP

    def __init__(self, drum_pad = None, *a, **k):
        raise liveobj_valid(drum_pad) or AssertionError
        super(ChokeParameter, self).__init__(name='Choke', *a, **k)
        self._pad = drum_pad
        self._on_pad_updated.subject = drum_pad

    @listens('choke_group')
    def _on_pad_updated(self):
        self.notify_value()

    @listenable_property
    def value(self):
        if len(self._pad.chains) > 0:
            return self._pad.choke_group
        return 0

    @value.setter
    def value(self, value):
        value = clamp(value, 0, MAX_CHOKE_GROUP)
        self._pad.choke_group = value

    @property
    def canonical_parent(self):
        return self._pad

    @property
    def display_value(self):
        return unicode(self.value)


def parameters_for_pad(pad):
    if not pad or len(pad.chains) == 0:
        return []
    return [generate_info(ChokeParameter(drum_pad=pad))]


class DrumPadParameterComponent(CompoundComponent, ParameterProvider):
    choke_encoder = StepEncoderControl(num_steps=10)

    def __init__(self, view_model = None, *a, **k):
        raise view_model is not None or AssertionError
        super(DrumPadParameterComponent, self).__init__(*a, **k)
        self._drum_pad = None
        self._parameters = []
        self._view_connector = self.register_component(DeviceViewConnector(parameter_provider=self, view=view_model.deviceParameterView))

    def _get_drum_pad(self):
        return self._drum_pad

    def _set_drum_pad(self, pad):
        if pad != self._drum_pad:
            self._drum_pad = pad
            self._rebuild_parameter_list()
            self._on_chains_in_pad_changed.subject = self._drum_pad

    drum_pad = property(_get_drum_pad, _set_drum_pad)

    @listens('chains')
    def _on_chains_in_pad_changed(self):
        self._rebuild_parameter_list()

    def _rebuild_parameter_list(self):
        for info in self._parameters:
            self.disconnect_disconnectable(info.parameter)

        self._parameters = parameters_for_pad(self._drum_pad)
        for info in self._parameters:
            self.register_disconnectable(info.parameter)

        self._view_connector.update()

    @property
    def parameters(self):
        return self._parameters

    @choke_encoder.value
    def choke_encoder(self, value, encoder):
        if len(self._parameters) > 0:
            self._parameters[0].parameter.value += value