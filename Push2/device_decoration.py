#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/device_decoration.py
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.base import depends, find_if, listenable_property, listens, liveobj_valid, SlotManager, Subject
from pushbase.decoration import LiveObjectDecorator, DecoratorFactory
from pushbase.internal_parameter import EnumWrappingParameter, InternalParameter
from pushbase.simpler_decoration import SimplerDeviceDecorator as SimplerDeviceDecoratorBase
from .device_options import DeviceTriggerOption, DeviceSwitchOption, DeviceOnOffOption
from .waveform_navigation import SimplerWaveformNavigation

def get_parameter_by_name(decorator, name):
    return find_if(lambda p: p.name == name, decorator._live_object.parameters)


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


class WaveformNavigationParameter(SlotManager, InternalParameter):
    """ Class for connecting a Simpler with a WaveformNavigation. It will create a new
        instance of WaveformNavigation for every sample. It also still acts as a
        parameter, for the current zooming implemenation.
    
        It also provides the "zoom" method interface, so it works with the
        pushbase.mapped_control.MappedControl class.
    """

    def __init__(self, simpler = None, *a, **k):
        super(WaveformNavigationParameter, self).__init__(*a, **k)
        self._simpler = simpler
        self._waveform_navigation = None
        self.__on_sample_changed.subject = simpler
        self.__on_sample_changed()

    @listenable_property
    def waveform_navigation(self):
        return self._waveform_navigation

    def zoom(self, value):
        if self._waveform_navigation:
            self._waveform_navigation.zoom(value)

    def touch_object(self, parameter):
        if self._waveform_navigation:
            self._waveform_navigation.touch_object(parameter)

    def release_object(self, parameter):
        if self._waveform_navigation:
            self._waveform_navigation.release_object(parameter)

    def change_object(self, parameter):
        if self._waveform_navigation:
            self._waveform_navigation.change_object(parameter)

    def focus_object(self, parameter):
        if self._waveform_navigation:
            self._waveform_navigation.focus_object(parameter)

    def reset_focus_and_animation(self):
        if self._waveform_navigation:
            self._waveform_navigation.reset_focus_and_animation()

    @listens('sample')
    def __on_sample_changed(self):
        sample = self._simpler.sample
        if self._waveform_navigation is not None:
            self.unregister_disconnectable(self._waveform_navigation)
            self._waveform_navigation.disconnect()
        if liveobj_valid(sample):
            self._waveform_navigation = self.register_disconnectable(SimplerWaveformNavigation(simpler=self._simpler, waveform_length=sample.length))
        else:
            self._waveform_navigation = None
        self.notify_waveform_navigation()


class _SimplerDeviceDecorator(SimplerDeviceDecoratorBase):
    waveform_real_time_channel_id = ''
    playhead_real_time_channel_id = ''

    def __init__(self, song = None, envelope_types_provider = None, *a, **k):
        self._song = song
        self._envelope_types_provider = envelope_types_provider if envelope_types_provider is not None else EnvelopeTypesList()
        super(_SimplerDeviceDecorator, self).__init__(*a, **k)
        self.setup_options()
        self.register_disconnectables(self.options)
        self.__on_parameters_changed.subject = self._live_object
        self.__on_signature_numerator_changed.subject = song
        self.__on_can_warp_as_changed.subject = self._live_object
        self.__on_can_warp_half_changed.subject = self._live_object
        self.__on_can_warp_double_changed.subject = self._live_object
        self.__on_start_marker_changed.subject = self._live_object.sample
        self.__on_end_marker_changed.subject = self._live_object.sample

    def setup_parameters(self):
        super(_SimplerDeviceDecorator, self).setup_parameters()
        self.zoom = WaveformNavigationParameter(name='Zoom', parent=self, simpler=self)
        self.zoom.focus_object(self.start)
        self.zoom.add_waveform_navigation_listener(self.notify_waveform_navigation)
        self.envelope = EnumWrappingParameter(name='Env. Type', parent=self, values_property_host=self._envelope_types_provider, index_property_host=self._envelope_types_provider, values_property='available_values', index_property='index', value_type=EnvelopeType)
        self._additional_parameters.extend([self.zoom, self.envelope])

    def setup_options(self):

        def get_simpler_flag(name):
            return liveobj_valid(self._live_object) and getattr(self._live_object, name)

        def call_simpler_function(name, *a):
            if liveobj_valid(self._live_object):
                return getattr(self._live_object, name)(*a)

        self.crop_option = DeviceTriggerOption(name='Crop', callback=partial(call_simpler_function, 'crop'))
        self.reverse_option = DeviceTriggerOption(name='Reverse', callback=partial(call_simpler_function, 'reverse'))
        self.one_shot_sustain_mode_option = DeviceSwitchOption(name='Trigger Mode', default_label='Trigger', second_label='Gate', parameter=get_parameter_by_name(self, 'Trigger Mode'))
        self.retrigger_option = DeviceOnOffOption(name='Retrigger', property_host=self._live_object, property_name='retrigger')
        self.warp_as_x_bars_option = DeviceTriggerOption(name='Warp as X Bars', default_label=self.get_warp_as_option_label(), callback=lambda : call_simpler_function('warp_as', call_simpler_function('guess_playback_length')), is_active=lambda : get_simpler_flag('can_warp_as'))
        self.warp_half_option = DeviceTriggerOption(name=':2', callback=partial(call_simpler_function, 'warp_half'), is_active=lambda : get_simpler_flag('can_warp_half'))
        self.warp_double_option = DeviceTriggerOption(name='x2', callback=partial(call_simpler_function, 'warp_double'), is_active=lambda : get_simpler_flag('can_warp_double'))
        self.lfo_sync_option = DeviceSwitchOption(name='LFO Sync Type', default_label='Free', second_label='Sync', parameter=get_parameter_by_name(self, 'L Sync'))
        self.loop_option = DeviceOnOffOption(name='Loop', property_host=get_parameter_by_name(self, 'S Loop On'), property_name='value')
        self.filter_slope_option = DeviceSwitchOption(name='Filter Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Filter Slope'))

    def get_parameter_by_name(self, name):
        return find_if(lambda p: p.name == name, self.parameters)

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
    def waveform_navigation(self):
        return self.zoom.waveform_navigation

    @property
    def available_resolutions(self):
        return (u'1 Bar', u'\xbd', u'\xbc', u'\u215b', u'\ue001', u'\ue002', u'Transients')

    @listens('parameters')
    def __on_parameters_changed(self):
        self.lfo_sync_option.set_parameter(get_parameter_by_name(self, 'L Sync'))
        self.filter_slope_option.set_parameter(get_parameter_by_name(self, 'Filter Slope'))

    def _reconnect_sample_listeners(self):
        super(_SimplerDeviceDecorator, self)._reconnect_sample_listeners()
        self._reconnect_to_markers()
        self._update_warp_as_label()

    def _reconnect_to_markers(self):
        self.__on_start_marker_changed.subject = self._live_object.sample
        self.__on_end_marker_changed.subject = self._live_object.sample

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


