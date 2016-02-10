#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/__init__.py
from __future__ import absolute_import, print_function
from ableton.v2.control_surface.capabilities import controller_id, inport, outport, AUTO_LOAD_KEY, CONTROLLER_ID_KEY, FIRMWARE_KEY, HIDDEN, NOTES_CC, PORTS_KEY, SCRIPT, SYNC, TYPE_KEY
from .firmware_handling import get_provided_firmware_version
from .push import Push

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536, product_ids=[21], model_name='Ableton Push'),
     PORTS_KEY: [inport(props=[HIDDEN, NOTES_CC, SCRIPT]),
                 inport(props=[]),
                 outport(props=[HIDDEN,
                  NOTES_CC,
                  SYNC,
                  SCRIPT]),
                 outport(props=[])],
     TYPE_KEY: 'push',
     FIRMWARE_KEY: get_provided_firmware_version(),
     AUTO_LOAD_KEY: True}


def create_instance(c_instance):
    """ Creates and returns the Push script """
    return Push(c_instance=c_instance)