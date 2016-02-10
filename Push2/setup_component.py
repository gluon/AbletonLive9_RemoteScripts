#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/setup_component.py
from __future__ import absolute_import, print_function
from ableton.v2.base import CompoundDisconnectable, SerializableListenableProperties, Subject, clamp, listenable_property
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import RadioButtonControl, StepEncoderControl, ToggleButtonControl, control_list
from ableton.v2.control_surface.mode import ModesComponent
from .pad_velocity_curve import PadVelocityCurveSettings
PAD_SETTING_STEP_SIZE = 20
MIN_USER_FACING_LED_BRIGHTNESS = 13
MIN_USER_FACING_DISPLAY_BRIGHTNESS = 2

class GeneralSettings(Subject):
    workflow = listenable_property.managed('scene')


class HardwareSettings(SerializableListenableProperties):
    min_led_brightness = MIN_USER_FACING_LED_BRIGHTNESS
    max_led_brightness = 127
    led_brightness = listenable_property.managed(max_led_brightness)
    min_display_brightness = MIN_USER_FACING_DISPLAY_BRIGHTNESS
    max_display_brightness = 255
    display_brightness = listenable_property.managed(max_display_brightness)


class DisplayDebugSettings(SerializableListenableProperties):
    show_row_spaces = listenable_property.managed(False)
    show_row_margins = listenable_property.managed(False)
    show_row_middle = listenable_property.managed(False)
    show_button_spaces = listenable_property.managed(False)
    show_unlit_button = listenable_property.managed(False)
    show_lit_button = listenable_property.managed(False)


class ProfilingSettings(SerializableListenableProperties):
    show_qml_stats = listenable_property.managed(False)
    show_usb_stats = listenable_property.managed(False)
    show_realtime_ipc_stats = listenable_property.managed(False)


class ExperimentalSettings(SerializableListenableProperties):
    new_waveform_navigation = listenable_property.managed(False)


class Settings(CompoundDisconnectable):

    def __init__(self, preferences = None, *a, **k):
        raise preferences is not None or AssertionError
        super(Settings, self).__init__(*a, **k)
        self._general = self.register_disconnectable(GeneralSettings())
        self._pad_settings = self.register_disconnectable(preferences.setdefault('settings_pad_velocity_curve', PadVelocityCurveSettings()))
        self._hardware = self.register_disconnectable(preferences.setdefault('settings_hardware', HardwareSettings()))
        self._display_debug = self.register_disconnectable(preferences.setdefault('settings_display_debug', DisplayDebugSettings()))
        self._profiling = self.register_disconnectable(preferences.setdefault('settings_profiling', ProfilingSettings()))
        self._experimental = self.register_disconnectable(preferences.setdefault('experimental', ExperimentalSettings()))

    @property
    def general(self):
        return self._general

    @property
    def pad_settings(self):
        return self._pad_settings

    @property
    def hardware(self):
        return self._hardware

    @property
    def display_debug(self):
        return self._display_debug

    @property
    def profiling(self):
        return self._profiling

    @property
    def experimental(self):
        return self._experimental


class GeneralSettingsComponent(Component):
    workflow_encoder = StepEncoderControl()
    led_brightness_encoder = StepEncoderControl(num_steps=60)
    display_brightness_encoder = StepEncoderControl(num_steps=120)

    def __init__(self, settings = None, hardware_settings = None, *a, **k):
        raise settings is not None or AssertionError
        raise hardware_settings is not None or AssertionError
        super(GeneralSettingsComponent, self).__init__(*a, **k)
        self._settings = settings
        self._hardware_settings = hardware_settings
        self.workflow_encoder.connect_property(settings, 'workflow', lambda v: ('clip' if v > 0 else 'scene'))

    @led_brightness_encoder.value
    def led_brightness_encoder(self, value, encoder):
        self._hardware_settings.led_brightness = clamp(self._hardware_settings.led_brightness + value, self._hardware_settings.min_led_brightness, self._hardware_settings.max_led_brightness)

    @display_brightness_encoder.value
    def display_brightness_encoder(self, value, encoder):
        self._hardware_settings.display_brightness = clamp(self._hardware_settings.display_brightness + value, self._hardware_settings.min_display_brightness, self._hardware_settings.max_display_brightness)


