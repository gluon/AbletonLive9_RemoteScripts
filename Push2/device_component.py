#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/device_component.py
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.base import SlotError, const, listenable_property, listens, liveobj_valid
from ableton.v2.control_surface.control import control_list, ButtonControl
from ableton.v2.control_surface.components.device import DeviceProvider as DeviceProviderBase
from pushbase.device_chain_utils import is_simpler
from pushbase.device_component import DeviceComponent as DeviceComponentBase
from pushbase.parameter_provider import generate_info, is_parameter_quantized
from .simpler_zoom import SimplerZoomHandling
from .device_parameter_bank_with_options import create_device_bank_with_options, OPTIONS_PER_BANK
from .real_time_channel import RealTimeDataComponent
from .parameter_mapping_sensitivities import PARAMETER_SENSITIVITIES, DEFAULT_SENSITIVITY_KEY, FINE_GRAINED_SENSITIVITY_KEY, CONTINUOUS_MAPPING_SENSITIVITY, FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY, QUANTIZED_MAPPING_SENSITIVITY

def parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    if is_quantized:
        return QUANTIZED_MAPPING_SENSITIVITY
    return CONTINUOUS_MAPPING_SENSITIVITY


def fine_grain_parameter_mapping_sensitivity(parameter):
    is_quantized = is_parameter_quantized(parameter, parameter and parameter.canonical_parent)
    if is_quantized:
        return QUANTIZED_MAPPING_SENSITIVITY
    return FINE_GRAINED_CONTINUOUS_MAPPING_SENSITIVITY


def parameter_sensitivities(device_class, parameter):
    sensitivities = {}
    try:
        param_name = parameter.name if liveobj_valid(parameter) else ''
        sensitivities = PARAMETER_SENSITIVITIES[device_class][param_name]
    except KeyError:
        pass

    for key, getter in ((DEFAULT_SENSITIVITY_KEY, parameter_mapping_sensitivity), (FINE_GRAINED_SENSITIVITY_KEY, fine_grain_parameter_mapping_sensitivity)):
        if key not in sensitivities:
            sensitivities[key] = getter(parameter)

    return sensitivities


class Push2DeviceProvider(DeviceProviderBase):
    allow_update_callback = const(True)

    def update_device_selection(self):
        if self.allow_update_callback():
            super(Push2DeviceProvider, self).update_device_selection()


