#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/VCM600/__init__.py
from VCM600 import VCM600

def create_instance(c_instance):
    """ Creates and returns the ADA1 script """
    return VCM600(c_instance)