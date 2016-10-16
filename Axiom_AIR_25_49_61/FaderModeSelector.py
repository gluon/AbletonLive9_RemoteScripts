#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/FaderModeSelector.py
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from consts import *

class FaderModeSelector(ModeSelectorComponent):
    """ SelectorComponent that assigns faders to different functions """

    def __init__(self, mixer, device, faders, fader_button_modes, master_fader_button):
        ModeSelectorComponent.__init__(self)
        self._mixer = mixer
        self._device = device
        self._faders = faders
        self._fader_button_modes = fader_button_modes
        self._master_fader_button = master_fader_button
        self._master_fader_button.set_on_off_values(GRN_FULL, LED_OFF)
        self._mode_index = 0
        self._submode_index = 0
        self._number_of_modes = 3

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._mixer = None
        self._device = None
        self._faders = None
        self._fader_button_modes = None
        self._master_fader_button = None

    def set_mode_buttons(self, buttons):
        for button in buttons:
            identify_sender = True
            button.add_value_listener(self._mode_value, identify_sender)
            self._modes_buttons.append(button)

    def number_of_modes(self):
        return self._number_of_modes

    def update(self):
        super(FaderModeSelector, self).update()
        if self.is_enabled():
            self._device.set_allow_update(False)
            self._mixer.set_allow_update(False)
            self._device.set_parameter_controls(())
            for index in range(len(self._faders)):
                strip = self._mixer.channel_strip(index)
                fader = self._faders[index]
                strip.set_volume_control(None)
                fader.release_parameter()
                if self._mode_index <= 1:
                    strip.set_volume_control(fader)

            if self._mode_index == 0:
                self._modes_buttons[0].send_value(AMB_FULL, True)
                self._modes_buttons[1].send_value(LED_OFF, True)
                self._fader_button_modes.set_mix_mode()
                self._mixer.master_strip().set_select_button(None)
                self._master_fader_button.turn_off()
            elif self._mode_index == 1:
                self._modes_buttons[0].send_value(GRN_FULL, True)
                self._modes_buttons[1].send_value(LED_OFF, True)
                self._fader_button_modes.set_track_select_mode()
                self._mixer.master_strip().set_select_button(self._master_fader_button)
            else:
                self._modes_buttons[0].send_value(LED_OFF, True)
                self._modes_buttons[1].send_value(RED_FULL, True)
                self._device.set_parameter_controls(self._faders)
                self._fader_button_modes.set_track_select_mode()
                self._mixer.master_strip().set_select_button(self._master_fader_button)
            self._device.set_allow_update(True)
            self._mixer.set_allow_update(True)

    def _mode_value(self, value, sender):
        if self.is_enabled():
            if value is not 0 or not sender.is_momentary():
                if self._modes_buttons.index(sender) == 0:
                    if self._mode_index != self.number_of_modes() - 1:
                        self._submode_index = (self._submode_index + 1) % (self.number_of_modes() - 1)
                    self.set_mode(self._submode_index)
                else:
                    self.set_mode(self.number_of_modes() - 1)