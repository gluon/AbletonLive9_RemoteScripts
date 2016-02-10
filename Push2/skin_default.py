#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/skin_default.py
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.control_surface import Skin
from ableton.v2.control_surface.elements import SelectedTrackColorFactory, SelectedClipColorFactory
from pushbase.colors import Blink, FallbackColor, Pulse
from pushbase.skin_default import Colors as ColorsBase
from .colors import Basic, determine_shaded_color_index, Rgb, translate_color_index

def shaded_color(color_index, shade_level = 1):
    return determine_shaded_color_index(translate_color_index(color_index), shade_level)


shade_transform = partial(shaded_color, shade_level=1)
shade_transform2 = partial(shaded_color, shade_level=2)
SelectedTrackColor = SelectedTrackColorFactory(transformation=translate_color_index)
SelectedClipColor = SelectedClipColorFactory(transformation=translate_color_index)
SelectedTrackColorShade = SelectedTrackColorFactory(transformation=shade_transform)
SelectedTrackColorShade2 = SelectedTrackColorFactory(transformation=shade_transform2)
SelectedClipColorShade = SelectedClipColorFactory(transformation=shade_transform)
SelectedClipColorShade2 = SelectedClipColorFactory(transformation=shade_transform2)
TRACK_SOLOED_COLOR = Rgb.OCEAN
RECORDING_COLOR = Rgb.RED
UNLIT_COLOR = Rgb.BLACK

