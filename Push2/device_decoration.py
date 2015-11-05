#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/device_decoration.py
from __future__ import absolute_import
from functools import partial
import Live
from ableton.v2.base import clamp, find_if, listens, liveobj_valid, SlotManager, Subject, listenable_property
from ableton.v2.base.collection import IndexedDict
from .decoration import LiveObjectDecorator, DecoratorFactory
from .internal_parameter import EnumWrappingParameter, InternalParameter, RelativeInternalParameter, WrappingParameter, to_percentage_display
from .device_options import DeviceTriggerOption, DeviceSwitchOption, DeviceOnOffOption

def from_sample_count(value, simpler):
    return float(value) / simpler.sample_length


def to_sample_count(value, simpler):
    return clamp(int(value * simpler.sample_length), 0, simpler.sample_length - 1)


def from_user_range(minv, maxv):
    return lambda v, s: (v - minv) / float(maxv - minv)


def to_user_range(minv, maxv):
    return lambda v, s: clamp(v * (maxv - minv) + minv, minv, maxv)


BoolWrappingParameter = partial(WrappingParameter, to_property_value=lambda integer, _simpler: bool(integer), from_property_value=lambda boolean, _simpler: int(boolean), value_items=['off', 'on'], display_value_conversion=lambda val: 'on' if val else 'off')

class EnvelopeType(int):
    pass


EnvelopeType.volume_env = EnvelopeType(0)
EnvelopeType.filter_env = EnvelopeType(1)
EnvelopeType.pitch_env = EnvelopeType(2)

class OscillatorType(int):
    pass


OscillatorType.a = OscillatorType(0)
OscillatorType.b = OscillatorType(1)
OscillatorType.c = OscillatorType(2)
OscillatorType.d = OscillatorType(3)
SimplerWarpModes = IndexedDict(((Live.Clip.WarpMode.beats, 'Beats'),
 (Live.Clip.WarpMode.tones, 'Tones'),
 (Live.Clip.WarpMode.texture, 'Texture'),
 (Live.Clip.WarpMode.repitch, 'Re-Pitch'),
 (Live.Clip.WarpMode.complex, 'Complex'),
 (Live.Clip.WarpMode.complex_pro, 'Pro')))

class NotifyingList(Subject):
    __events__ = ('index',)

    def __init__(self, available_values, default_value = None, *a, **k):
        super(NotifyingList, self).__init__(*a, **k)
        self._index = default_value if default_value is not None else 0
        self._available_values = available_values

    @property
    def available_values(self):
        return self._available_values

    def _get_index(self):
        return self._index

    def _set_index(self, value):
        if value < 0 or value >= len(self.available_values):
            raise IndexError
        self._index = value
        self.notify_index()

    index = property(_get_index, _set_index)


class EnvelopeTypesList(NotifyingList):

    def __init__(self):
        super(EnvelopeTypesList, self).__init__(available_values=['Volume', 'Filter', 'Pitch'], default_value=EnvelopeType.volume_env)


class OscillatorTypesList(NotifyingList):

    def __init__(self):
        super(OscillatorTypesList, self).__init__(available_values=['A',
         'B',
         'C',
         'D'], default_value=OscillatorType.a)


class BandTypesList(NotifyingList):

    def __init__(self):
        super(BandTypesList, self).__init__(available_values=range(1, 9))


