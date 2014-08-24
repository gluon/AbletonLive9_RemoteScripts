#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/LV2_LX2_LC2_LD2/LV2DeviceController.py
import Live
from FaderfoxDeviceController import FaderfoxDeviceController

class LV2DeviceController(FaderfoxDeviceController):
    __module__ = __name__

    def __init__(self, parent):
        LV2DeviceController.realinit(self, parent)

    def realinit(self, parent):
        FaderfoxDeviceController.realinit(self, parent)