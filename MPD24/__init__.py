#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MPD24/__init__.py
from _Generic.GenericScript import GenericScript
import Live
from config import *

def create_instance(c_instance):
    """ The generic script can be customised by using parameters (see config.py). """
    return GenericScript(c_instance, Live.MidiMap.MapMode.absolute, Live.MidiMap.MapMode.absolute, DEVICE_CONTROLS, TRANSPORT_CONTROLS, VOLUME_CONTROLS, TRACKARM_CONTROLS, BANK_CONTROLS, CONTROLLER_DESCRIPTION)


from _Framework.Capabilities import *

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536, product_ids=[104], model_name='Akai MPD24'),
     PORTS_KEY: [inport(props=[NOTES_CC, REMOTE, SCRIPT]),
                 inport(props=[NOTES_CC]),
                 inport(props=[NOTES_CC]),
                 outport(props=[SCRIPT]),
                 outport(props=[])]}