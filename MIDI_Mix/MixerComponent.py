#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MIDI_Mix/MixerComponent.py
from _Framework.Control import ButtonControl
from _APC.MixerComponent import MixerComponent as MixerComponentBase

class MixerComponent(MixerComponentBase):
    bank_up_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    bank_down_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)

    def set_send_controls(self, controls):
        self._send_controls = controls
        if controls:
            for index, strip in enumerate(self._channel_strips):
                strip.set_send_controls((controls.get_button(index, 0), controls.get_button(index, 1)))

    @bank_up_button.pressed
    def bank_up_button(self, button):
        new_offset = self._track_offset + len(self._channel_strips)
        if len(self.tracks_to_use()) > new_offset:
            self.set_track_offset(new_offset)

    @bank_down_button.pressed
    def bank_down_button(self, button):
        self.set_track_offset(max(0, self._track_offset - len(self._channel_strips)))