class Colors(ColorsBase):

    class DefaultButton:
        On = Basic.ON
        Off = Basic.HALF
        Disabled = Basic.OFF
        Alert = Basic.FULL_PULSE_SLOW
        Transparent = Basic.TRANSPARENT

    class Instrument:
        NoteBase = SelectedTrackColor
        NoteScale = Rgb.WHITE
        NoteNotScale = Rgb.BLACK
        NoteInvalid = Rgb.BLACK
        Feedback = Rgb.GREEN
        FeedbackRecord = Rgb.RED
        NoteAction = Rgb.RED

    class DrumGroup:
        PadSelected = Rgb.WHITE
        PadSelectedNotSoloed = Rgb.WHITE
        PadFilled = SelectedTrackColor
        PadEmpty = SelectedTrackColorShade2
        PadMuted = Rgb.LIGHT_GREY
        PadMutedSelected = Rgb.WHITE
        PadSoloed = Rgb.BLUE
        PadSoloedSelected = Rgb.WHITE
        PadInvisible = Rgb.BLACK
        PadAction = Rgb.WHITE

    class SlicedSimpler:
        SliceSelected = Rgb.WHITE
        SliceUnselected = SelectedTrackColor
        NoSlice = SelectedTrackColorShade2

    class Melodic:
        Playhead = Rgb.GREEN
        PlayheadRecord = RECORDING_COLOR

    class LoopSelector:
        Playhead = Rgb.GREEN
        PlayheadRecord = RECORDING_COLOR
        SelectedPage = Rgb.WHITE
        InsideLoopStartBar = Rgb.LIGHT_GREY
        InsideLoop = Rgb.LIGHT_GREY
        OutsideLoop = Rgb.BLACK

    class NoteEditor:

        class Step:
            Low = SelectedClipColorShade2
            High = SelectedClipColorShade
            Full = SelectedClipColor
            Muted = Rgb.LIGHT_GREY

        class StepEditing:
            Low = Pulse(Rgb.WHITE, Rgb.LIGHT_GREY, 48)
            High = Pulse(Rgb.WHITE, Rgb.LIGHT_GREY, 48)
            Full = Pulse(Rgb.WHITE, Rgb.LIGHT_GREY, 48)
            Muted = Rgb.WHITE

        StepSelected = Rgb.WHITE
        StepEmpty = Rgb.DARK_GREY
        StepDisabled = Rgb.BLACK
        Playhead = Rgb.GREEN
        PlayheadRecord = RECORDING_COLOR
        QuantizationSelected = Rgb.WHITE
        QuantizationUnselected = Rgb.DARK_GREY
        NoteBase = Rgb.LIGHT_GREY
        NoteScale = Rgb.DARK_GREY
        NoteNotScale = Rgb.BLACK
        NoteInvalid = Rgb.BLACK

    class DrumGroupNoteEditor(NoteEditor):
        pass

    class Option:
        Selected = Rgb.WHITE
        Unselected = Rgb.DARK_GREY
        On = Rgb.WHITE
        Off = Rgb.DARK_GREY
        Unused = Rgb.BLACK

    class Mixer:
        TrackSelected = Rgb.WHITE
        NoTrack = Rgb.BLACK
        MutedTrack = Rgb.DARK_GREY
        MuteOn = Rgb.YELLOW_SHADE
        MuteOff = Rgb.YELLOW
        SoloOn = TRACK_SOLOED_COLOR
        SoloOff = Rgb.DEEP_OCEAN
        LockedMuteMode = Pulse(Rgb.BLACK, Rgb.YELLOW, 48)
        LockedSoloMode = Pulse(Rgb.BLACK, TRACK_SOLOED_COLOR, 48)

    class MixerControlView:
        SectionSelected = Rgb.WHITE
        SectionUnSelected = Rgb.DARK_GREY

    class TrackControlView:
        ButtonOn = Rgb.WHITE
        ButtonOff = Rgb.DARK_GREY
        ButtonDisabled = Rgb.BLACK

    class ItemNavigation:
        ItemSelected = Rgb.WHITE
        NoItem = Rgb.BLACK
        ItemNotSelected = SelectedTrackColor

    class Browser:
        Navigation = FallbackColor(Rgb.WHITE, Basic.ON)
        NavigationDisabled = FallbackColor(Rgb.DARK_GREY, Basic.OFF)
        Option = Rgb.WHITE
        OptionDisabled = Rgb.DARK_GREY

    class Scales:
        Navigation = FallbackColor(Rgb.WHITE, Basic.ON)
        NavigationDisabled = FallbackColor(Rgb.DARK_GREY, Basic.OFF)
        OptionOn = Rgb.WHITE
        OptionOff = Rgb.DARK_GREY
        NoOption = Rgb.BLACK
        Close = Rgb.WHITE

    class Clip:
        Option = Rgb.WHITE
        OptionDisabled = Rgb.DARK_GREY

    class Transport:
        PlayOn = Rgb.GREEN
        PlayOff = Rgb.WHITE

    class Recording:
        On = RECORDING_COLOR
        Off = Rgb.WHITE
        Transition = Blink(RECORDING_COLOR, Rgb.BLACK, 48)
        ArrangementRecordingOn = Pulse(RECORDING_COLOR, Rgb.BLACK, 48)
        FixedLengthRecordingOn = Rgb.WHITE
        FixedLengthRecordingOff = Rgb.DARK_GREY

    class Automation:
        On = Rgb.RED
        Off = Rgb.WHITE

    class Session:
        Scene = Rgb.GREEN
        SceneTriggered = FallbackColor(Blink(Rgb.GREEN, Rgb.BLACK, 24), 24)
        NoScene = Rgb.BLACK
        ClipStopped = Rgb.AMBER
        ClipStarted = Pulse(Rgb.GREEN_SHADE, Rgb.GREEN, 48)
        ClipRecording = Pulse(Rgb.BLACK, Rgb.RED, 48)
        ClipTriggeredPlay = Blink(Rgb.GREEN, Rgb.BLACK, 24)
        ClipTriggeredRecord = Blink(Rgb.RED, Rgb.BLACK, 24)
        ClipEmpty = Rgb.BLACK
        RecordButton = Rgb.RED_SHADE
        StopClip = Rgb.RED
        StopClipTriggered = Blink(Rgb.RED, Rgb.BLACK, 24)
        StoppedClip = Rgb.DARK_GREY

    class StopClips:
        SoloedTrack = Pulse(Rgb.BLACK, TRACK_SOLOED_COLOR, 48)
        MutedTrack = Pulse(Rgb.BLACK, Rgb.DARK_GREY, 48)
        LockedStopMode = Pulse(Rgb.BLACK, Rgb.RED, 48)

    class Zooming:
        Selected = Rgb.WHITE
        Stopped = Rgb.LIGHT_GREY
        Playing = Pulse(Rgb.GREEN_SHADE, Rgb.GREEN, 48)
        Empty = Rgb.BLACK

    class NoteRepeat:
        RateSelected = Rgb.GREEN
        RateUnselected = Rgb.WHITE

    class Metronome:
        On = Basic.FAST_PULSE
        Off = Basic.ON

    class FixedLength:
        On = Basic.FULL_PULSE_SLOW
        Off = Basic.ON

    class Accent:
        On = Basic.FULL_PULSE_SLOW
        Off = Basic.ON


def make_default_skin():
    return Skin(Colors)