class PadSettingsComponent(Component):
    sensitivity_encoder = StepEncoderControl(num_steps=PAD_SETTING_STEP_SIZE)
    gain_encoder = StepEncoderControl(num_steps=PAD_SETTING_STEP_SIZE)
    dynamics_encoder = StepEncoderControl(num_steps=PAD_SETTING_STEP_SIZE)

    def __init__(self, pad_settings = None, hardware_settings = None, *a, **k):
        raise pad_settings is not None or AssertionError
        super(PadSettingsComponent, self).__init__(*a, **k)
        self._pad_settings = pad_settings

    @sensitivity_encoder.value
    def sensitivity_encoder(self, value, encoder):
        self._pad_settings.sensitivity = clamp(self._pad_settings.sensitivity + value, self._pad_settings.min_sensitivity, self._pad_settings.max_sensitivity)

    @gain_encoder.value
    def gain_encoder(self, value, encoder):
        self._pad_settings.gain = clamp(self._pad_settings.gain + value, self._pad_settings.min_gain, self._pad_settings.max_gain)

    @dynamics_encoder.value
    def dynamics_encoder(self, value, encoder):
        self._pad_settings.dynamics = clamp(self._pad_settings.dynamics + value, self._pad_settings.min_dynamics, self._pad_settings.max_dynamics)


class DisplayDebugSettingsComponent(Component):
    show_row_spaces_button = ToggleButtonControl()
    show_row_margins_button = ToggleButtonControl()
    show_row_middle_button = ToggleButtonControl()
    show_button_spaces_button = ToggleButtonControl()
    show_unlit_button_button = ToggleButtonControl()
    show_lit_button_button = ToggleButtonControl()

    def __init__(self, settings = None, *a, **k):
        raise settings is not None or AssertionError
        super(DisplayDebugSettingsComponent, self).__init__(*a, **k)
        self.show_row_spaces_button.connect_property(settings, 'show_row_spaces')
        self.show_row_margins_button.connect_property(settings, 'show_row_margins')
        self.show_row_middle_button.connect_property(settings, 'show_row_middle')
        self.show_button_spaces_button.connect_property(settings, 'show_button_spaces')
        self.show_unlit_button_button.connect_property(settings, 'show_unlit_button')
        self.show_lit_button_button.connect_property(settings, 'show_lit_button')


class ProfilingSettingsComponent(Component):
    show_qml_stats_button = ToggleButtonControl()
    show_usb_stats_button = ToggleButtonControl()
    show_realtime_ipc_stats_button = ToggleButtonControl()

    def __init__(self, settings = None, *a, **k):
        raise settings is not None or AssertionError
        super(ProfilingSettingsComponent, self).__init__(*a, **k)
        self.show_qml_stats_button.connect_property(settings, 'show_qml_stats')
        self.show_usb_stats_button.connect_property(settings, 'show_usb_stats')
        self.show_realtime_ipc_stats_button.connect_property(settings, 'show_realtime_ipc_stats')


class ExperimentalSettingsComponent(Component):
    new_waveform_navigation_button = ToggleButtonControl()

    def __init__(self, settings = None, *a, **k):
        raise settings is not None or AssertionError
        super(ExperimentalSettingsComponent, self).__init__(*a, **k)
        self.new_waveform_navigation_button.connect_property(settings, 'new_waveform_navigation')


class SetupComponent(ModesComponent):
    category_radio_buttons = control_list(RadioButtonControl, checked_color='Option.Selected', unchecked_color='Option.Unselected')

    def __init__(self, settings = None, pad_curve_sender = None, in_developer_mode = False, *a, **k):
        if not settings is not None:
            raise AssertionError
            super(SetupComponent, self).__init__(*a, **k)
            self._settings = settings
            self._pad_curve_sender = pad_curve_sender
            self._general = self.register_component(GeneralSettingsComponent(settings=settings.general, hardware_settings=settings.hardware, is_enabled=False))
            self._pad_settings = self.register_component(PadSettingsComponent(pad_settings=settings.pad_settings, is_enabled=False))
            self._display_debug = self.register_component(DisplayDebugSettingsComponent(settings=settings.display_debug, is_enabled=False))
            self._profiling = self.register_component(ProfilingSettingsComponent(settings=settings.profiling, is_enabled=False))
            self._experimental = self.register_component(ExperimentalSettingsComponent(settings=settings.experimental, is_enabled=False))
            self.add_mode('Settings', [self._general, self._pad_settings])
            self.add_mode('Info', [])
            in_developer_mode and self.add_mode('Display Debug', [self._display_debug])
            self.add_mode('Profiling', [self._profiling])
            self.add_mode('Experimental', [self._experimental])
        self.selected_mode = 'Settings'
        self.category_radio_buttons.control_count = len(self.modes)
        self.category_radio_buttons.checked_index = 0

    @property
    def general(self):
        return self._general

    @property
    def pad_settings(self):
        return self._pad_settings

    @property
    def display_debug(self):
        return self._display_debug

    @property
    def profiling(self):
        return self._profiling

    @property
    def experimental(self):
        return self._experimental

    @property
    def settings(self):
        return self._settings

    @property
    def velocity_curve(self):
        return self._pad_curve_sender

    @category_radio_buttons.checked
    def category_radio_buttons(self, button):
        self.selected_mode = self.modes[button.index]