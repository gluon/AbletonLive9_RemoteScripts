#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/LV2_LX2_LC2_LD2/LV2_LX2_LC2_LD2.py
import Live
from FaderfoxScript import FaderfoxScript
from LV2MixerController import LV2MixerController
from LV2DeviceController import LV2DeviceController
from FaderfoxDeviceController import FaderfoxDeviceController
from LV2TransportController import LV2TransportController
from consts import *

class LV2_LX2_LC2_LD2(FaderfoxScript):
    __module__ = __name__
    __doc__ = 'Automap script for LV2 Faderfox controllers'
    __name__ = 'LV2_LX2_LC2_LD2 Remote Script'

    def __init__(self, c_instance):
        LV2_LX2_LC2_LD2.realinit(self, c_instance)

    def realinit(self, c_instance):
        self.suffix = '2'
        FaderfoxScript.realinit(self, c_instance)
        self.mixer_controller = LV2MixerController(self)
        self.device_controller = LV2DeviceController(self)
        self.transport_controller = LV2TransportController(self)
        self.components = [self.mixer_controller, self.device_controller, self.transport_controller]

    def suggest_map_mode(self, cc_no, channel):
        return -1