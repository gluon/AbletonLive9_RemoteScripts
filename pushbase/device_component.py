# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/device_component.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function
from ableton.v2.base import depends, listens, liveobj_valid, liveobj_changed
from ableton.v2.control_surface import CompoundComponent
from .device_parameter_bank import create_device_bank
from .parameter_provider import ParameterProvider
from .simpler_slice_nudging import SimplerSliceNudging

class DeviceComponent(ParameterProvider, CompoundComponent):
    """
    Device component that serves as parameter provider for the
    DeviceParameterComponent.
    """
    __events__ = ('device', )
    _provided_parameters = tuple()

    @depends(device_provider=None)
    def __init__(self, device_decorator_factory=None, banking_info=None, device_bank_registry=None, device_provider=None, *a, **k):
        self._bank = None
        self._banking_info = banking_info
        self._decorated_device = None
        self._decorator_factory = device_decorator_factory
        self._device_provider = device_provider
        self._device_bank_registry = device_bank_registry
        super(DeviceComponent, self).__init__(*a, **k)
        self._initialize_subcomponents()
        self.__on_bank_changed.subject = device_bank_registry
        self.__on_provided_device_changed.subject = device_provider
        self.__on_provided_device_changed()
        return

    def set_device(self, device):
        self._device_provider.device = device

    def device(self):
        return self._decorated_device

    def _initialize_subcomponents(self):
        self._slice_nudging = self.register_disconnectable(SimplerSliceNudging())

    @property
    def parameters(self):
        return self._provided_parameters

    @listens('device_bank')
    def __on_bank_changed(self, device, bank):
        self._set_bank_index(device, bank)

    def _set_bank_index(self, device, bank):
        if self._bank is not None:
            self._bank.index = bank
        return

    def _update_parameters(self):
        self._provided_parameters = self._get_provided_parameters()
        self.notify_parameters()

    def _setup_bank(self, device, bank_factory=create_device_bank):
        if self._bank is not None:
            self.disconnect_disconnectable(self._bank)
            self._bank = None
        if liveobj_valid(device):
            self._bank = self.register_disconnectable(bank_factory(device, self._banking_info))
        return

    def _get_decorated_device(self, device):
        if self._decorator_factory is not None:
            return self._decorator_factory.decorate(device)
        else:
            return device

    def _device_changed(self, device):
        current_device = getattr(self.device(), '_live_object', self.device())
        return liveobj_changed(current_device, device)

    @listens('device')
    def __on_provided_device_changed(self):
        self._on_device_changed(self._device_provider.device)

    @listens('parameters')
    def __on_parameters_changed_in_device(self):
        self._update_parameters()

    def _on_device_changed(self, device):
        if self._device_changed(device):
            self._set_device(device)

    def _set_decorated_device(self, decorated_device):
        self._setup_bank(decorated_device)
        self._on_bank_parameters_changed.subject = self._bank
        self._slice_nudging.set_device(decorated_device)
        self._decorated_device = decorated_device

    def _set_device(self, device):
        decorated_device = self._get_decorated_device(device)
        self._set_decorated_device(decorated_device)
        bank_index_for_device = self._device_bank_registry.get_device_bank(device)
        self._set_bank_index(device, bank_index_for_device)
        self.notify_device()
        self._update_parameters()
        self.__on_parameters_changed_in_device.subject = device

    @listens('parameters')
    def _on_bank_parameters_changed(self):
        self._update_parameters()

    def _current_bank_details(self):
        if self._bank is not None:
            return (self._bank.name, self._bank.parameters)
        else:
            return (
             '', [None] * 8)

    def _number_of_parameter_banks(self):
        if self._bank is not None:
            return self._bank.bank_count()
        else:
            return 0

    def _get_provided_parameters(self):
        _, parameters = self._current_bank_details() if self.device() else (None, ())
        return [ self._create_parameter_info(p) for p in parameters ]

    def _create_parameter_info(self, parameter, name):
        raise NotImplementedError()