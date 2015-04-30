#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Push/__init__.py
from Push import Push
from FirmwareHandling import get_provided_firmware_version
from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, HIDDEN, NOTES_CC, SCRIPT, SYNC, TYPE_KEY, FIRMWARE_KEY, AUTO_LOAD_KEY

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
    return Push(c_instance)