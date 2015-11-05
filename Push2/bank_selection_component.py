#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/bank_selection_component.py
from __future__ import absolute_import
from ableton.v2.base import NamedTuple, listenable_property, listens, listens_group, liveobj_valid, SlotManager, nop
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import control_list, forward_control, ButtonControl
from .item_lister_component import ItemListerComponent, ItemProvider
from .bank_definitions import MAIN_KEY

class BankProvider(ItemProvider, SlotManager):

    def __init__(self, bank_registry = None, banking_info = None, *a, **k):
        raise bank_registry is not None or AssertionError
        raise banking_info is not None or AssertionError
        super(BankProvider, self).__init__(*a, **k)
        self._bank_registry = bank_registry
        self._banking_info = banking_info
        self._device = None
        self._on_device_bank_changed.subject = bank_registry

    def set_device(self, device):
        if self._device != device:
            self._device = device
            self.notify_items()
            self.notify_selected_item()

    @property
    def device(self):
        return self._device

    @property
    def items(self):
        nesting_level = 0
        bank_names = self.internal_bank_names(self._banking_info.device_bank_names(self._device))
        return [ (NamedTuple(name=b), nesting_level) for b in bank_names ]

    @property
    def selected_item(self):
        selected = None
        if liveobj_valid(self._device) and len(self.items) > 0:
            bank_index = self._bank_registry.get_device_bank(self._device)
            selected = self.items[bank_index][0]
        return selected

    def select_item(self, item):
        nesting_level = 0
        bank_index = self.items.index((item, nesting_level))
        self._bank_registry.set_device_bank(self._device, bank_index)

    @listens('device_bank')
    def _on_device_bank_changed(self, device, _):
        if device == self._device:
            self.notify_selected_item()

    def internal_bank_names(self, original_bank_names):
        num_banks = len(original_bank_names)
        return original_bank_names if num_banks > 0 else [MAIN_KEY]


class EditModeOptionsComponent(Component):
    option_buttons = control_list(ButtonControl, color='ItemNavigation.ItemSelected', control_count=8)

    def __init__(self, back_callback = nop, device_options_provider = None, *a, **k):
        super(EditModeOptionsComponent, self).__init__(*a, **k)
        self._device = None
        self._device_options_provider = device_options_provider
        self._back = back_callback
        self.__on_device_changed.subject = device_options_provider
        self.__on_options_changed.subject = device_options_provider
        self._update_button_feedback()

    def _option_for_button(self, button):
        options = self.options
        return options[button.index - 1] if len(options) > button.index - 1 else None

    @option_buttons.pressed
    def option_buttons(self, button):
        if button.index == 0:
            self._back()
        else:
            option = self._option_for_button(button)
            if option:
                try:
                    option.trigger()
                except RuntimeError:
                    pass

    def _set_device(self, device):
        self._device = device
        self.__on_device_name_changed.subject = device
        self.notify_device()

    @listenable_property
    def device(self):
        return self._device.name if liveobj_valid(self._device) else ''

    @listenable_property
    def options(self):
        return self._device_options_provider.options if self._device_options_provider else []

    @listens('device')
    def __on_device_changed(self):
        self._update_device()

    @listens('name')
    def __on_device_name_changed(self):
        self.notify_device()

    @listens('options')
    def __on_options_changed(self):
        self.__on_active_options_changed.replace_subjects(self.options)
        self._update_button_feedback()
        self.notify_options()

    @listens_group('active')
    def __on_active_options_changed(self, _):
        self._update_button_feedback()

    def _update_button_feedback(self):
        for button in self.option_buttons:
            if button.index > 0:
                option = self._option_for_button(button)
                has_active_option = option and option.active
                button.color = 'ItemNavigation.' + ('ItemNotSelected' if has_active_option else 'NoItem')

    def _update_device(self):
        self._set_device(self._device_options_provider.device())

    def update(self):
        super(EditModeOptionsComponent, self).update()
        if self.is_enabled():
            self._update_device()


class BankSelectionComponent(ItemListerComponent):
    __events__ = ('back',)
    select_buttons = forward_control(ItemListerComponent.select_buttons)

    def __init__(self, bank_registry = None, banking_info = None, device_options_provider = None, *a, **k):
        self._bank_provider = BankProvider(bank_registry=bank_registry, banking_info=banking_info)
        super(BankSelectionComponent, self).__init__(item_provider=self._bank_provider, *a, **k)
        self._options = self.register_component(EditModeOptionsComponent(back_callback=self.notify_back, device_options_provider=device_options_provider))
        self.register_disconnectable(self._bank_provider)

    @select_buttons.checked
    def select_buttons(self, button):
        self._bank_provider.select_item(self.items[button.index].item)

    def set_option_buttons(self, buttons):
        self._options.option_buttons.set_control_element(buttons)

    def set_device(self, item):
        device = item if item != self._bank_provider.device else None
        self._bank_provider.set_device(device)

    @property
    def options(self):
        return self._options