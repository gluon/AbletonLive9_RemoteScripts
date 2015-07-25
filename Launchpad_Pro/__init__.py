#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Launchpad_Pro/__init__.py
from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad_Pro import Launchpad_Pro

def create_instance(c_instance):
    return Launchpad_Pro(c_instance)


def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661, product_ids=[81,
                         82,
                         83,
                         84,
                         85,
                         86,
                         87,
                         88,
                         89,
                         90,
                         91,
                         92,
                         93,
                         94,
                         95,
                         96], model_name=['Launchpad Pro',
                         'Launchpad Pro 2',
                         'Launchpad Pro 3',
                         'Launchpad Pro 4',
                         'Launchpad Pro 5',
                         'Launchpad Pro 6',
                         'Launchpad Pro 7',
                         'Launchpad Pro 8',
                         'Launchpad Pro 9',
                         'Launchpad Pro 10',
                         'Launchpad Pro 11',
                         'Launchpad Pro 12',
                         'Launchpad Pro 13',
                         'Launchpad Pro 14',
                         'Launchpad Pro 15',
                         'Launchpad Pro 16']),
     PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT, REMOTE]),
                 inport(props=[]),
                 outport(props=[NOTES_CC,
                  SYNC,
                  SCRIPT,
                  REMOTE]),
                 outport(props=[])]}