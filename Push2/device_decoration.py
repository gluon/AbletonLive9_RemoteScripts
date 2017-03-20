# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/device_decoration.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from functools import partial
import Live
from ableton.v2.base import EventObject, depends, find_if, listenable_property, listens, liveobj_valid
from pushbase.decoration import LiveObjectDecorator, DecoratorFactory
from pushbase.internal_parameter import EnumWrappingParameter, InternalParameter
from pushbase.message_box_component import Messenger
from pushbase.simpler_decoration import SimplerDeviceDecorator as SimplerDeviceDecoratorBase
from .device_options import DeviceTriggerOption, DeviceSwitchOption, DeviceOnOffOption
from .waveform_navigation import Region, SimplerWaveformNavigation
RESET_SLICING_NOTIFICATION = 'Slicing has been reset'
MAX_NUMBER_SLICES = 64

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

class NotifyingList(EventObject):
    __events__ = ('index', )

    def __init__(self, available_values, default_value=None, *a, **k):
        super(NotifyingList, self).__init__(*a, **k)
        self._index = default_value if default_value is not None else 0
        self._available_values = available_values
        return

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
        super(EnvelopeTypesList, self).__init__(available_values=[
         'Volume', 'Filter', 'Pitch'], default_value=EnvelopeType.volume_env)


class OscillatorTypesList(NotifyingList):

    def __init__(self):
        super(OscillatorTypesList, self).__init__(available_values=[
         'A', 'B', 'C', 'D'], default_value=OscillatorType.a)


class BandTypesList(NotifyingList):

    def __init__(self):
        super(BandTypesList, self).__init__(available_values=range(1, 9))


class WaveformNavigationParameter(InternalParameter):
    """ Class for connecting a Simpler with a WaveformNavigation. It will create a new
        instance of WaveformNavigation for every sample. It also still acts as a
        parameter, for the current zooming implemenation.
    
        It also provides the "zoom" method interface, so it works with the
        pushbase.mapped_control.MappedControl class.
    """

    def __init__(self, simpler=None, *a, **k):
        super(WaveformNavigationParameter, self).__init__(*a, **k)
        self._simpler = simpler
        self._waveform_navigation = None
        self.post_sample_changed()
        return

    @listenable_property
    def waveform_navigation(self):
        return self._waveform_navigation

    @property
    def visible_region(self):
        if self._waveform_navigation:
            return self._waveform_navigation.visible_region
        return Region(0, 1)

    @visible_region.setter
    def visible_region(self, region):
        if self._waveform_navigation:
            self._waveform_navigation.visible_region = region

    def set_visible_region(self, region):
        if self._waveform_navigation:
            self._waveform_navigation.set_visible_region(region)

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

    def focus_region_of_interest(self, roi_identifier, focused_object):
        if self._waveform_navigation:
            self._waveform_navigation.focus_region_of_interest(roi_identifier, focused_object)

    def reset_focus_and_animation(self):
        if self._waveform_navigation:
            self._waveform_navigation.reset_focus_and_animation()

    def post_sample_changed(self):
        sample = self._simpler.sample
        if self._waveform_navigation is not None:
            self.unregister_disconnectable(self._waveform_navigation)
            self._waveform_navigation.disconnect()
        if liveobj_valid(sample):
            self._waveform_navigation = self.register_disconnectable(SimplerWaveformNavigation(simpler=self._simpler))
        else:
            self._waveform_navigation = None
        self.notify_waveform_navigation()
        return


class SlicePoint(object):

    def __init__(self, identifier, time):
        self.__id__ = identifier
        self.time = time

    def __eq__(self, other):
        if isinstance(other, SlicePoint):
            return self.__id__ == other.__id__ and self.time == other.time
        return False

    def __ne__(self, other):
        return not self == other


