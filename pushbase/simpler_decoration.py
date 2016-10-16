#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/simpler_decoration.py
from __future__ import absolute_import, print_function
from functools import partial
import Live
from ableton.v2.base import clamp, liveobj_valid, listenable_property, listens, SlotManager, Subject
from ableton.v2.base.collection import IndexedDict
from .decoration import DecoratorFactory, LiveObjectDecorator
from .internal_parameter import EnumWrappingParameter, RelativeInternalParameter, to_percentage_display, WrappingParameter
BoolWrappingParameter = partial(WrappingParameter, to_property_value=lambda integer, _simpler: bool(integer), from_property_value=lambda boolean, _simpler: int(boolean), value_items=['off', 'on'], display_value_conversion=lambda val: ('on' if val else 'off'))

def from_user_range(minv, maxv):
    return lambda v, s: (v - minv) / float(maxv - minv)


def to_user_range(minv, maxv):
    return lambda v, s: clamp(v * (maxv - minv) + minv, minv, maxv)


def from_sample_count(value, sample):
    return float(value) / sample.length


def to_sample_count(value, sample):
    return clamp(int(value * sample.length), 0, sample.length - 1)


SimplerWarpModes = IndexedDict(((Live.Clip.WarpMode.beats, 'Beats'),
 (Live.Clip.WarpMode.tones, 'Tones'),
 (Live.Clip.WarpMode.texture, 'Texture'),
 (Live.Clip.WarpMode.repitch, 'Re-Pitch'),
 (Live.Clip.WarpMode.complex, 'Complex'),
 (Live.Clip.WarpMode.complex_pro, 'Pro')))

