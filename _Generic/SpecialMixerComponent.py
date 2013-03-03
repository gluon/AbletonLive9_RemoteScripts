#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Generic/SpecialMixerComponent.py
import Live
from _Framework.MixerComponent import MixerComponent
from SelectChanStripComponent import SelectChanStripComponent

class SpecialMixerComponent(MixerComponent):
    """ Class encompassing several selecting channel strips to form a mixer """

    def __init__(self, num_tracks, num_returns = 0, with_eqs = False, with_filters = False):
        MixerComponent.__init__(self, num_tracks, num_returns, with_eqs, with_filters)

    def _create_strip(self):
        return SelectChanStripComponent()