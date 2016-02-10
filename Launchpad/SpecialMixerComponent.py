#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad/SpecialMixerComponent.py
import Live
from _Framework.MixerComponent import MixerComponent
from DefChannelStripComponent import DefChannelStripComponent
from _Framework.ButtonElement import ButtonElement

class SpecialMixerComponent(MixerComponent):
    """ Class encompassing several defaultable channel strips to form a mixer """

    def __init__(self, num_tracks, num_returns = 0):
        MixerComponent.__init__(self, num_tracks, num_returns)
        self._unarm_all_button = None
        self._unsolo_all_button = None
        self._unmute_all_button = None

    def disconnect(self):
        if self._unarm_all_button != None:
            self._unarm_all_button.remove_value_listener(self._unarm_all_value)
            self._unarm_all_button = None
        if self._unsolo_all_button != None:
            self._unsolo_all_button.remove_value_listener(self._unsolo_all_value)
            self._unsolo_all_button = None
        if self._unmute_all_button != None:
            self._unmute_all_button.remove_value_listener(self._unmute_all_value)
            self._unmute_all_button = None
        MixerComponent.disconnect(self)

    def set_global_buttons(self, unarm_all, unsolo_all, unmute_all):
        if not isinstance(unarm_all, (ButtonElement, type(None))):
            raise AssertionError
            raise isinstance(unsolo_all, (ButtonElement, type(None))) or AssertionError
            if not isinstance(unmute_all, (ButtonElement, type(None))):
                raise AssertionError
                if self._unarm_all_button != None:
                    self._unarm_all_button.remove_value_listener(self._unarm_all_value)
                self._unarm_all_button = unarm_all
                if self._unarm_all_button != None:
                    self._unarm_all_button.add_value_listener(self._unarm_all_value)
                    self._unarm_all_button.turn_off()
                if self._unsolo_all_button != None:
                    self._unsolo_all_button.remove_value_listener(self._unsolo_all_value)
                self._unsolo_all_button = unsolo_all
                if self._unsolo_all_button != None:
                    self._unsolo_all_button.add_value_listener(self._unsolo_all_value)
                    self._unsolo_all_button.turn_off()
                self._unmute_all_button != None and self._unmute_all_button.remove_value_listener(self._unmute_all_value)
            self._unmute_all_button = unmute_all
            self._unmute_all_button != None and self._unmute_all_button.add_value_listener(self._unmute_all_value)
            self._unmute_all_button.turn_off()

    def _create_strip(self):
        return DefChannelStripComponent()

    def _unarm_all_value(self, value):
        raise self.is_enabled() or AssertionError
        raise self._unarm_all_button != None or AssertionError
        raise value in range(128) or AssertionError
        if value != 0 or not self._unarm_all_button.is_momentary():
            for track in self.song().tracks:
                if track.can_be_armed and track.arm:
                    track.arm = False

    def _unsolo_all_value(self, value):
        raise self.is_enabled() or AssertionError
        raise self._unsolo_all_button != None or AssertionError
        raise value in range(128) or AssertionError
        if value != 0 or not self._unsolo_all_button.is_momentary():
            for track in tuple(self.song().tracks) + tuple(self.song().return_tracks):
                if track.solo:
                    track.solo = False

    def _unmute_all_value(self, value):
        raise self.is_enabled() or AssertionError
        raise self._unmute_all_button != None or AssertionError
        raise value in range(128) or AssertionError
        if value != 0 or not self._unmute_all_button.is_momentary():
            for track in tuple(self.song().tracks) + tuple(self.song().return_tracks):
                if track.mute:
                    track.mute = False