class _SimplerDeviceDecorator(Subject, SlotManager, LiveObjectDecorator):
    __events__ = ('slices',)
    waveform_real_time_channel_id = ''
    playhead_real_time_channel_id = ''

    def __init__(self, song = None, envelope_types_provider = None, *a, **k):
        super(_SimplerDeviceDecorator, self).__init__(*a, **k)
        self._song = song
        self._envelope_types_provider = envelope_types_provider if envelope_types_provider is not None else EnvelopeTypesList()
        self.setup_parameters()
        self.setup_options()
        for disconnectable in self.options + self._additional_parameters:
            self.register_disconnectable(disconnectable)

        self.__on_parameters_changed.subject = self._live_object
        self.__on_sample_changed.subject = self._live_object
        self.__on_playback_mode_changed.subject = self._live_object
        self.__on_slices_changed.subject = self._live_object
        self.__on_start_marker_changed.subject = self._live_object
        self.__on_end_marker_changed.subject = self._live_object
        self.__on_signature_numerator_changed.subject = song
        self.__on_can_warp_as_changed.subject = self._live_object
        self.__on_can_warp_half_changed.subject = self._live_object
        self.__on_can_warp_double_changed.subject = self._live_object

    def setup_parameters(self):
        self.zoom = InternalParameter(name='Zoom', parent=self._live_object)
        self.start = WrappingParameter(name='Start', parent=self._live_object, source_property='start_marker', from_property_value=from_sample_count, to_property_value=to_sample_count)
        self.end = WrappingParameter(name='End', parent=self._live_object, source_property='end_marker', from_property_value=from_sample_count, to_property_value=to_sample_count)
        self.sensitivity = WrappingParameter(name='Sensitivity', parent=self._live_object, source_property='slicing_sensitivity', display_value_conversion=to_percentage_display)
        self.mode = EnumWrappingParameter(name='Mode', parent=self, values_property='available_playback_modes', index_property='playback_mode', value_type=Live.SimplerDevice.PlaybackMode)
        self.envelope = EnumWrappingParameter(name='Env. Type', parent=self._envelope_types_provider, values_property='available_values', index_property='index', value_type=EnvelopeType)
        self.warp = BoolWrappingParameter(name='Warp', parent=self._live_object, source_property='warping')
        self.warp_mode_param = EnumWrappingParameter(name='Warp Mode', parent=self, values_property='available_warp_modes', index_property='warp_mode', value_type=Live.Clip.WarpMode, to_index_conversion=lambda i: Live.Clip.WarpMode(SimplerWarpModes.key_by_index(i)), from_index_conversion=lambda i: SimplerWarpModes.index_by_key(i))
        self.nudge = RelativeInternalParameter(name='Nudge', parent=self._live_object)
        self.slicing_playback_mode_param = EnumWrappingParameter(name='Playback', parent=self, values_property='available_slicing_playback_modes', index_property='slicing_playback_mode', value_type=Live.SimplerDevice.SlicingPlaybackMode)
        self.voices_param = EnumWrappingParameter(name='Voices', parent=self, values_property='available_voice_numbers', index_property='voices', to_index_conversion=lambda i: self.available_voice_numbers[i], from_index_conversion=lambda i: self.available_voice_numbers.index(i), value_type=int)
        self.granulation_resolution = EnumWrappingParameter(name='Preserve', parent=self, values_property='available_resolutions', index_property='beats_granulation_resolution', value_type=int)
        self.transient_loop_mode = EnumWrappingParameter(name='Loop Mode', parent=self, values_property='available_transient_loop_modes', index_property='beats_transient_loop_mode', value_type=Live.SimplerDevice.TransientLoopMode)
        self.transient_envelope = WrappingParameter(name='Envelope', parent=self._live_object, source_property='beats_transient_envelope', from_property_value=from_user_range(0.0, 100.0), to_property_value=to_user_range(0.0, 100.0))
        self.tones_grain_size_param = WrappingParameter(name='Grain Size Tones', parent=self._live_object, source_property='tones_grain_size', from_property_value=from_user_range(12.0, 100.0), to_property_value=to_user_range(12.0, 100.0))
        self.texture_grain_size_param = WrappingParameter(name='Grain Size Texture', parent=self._live_object, source_property='texture_grain_size', from_property_value=from_user_range(2.0, 263.0), to_property_value=to_user_range(2.0, 263.0))
        self.flux = WrappingParameter(name='Flux', parent=self._live_object, source_property='texture_flux', from_property_value=from_user_range(0.0, 100.0), to_property_value=to_user_range(0.0, 100.0))
        self.formants = WrappingParameter(name='Formants', parent=self._live_object, source_property='complex_pro_formants', from_property_value=from_user_range(0.0, 100.0), to_property_value=to_user_range(0.0, 100.0))
        self.complex_pro_envelope_param = WrappingParameter(name='Envelope Complex Pro', parent=self._live_object, source_property='complex_pro_envelope', from_property_value=from_user_range(8.0, 256.0), to_property_value=to_user_range(8.0, 256.0))
        self.pad_slicing_param = BoolWrappingParameter(name='Pad Slicing', parent=self._live_object, source_property='pad_slicing')
        self.gain_param = WrappingParameter(name='Gain', parent=self._live_object, source_property='gain', display_value_conversion=lambda _: self._live_object.gain_display_string() if liveobj_valid(self._live_object) else '')
        self._additional_parameters = (self.zoom,
         self.end,
         self.start,
         self.sensitivity,
         self.mode,
         self.envelope,
         self.warp,
         self.warp_mode_param,
         self.nudge,
         self.slicing_playback_mode_param,
         self.voices_param,
         self.granulation_resolution,
         self.transient_loop_mode,
         self.transient_envelope,
         self.tones_grain_size_param,
         self.texture_grain_size_param,
         self.flux,
         self.formants,
         self.complex_pro_envelope_param,
         self.pad_slicing_param,
         self.gain_param)

    def setup_options(self):

        def get_simpler_flag(name):
            return liveobj_valid(self._live_object) and getattr(self._live_object, name)

        def call_simpler_function(name, *a):
            if liveobj_valid(self._live_object):
                return getattr(self._live_object, name)(*a)

        self.crop_option = DeviceTriggerOption(name='Crop', callback=partial(call_simpler_function, 'crop'))
        self.reverse_option = DeviceTriggerOption(name='Reverse', callback=partial(call_simpler_function, 'reverse'))
        self.one_shot_sustain_mode_option = DeviceSwitchOption(name='Trigger Mode', default_label='Trigger', second_label='Gate', parameter=self.get_parameter_by_name('Trigger Mode'))
        self.retrigger_option = DeviceOnOffOption(name='Retrigger', property_host=self._live_object, property_name='retrigger')
        self.warp_as_x_bars_option = DeviceTriggerOption(name='Warp as X Bars', default_label=self.get_warp_as_option_label(), callback=lambda : call_simpler_function('warp_as', call_simpler_function('guess_playback_length')), is_active=lambda : get_simpler_flag('can_warp_as'))
        self.warp_half_option = DeviceTriggerOption(name=':2', callback=partial(call_simpler_function, 'warp_half'), is_active=lambda : get_simpler_flag('can_warp_half'))
        self.warp_double_option = DeviceTriggerOption(name='x2', callback=partial(call_simpler_function, 'warp_double'), is_active=lambda : get_simpler_flag('can_warp_double'))
        self.lfo_sync_option = DeviceSwitchOption(name='LFO Sync Type', default_label='Free', second_label='Sync', parameter=self.get_parameter_by_name('L Sync'))
        self.loop_option = DeviceOnOffOption(name='Loop', property_host=self.get_parameter_by_name('S Loop On'), property_name='value')
        self.filter_slope_option = DeviceSwitchOption(name='Filter Slope', default_label='12dB', second_label='24dB', parameter=self.get_parameter_by_name('Filter Slope'))

    def get_parameter_by_name(self, name):
        return find_if(lambda p: p.name == name, self._live_object.parameters)

    @property
    def available_resolutions(self):
        return ('1 Bar', '1/2', '1/4', '1/8', '1/16', '1/32', 'Transients')

    @property
    def available_transient_loop_modes(self):
        return ('Off', 'Forward', 'Alternate')

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + self._additional_parameters

    @property
    def options(self):
        return (self.crop_option,
         self.reverse_option,
         self.one_shot_sustain_mode_option,
         self.retrigger_option,
         self.warp_as_x_bars_option,
         self.warp_half_option,
         self.warp_double_option,
         self.lfo_sync_option,
         self.loop_option,
         self.filter_slope_option)

    @listenable_property
    def current_playback_mode(self):
        return str(self._live_object.playback_mode)

    @property
    def available_voice_numbers(self):
        return list(Live.SimplerDevice.get_available_voice_numbers())

    @property
    def available_playback_modes(self):
        return ['Classic', 'One-Shot', 'Slicing']

    @property
    def available_warp_modes(self):
        return SimplerWarpModes.values()

    @property
    def available_slicing_playback_modes(self):
        return ['Mono', 'Poly', 'Thru']

    @listens('parameters')
    def __on_parameters_changed(self):
        self.lfo_sync_option.set_parameter(self.get_parameter_by_name('L Sync'))
        self.filter_slope_option.set_parameter(self.get_parameter_by_name('Filter Slope'))

    @listens('sample_file_path')
    def __on_sample_changed(self):
        self.start.connect()
        self.end.connect()
        self.sensitivity.connect()
        self.warp.connect()
        self.warp_mode_param.connect()
        self.granulation_resolution.connect()
        self.transient_loop_mode.connect()
        self.transient_envelope.connect()
        self.tones_grain_size_param.connect()
        self.texture_grain_size_param.connect()
        self.flux.connect()
        self.formants.connect()
        self.complex_pro_envelope_param.connect()
        self.gain_param.connect()
        self._reconnect_to_slices()
        self._reconnect_to_markers()
        self._update_warp_as_label()

    def _reconnect_to_slices(self):
        self.__on_slices_changed.subject = None
        self.__on_slices_changed.subject = self._live_object
        self.notify_slices()

    def _reconnect_to_markers(self):
        self.__on_start_marker_changed.subject = None
        self.__on_start_marker_changed.subject = self._live_object
        self.__on_end_marker_changed.subject = None
        self.__on_end_marker_changed.subject = self._live_object

    @listens('playback_mode')
    def __on_playback_mode_changed(self):
        self.notify_current_playback_mode()

    @listens('slices')
    def __on_slices_changed(self):
        self.notify_slices()

    def _update_warp_as_label(self):
        self.warp_as_x_bars_option.default_label = self.get_warp_as_option_label()

    @listens('start_marker')
    def __on_start_marker_changed(self):
        self._update_warp_as_label()

    @listens('end_marker')
    def __on_end_marker_changed(self):
        self._update_warp_as_label()

    @listens('signature_numerator')
    def __on_signature_numerator_changed(self):
        self._update_warp_as_label()

    @listens('can_warp_as')
    def __on_can_warp_as_changed(self):
        self.warp_as_x_bars_option.notify_active()

    @listens('can_warp_half')
    def __on_can_warp_half_changed(self):
        self.warp_half_option.notify_active()

    @listens('can_warp_double')
    def __on_can_warp_double_changed(self):
        self.warp_double_option.notify_active()

    def get_warp_as_option_label(self):
        try:
            bars = int(self._live_object.guess_playback_length() / self._song.signature_numerator)
            return 'Warp as %d Bar%s' % (bars, 's' if bars > 1 else '')
        except RuntimeError:
            return 'Warp as X Bars'