class SimplerPositions(EventObject):
    __events__ = ('warp_markers', 'before_update_all', 'after_update_all')
    start = listenable_property.managed(0.0)
    end = listenable_property.managed(0.0)
    start_marker = listenable_property.managed(0.0)
    end_marker = listenable_property.managed(0.0)
    active_start = listenable_property.managed(0.0)
    active_end = listenable_property.managed(0.0)
    loop_start = listenable_property.managed(0.0)
    loop_end = listenable_property.managed(0.0)
    loop_fade_in_samples = listenable_property.managed(0.0)
    env_fade_in = listenable_property.managed(0.0)
    env_fade_out = listenable_property.managed(0.0)
    slices = listenable_property.managed([])
    selected_slice = listenable_property.managed(SlicePoint(0, 0.0))
    use_beat_time = listenable_property.managed(False)

    def __init__(self, simpler=None, *a, **k):
        assert simpler is not None
        super(SimplerPositions, self).__init__(*a, **k)
        self._simpler = simpler
        self.__on_active_start_changed.subject = simpler.view
        self.__on_active_end_changed.subject = simpler.view
        self.__on_loop_start_changed.subject = simpler.view
        self.__on_loop_end_changed.subject = simpler.view
        self.__on_loop_fade_changed.subject = simpler.view
        self.__on_env_fade_in_changed.subject = simpler.view
        self.__on_env_fade_out_changed.subject = simpler.view
        self.__on_selected_slice_changed.subject = simpler.view
        self.post_sample_changed()
        return

    def post_sample_changed(self):
        self.__on_start_marker_changed.subject = self._simpler.sample
        self.__on_end_marker_changed.subject = self._simpler.sample
        self.__on_slices_changed.subject = self._simpler.sample
        self.__on_warping_changed.subject = self._simpler.sample
        self.__on_warp_markers_changed.subject = self._simpler.sample
        self.update_all()

    def _convert_sample_time(self, sample_time):
        """
        Converts to beat time, if the sample is warped
        """
        sample = self._simpler.sample
        if liveobj_valid(sample) and sample.warping:
            return sample.sample_to_beat_time(sample_time)
        return sample_time

    @listens('start_marker')
    def __on_start_marker_changed(self):
        if liveobj_valid(self._simpler.sample):
            self.start_marker = self._convert_sample_time(self._simpler.sample.start_marker)

    @listens('end_marker')
    def __on_end_marker_changed(self):
        if liveobj_valid(self._simpler.sample):
            self.end_marker = self._convert_sample_time(self._simpler.sample.end_marker)

    @listens('sample_start')
    def __on_active_start_changed(self):
        self.active_start = self._convert_sample_time(self._simpler.view.sample_start)

    @listens('sample_end')
    def __on_active_end_changed(self):
        self.active_end = self._convert_sample_time(self._simpler.view.sample_end)

    @listens('sample_loop_start')
    def __on_loop_start_changed(self):
        self.loop_start = self._convert_sample_time(self._simpler.view.sample_loop_start)

    @listens('sample_loop_end')
    def __on_loop_end_changed(self):
        self.loop_end = self._convert_sample_time(self._simpler.view.sample_loop_end)

    @listens('sample_loop_fade')
    def __on_loop_fade_changed(self):
        self.loop_fade_in_samples = self._simpler.view.sample_loop_fade

    @listens('sample_env_fade_in')
    def __on_env_fade_in_changed(self):
        if liveobj_valid(self._simpler.sample):
            start_marker = self._simpler.sample.start_marker
            fade_in_end = start_marker + self._simpler.view.sample_env_fade_in
            self.env_fade_in = self._convert_sample_time(fade_in_end) - self._convert_sample_time(start_marker)

    @listens('sample_env_fade_out')
    def __on_env_fade_out_changed(self):
        if liveobj_valid(self._simpler.sample):
            end_marker = self._simpler.sample.end_marker
            fade_out_start = end_marker - self._simpler.view.sample_env_fade_out
            self.env_fade_out = self._convert_sample_time(end_marker) - self._convert_sample_time(fade_out_start)

    @listens('slices')
    def __on_slices_changed(self):
        if liveobj_valid(self._simpler.sample):
            self.slices = [ SlicePoint(s, self._convert_sample_time(s)) for s in self._simpler.sample.slices
                          ]

    @listens('selected_slice')
    def __on_selected_slice_changed(self):
        if liveobj_valid(self._simpler.sample):
            t = self._convert_sample_time(self._simpler.view.selected_slice)
            self.selected_slice = SlicePoint(t, t)

    @listens('warping')
    def __on_warping_changed(self):
        self.update_all()

    @listens('warp_markers')
    def __on_warp_markers_changed(self):
        self.update_all()
        self.notify_warp_markers()

    def update_all(self):
        if liveobj_valid(self._simpler.sample):
            self.notify_before_update_all()
            self.start = self._convert_sample_time(0)
            self.end = self._convert_sample_time(self._simpler.sample.length)
            self.__on_start_marker_changed()
            self.__on_end_marker_changed()
            self.__on_active_start_changed()
            self.__on_active_end_changed()
            self.__on_loop_start_changed()
            self.__on_loop_end_changed()
            self.__on_loop_fade_changed()
            self.__on_env_fade_in_changed()
            self.__on_env_fade_out_changed()
            self.__on_slices_changed()
            self.__on_selected_slice_changed()
            self.use_beat_time = self._simpler.sample.warping
            self.notify_after_update_all()


