#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AIRA_MX_1/__init__.py
from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, SCRIPT, controller_id, inport, outport
from RolandMX1 import RolandMX1

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=1410, product_ids=[419], model_name=['MX-1']),
     PORTS_KEY: [inport(props=[]),
                 inport(props=[SCRIPT]),
                 outport(props=[]),
                 outport(props=[SCRIPT])]}


def create_instance(c_instance):
    return RolandMX1(c_instance=c_instance)