class _OperatorDeviceDecorator(LiveObjectDecorator):

    def __init__(self, song = None, osc_types_provider = None, *a, **k):
        super(_OperatorDeviceDecorator, self).__init__(*a, **k)
        self._osc_types_provider = osc_types_provider if osc_types_provider is not None else OscillatorTypesList()
        self.oscillator = EnumWrappingParameter(name='Oscillator', parent=self._osc_types_provider, values_property='available_values', index_property='index', value_type=OscillatorType)

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + (self.oscillator,)


class _Eq8DeviceDecorator(LiveObjectDecorator):

    def __init__(self, song = None, band_types_provider = None, *a, **k):
        super(_Eq8DeviceDecorator, self).__init__(*a, **k)
        self._band_types_provider = band_types_provider if band_types_provider is not None else BandTypesList()
        self.band = EnumWrappingParameter(name='Band', parent=self._band_types_provider, values_property='available_values', index_property='index')

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + (self.band,)


class DeviceDecoratorFactory(DecoratorFactory):
    DECORATOR_CLASSES = {'OriginalSimpler': _SimplerDeviceDecorator,
     'Operator': _OperatorDeviceDecorator,
     'Eq8': _Eq8DeviceDecorator}

    @classmethod
    def generate_decorated_device(cls, device, additional_properties = {}, song = None, *a, **k):
        decorated = cls.DECORATOR_CLASSES[device.class_name](live_object=device, additional_properties=additional_properties, song=song, *a, **k)
        return decorated

    @classmethod
    def _should_be_decorated(cls, device):
        return liveobj_valid(device) and device.class_name in cls.DECORATOR_CLASSES

    def _get_decorated_object(self, device, additional_properties, *a, **k):
        return self.generate_decorated_device(device, additional_properties=additional_properties, *a, **k)


