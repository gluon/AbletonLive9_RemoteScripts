#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/MixerComponent.py
from itertools import izip_longest
from _Framework.Control import control_list, ButtonControl
from _Framework.ChannelStripComponent import ChannelStripComponent as ChannelStripComponentBase
from _Framework.MixerComponent import MixerComponent as MixerComponentBase

class ChannelStripComponent(ChannelStripComponentBase):
    send_lights = control_list(ButtonControl, control_count=2, color='Mixer.Sends', disabled_color='Mixer.NoTrack')
    pan_light = ButtonControl(color='Mixer.Pans', disabled_color='Mixer.NoTrack')

    def set_track(self, track):
        super(ChannelStripComponent, self).set_track(track)
        self.pan_light.enabled = bool(track)
        for light in self.send_lights:
            light.enabled = bool(track)


class MixerComponent(MixerComponentBase):
    next_sends_button = ButtonControl()
    prev_sends_button = ButtonControl()

    def __init__(self, *a, **k):
        super(MixerComponent, self).__init__(*a, **k)
        self._update_send_buttons()

    def _create_strip(self):
        return ChannelStripComponent()

    def set_send_controls(self, controls):
        self._send_controls = controls
        for index, channel_strip in enumerate(self._channel_strips):
            if self.send_index is None:
                channel_strip.set_send_controls([None])
            else:
                send_controls = [ controls.get_button(index, i) for i in xrange(2) ] if controls else [None]
                skipped_sends = [ None for _ in xrange(self.send_index) ]
                channel_strip.set_send_controls(skipped_sends + send_controls)

    def set_send_lights(self, lights):
        for index, channel_strip in enumerate(self._channel_strips):
            elements = None
            if lights is not None:
                lights.reset()
                elements = None if self.send_index is None else [ lights.get_button(index, i) for i in xrange(2) ]
            channel_strip.send_lights.set_control_element(elements)

    def set_pan_lights(self, lights):
        for strip, light in izip_longest(self._channel_strips, lights or []):
            strip.pan_light.set_control_element(light)

    def _get_send_index(self):
        return super(MixerComponent, self)._get_send_index()

    def _set_send_index(self, index):
        if index is not None and index % 2 > 0:
            index -= 1
        super(MixerComponent, self)._set_send_index(index)
        self._update_send_buttons()

    send_index = property(_get_send_index, _set_send_index)

    def _update_send_buttons(self):
        self.next_sends_button.enabled = self.send_index is not None and self.send_index < self.num_sends - 2
        self.prev_sends_button.enabled = self.send_index is not None and self.send_index > 0

    @next_sends_button.pressed
    def next_sends_button(self, button):
        self.send_index = min(self.send_index + 2, self.num_sends - 1)

    @prev_sends_button.pressed
    def prev_sends_button(self, button):
        self.send_index = max(self.send_index - 2, 0)

    def set_track_select_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.TrackSelected', 'Mixer.TrackUnselected')
            strip.set_select_button(button)

    def set_solo_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.SoloOn', 'Mixer.SoloOff')
            strip.set_solo_button(button)

    def set_mute_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.MuteOn', 'Mixer.MuteOff')
            strip.set_mute_button(button)

    def set_arm_buttons(self, buttons):
        for strip, button in izip_longest(self._channel_strips, buttons or []):
            if button:
                button.set_on_off_values('Mixer.ArmSelected', 'Mixer.ArmUnselected')
            strip.set_arm_button(button)