def center_point(start, end):
    return int((end - start) / 2.0) + start


def insert_new_slice(simpler):
    sample = simpler.sample
    view = simpler.view
    slices = list(sample.slices) + [sample.end_marker]
    selected_slice = view.selected_slice
    if selected_slice in slices:
        slice_index = slices.index(selected_slice)
        new_slice_point = center_point(selected_slice, slices[slice_index + 1])
        if new_slice_point not in slices:
            sample.insert_slice(new_slice_point)
            view.selected_slice = new_slice_point


class _SimplerDeviceDecorator(SimplerDeviceDecoratorBase, Messenger):
    waveform_real_time_channel_id = ''
    playhead_real_time_channel_id = ''

    def __init__(self, song=None, envelope_types_provider=None, *a, **k):
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
        self.__on_selected_slice_changed.subject = self._live_object.view
        return

    def setup_parameters(self):
        super(_SimplerDeviceDecorator, self).setup_parameters()
        self.positions = self.register_disconnectable(SimplerPositions(self))
        self.zoom = WaveformNavigationParameter(name='Zoom', parent=self, simpler=self)
        self.zoom.focus_region_of_interest('start_end_marker', self.get_parameter_by_name('Start'))
        self.zoom.add_waveform_navigation_listener(self.notify_waveform_navigation)
        self.envelope = EnumWrappingParameter(name='Env. Type', parent=self, values_host=self._envelope_types_provider, index_property_host=self._envelope_types_provider, values_property='available_values', index_property='index', value_type=EnvelopeType)
        self._additional_parameters.extend([
         self.zoom,
         self.envelope])

    def setup_options(self):

        def get_simpler_flag(name):
            return liveobj_valid(self._live_object) and getattr(self._live_object, name)

        def call_simpler_function(name, *a):
            if liveobj_valid(self._live_object):
                return getattr(self._live_object, name)(*a)

        def sample_available():
            return liveobj_valid(self._live_object) and liveobj_valid(self._live_object.sample)

        def call_sample_function(name, *a):
            if sample_available():
                return getattr(self._live_object.sample, name)(*a)

        def reset_slices():
            call_sample_function('reset_slices')
            self.show_notification(RESET_SLICING_NOTIFICATION)

        def split_slice_available():
            if sample_available():
                slices = self._live_object.sample.slices
                return len(slices) != MAX_NUMBER_SLICES or slices[-1] != self._live_object.view.selected_slice
            return False

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
        self.clear_slices_action = DeviceTriggerOption(name='Clear Slices', default_label='Clear Slices', callback=lambda : call_sample_function('clear_slices'), is_active=lambda : sample_available() and len(self._live_object.sample.slices) > 1)
        self.reset_slices_action = DeviceTriggerOption(name='Reset Slices', default_label='Reset Slices', callback=reset_slices, is_active=lambda : sample_available())
        self.split_slice_action = DeviceTriggerOption(name='Split Slice', default_label='Split Slice', callback=lambda : insert_new_slice(self._live_object), is_active=split_slice_available)

    def get_parameter_by_name(self, name):
        return find_if(lambda p: p.name == name, self.parameters)

    @property
    def options(self):
        return (
         self.crop_option,
         self.reverse_option,
         self.one_shot_sustain_mode_option,
         self.retrigger_option,
         self.warp_as_x_bars_option,
         self.warp_half_option,
         self.warp_double_option,
         self.lfo_sync_option,
         self.loop_option,
         self.filter_slope_option,
         self.clear_slices_action,
         self.reset_slices_action,
         self.split_slice_action)

    @listenable_property
    def waveform_navigation(self):
        return self.zoom.waveform_navigation

    @property
    def available_resolutions(self):
        return (u'1 Bar', u'\xbd', u'\xbc', u'\u215b', u'\ue001', u'\ue002', u'Transients')

    @property
    def available_slicing_beat_divisions(self):
        return (u'\ue001', u'\ue001T', u'\u215b', u'\u215bT', u'\xbc', u'\xbcT', u'\xbd',
                u'\xbdT', u'1 Bar', u'2 Bars', u'4 Bars')

    @listens('parameters')
    def __on_parameters_changed(self):
        self.lfo_sync_option.set_parameter(get_parameter_by_name(self, 'L Sync'))
        self.filter_slope_option.set_parameter(get_parameter_by_name(self, 'Filter Slope'))

    def _reconnect_sample_listeners(self):
        super(_SimplerDeviceDecorator, self)._reconnect_sample_listeners()
        self._reconnect_to_markers()
        self._update_warp_as_label()
        self.positions.post_sample_changed()
        self.zoom.post_sample_changed()
        self.zoom.focus_region_of_interest('start_end_marker', self.get_parameter_by_name('Start'))

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

    @listens('selected_slice')
    def __on_selected_slice_changed(self):
        self.split_slice_action.notify_active()

    def _on_sample_changed(self):
        super(_SimplerDeviceDecorator, self)._on_sample_changed()
        self.clear_slices_action.notify_active()
        self.reset_slices_action.notify_active()
        self.split_slice_action.notify_active()

    def _on_slices_changed(self):
        super(_SimplerDeviceDecorator, self)._on_slices_changed()
        self.clear_slices_action.notify_active()

    def get_warp_as_option_label(self):
        try:
            bars = int(self._live_object.guess_playback_length() / self._song.signature_numerator)
            return 'Warp as %d Bar%s' % (bars, 's' if bars > 1 else '')
        except RuntimeError:
            return 'Warp as X Bars'


