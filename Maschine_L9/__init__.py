#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk1\__init__.py
from Maschine import Maschine

def create_instance(c_instance):
    return Maschine(c_instance)


def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=9000, product_ids=[2], model_name='Maschine Mk2'),
     PORTS_KEY: [inport(props=[NOTES_CC, REMOTE, SCRIPT]), outport(props=[NOTES_CC, REMOTE, SCRIPT])]}