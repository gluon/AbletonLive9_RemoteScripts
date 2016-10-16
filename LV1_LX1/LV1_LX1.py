#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/LV1_LX1/LV1_LX1.py
from LV2_LX2_LC2_LD2.FaderfoxComponent import FaderfoxComponent
from LV2_LX2_LC2_LD2.FaderfoxScript import FaderfoxScript
from LV2_LX2_LC2_LD2.FaderfoxMixerController import FaderfoxMixerController
from LV2_LX2_LC2_LD2.FaderfoxDeviceController import FaderfoxDeviceController
from LV2_LX2_LC2_LD2.FaderfoxTransportController import FaderfoxTransportController

class LV1_LX1(FaderfoxScript):
    __module__ = __name__
    __doc__ = 'Automap script for LV1 Faderfox controllers'
    __name__ = 'LV1_LX1 Remote Script'

    def __init__(self, c_instance):
        LV1_LX1.realinit(self, c_instance)

    def realinit(self, c_instance):
        self.suffix = '1'
        FaderfoxScript.realinit(self, c_instance)
        self.is_lv1 = True
        self.log('lv1 lx1')
        self.mixer_controller = FaderfoxMixerController(self)
        self.device_controller = FaderfoxDeviceController(self)
        self.transport_controller = FaderfoxTransportController(self)
        self.components = [self.mixer_controller, self.device_controller, self.transport_controller]