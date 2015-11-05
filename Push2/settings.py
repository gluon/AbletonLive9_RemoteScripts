#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/settings.py
from pushbase.setting import OnOffSetting

def create_settings(preferences = None):
    preferences = preferences if preferences is not None else {}
    return {'workflow': OnOffSetting(name='Workflow', value_labels=['Scene', 'Clip'], default_value=True, preferences=preferences)}