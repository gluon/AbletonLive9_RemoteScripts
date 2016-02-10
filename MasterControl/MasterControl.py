#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MasterControl/MasterControl.py
from MackieControl.MackieControl import MackieControl

class MasterControl(MackieControl):
    """ Main class derived from MackieControl """

    def __init__(self, c_instance):
        MackieControl.__init__(self, c_instance)