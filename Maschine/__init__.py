#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\__init__.py
from MaschineMk1 import MaschineMk1

def create_instance(c_instance):
    return MaschineMk1(c_instance)


from _Framework.Capabilities import *

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=9000, product_ids=[2], model_name='Maschine Mk2'),
     PORTS_KEY: [inport(props=[HIDDEN, NOTES_CC, SCRIPT]),
                 inport(props=[]),
                 outport(props=[HIDDEN,
                  NOTES_CC,
                  SYNC,
                  SCRIPT]),
                 outport(props=[])]}