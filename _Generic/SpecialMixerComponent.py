#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_Generic/SpecialMixerComponent.py
import Live
from _Framework.MixerComponent import MixerComponent
from SelectChanStripComponent import SelectChanStripComponent

class SpecialMixerComponent(MixerComponent):
    """ Class encompassing several selecting channel strips to form a mixer """

    def _create_strip(self):
        return SelectChanStripComponent()