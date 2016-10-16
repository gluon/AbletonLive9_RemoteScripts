#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_MK2/Skin.py
from _Framework.Skin import Skin
from .Colors import Rgb

class Colors:

    class Session:
        SceneTriggered = Rgb.GREEN_BLINK
        NoScene = Rgb.BLACK
        ClipStarted = Rgb.GREEN_PULSE
        ClipRecording = Rgb.RED_PULSE
        ClipTriggeredPlay = Rgb.GREEN_BLINK
        ClipTriggeredRecord = Rgb.RED_BLINK
        ClipEmpty = Rgb.BLACK
        RecordButton = Rgb.RED_HALF
        StopClip = Rgb.RED
        StopClipTriggered = Rgb.RED_BLINK
        StoppedClip = Rgb.RED_HALF
        Enabled = Rgb.YELLOW

    class Zooming:
        Selected = Rgb.AMBER
        Stopped = Rgb.RED
        Playing = Rgb.GREEN
        Empty = Rgb.BLACK

    class Mixer:
        Disabled = Rgb.BLACK

        class Volume:
            On = Rgb.GREEN
            Off = Rgb.GREEN_HALF

        class Pan:
            On = Rgb.ORANGE
            Off = Rgb.ORANGE_HALF

        class Mute:
            On = Rgb.YELLOW
            Off = Rgb.YELLOW_HALF

        class Solo:
            On = Rgb.BLUE
            Off = Rgb.BLUE_HALF

        class Arm:
            On = Rgb.RED
            Off = Rgb.RED_HALF

    class Sends:

        class Send0:
            On = Rgb.DARK_BLUE
            Off = Rgb.DARK_BLUE_HALF

        class Send1:
            On = Rgb.BLUE
            Off = Rgb.BLUE_HALF

    class Mode:

        class SessionMode:
            On = Rgb.GREEN
            Off = Rgb.GREEN_HALF

        class User1Mode:
            On = Rgb.DARK_BLUE
            Off = Rgb.DARK_BLUE_HALF

        class User2Mode:
            On = Rgb.PURPLE
            Off = Rgb.PURPLE_HALF

        class MixerMode:
            On = Rgb.LIGHT_BLUE
            GroupOn = Rgb.LIGHT_BLUE
            Off = Rgb.LIGHT_BLUE_HALF

        class VolumeMode:
            On = Rgb.GREEN
            GroupOn = Rgb.GREEN_HALF
            Off = Rgb.BLACK

        class PanMode:
            On = Rgb.ORANGE
            GroupOn = Rgb.ORANGE_HALF
            Off = Rgb.BLACK

        class SendAMode:
            On = Rgb.DARK_BLUE
            GroupOn = Rgb.DARK_BLUE_HALF
            Off = Rgb.BLACK

        class SendBMode:
            On = Rgb.BLUE
            GroupOn = Rgb.BLUE_HALF
            Off = Rgb.BLACK

    class Scrolling:
        Enabled = Rgb.GREEN_HALF
        Pressed = Rgb.GREEN
        Disabled = Rgb.BLACK


def make_default_skin():
    return Skin(Colors)