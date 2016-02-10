#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MiniLab/__init__.py
from .MiniLab import MiniLab
import _Framework.Capabilities as caps

def get_capabilities():
    return {caps.CONTROLLER_ID_KEY: caps.controller_id(vendor_id=7285, product_ids=[516], model_name=['Arturia MINILAB']),
     caps.PORTS_KEY: [caps.inport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE]), caps.outport(props=[caps.SCRIPT])]}


def create_instance(c_instance):
    return MiniLab(c_instance)