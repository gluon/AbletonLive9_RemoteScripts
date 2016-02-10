#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/__init__.py
from Axiom_AIR_25_49_61 import Axiom_AIR_25_49_61
from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=1891, product_ids=[8243], model_name='Axiom AIR 49'),
     PORTS_KEY: [inport(props=[NOTES_CC]),
                 inport(props=[SCRIPT]),
                 inport(props=[NOTES_CC]),
                 outport(props=[NOTES_CC]),
                 outport(props=[SCRIPT])]}


def create_instance(c_instance):
    return Axiom_AIR_25_49_61(c_instance)