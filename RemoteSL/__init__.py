#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/RemoteSL/__init__.py
from RemoteSL import RemoteSL

def create_instance(c_instance):
    return RemoteSL(c_instance)


from _Framework.Capabilities import *

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661, product_ids=[11], model_name='SL MkII'),
     PORTS_KEY: [inport(props=[NOTES_CC, REMOTE]),
                 inport(props=[NOTES_CC, REMOTE, SCRIPT]),
                 outport(props=[NOTES_CC, SYNC]),
                 outport(props=[SCRIPT])]}