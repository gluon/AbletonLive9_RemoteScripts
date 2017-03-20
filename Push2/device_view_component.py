# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/device_view_component.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from ableton.v2.base import const, listens, liveobj_valid
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.mode import ModesComponent

class DeviceViewConnector(Component):

    def __init__(self, device_component=None, parameter_provider=None, device_type_provider=const('default'), view=None, *a, **k):
        assert device_component is not None
        assert parameter_provider is not None
        assert view is not None
        super(DeviceViewConnector, self).__init__(*a, **k)
        self._device_component = device_component
        self._parameter_provider = parameter_provider
        self._view = view
        self._parameters = None
        self._parameter_names = []
        self._device_type_provider = device_type_provider
        return

    def update(self):
        super(DeviceViewConnector, self).update()
        if self.is_enabled():
            self._view.deviceType = self._device_type_provider()
        self._view.device = self._device_component.device()
        parameters = self._value_for_state(map(lambda p: p and p.parameter, self._parameter_provider.parameters), [])
        if self._parameters_changed(parameters):
            self._view.parameters = parameters
            self._parameters = parameters
            self._parameter_names = self._extract_names(parameters)

    def on_enabled_changed(self):
        self._view.visible = self.is_enabled()
        self._on_parameters_changed.subject = self._value_for_state(self._parameter_provider, None)
        super(DeviceViewConnector, self).on_enabled_changed()
        return

    @listens('parameters')
    def _on_parameters_changed(self):
        self.update()

    def _extract_names(self, parameters):
        return [ (p.name if p else None) for p in parameters ]

    def _parameters_changed(self, new_parameters):
        return new_parameters != self._parameters or self._extract_names(new_parameters) != self._parameter_names

    def _value_for_state(self, enabled_value, disabled_value):
        if self.is_enabled():
            return enabled_value
        return disabled_value


class SimplerDeviceViewConnector(DeviceViewConnector):

    def update(self):
        super(SimplerDeviceViewConnector, self).update()
        device = self._value_for_state(self._device_component.device(), None)
        assert device == None or device.class_name == 'OriginalSimpler'
        self._view.properties = device
        self._view.wants_waveform_shown = self._parameter_provider.wants_waveform_shown
        return


class DeviceViewComponent(ModesComponent):

    def __init__(self, device_component=None, view_model=None, *a, **k):
        assert device_component is not None
        assert view_model is not None
        super(DeviceViewComponent, self).__init__(*a, **k)
        self._get_device = device_component.device
        for view in (view_model.deviceParameterView, view_model.simplerDeviceView):
            view.visible = False

        self.add_mode('default', DeviceViewConnector(device_component=device_component, parameter_provider=device_component, device_type_provider=self._device_type, view=view_model.deviceParameterView, is_enabled=False))
        self.add_mode('OriginalSimpler', SimplerDeviceViewConnector(device_component=device_component, parameter_provider=device_component, device_type_provider=self._device_type, view=view_model.simplerDeviceView, is_enabled=False))
        self._on_parameters_changed.subject = device_component
        self._on_parameters_changed()
        return

    def on_enabled_changed(self):
        self._last_selected_mode = None
        super(DeviceViewComponent, self).on_enabled_changed()
        return

    def update(self):
        super(DeviceViewComponent, self).update()
        if self.is_enabled():
            self.selected_mode = self._mode_to_select()

    def _device_type(self):
        device = self._get_device()
        if liveobj_valid(device):
            return device.class_name
        return ''

    def _mode_to_select(self):
        device = self._get_device()
        device_type = device and device.class_name
        if self.get_mode(device_type) != None:
            return device_type
        else:
            return 'default'

    @listens('parameters')
    def _on_parameters_changed(self):
        self.selected_mode = self._mode_to_select()