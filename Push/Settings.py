#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/Settings.py
from Setting import OnOffSetting, EnumerableSetting
from PadSensitivity import PadParameters
import consts

def make_pad_parameters(curve_value, threshold_value):
    """
    Creates a valid PadParameters object merging the sensitivity curve
    and threshold settings.
    """
    threshold_range = consts.MAX_THRESHOLD_STEP - consts.MIN_THRESHOLD_STEP
    t = float(threshold_value - consts.MIN_THRESHOLD_STEP) / float(threshold_range)
    return PadParameters(curve_value, on_threshold=int((1 - t) * consts.MIN_ON_THRESHOLD + t * consts.MAX_ON_THRESHOLD), off_threshold=int((1 - t) * consts.MIN_OFF_THRESHOLD + t * consts.MAX_OFF_THRESHOLD))


action_pad_sensitivity = PadParameters(off_threshold=190, on_threshold=210, gain=85000, curve1=120000, curve2=60000)

def _create_pad_settings():
    return [PadParameters(gain=100000, curve1=45000, curve2=0, name='Linear'),
     PadParameters(gain=85000, curve1=120000, curve2=60000, name='Log 1 (Default)'),
     PadParameters(gain=85000, curve1=120000, curve2=50000, name='Log 2'),
     PadParameters(gain=100000, curve1=120000, curve2=50000, name='Log 3'),
     PadParameters(gain=130000, curve1=120000, curve2=50000, name='Log 4'),
     PadParameters(gain=140000, curve1=120000, curve2=0, name='Log 5')]


def _threshold_formatter(value):
    return str(value) if value != 0 else '0 (Default)'


SETTING_THRESHOLD = 0
SETTING_CURVE = 1
SETTING_WORKFLOW = 2
SETTING_AFTERTOUCH_THRESHOLD = 3

def create_settings(preferences = None):
    preferences = preferences if preferences != None else {}
    pad_settings = _create_pad_settings()
    return {SETTING_WORKFLOW: OnOffSetting(name='Workflow', value_labels=['Scene', 'Clip'], default_value=True, preferences=preferences),
     SETTING_THRESHOLD: EnumerableSetting(name='Pad Threshold', values=range(consts.MIN_THRESHOLD_STEP, consts.MAX_THRESHOLD_STEP + 1), default_value=0, preferences=preferences, value_formatter=_threshold_formatter),
     SETTING_CURVE: EnumerableSetting(name='Velocity Curve', values=pad_settings, default_value=pad_settings[1], preferences=preferences),
     SETTING_AFTERTOUCH_THRESHOLD: EnumerableSetting(name='Aftertouch Threshold', values=range(128), default_value=consts.INSTRUMENT_AFTERTOUCH_THRESHOLD, preferences=preferences)}