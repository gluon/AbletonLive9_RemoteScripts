#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/device_component.py
from __future__ import absolute_import
from functools import partial
from ableton.v2.base import SlotError, const, listenable_property, listens, liveobj_changed, liveobj_valid
from ableton.v2.control_surface import CompoundComponent
from pushbase.provider_device_component import ProviderDeviceComponent
from pushbase.parameter_provider import fine_grain_parameter_mapping_sensitivity, generate_info, parameter_mapping_sensitivity
from .simpler_zoom import SimplerZoomHandling, is_simpler
from .simpler_slice_nudging import SimplerSliceNudging
from .device_parameter_bank import create_device_bank
from .device_parameter_bank_with_options import create_device_bank_with_options, OPTIONS_PER_BANK
from .real_time_channel import RealTimeDataComponent
from .parameter_mapping_sensitivities import PARAMETER_SENSITIVITIES, DEFAULT_SENSITIVITY_KEY, FINE_GRAINED_SENSITIVITY_KEY

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


class DeviceComponentWithBank(ProviderDeviceComponent, CompoundComponent):

    def __init__(self, banking_info = None, *a, **k):
        raise banking_info is not None or AssertionError
        self._bank = None
        self._banking_info = banking_info
        super(DeviceComponentWithBank, self).__init__(*a, **k)

    def _get_bank_index(self):
        return self._bank.index if self._bank is not None else 0

    def _set_bank_index(self, index):
        if self._bank is not None:
            self._bank.index = index

    _bank_index = property(_get_bank_index, _set_bank_index)

    def _setup_bank(self, device, bank_factory = create_device_bank):
        if self._bank is not None:
            self.disconnect_disconnectable(self._bank)
            self._bank = None
        if liveobj_valid(device):
            self._bank = self.register_disconnectable(bank_factory(device, self._banking_info))

    def set_device(self, device):
        if self._device_changed(device):
            self._setup_bank(device)
            self._on_bank_parameters_changed.subject = self._bank
        super(DeviceComponentWithBank, self).set_device(device)

    @listens('parameters')
    def _on_bank_parameters_changed(self):
        self.update()
        self.notify_parameters()

    def _current_bank_details(self):
        return (self._bank.name, self._bank.parameters) if self._bank is not None else ('', [None] * 8)

    def _number_of_parameter_banks(self):
        return self._bank.bank_count() if self._bank is not None else 0

    def _get_provided_parameters(self):
        _, parameters = self._current_bank_details() if self._device else (None, ())
        return [ self._create_parameter_info(p) for p in parameters ]


class DeviceComponent(DeviceComponentWithBank):
    ZOOMABLE_PARAMETERS = ('S Start', 'S Length', 'Start', 'End', 'Nudge')
    PARAMETERS_RELATIVE_TO_ACTIVE_AREA = ('S Start', 'S Length')
    allow_update_callback = const(True)

    def __init__(self, device_decorator_factory = None, *a, **k):
        raise device_decorator_factory is not None or AssertionError
        super(DeviceComponent, self).__init__(*a, **k)
        self._playhead_real_time_data = self.register_component(RealTimeDataComponent(channel_type='playhead'))
        self._waveform_real_time_data = self.register_component(RealTimeDataComponent(channel_type='waveform'))
        self._decorator_factory = device_decorator_factory
        self._zoom_handling = self.register_disconnectable(SimplerZoomHandling())
        self._slice_nudging = self.register_disconnectable(SimplerSliceNudging())
        self.default_sensitivity = partial(self._sensitivity, DEFAULT_SENSITIVITY_KEY)
        self.fine_sensitivity = partial(self._sensitivity, FINE_GRAINED_SENSITIVITY_KEY)
        self._processed_zoom_requests = 0
        self._on_simpler_zoom_changed.subject = self._zoom_handling
        self.__on_waveform_channel_changed.subject = self._waveform_real_time_data
        self.__on_playhead_channel_changed.subject = self._playhead_real_time_data

    def disconnect(self):
        super(DeviceComponent, self).disconnect()
        self._playhead_real_time_data.set_data(None)
        self._waveform_real_time_data.set_data(None)

    def set_device(self, device):
        if self._device_changed(device):
            decorated_device = self._decorator_factory.decorate(device, song=self.song)
            super(DeviceComponent, self).set_device(decorated_device)
            self._zoom_handling.set_parameter_host(decorated_device)
            self._slice_nudging.set_device(decorated_device)
            self.__on_file_path_changed.subject = decorated_device if is_simpler(decorated_device) else None
            self._playhead_real_time_data.set_data(device)
            self._waveform_real_time_data.set_data(device)
            self.notify_options()

    def _device_changed(self, device):
        current_device = getattr(self._device, '_live_object', self._device)
        return not self._locked_to_device and liveobj_changed(current_device, device)

    def request_zoom(self, zoom_factor):
        self._zoom_handling.request_zoom(zoom_factor)
        self._processed_zoom_requests += 1
        self.notify_processed_zoom_requests()

    @listenable_property
    def processed_zoom_requests(self):
        return self._processed_zoom_requests

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
        changed_parameters = False
        for index, info in enumerate(self._provided_parameters):
            if info.name in self.ZOOMABLE_PARAMETERS:
                changed_parameters = True
                self._provided_parameters[index] = self._create_parameter_info(info.parameter)

        if changed_parameters:
            self.notify_parameters()

    @listens('sample_file_path')
    def __on_file_path_changed(self):
        self._waveform_real_time_data.invalidate()

    def _has_simpler_in_multi_sample_mode(self):
        device = self.device()
        return is_simpler(device) and device.multi_sample_mode

    def _create_parameter_info(self, parameter):

        def is_available(param):
            name = param.name if param != None else ''
            return not self._has_simpler_in_multi_sample_mode() or name not in self.ZOOMABLE_PARAMETERS + ('Zoom',)

        return generate_info(parameter if is_available(parameter) else None, default_sens_factory=self.default_sensitivity, fine_sens_factory=self.fine_sensitivity)

    def _sensitivity(self, sensitivity_key, parameter):
        device = self.device()
        sensitivity = parameter_sensitivities(device.class_name, parameter)[sensitivity_key]
        if liveobj_valid(parameter) and is_simpler(device) and device.sample_length > 0:
            if parameter.name in self.ZOOMABLE_PARAMETERS:
                sensitivity *= self._zoom_handling.zoom_factor
            if parameter.name in self.PARAMETERS_RELATIVE_TO_ACTIVE_AREA:
                active_area_quotient = device.sample_length / float(device.end_marker - device.start_marker + 1)
                sensitivity *= active_area_quotient
        return sensitivity

    def update_device_selection(self):
        if self.allow_update_callback():
            super(DeviceComponent, self).update_device_selection()

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