class _OperatorDeviceDecorator(EventObject, LiveObjectDecorator):

    def __init__(self, song=None, osc_types_provider=None, *a, **k):
        super(_OperatorDeviceDecorator, self).__init__(*a, **k)
        self._osc_types_provider = osc_types_provider if osc_types_provider is not None else OscillatorTypesList()
        self.__on_parameters_changed.subject = self._live_object
        self.oscillator = EnumWrappingParameter(name='Oscillator', parent=self, values_host=self._osc_types_provider, index_property_host=self._osc_types_provider, values_property='available_values', index_property='index', value_type=OscillatorType)
        self.filter_slope_option = DeviceSwitchOption(name='Filter Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Filter Slope'))
        self.register_disconnectables(self.options)
        return

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + (self.oscillator,)

    @property
    def options(self):
        return (
         self.filter_slope_option,)

    @listens('parameters')
    def __on_parameters_changed(self):
        self.filter_slope_option.set_parameter(get_parameter_by_name(self, 'Filter Slope'))


class _SamplerDeviceDecorator(EventObject, LiveObjectDecorator):

    def __init__(self, song=None, *a, **k):
        super(_SamplerDeviceDecorator, self).__init__(*a, **k)
        self.__on_parameters_changed.subject = self._live_object
        self.filter_slope_option = DeviceSwitchOption(name='Filter Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Filter Slope'))
        self.register_disconnectables(self.options)

    @property
    def options(self):
        return (
         self.filter_slope_option,)

    @listens('parameters')
    def __on_parameters_changed(self):
        self.filter_slope_option.set_parameter(get_parameter_by_name(self, 'Filter Slope'))


