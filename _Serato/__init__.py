#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Serato/__init__.py
from Serato import Serato

def create_instance(c_instance):
    """ Creates and returns the Serato script """
    return Serato(c_instance)