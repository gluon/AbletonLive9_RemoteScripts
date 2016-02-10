#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/settings.py
from __future__ import absolute_import, print_function
from pushbase.setting import OnOffSetting

def create_settings(preferences = None):
    preferences = preferences if preferences is not None else {}
    return {'workflow': OnOffSetting(name='Workflow', value_labels=['Scene', 'Clip'], default_value=True, preferences=preferences)}