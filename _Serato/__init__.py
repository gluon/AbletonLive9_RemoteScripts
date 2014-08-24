#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/_Serato/__init__.py
from Serato import Serato

def create_instance(c_instance):
    """ Creates and returns the Serato script """
    return Serato(c_instance)