#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AxiomPro/MixerOrDeviceModeSelector.py
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from _Framework.LogicalDisplaySegment import LogicalDisplaySegment
from EncoderMixerModeSelector import EncoderMixerModeSelector
from PageableDeviceComponent import PageableDeviceComponent
from PeekableEncoderElement import PeekableEncoderElement

class MixerOrDeviceModeSelector(ModeSelectorComponent):
    """ Class that toggles between mixer and device modes """

    def __init__(self, mixer_modes, device, encoders, page_buttons):
        raise isinstance(mixer_modes, EncoderMixerModeSelector) or AssertionError
        raise isinstance(device, PageableDeviceComponent) or AssertionError
        raise isinstance(encoders, tuple) or AssertionError
        raise isinstance(page_buttons, tuple) or AssertionError
        ModeSelectorComponent.__init__(self)
        self._mixer_modes = mixer_modes
        self._device = device
        self._encoders = encoders
        self._page_buttons = page_buttons
        self._peek_button = None
        self._encoders_display = None
        self._value_display = None
        self._device_display = None
        self._page_displays = None
        self._device_dummy_source = DisplayDataSource()
        self._parameter_source = DisplayDataSource()
        self._device_dummy_source.set_display_string('Mixer')
        self._clean_value_display_in = -1
        self._must_update_encoder_display = False
        self._register_timer_callback(self._on_timer)
        identify_sender = True
        for encoder in self._encoders:
            encoder.add_value_listener(self._parameter_value, identify_sender)

        self.set_mode(0)

    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        self._mixer_modes = None
        self._device = None
        self._encoders = None
        self._page_buttons = None
        self._encoders_display = None
        self._value_display = None
        self._device_display = None
        self._page_displays = None
        self._device_dummy_source = None
        self._parameter_source = None
        ModeSelectorComponent.disconnect(self)

    def set_displays(self, encoders_display, value_display, device_display, page_displays):
        if not isinstance(encoders_display, PhysicalDisplayElement):
            raise AssertionError
            raise isinstance(value_display, PhysicalDisplayElement) or AssertionError
            raise isinstance(device_display, PhysicalDisplayElement) or AssertionError
            raise isinstance(page_displays, tuple) or AssertionError
            self._encoders_display = encoders_display
            self._value_display = value_display
            self._device_display = device_display
            self._page_displays = page_displays
            self._value_display != None and self._value_display.segment(0).set_data_source(self._parameter_source)
        self.update()

    def set_peek_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._peek_button != button:
                if self._peek_button != None:
                    self._peek_button.remove_value_listener(self._peek_value)
                self._peek_button = button
                self._peek_button != None and self._peek_button.add_value_listener(self._peek_value)
            self.update()

    def number_of_modes(self):
        return 2

    def update(self):
        super(MixerOrDeviceModeSelector, self).update()
        if self.is_enabled():
            if self._mode_index == 0:
                self._device.set_parameter_controls(None)
                self._device.set_bank_buttons(None)
                self._mixer_modes.set_controls(self._encoders)
                self._mixer_modes.set_modes_buttons(self._page_buttons)
                if self._device_display != None:
                    self._device_display.segment(0).set_data_source(self._mixer_modes.current_page_data_source())
                    self._device_display.update()
                if self._encoders_display != None:
                    for index in range(len(self._encoders)):
                        self._encoders_display.segment(index).set_data_source(self._mixer_modes.parameter_data_source(index))

                    self._encoders_display.update()
                if self._page_displays != None:
                    for index in range(len(self._page_displays)):
                        self._page_displays[index].segment(0).set_data_source(self._mixer_modes.page_name_data_source(index))
                        self._page_displays[index].update()

            elif self._mode_index == 1:
                self._mixer_modes.set_controls(None)
                self._mixer_modes.set_modes_buttons(None)
                self._device.set_parameter_controls(self._encoders)
                self._device.set_bank_buttons(self._page_buttons)
                if self._device_display != None:
                    self._device_display.segment(0).set_data_source(self._device.device_name_data_source())
                    self._device_display.update()
                if self._encoders_display != None:
                    for index in range(len(self._encoders)):
                        self._encoders_display.segment(index).set_data_source(self._device.parameter_name_data_source(index))

                    self._encoders_display.update()
                if self._page_displays != None:
                    for index in range(len(self._page_displays)):
                        self._page_displays[index].segment(0).set_data_source(self._device.page_name_data_source(index))
                        self._page_displays[index].update()

            else:
                print 'Invalid mode index'
                raise False or AssertionError

    def _parameter_value(self, value, control):
        if not control in self._encoders:
            raise AssertionError
            if self.is_enabled():
                parameter = control.mapped_parameter()
                parameter != None and self._parameter_source.set_display_string(parameter.name + ': ' + parameter.__str__())
            else:
                self._parameter_source.set_display_string('<unmapped>')
            self._clean_value_display_in = 20

    def _on_timer(self):
        if self._clean_value_display_in > 0:
            self._clean_value_display_in -= 1
            if self._clean_value_display_in == 0:
                self._parameter_source.set_display_string('')
                self._clean_value_display_in = -1
        if self._must_update_encoder_display:
            self._encoders_display.update()
            self._must_update_encoder_display = False

    def _peek_value(self, value):
        if not self._peek_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            new_peek_mode = value != 0
            peek_changed = False
            for encoder in self._encoders:
                if new_peek_mode != encoder.get_peek_mode():
                    encoder.set_peek_mode(new_peek_mode)
                    peek_changed = True

            self._must_update_encoder_display = peek_changed and self._encoders_display != None and True