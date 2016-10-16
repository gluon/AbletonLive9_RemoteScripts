#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/APC20/SliderModesComponent.py
from _Framework.ButtonElement import ButtonElement
from _Framework.ModeSelectorComponent import ModeSelectorComponent

class SliderModesComponent(ModeSelectorComponent):
    """ SelectorComponent that assigns sliders to different functions """

    def __init__(self, mixer, sliders, *a, **k):
        raise len(sliders) == 8 or AssertionError
        super(SliderModesComponent, self).__init__(*a, **k)
        self._mixer = mixer
        self._sliders = sliders
        self._mode_index = 0

    def disconnect(self):
        super(SliderModesComponent, self).disconnect()
        self._mixer = None
        self._sliders = None

    def set_mode_buttons(self, buttons):
        raise isinstance(buttons, (tuple, type(None))) or AssertionError
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)

        self._modes_buttons = []
        if buttons != None:
            for button in buttons:
                raise isinstance(button, ButtonElement) or AssertionError
                identify_sender = True
                button.add_value_listener(self._mode_value, identify_sender)
                self._modes_buttons.append(button)

        self.update()

    def number_of_modes(self):
        return 8

    def update(self):
        super(SliderModesComponent, self).update()
        if not (self.is_enabled() and self._mode_index in range(self.number_of_modes())):
            raise AssertionError
            for index in range(len(self._modes_buttons)):
                if index == self._mode_index:
                    self._modes_buttons[index].turn_on()
                else:
                    self._modes_buttons[index].turn_off()

            for index in range(len(self._sliders)):
                strip = self._mixer.channel_strip(index)
                slider = self._sliders[index]
                slider.use_default_message()
                slider.set_identifier(slider.message_identifier() - self._mode_index)
                strip.set_volume_control(None)
                strip.set_pan_control(None)
                strip.set_send_controls((None, None, None))
                slider.release_parameter()
                if self._mode_index == 0:
                    strip.set_volume_control(slider)
                elif self._mode_index == 1:
                    strip.set_pan_control(slider)
                elif self._mode_index < 5:
                    send_controls = [None, None, None]
                    send_controls[self._mode_index - 2] = slider
                    strip.set_send_controls(tuple(send_controls))