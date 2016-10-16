#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Novation_Impulse/__init__.py
from Novation_Impulse import Novation_Impulse

def create_instance(c_instance):
    return Novation_Impulse(c_instance)


from _Framework.Capabilities import *

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661, product_ids=[25], model_name='Impulse 25'),
     PORTS_KEY: [inport(props=[NOTES_CC, REMOTE, SCRIPT]), inport(props=[NOTES_CC, REMOTE]), outport(props=[NOTES_CC, REMOTE, SCRIPT])]}