class SimplerDecoratedPropertiesCopier(object):
    ADDITIONAL_PROPERTIES = ['playhead_real_time_channel_id', 'waveform_real_time_channel_id']

    def __init__(self, decorated_object = None, factory = None, *a, **k):
        raise liveobj_valid(decorated_object) or AssertionError
        raise factory is not None or AssertionError
        raise decorated_object in factory.decorated_objects or AssertionError
        super(SimplerDecoratedPropertiesCopier, self).__init__(*a, **k)
        self._decorated_object = decorated_object
        self._factory = factory
        self._copied_additional_properties = {}
        self._nested_properties = {}
        self.copy_properties({'zoom': lambda s: s.zoom.linear_value,
         self.ADDITIONAL_PROPERTIES[0]: None,
         self.ADDITIONAL_PROPERTIES[1]: None})

    def copy_properties(self, properties):
        for prop, getter in properties.iteritems():
            if getter:
                self._nested_properties[prop] = getter(self._decorated_object)
            else:
                self._copied_additional_properties[prop] = getattr(self._decorated_object, prop)

    def apply_properties(self, new_object, song):
        decorated = self._factory.decorate(new_object, additional_properties=self._copied_additional_properties, song=song)
        self._apply_nested_properties(decorated)
        return decorated

    def _apply_nested_properties(self, decorated_object):
        if 'zoom' in self._nested_properties:
            decorated_object.zoom.linear_value = self._nested_properties['zoom']