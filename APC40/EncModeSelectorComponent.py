#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC40/EncModeSelectorComponent.py
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.MixerComponent import MixerComponent

class EncModeSelectorComponent(ModeSelectorComponent):
    """ Class that reassigns encoders on the AxiomPro to different mixer functions """

    def __init__(self, mixer):
        raise isinstance(mixer, MixerComponent) or AssertionError
        ModeSelectorComponent.__init__(self)
        self._controls = None
        self._mixer = mixer

    def disconnect(self):
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)

        self._controls = None
        self._mixer = None
        ModeSelectorComponent.disconnect(self)

    def set_modes_buttons(self, buttons):
        raise buttons == None or isinstance(buttons, tuple) or len(buttons) == self.number_of_modes() or AssertionError
        identify_sender = True
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)

        self._modes_buttons = []
        if buttons != None:
            for button in buttons:
                raise isinstance(button, ButtonElement) or AssertionError
                self._modes_buttons.append(button)
                button.add_value_listener(self._mode_value, identify_sender)

        self.set_mode(0)
        self.update()

    def set_controls(self, controls):
        raise controls == None or isinstance(controls, tuple) and len(controls) == 8 or AssertionError
        self._controls = controls
        self.set_mode(0)
        self.update()

    def number_of_modes(self):
        return 4

    def on_enabled_changed(self):
        self.update()

    def update(self):
        if not self._modes_buttons != None:
            raise AssertionError
            if self.is_enabled() and self._modes_buttons != None:
                for button in self._modes_buttons:
                    if self._modes_buttons.index(button) == self._mode_index:
                        button.turn_on()
                    else:
                        button.turn_off()

            if self._controls != None:
                for index in range(len(self._controls)):
                    if self._mode_index == 0:
                        self._mixer.channel_strip(index).set_pan_control(self._controls[index])
                        self._mixer.channel_strip(index).set_send_controls((None, None, None))
                    elif self._mode_index == 1:
                        self._mixer.channel_strip(index).set_pan_control(None)
                        self._mixer.channel_strip(index).set_send_controls((self._controls[index], None, None))
                    elif self._mode_index == 2:
                        self._mixer.channel_strip(index).set_pan_control(None)
                        self._mixer.channel_strip(index).set_send_controls((None, self._controls[index], None))
                    elif self._mode_index == 3:
                        self._mixer.channel_strip(index).set_pan_control(None)
                        self._mixer.channel_strip(index).set_send_controls((None, None, self._controls[index]))
                    else:
                        print 'Invalid mode index'
                        raise False or AssertionError