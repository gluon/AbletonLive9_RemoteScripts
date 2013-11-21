#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/APC40/__init__.py
from APC40 import APC40

def create_instance(c_instance):
    """ Creates and returns the APC40 script """
    return APC40(c_instance)


from _Framework.Capabilities import *

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536, product_ids=[115], model_name='Akai APC40'),
     PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT, REMOTE]), outport(props=[SCRIPT, REMOTE])]}