class _OperatorDeviceDecorator(SlotManager, LiveObjectDecorator):

    def __init__(self, song = None, osc_types_provider = None, *a, **k):
        super(_OperatorDeviceDecorator, self).__init__(*a, **k)
        self._osc_types_provider = osc_types_provider if osc_types_provider is not None else OscillatorTypesList()
        self.__on_parameters_changed.subject = self._live_object
        self.oscillator = EnumWrappingParameter(name='Oscillator', parent=self, values_property_host=self._osc_types_provider, index_property_host=self._osc_types_provider, values_property='available_values', index_property='index', value_type=OscillatorType)
        self.filter_slope_option = DeviceSwitchOption(name='Filter Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Filter Slope'))
        self.register_disconnectables(self.options)

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + (self.oscillator,)

    @property
    def options(self):
        return (self.filter_slope_option,)

    @listens('parameters')
    def __on_parameters_changed(self):
        self.filter_slope_option.set_parameter(get_parameter_by_name(self, 'Filter Slope'))


class _SamplerDeviceDecorator(SlotManager, LiveObjectDecorator):

    def __init__(self, song = None, *a, **k):
        super(_SamplerDeviceDecorator, self).__init__(*a, **k)
        self.__on_parameters_changed.subject = self._live_object
        self.filter_slope_option = DeviceSwitchOption(name='Filter Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Filter Slope'))
        self.register_disconnectables(self.options)

    @property
    def options(self):
        return (self.filter_slope_option,)

    @listens('parameters')
    def __on_parameters_changed(self):
        self.filter_slope_option.set_parameter(get_parameter_by_name(self, 'Filter Slope'))


class _AutoFilterDeviceDecorator(SlotManager, LiveObjectDecorator):

    def __init__(self, song = None, *a, **k):
        super(_AutoFilterDeviceDecorator, self).__init__(*a, **k)
        self.__on_parameters_changed.subject = self._live_object
        self.slope_option = DeviceSwitchOption(name='Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Slope'))
        self.register_disconnectables(self.options)

    @property
    def options(self):
        return (self.slope_option,)

    @listens('parameters')
    def __on_parameters_changed(self):
        self.slope_option.set_parameter(get_parameter_by_name(self, 'Slope'))


class _Eq8DeviceDecorator(LiveObjectDecorator):

    def __init__(self, song = None, band_types_provider = None, *a, **k):
        super(_Eq8DeviceDecorator, self).__init__(*a, **k)
        self._band_types_provider = band_types_provider if band_types_provider is not None else BandTypesList()
        self.band = EnumWrappingParameter(name='Band', parent=self, values_property_host=self._band_types_provider, index_property_host=self._band_types_provider, values_property='available_values', index_property='index')

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + (self.band,)


class DeviceDecoratorFactory(DecoratorFactory):
    DECORATOR_CLASSES = {'OriginalSimpler': _SimplerDeviceDecorator,
     'Operator': _OperatorDeviceDecorator,
     'MultiSampler': _SamplerDeviceDecorator,
     'AutoFilter': _AutoFilterDeviceDecorator,
     'Eq8': _Eq8DeviceDecorator}

    @classmethod
    def generate_decorated_device(cls, device, additional_properties = {}, song = None, *a, **k):
        decorated = cls.DECORATOR_CLASSES[device.class_name](live_object=device, additional_properties=additional_properties, song=song, *a, **k)
        return decorated

    @classmethod
    def _should_be_decorated(cls, device):
        return liveobj_valid(device) and device.class_name in cls.DECORATOR_CLASSES

    @depends(song=None)
    def _get_decorated_object(self, device, additional_properties, song = None, *a, **k):
        return self.generate_decorated_device(device, additional_properties=additional_properties, song=song, *a, **k)


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