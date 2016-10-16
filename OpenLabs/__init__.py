#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/OpenLabs/__init__.py
import Live
from OpenLabs import OpenLabs

def create_instance(c_instance):
    """ Creates and returns the OpenLabs script """
    return OpenLabs(c_instance)