#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_MK2/__init__.py
from .Launchpad_MK2 import Launchpad_MK2
from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=5042, product_ids=[105,
                         106,
                         107,
                         108,
                         109,
                         110,
                         111,
                         112,
                         113,
                         114,
                         115,
                         116,
                         117,
                         118,
                         119,
                         120], model_name=['Launchpad MK2',
                         'Launchpad MK2 2',
                         'Launchpad MK2 3',
                         'Launchpad MK2 4',
                         'Launchpad MK2 5',
                         'Launchpad MK2 6',
                         'Launchpad MK2 7',
                         'Launchpad MK2 8',
                         'Launchpad MK2 9',
                         'Launchpad MK2 10',
                         'Launchpad MK2 11',
                         'Launchpad MK2 12',
                         'Launchpad MK2 13',
                         'Launchpad MK2 14',
                         'Launchpad MK2 15',
                         'Launchpad MK2 16']),
     PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT, REMOTE]), outport(props=[NOTES_CC,
                  SCRIPT,
                  SYNC,
                  REMOTE])]}


def create_instance(c_instance):
    return Launchpad_MK2(c_instance)