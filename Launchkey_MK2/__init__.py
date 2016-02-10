#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchkey_MK2/__init__.py
import _Framework.Capabilities as caps
from .Launchkey_MK2 import Launchkey_MK2

def get_capabilities():
    return {caps.CONTROLLER_ID_KEY: caps.controller_id(vendor_id=4661, product_ids=[31610,
                              31866,
                              32122,
                              123,
                              124,
                              125], model_name=['Launchkey MK2 25', 'Launchkey MK2 49', 'Launchkey MK2 61']),
     caps.PORTS_KEY: [caps.inport(props=[]),
                      caps.inport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE]),
                      caps.outport(props=[]),
                      caps.outport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE])]}


def create_instance(c_instance):
    return Launchkey_MK2(c_instance)