#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/SkinDefault.py
from _Framework.Skin import Skin
from .Colors import Rgb

class Colors:

    class DefaultButton:
        On = Rgb.GREEN
        Off = Rgb.GREEN_HALF
        Disabled = Rgb.BLACK

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
        Enabled = Rgb.GREEN
        Off = Rgb.GREEN_HALF

    class Zooming:
        Selected = Rgb.AMBER
        Stopped = Rgb.RED
        Playing = Rgb.GREEN
        Empty = Rgb.BLACK

    class Mixer:
        ArmOn = Rgb.RED
        ArmOff = Rgb.RED_HALF
        SoloOn = Rgb.BLUE
        SoloOff = Rgb.BLUE_HALF
        MuteOn = Rgb.YELLOW_HALF
        MuteOff = Rgb.YELLOW
        Selected = Rgb.LIGHT_BLUE
        Unselected = Rgb.LIGHT_BLUE_HALF
        Volume = Rgb.GREEN
        Pan = Rgb.ORANGE
        Sends = Rgb.WHITE

    class Sends:
        A = Rgb.DARK_BLUE
        AAvail = Rgb.DARK_BLUE_HALF
        B = Rgb.BLUE
        BAvail = Rgb.BLUE_HALF
        C = Rgb.LIGHT_BLUE
        CAvail = Rgb.LIGHT_BLUE_HALF
        D = Rgb.MINT
        DAvail = Rgb.MINT_HALF
        E = Rgb.DARK_YELLOW
        EAvail = Rgb.DARK_YELLOW_HALF
        F = Rgb.YELLOW
        FAvail = Rgb.YELLOW_HALF
        G = Rgb.ORANGE
        GAvail = Rgb.ORANGE_HALF
        H = Rgb.RED
        HAvail = Rgb.RED_HALF

    class Device:
        On = Rgb.PURPLE
        Off = Rgb.PURPLE_HALF
        Disabled = Rgb.BLACK

    class Recording:
        On = Rgb.RED
        Off = Rgb.RED_HALF
        Transition = Rgb.RED_BLINK

    class DrumGroup:
        PadEmpty = Rgb.BLACK
        PadFilled = Rgb.YELLOW
        PadSelected = Rgb.LIGHT_BLUE
        PadSelectedNotSoloed = Rgb.LIGHT_BLUE
        PadMuted = Rgb.DARK_ORANGE
        PadMutedSelected = Rgb.LIGHT_BLUE
        PadSoloed = Rgb.DARK_BLUE
        PadSoloedSelected = Rgb.LIGHT_BLUE
        PadInvisible = Rgb.BLACK
        PadAction = Rgb.RED

    class Instrument:
        FeedbackRecord = Rgb.RED
        Feedback = Rgb.GREEN

    class Mode:

        class Session:
            On = Rgb.GREEN
            Off = Rgb.GREEN_HALF

        class Chromatic:
            On = Rgb.LIGHT_BLUE
            Off = Rgb.LIGHT_BLUE_HALF

        class Drum:
            On = Rgb.YELLOW
            Off = Rgb.YELLOW_HALF

        class Device:
            On = Rgb.PURPLE
            Off = Rgb.PURPLE_HALF

        class User:
            On = Rgb.DARK_BLUE
            Off = Rgb.DARK_BLUE_HALF

        class RecordArm:
            On = Rgb.RED
            Off = Rgb.RED_HALF

        class TrackSelect:
            On = Rgb.LIGHT_BLUE
            Off = Rgb.LIGHT_BLUE_HALF

        class Mute:
            On = Rgb.YELLOW
            Off = Rgb.YELLOW_HALF

        class Solo:
            On = Rgb.BLUE
            Off = Rgb.BLUE_HALF

        class Volume:
            On = Rgb.GREEN
            Off = Rgb.GREEN_HALF

        class Pan:
            On = Rgb.ORANGE
            Off = Rgb.ORANGE_HALF

        class Sends:
            On = Rgb.WHITE
            Off = Rgb.DARK_GREY

        class StopClip:
            On = Rgb.RED
            Off = Rgb.RED_HALF

    class Scrolling:
        Enabled = Rgb.YELLOW_HALF
        Pressed = Rgb.YELLOW
        Disabled = Rgb.BLACK

    class Misc:
        UserMode = Rgb.DARK_BLUE
        Shift = Rgb.DARK_GREY
        ShiftOn = Rgb.WHITE


def make_default_skin():
    return Skin(Colors)