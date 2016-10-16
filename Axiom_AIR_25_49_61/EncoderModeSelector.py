#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/EncoderModeSelector.py
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from consts import *

class EncoderModeSelector(ModeSelectorComponent):
    """ SelectorComponent that assigns encoders to different functions """

    def __init__(self, mixer, device, encoders):
        ModeSelectorComponent.__init__(self)
        self._mixer = mixer
        self._device = device
        self._encoders = encoders
        self._mode_index = 1
        self._submode_index = 1
        self._number_of_modes = 4

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._mixer = None
        self._device = None
        self._encoders = None

    def set_mode_buttons(self, buttons):
        for button in buttons:
            identify_sender = True
            button.add_value_listener(self._mode_value, identify_sender)
            self._modes_buttons.append(button)

    def number_of_modes(self):
        return self._number_of_modes

    def update(self):
        super(EncoderModeSelector, self).update()
        if self.is_enabled():
            self._device.set_allow_update(False)
            self._mixer.set_allow_update(False)
            self._device.set_parameter_controls(())
            self._mixer.set_send_controls(())
            for index in range(len(self._encoders)):
                strip = self._mixer.channel_strip(index)
                encoder = self._encoders[index]
                strip.set_volume_control(None)
                strip.set_pan_control(None)
                encoder.release_parameter()
                if self._mode_index == 0:
                    strip.set_volume_control(encoder)
                    encoder.set_on_off_values(AMB_FULL, LED_OFF)
                elif self._mode_index == 1:
                    strip.set_pan_control(encoder)
                    encoder.set_on_off_values(RED_FULL, LED_OFF)
                elif self._mode_index == 2:
                    encoder.set_on_off_values(GRN_FULL, LED_OFF)
                elif self._mode_index == 3:
                    encoder.set_on_off_values(RED_FULL, LED_OFF)

            if self._mode_index == 0:
                self._modes_buttons[0].send_value(AMB_FULL, True)
                self._modes_buttons[1].send_value(LED_OFF, True)
            elif self._mode_index == 1:
                self._modes_buttons[0].send_value(RED_FULL, True)
                self._modes_buttons[1].send_value(LED_OFF, True)
            elif self._mode_index == 2:
                self._modes_buttons[0].send_value(GRN_FULL, True)
                self._modes_buttons[1].send_value(LED_OFF, True)
                self._mixer.set_send_controls(self._encoders)
            elif self._mode_index == 3:
                self._modes_buttons[0].send_value(LED_OFF, True)
                self._modes_buttons[1].send_value(RED_FULL, True)
                self._device.set_parameter_controls(self._encoders)
            self._device.set_allow_update(True)
            self._mixer.set_allow_update(True)

    def _mode_value(self, value, sender):
        if self.is_enabled() and value is not 0 or not sender.is_momentary():
            if self._modes_buttons.index(sender) == 0:
                if self._mode_index != self.number_of_modes() - 1:
                    self._submode_index = (self._submode_index + 1) % (self.number_of_modes() - 1)
                self.set_mode(self._submode_index)
            else:
                self.set_mode(self.number_of_modes() - 1)