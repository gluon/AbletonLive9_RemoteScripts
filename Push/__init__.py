#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/__init__.py
from Push import Push
from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, FIRMWARE_KEY, AUTO_LOAD_KEY

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536, product_ids=[21], model_name='Ableton Push'),
     PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT]),
                 inport(props=[]),
                 outport(props=[NOTES_CC, SYNC, SCRIPT]),
                 outport(props=[])],
     FIRMWARE_KEY: 'push_updater',
     AUTO_LOAD_KEY: True}


def create_instance(c_instance):
    """ Creates and returns the L9C script """
    return Push(c_instance)