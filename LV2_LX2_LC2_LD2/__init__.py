#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/LV2_LX2_LC2_LD2/__init__.py
import Live
from LV2_LX2_LC2_LD2 import LV2_LX2_LC2_LD2
from FaderfoxScript import FaderfoxScript

def create_instance(c_instance):
    return LV2_LX2_LC2_LD2(c_instance)