class SimplerDeviceDecorator(Subject, SlotManager, LiveObjectDecorator):

    def __init__(self, *a, **k):
        super(SimplerDeviceDecorator, self).__init__(*a, **k)
        self._sample_based_parameters = []
        self._additional_parameters = []
        self.setup_parameters()
        self.register_disconnectables(self._decorated_parameters())
        self.__on_playback_mode_changed.subject = self._live_object
        self.__on_sample_changed.subject = self._live_object
        self.__on_slices_changed.subject = self._live_object.sample

    def setup_parameters(self):
        self.start = WrappingParameter(name='Start', parent=self, property_host=self._live_object.sample, source_property='start_marker', from_property_value=from_sample_count, to_property_value=to_sample_count)
        self.end = WrappingParameter(name='End', parent=self, property_host=self._live_object.sample, source_property='end_marker', from_property_value=from_sample_count, to_property_value=to_sample_count)
        self.sensitivity = WrappingParameter(name='Sensitivity', parent=self, property_host=self._live_object.sample, source_property='slicing_sensitivity', display_value_conversion=to_percentage_display)
        self.mode = EnumWrappingParameter(name='Mode', parent=self, values_property_host=self, index_property_host=self, values_property='available_playback_modes', index_property='playback_mode')
        self.slicing_playback_mode_param = EnumWrappingParameter(name='Playback', parent=self, values_property_host=self, index_property_host=self, values_property='available_slicing_playback_modes', index_property='slicing_playback_mode')
        self.pad_slicing_param = BoolWrappingParameter(name='Pad Slicing', parent=self, property_host=self._live_object, source_property='pad_slicing')
        self.nudge = RelativeInternalParameter(name='Nudge', parent=self)
        self.multi_sample_mode_param = BoolWrappingParameter(name='Multi Sample', parent=self, property_host=self._live_object, source_property='multi_sample_mode')
        self.warp = BoolWrappingParameter(name='Warp', parent=self, property_host=self._live_object.sample, source_property='warping')
        self.warp_mode_param = EnumWrappingParameter(name='Warp Mode', parent=self, values_property_host=self, index_property_host=self._live_object.sample, values_property='available_warp_modes', index_property='warp_mode', to_index_conversion=lambda i: Live.Clip.WarpMode(SimplerWarpModes.key_by_index(i)), from_index_conversion=lambda i: SimplerWarpModes.index_by_key(i))
        self.voices_param = EnumWrappingParameter(name='Voices', parent=self, values_property_host=self, index_property_host=self, values_property='available_voice_numbers', index_property='voices', to_index_conversion=lambda i: self.available_voice_numbers[i], from_index_conversion=lambda i: self.available_voice_numbers.index(i))
        self.granulation_resolution = EnumWrappingParameter(name='Preserve', parent=self, values_property_host=self, index_property_host=self._live_object.sample, values_property='available_resolutions', index_property='beats_granulation_resolution')
        self.transient_loop_mode = EnumWrappingParameter(name='Loop Mode', parent=self, values_property_host=self, index_property_host=self._live_object.sample, values_property='available_transient_loop_modes', index_property='beats_transient_loop_mode')
        self.transient_envelope = WrappingParameter(name='Envelope', parent=self, property_host=self._live_object.sample, source_property='beats_transient_envelope', from_property_value=from_user_range(0.0, 100.0), to_property_value=to_user_range(0.0, 100.0))
        self.tones_grain_size_param = WrappingParameter(name='Grain Size Tones', parent=self, property_host=self._live_object.sample, source_property='tones_grain_size', from_property_value=from_user_range(12.0, 100.0), to_property_value=to_user_range(12.0, 100.0))
        self.texture_grain_size_param = WrappingParameter(name='Grain Size Texture', parent=self, property_host=self._live_object.sample, source_property='texture_grain_size', from_property_value=from_user_range(2.0, 263.0), to_property_value=to_user_range(2.0, 263.0))
        self.flux = WrappingParameter(name='Flux', parent=self, property_host=self._live_object.sample, source_property='texture_flux', from_property_value=from_user_range(0.0, 100.0), to_property_value=to_user_range(0.0, 100.0))
        self.formants = WrappingParameter(name='Formants', parent=self, property_host=self._live_object.sample, source_property='complex_pro_formants', from_property_value=from_user_range(0.0, 100.0), to_property_value=to_user_range(0.0, 100.0))
        self.complex_pro_envelope_param = WrappingParameter(name='Envelope Complex Pro', parent=self, property_host=self._live_object.sample, source_property='complex_pro_envelope', from_property_value=from_user_range(8.0, 256.0), to_property_value=to_user_range(8.0, 256.0))
        self.gain_param = WrappingParameter(name='Gain', parent=self, property_host=self._live_object.sample, source_property='gain', display_value_conversion=lambda _: (self._live_object.sample.gain_display_string() if liveobj_valid(self._live_object) and liveobj_valid(self._live_object.sample) else ''))
        self._sample_based_parameters.extend([self.start,
         self.end,
         self.sensitivity,
         self.warp,
         self.transient_envelope,
         self.tones_grain_size_param,
         self.texture_grain_size_param,
         self.flux,
         self.formants,
         self.complex_pro_envelope_param,
         self.gain_param])
        self._additional_parameters.extend([self.mode,
         self.slicing_playback_mode_param,
         self.pad_slicing_param,
         self.nudge,
         self.multi_sample_mode_param,
         self.warp_mode_param,
         self.voices_param,
         self.granulation_resolution,
         self.transient_loop_mode])

    def _decorated_parameters(self):
        return tuple(self._sample_based_parameters) + tuple(self._additional_parameters)

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + self._decorated_parameters()

    @property
    def available_playback_modes(self):
        return ['Classic', 'One-Shot', 'Slicing']

    @property
    def available_slicing_playback_modes(self):
        return ['Mono', 'Poly', 'Thru']

    @property
    def available_voice_numbers(self):
        return list(Live.SimplerDevice.get_available_voice_numbers())

    @property
    def available_warp_modes(self):
        return SimplerWarpModes.values()

    @property
    def available_resolutions(self):
        return (u'1 Bar', u'1/2', u'1/4', u'1/8', u'1/16', u'1/32', u'Transients')

    @property
    def available_transient_loop_modes(self):
        return ('Off', 'Forward', 'Alternate')

    @listenable_property
    def current_playback_mode(self):
        return self._live_object.playback_mode

    @listenable_property
    def slices(self):
        if liveobj_valid(self._live_object) and liveobj_valid(self._live_object.sample):
            return self._live_object.sample.slices
        return []

    @listens('sample')
    def __on_sample_changed(self):
        self._reconnect_sample_listeners()

    def _reconnect_sample_listeners(self):
        for param in self._sample_based_parameters:
            param.set_property_host(self._live_object.sample)

        for param in (self.warp_mode_param, self.granulation_resolution, self.transient_loop_mode):
            param.set_index_property_host(self._live_object.sample)

        self._reconnect_to_slices()

    def _reconnect_to_slices(self):
        self.__on_slices_changed.subject = self._live_object.sample
        self.notify_slices()

    @listens('slices')
    def __on_slices_changed(self):
        self.notify_slices()

    @listens('playback_mode')
    def __on_playback_mode_changed(self):
        self.notify_current_playback_mode()


class SimplerDecoratorFactory(DecoratorFactory):
    _decorator = SimplerDeviceDecorator

    @classmethod
    def _should_be_decorated(cls, device):
        return liveobj_valid(device) and device.class_name == 'OriginalSimpler'