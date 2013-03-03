#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/Settings.py
from Setting import OnOffSetting, EnumerableSetting
from PadSensitivity import PadParameters

def _create_pad_settings():
    return [PadParameters(off_threshold=150, on_threshold=200, gain=100000, curve1=45000, curve2=0, name='-1'),
     PadParameters(off_threshold=100, on_threshold=120, gain=85000, curve1=120000, curve2=60000, name='Default'),
     PadParameters(off_threshold=90, on_threshold=110, gain=100000, curve1=120000, curve2=50000, name='+1'),
     PadParameters(off_threshold=85, on_threshold=100, gain=100000, curve1=120000, curve2=50000, name='+2'),
     PadParameters(off_threshold=85, on_threshold=95, gain=130000, curve1=120000, curve2=50000, name='+3'),
     PadParameters(off_threshold=85, on_threshold=95, gain=140000, curve1=120000, curve2=0, name='+4')]


def create_settings(preferences = None):
    preferences = preferences if preferences != None else {}
    pad_settings = _create_pad_settings()
    return {'SceneList': OnOffSetting(name='Scene List', default_value=True, preferences=preferences),
     'PadParams': EnumerableSetting(name='Pad Sensitivity', values=pad_settings, default_value=pad_settings[1], preferences=preferences)}