class _AutoFilterDeviceDecorator(EventObject, LiveObjectDecorator):

    def __init__(self, song=None, *a, **k):
        super(_AutoFilterDeviceDecorator, self).__init__(*a, **k)
        self.__on_parameters_changed.subject = self._live_object
        self.slope_option = DeviceSwitchOption(name='Slope', default_label='12dB', second_label='24dB', parameter=get_parameter_by_name(self, 'Slope'))
        self.register_disconnectables(self.options)

    @property
    def options(self):
        return (
         self.slope_option,)

    @listens('parameters')
    def __on_parameters_changed(self):
        self.slope_option.set_parameter(get_parameter_by_name(self, 'Slope'))


class _Eq8DeviceDecorator(LiveObjectDecorator):

    def __init__(self, song=None, band_types_provider=None, *a, **k):
        super(_Eq8DeviceDecorator, self).__init__(*a, **k)
        self._band_types_provider = band_types_provider if band_types_provider is not None else BandTypesList()
        self.band = EnumWrappingParameter(name='Band', parent=self, values_host=self._band_types_provider, index_property_host=self._band_types_provider, values_property='available_values', index_property='index')
        return

    @property
    def parameters(self):
        return tuple(self._live_object.parameters) + (self.band,)


class DeviceDecoratorFactory(DecoratorFactory):
    DECORATOR_CLASSES = {'OriginalSimpler': _SimplerDeviceDecorator,
       'Operator': _OperatorDeviceDecorator,
       'MultiSampler': _SamplerDeviceDecorator,
       'AutoFilter': _AutoFilterDeviceDecorator,
       'Eq8': _Eq8DeviceDecorator
       }

    @classmethod
    def generate_decorated_device(cls, device, additional_properties={}, song=None, *a, **k):
        decorated = cls.DECORATOR_CLASSES[device.class_name](live_object=device, additional_properties=additional_properties, song=song, *a, **k)
        return decorated

    @classmethod
    def _should_be_decorated(cls, device):
        return liveobj_valid(device) and device.class_name in cls.DECORATOR_CLASSES

    @depends(song=None)
    def _get_decorated_object(self, device, additional_properties, song=None, *a, **k):
        return self.generate_decorated_device(device, additional_properties=additional_properties, song=song, *a, **k)


class SimplerDecoratedPropertiesCopier(object):
    ADDITIONAL_PROPERTIES = [
     'playhead_real_time_channel_id',
     'waveform_real_time_channel_id']

    def __init__(self, decorated_object=None, factory=None, *a, **k):
        assert liveobj_valid(decorated_object)
        assert factory is not None
        assert decorated_object in factory.decorated_objects
        super(SimplerDecoratedPropertiesCopier, self).__init__(*a, **k)
        self._decorated_object = decorated_object
        self._factory = factory
        self._copied_additional_properties = {}
        self._nested_properties = {}
        self.copy_properties({self.ADDITIONAL_PROPERTIES[0]: None,
           self.ADDITIONAL_PROPERTIES[1]: None
           })
        return

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
        if decorated_object.zoom.waveform_navigation is not None and self._decorated_object.zoom.waveform_navigation is not None:
            decorated_object.zoom.waveform_navigation.copy_state(self._decorated_object.zoom.waveform_navigation)
        return