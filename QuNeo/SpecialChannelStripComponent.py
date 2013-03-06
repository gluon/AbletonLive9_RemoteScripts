#Embedded file name: /Applications/Ableton Live 8.app/Contents/App-Resources/MIDI Remote Scripts/QuNeo/SpecialChannelStripComponent.py
import Live
from _Framework.ChannelStripComponent import ChannelStripComponent
TRACK_FOLD_DELAY = 5

class SpecialChannelStripComponent(ChannelStripComponent):
    """ Subclass of channel strip component using select button for (un)folding tracks """
    __module__ = __name__

    def __init__(self):
        ChannelStripComponent.__init__(self)
        self._toggle_fold_ticks_delay = -1
        self._register_timer_callback(self._on_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        ChannelStripComponent.disconnect(self)

    def _select_value(self, value):
        ChannelStripComponent._select_value(self, value)
        if self.is_enabled() and self._track != None:
            if self._track.is_foldable and self._select_button.is_momentary() and value != 0:
                self._toggle_fold_ticks_delay = TRACK_FOLD_DELAY
            else:
                self._toggle_fold_ticks_delay = -1

    def _on_timer(self):
        if self.is_enabled() and self._track != None and self._toggle_fold_ticks_delay > -1:
            if not self._track.is_foldable:
                raise AssertionError
                if self._toggle_fold_ticks_delay == 0:
                    self._track.fold_state = not self._track.fold_state
                self._toggle_fold_ticks_delay -= 1