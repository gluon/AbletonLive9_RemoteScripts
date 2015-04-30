#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/OpenLabs/__init__.py
import Live
from OpenLabs import OpenLabs

def create_instance(c_instance):
    """ Creates and returns the OpenLabs script """
    return OpenLabs(c_instance)