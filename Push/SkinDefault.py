#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/SkinDefault.py
from Colors import Basic, Rgb, Pulse, Blink, BiLed

class Colors:

    class Option:
        Selected = BiLed.YELLOW
        Unselected = BiLed.YELLOW_HALF
        On = BiLed.YELLOW
        Off = BiLed.OFF
        Unused = BiLed.OFF

    class List:
        ScrollerOn = BiLed.AMBER
        ScrollerOff = BiLed.AMBER_HALF

    class DefaultButton:
        On = Basic.FULL
        Off = Basic.HALF
        Disabled = Basic.OFF
        Alert = Basic.FULL_BLINK_SLOW

    class DefaultMatrix:
        On = Rgb.WHITE
        Off = Rgb.BLACK

    class Scales:
        Selected = BiLed.GREEN
        Unselected = BiLed.GREEN_HALF
        FixedOn = BiLed.AMBER
        FixedOff = BiLed.AMBER_HALF
        Diatonic = BiLed.AMBER
        Chromatic = BiLed.AMBER_HALF

    class Instrument:
        NoteBase = Rgb.OCEAN
        NoteScale = Rgb.WHITE
        NoteForeign = Rgb.MAGENTA
        NoteInvalid = Rgb.BLACK
        NoteInactive = Rgb.BLACK
        NoteOff = Rgb.BLACK
        Feedback = Rgb.GREEN

    class Recording:
        On = Basic.FULL
        Off = Basic.HALF
        Transition = Basic.FULL_BLINK_FAST

    class Session:
        SceneSelected = BiLed.GREEN
        SceneUnselected = BiLed.OFF
        SceneTriggered = BiLed.BLUE
        ClipStopped = Rgb.AMBER
        ClipStarted = (Rgb.BLUE.shade(1), Rgb.GREEN, 48)
        ClipRecording = Pulse(Rgb.BLACK, Rgb.RED, 48)
        ClipTriggeredPlay = (Rgb.BLUE, Rgb.BLACK, 24)
        ClipTriggeredRecord = Blink(Rgb.RED, Rgb.BLACK, 24)
        ClipEmpty = Rgb.BLACK
        RecordButton = Rgb.RED.shade(2)

    class Zooming:
        Selected = Rgb.AMBER
        Stopped = Rgb.RED
        Playing = Rgb.GREEN
        Empty = Rgb.BLACK

    class TrackState:
        Common = Rgb.BLACK
        Stopped = Rgb.RED
        Disabled = Basic.OFF

    class DrumGroup:
        PadSelected = Rgb.OCEAN
        PadSelectedNotSoloed = Rgb.OCEAN
        PadFilled = Rgb.YELLOW
        PadEmpty = Rgb.YELLOW.shade(1)
        PadMuted = Rgb.AMBER
        PadMutedSelected = Rgb.OCEAN
        PadSoloed = Rgb.OCEAN.highlight()
        PadSoloedSelected = Rgb.OCEAN
        PadInvisible = Rgb.BLACK

    class LoopSelector:
        Playhead = Rgb.GREEN
        SelectedPage = Rgb.OCEAN
        InsideLoop = Rgb.WHITE
        OutsideLoop = Rgb.DARK_GREY

    class NoteEditor:
        Step = Rgb.SKY.highlight()
        StepHighVelocity = Rgb.OCEAN
        StepFullVelocity = Rgb.BLUE
        StepMuted = Rgb.AMBER.shade(2)
        StepEmpty = Rgb.BLACK
        StepDisabled = Rgb.RED.shade(2)
        Playhead = Rgb.GREEN
        QuantizationSelected = BiLed.GREEN
        QuantizationUnselected = BiLed.YELLOW

    class NoteRepeat:
        RateSelected = BiLed.RED
        RateUnselected = BiLed.YELLOW

    class Mixer:
        SoloOn = Rgb.OCEAN
        SoloOff = Rgb.OCEAN.shade(2)
        MuteOn = BiLed.AMBER_HALF
        MuteOff = BiLed.AMBER
        StopTrack = Rgb.RED
        StoppingTrack = Blink(Rgb.RED, Rgb.BLACK, 24)

    class Browser:
        Load = BiLed.GREEN
        LoadNext = BiLed.YELLOW
        LoadNotPossible = BiLed.OFF
        Loading = BiLed.OFF

    class MessageBox:
        Cancel = BiLed.GREEN