class DeviceComponent(DeviceComponentBase):
    ZOOM_SENSITIVE_PARAMETERS = ('S Start', 'S Length', 'Start', 'End', 'Nudge')
    PARAMETERS_RELATIVE_TO_ACTIVE_AREA = ('S Start', 'S Length')
    parameter_touch_buttons = control_list(ButtonControl, control_count=8)

    def _initialize_subcomponents(self):
        super(DeviceComponent, self)._initialize_subcomponents()
        self._playhead_real_time_data = self.register_component(RealTimeDataComponent(channel_type='playhead'))
        self._waveform_real_time_data = self.register_component(RealTimeDataComponent(channel_type='waveform'))
        self._zoom_handling = self.register_disconnectable(SimplerZoomHandling())
        self.default_sensitivity = partial(self._sensitivity, DEFAULT_SENSITIVITY_KEY)
        self.fine_sensitivity = partial(self._sensitivity, FINE_GRAINED_SENSITIVITY_KEY)
        self._processed_zoom_requests = 0
        self._use_waveform_navigation = False
        self._on_simpler_zoom_changed.subject = self._zoom_handling
        self.__on_waveform_channel_changed.subject = self._waveform_real_time_data
        self.__on_playhead_channel_changed.subject = self._playhead_real_time_data

    def disconnect(self):
        super(DeviceComponent, self).disconnect()
        self._playhead_real_time_data.set_data(None)
        self._waveform_real_time_data.set_data(None)

    @property
    def use_waveform_navigation(self):
        return self._use_waveform_navigation

    @use_waveform_navigation.setter
    def use_waveform_navigation(self, value):
        self._use_waveform_navigation = value
        self._update_parameter_sensitivity()

    def _set_device(self, device):
        super(DeviceComponent, self)._set_device(device)
        simpler = self.device() if is_simpler(self.device()) else None
        if liveobj_valid(simpler):
            simpler.zoom.reset_focus_and_animation()
        self._zoom_handling.set_parameter_host(simpler)
        self.__on_sample_or_file_path_changed.subject = simpler
        self.__on_waveform_visible_start_changed.subject = simpler
        self.__on_waveform_visible_end_changed.subject = simpler
        self._playhead_real_time_data.set_data(device)
        self._waveform_real_time_data.set_data(device)
        self.notify_options()

    def request_zoom(self, zoom_factor):
        self._zoom_handling.request_zoom(zoom_factor)
        self._processed_zoom_requests += 1
        self.notify_processed_zoom_requests()

    @listenable_property
    def processed_zoom_requests(self):
        return self._processed_zoom_requests

    @parameter_touch_buttons.pressed
    def parameter_touch_buttons(self, button):
        if is_simpler(self.device()):
            parameter = self._provided_parameters[button.index].parameter
            if parameter is not None:
                self.device().zoom.touch_object(parameter)

    @parameter_touch_buttons.released
    def parameter_touch_buttons(self, button):
        if is_simpler(self.device()):
            parameter = self._provided_parameters[button.index].parameter
            if parameter is not None:
                self.device().zoom.release_object(parameter)

    @listens('channel_id')
    def __on_waveform_channel_changed(self):
        self._update_real_time_channel('waveform')

    @listens('channel_id')
    def __on_playhead_channel_changed(self):
        self._update_real_time_channel('playhead')

    def _update_real_time_channel(self, channel_name):
        device = self.device()
        if is_simpler(device):
            rt_data = getattr(self, '_%s_real_time_data' % channel_name)
            setattr(device, channel_name + '_real_time_channel_id', rt_data.channel_id)

    @listens('zoom')
    def _on_simpler_zoom_changed(self):
        if not self.use_waveform_navigation:
            self._update_parameter_sensitivity()

    @listens('waveform_navigation.visible_start')
    def __on_waveform_visible_start_changed(self, *a):
        if self.use_waveform_navigation:
            self._update_parameter_sensitivity()

    @listens('waveform_navigation.visible_end')
    def __on_waveform_visible_end_changed(self, *a):
        if self.use_waveform_navigation:
            self._update_parameter_sensitivity()

    def _update_parameter_sensitivity(self):
        changed_parameters = False
        for index, info in enumerate(self._provided_parameters):
            if info.name in self.ZOOM_SENSITIVE_PARAMETERS:
                changed_parameters = True
                self._provided_parameters[index] = self._create_parameter_info(info.parameter)

        if changed_parameters:
            self.notify_parameters()

    @listens('sample.file_path')
    def __on_sample_or_file_path_changed(self):
        self._waveform_real_time_data.invalidate()

    def _get_provided_parameters(self):
        _, parameters = self._current_bank_details() if self.device() else (None, ())
        return [ self._create_parameter_info(p) for p in parameters ]

    def _has_simpler_in_multi_sample_mode(self):
        device = self.device()
        return is_simpler(device) and device.multi_sample_mode

    def _create_parameter_info(self, parameter):

        def is_available(param):
            name = param.name if param != None else ''
            return not self._has_simpler_in_multi_sample_mode() or name not in self.ZOOM_SENSITIVE_PARAMETERS + ('Zoom',)

        return generate_info(parameter if is_available(parameter) else None, default_sens_factory=self.default_sensitivity, fine_sens_factory=self.fine_sensitivity)

    def _sensitivity(self, sensitivity_key, parameter):
        device = self.device()
        sensitivity = parameter_sensitivities(device.class_name, parameter)[sensitivity_key]
        if liveobj_valid(parameter) and is_simpler(device) and liveobj_valid(device.sample):
            if parameter.name in self.ZOOM_SENSITIVE_PARAMETERS:
                if self.use_waveform_navigation:
                    sensitivity *= device.waveform_navigation.visible_proportion
                else:
                    sensitivity *= self._zoom_handling.zoom_factor
            if parameter.name in self.PARAMETERS_RELATIVE_TO_ACTIVE_AREA:
                active_area_quotient = device.sample.length / float(device.sample.end_marker - device.sample.start_marker + 1)
                sensitivity *= active_area_quotient
        return sensitivity

    @listenable_property
    def options(self):
        return getattr(self._bank, 'options', [None] * OPTIONS_PER_BANK)

    @property
    def wants_waveform_shown(self):
        return getattr(self._bank, 'wants_waveform_shown', True)

    @listens('options')
    def __on_options_changed(self):
        self.notify_options()

    def _setup_bank(self, device):
        super(DeviceComponent, self)._setup_bank(device, bank_factory=create_device_bank_with_options)
        try:
            self.__on_options_changed.subject = self._bank
        except SlotError:
            pass