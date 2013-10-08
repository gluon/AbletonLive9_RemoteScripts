#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Novation_Impulse/__init__.py
from Novation_Impulse2 import Novation_Impulse2

def create_instance(c_instance):
    return Novation_Impulse2(c_instance)


from _Framework.Capabilities import *

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661, product_ids=[25], model_name='Impulse 25'),
     PORTS_KEY: [inport(props=[NOTES_CC, REMOTE, SCRIPT]), inport(props=[NOTES_CC, REMOTE]), outport(props=[NOTES_CC, REMOTE, SCRIPT])]}