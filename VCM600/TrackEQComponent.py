#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/VCM600/TrackEQComponent.py
import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.EncoderElement import EncoderElement
from _Generic.Devices import get_parameter_by_name
EQ_DEVICES = {'Eq8': {'Gains': [ '%i Gain A' % (index + 1) for index in range(8) ]},
 'FilterEQ3': {'Gains': ['GainLo', 'GainMid', 'GainHi'],
               'Cuts': ['LowOn', 'MidOn', 'HighOn']}}

class TrackEQComponent(ControlSurfaceComponent):
    """ Class representing a track's EQ, it attaches to the last EQ device in the track """

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._track = None
        self._device = None
        self._gain_controls = None
        self._cut_buttons = None

    def disconnect(self):
        if self._gain_controls != None:
            for control in self._gain_controls:
                control.release_parameter()

            self._gain_controls = None
        if self._cut_buttons != None:
            for button in self._cut_buttons:
                button.remove_value_listener(self._cut_value)

        self._cut_buttons = None
        if self._track != None:
            self._track.remove_devices_listener(self._on_devices_changed)
            self._track = None
        self._device = None
        if self._device != None:
            device_dict = EQ_DEVICES[self._device.class_name]
            if 'Cuts' in device_dict.keys():
                cut_names = device_dict['Cuts']
                for cut_name in cut_names:
                    parameter = get_parameter_by_name(self._device, cut_name)
                    if parameter != None and parameter.value_has_listener(self._on_cut_changed):
                        parameter.remove_value_listener(self._on_cut_changed)

    def on_enabled_changed(self):
        self.update()

    def set_track(self, track):
        if not (track == None or isinstance(track, Live.Track.Track)):
            raise AssertionError
            if self._track != None:
                self._track.remove_devices_listener(self._on_devices_changed)
                if self._gain_controls != None and self._device != None:
                    for control in self._gain_controls:
                        control.release_parameter()

            self._track = track
            self._track != None and self._track.add_devices_listener(self._on_devices_changed)
        self._on_devices_changed()

    def set_cut_buttons(self, buttons):
        if not (buttons == None or isinstance(buttons, tuple)):
            raise AssertionError
            if buttons != self._cut_buttons and self._cut_buttons != None:
                for button in self._cut_buttons:
                    button.remove_value_listener(self._cut_value)

            self._cut_buttons = buttons
            if self._cut_buttons != None:
                for button in self._cut_buttons:
                    button.add_value_listener(self._cut_value, identify_sender=True)

            self.update()

    def set_gain_controls(self, controls):
        raise controls != None or AssertionError
        raise isinstance(controls, tuple) or AssertionError
        if self._device != None and self._gain_controls != None:
            for control in self._gain_controls:
                control.release_parameter()

        for control in controls:
            raise control != None or AssertionError
            raise isinstance(control, EncoderElement) or AssertionError

        self._gain_controls = controls
        self.update()

    def update(self):
        super(TrackEQComponent, self).update()
        if self.is_enabled() and self._device != None:
            device_dict = EQ_DEVICES[self._device.class_name]
            if self._gain_controls != None:
                gain_names = device_dict['Gains']
                for index in range(len(self._gain_controls)):
                    self._gain_controls[index].release_parameter()
                    if len(gain_names) > index:
                        parameter = get_parameter_by_name(self._device, gain_names[index])
                        if parameter != None:
                            self._gain_controls[index].connect_to(parameter)

            if self._cut_buttons != None and 'Cuts' in device_dict.keys():
                cut_names = device_dict['Cuts']
                for index in range(len(self._cut_buttons)):
                    self._cut_buttons[index].turn_off()
                    if len(cut_names) > index:
                        parameter = get_parameter_by_name(self._device, cut_names[index])
                        if parameter != None:
                            if parameter.value == 0.0:
                                self._cut_buttons[index].turn_on()
                            if not parameter.value_has_listener(self._on_cut_changed):
                                parameter.add_value_listener(self._on_cut_changed)

        else:
            if self._cut_buttons != None:
                for button in self._cut_buttons:
                    if button != None:
                        button.turn_off()

            if self._gain_controls != None:
                for control in self._gain_controls:
                    control.release_parameter()

    def _cut_value(self, value, sender):
        if not sender in self._cut_buttons:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled() and self._device != None:
                    if not sender.is_momentary() or value is not 0:
                        device_dict = EQ_DEVICES[self._device.class_name]
                        if 'Cuts' in device_dict.keys():
                            cut_names = device_dict['Cuts']
                            index = list(self._cut_buttons).index(sender)
                            parameter = index in range(len(cut_names)) and get_parameter_by_name(self._device, cut_names[index])
                            parameter.value = parameter != None and parameter.is_enabled and float(int(parameter.value + 1) % 2)

    def _on_devices_changed(self):
        if self._device != None:
            device_dict = EQ_DEVICES[self._device.class_name]
            if 'Cuts' in device_dict.keys():
                cut_names = device_dict['Cuts']
                for cut_name in cut_names:
                    parameter = get_parameter_by_name(self._device, cut_name)
                    if parameter != None and parameter.value_has_listener(self._on_cut_changed):
                        parameter.remove_value_listener(self._on_cut_changed)

        self._device = None
        if self._track != None:
            for index in range(len(self._track.devices)):
                device = self._track.devices[-1 * (index + 1)]
                if device.class_name in EQ_DEVICES.keys():
                    self._device = device
                    break

        self.update()

    def _on_cut_changed(self):
        if not self._device != None:
            raise AssertionError
            raise 'Cuts' in EQ_DEVICES[self._device.class_name].keys() or AssertionError
            cut_names = self.is_enabled() and self._cut_buttons != None and EQ_DEVICES[self._device.class_name]['Cuts']
            for index in range(len(self._cut_buttons)):
                self._cut_buttons[index].turn_off()
                if len(cut_names) > index:
                    parameter = get_parameter_by_name(self._device, cut_names[index])
                    if parameter != None and parameter.value == 0.0:
                        self._cut_buttons[index].turn_on()