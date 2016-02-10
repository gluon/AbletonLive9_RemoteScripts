#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MPD226/__init__.py
import _Framework.Capabilities as caps
from .MPD226 import MPD226

def get_capabilities():
    return {caps.CONTROLLER_ID_KEY: caps.controller_id(vendor_id=2536, product_ids=[53], model_name='MPD226'),
     caps.PORTS_KEY: [caps.inport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE]), caps.outport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE])]}


def create_instance(c_instance):
    return MPD226(c_instance)