#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/MasterControl/MasterControl.py
from MackieControl.MackieControl import MackieControl

class MasterControl(MackieControl):
    """ Main class derived from MackieControl """

    def __init__(self, c_instance):
        MackieControl.__init__(self, c_instance)