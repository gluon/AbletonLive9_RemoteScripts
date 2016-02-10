#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AIRA_MX_1/NotifyingMixerComponent.py
from _Framework.MixerComponent import MixerComponent
from _Framework.Control import ButtonControl

class NotifyingMixerComponent(MixerComponent):
    """
    Special mixer class that uses return tracks alongside midi and
    audio tracks and includes controls for incrementing/decrementing
    between sends.
    """
    send_index_up_button = ButtonControl()
    send_index_down_button = ButtonControl()
    modifier_button = ButtonControl(color=0, pressed_color=127)

    def tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    @send_index_up_button.pressed
    def send_index_up_button(self, button):
        self._adjust_send_index(1)

    @send_index_down_button.pressed
    def send_index_down_button(self, button):
        self._adjust_send_index(-1)

    def _adjust_send_index(self, factor):
        new_index = self.send_index + factor
        if 0 <= new_index < self.num_sends:
            self.send_index = new_index
            self._show_msg_callback('Tone/Filter Controlling Send: %s' % self.song().return_tracks[self.send_index].name)