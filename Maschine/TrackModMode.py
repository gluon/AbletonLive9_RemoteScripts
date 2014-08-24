#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\TrackModMode.py
import Live
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from MIDI_Map import *
from PadScale import *
from MaschineMode import *
XFADE_SEQ = (2, 0, 1)

def arm_exclusive(song, track = None):
    if not track:
        track = song.view.selected_track
    if track and track.can_be_armed and not track.arm:
        tracks = song.tracks
        for songtrack in tracks:
            if songtrack != track and songtrack and songtrack.can_be_armed and songtrack.arm:
                songtrack.arm = False

        track.arm = True


class TrackElement:

    def __init__(self, index, *a, **k):
        self._button = None
        self._index = index
        self._track = None
        self.blinking = False
        self._mode = None
        self._colors = None

    def release(self):
        if self._button != None:
            self._button.remove_value_listener(self._launch_value)
            self._track = None
            self._button = None

    def set_button(self, button, track, mode):
        if not isinstance(mode, TrackModMode):
            raise AssertionError
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if not (track == None or isinstance(track, Live.Track.Track)):
                raise AssertionError
                self._track = track
                self._mode = mode
                if button != self._button:
                    self._button != None and self._button.remove_value_listener(self._do_value)
                self._button = button
                self._button != None and self._button.add_value_listener(self._do_value)

    def _do_value(self, value):
        self._mode.handle_action(value, self._track)

    def _listen_event(self):
        self.update()

    def notify(self, onoffval):
        if self._colors:
            self._button.send_color_direct(self._colors[onoffval])

    def navigate(self, dir, modifier, alt_modifier = False):
        pass

    def update(self):
        self._button.send_color_direct(self._mode._get_color(self))

    def release(self):
        if self._button != None:
            self._mode.unbind_listener(self)
            self._button.remove_value_listener(self._do_value)
            self._track = None
            self._button = None
            self._colors = None


class TrackAssign(object):

    def __init__(self):
        self.track_offset = 0
        self.elements = tuple((TrackElement(idx) for idx in range(16)))

    def release(self):
        for track_element in self.elements:
            if track_element:
                track_element.release()

    def inc_offset(self, diff, nr_of_tracks):
        new_last_track = diff + self.track_offset + 16
        if diff < 0 and self.track_offset > 0:
            self.track_offset += diff
            return True
        elif diff > 0 and new_last_track < nr_of_tracks:
            self.track_offset += diff
            return True
        return False

    def ajust_track_offest(self, nr_of_tracks):
        self.track_offset = min(self.track_offset, max(0, nr_of_tracks - 16 - 1))


class TrackModMode(MaschineMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackModMode, self).__init__(*a, **k)
        if not isinstance(track_assign, TrackAssign):
            raise AssertionError
        self._track_assign = track_assign

    def get_color(self, value, column_index, row_index):
        pass

    def notify(self, blink_state):
        pass

    def navigate(self, dir, modifier, alt_modifier = False):
        tracks = self.song().tracks
        if self._track_assign.inc_offset(dir, len(tracks)):
            self._free_listeners()
            self._assign(False)
            offset = self._track_assign.track_offset + 1
            self.canonical_parent.show_message('Track Mode assigned to Tracks ' + str(offset) + ' to ' + str(16 + offset))
            self.canonical_parent.timed_message(2, 'Tracks Mode to:' + str(offset) + ' to ' + str(16 + offset))

    def unbind_listener(self, track_element):
        pass

    def unbind(self):
        pass

    def is_lock_mode(self):
        return False

    def on_selected_track_changed(self):
        pass

    def enter(self):
        self._active = True
        self._assign()

    def exit(self):
        self._active = False
        self._release()

    def set_listener(self, track_ele):
        pass

    def on_track_list_changed(self):
        if self._active:
            self._free_listeners()
            self._assign(False)

    def _free_listeners(self):
        for track_ele in self._track_assign.elements:
            self.unbind_listener(track_ele)

    def get_color(self, value, column, row):
        index = (3 - row) * 4 + column
        return OFF_COLOR

    def refresh(self):
        if self._active:
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    index = (3 - row) * 4 + column
                    tindex = index + self._track_assign.track_offset
                    track_ele = self._track_assign.elements[index]
                    button.reset()
                    button.send_color_direct(self._get_color(track_ele))

    def _assign(self, register = True):
        tracks = self.song().tracks
        self._track_assign.ajust_track_offest(len(tracks))
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                index = (3 - row) * 4 + column
                tindex = index + self._track_assign.track_offset
                if register:
                    self.canonical_parent._forwarding_registry[MIDI_NOTE_ON_STATUS, button.get_identifier()] = button
                    self.canonical_parent._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button
                    button.set_to_notemode(False)
                track_ele = self._track_assign.elements[index]
                if index < len(tracks):
                    track_ele.set_button(button, tracks[tindex], self)
                    self.set_listener(track_ele)
                else:
                    track_ele.set_button(button, None, self)
                button.send_color_direct(self._get_color(track_ele))

    def handle_action(self, value, track):
        pass

    def _release(self):
        self._track_assign.release()

    def _get_color(self, track_ele):
        return OFF_COLOR


class TrackArmMode(TrackModMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackArmMode, self).__init__(track_assign, *a, **k)
        self.exclusive = True

    def _get_color(self, track_ele):
        track = track_ele._track
        if track == None:
            return OFF_COLOR
        elif not (track.can_be_armed and track.arm == False and 1):
            onoffindex = 0
            if track.has_midi_input:
                return PColor.ARM_MIDI[onoffindex]
            elif track.has_audio_input:
                return PColor.ARM_AUDIO[onoffindex]
            else:
                return PColor.ARM_OTHER[onoffindex]
        else:
            return PColor.ARM_NO_ARM[0]

    def set_listener(self, track_ele):
        if track_ele._track and track_ele._track.can_be_armed:
            track_ele._track.add_arm_listener(track_ele._listen_event)

    def unbind_listener(self, track_element):
        if track_element._track and track_element._track.can_be_armed:
            track_element._track.remove_arm_listener(track_element._listen_event)

    def handle_action(self, value, track):
        if value > 0 and track and track.can_be_armed:
            if self.exclusive and not track.arm:
                tracks = self.song().tracks
                for songtrack in tracks:
                    if songtrack != track and songtrack and songtrack.can_be_armed and songtrack.arm:
                        songtrack.arm = False

            track.arm = not track.arm
            return True
        return False


class TrackSoloMode(TrackModMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackSoloMode, self).__init__(track_assign, *a, **k)
        self.exclusive = True

    def _get_color(self, track_ele):
        track = track_ele._track
        if track == None:
            return OFF_COLOR
        else:
            return PColor.SOLO_TRACK[track.solo == False and 1 or 0]

    def set_listener(self, track_ele):
        if track_ele._track:
            track_ele._track.add_solo_listener(track_ele._listen_event)

    def unbind_listener(self, track_element):
        if track_element._track:
            track_element._track.remove_solo_listener(track_element._listen_event)

    def handle_action(self, value, track):
        if value > 0 and track:
            if self.exclusive and not track.solo:
                tracks = self.song().tracks
                for songtrack in tracks:
                    if songtrack != track and songtrack and songtrack.solo:
                        songtrack.solo = False

            track.solo = not track.solo


class TrackStopMode(TrackModMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackStopMode, self).__init__(track_assign, *a, **k)

    def _track_status(self, track):
        clipslots = track.clip_slots
        stop_fired = track.fired_slot_index == -2
        play_fired = track.fired_slot_index >= 0
        clip_playing = False
        has_clip = False
        if clipslots != None:
            for cs_index in range(len(clipslots)):
                clip_slot = clipslots[cs_index]
                if clip_slot.has_clip:
                    has_clip = True
                    if clip_slot.clip.is_playing:
                        clip_playing = True
                elif clip_slot.controls_other_clips:
                    has_clip = True
                    if clip_slot.is_playing:
                        clip_playing = True
                    if clip_slot.is_triggered:
                        play_fired = True
                elif clip_slot.is_triggered:
                    stop_fired = True

        return (has_clip,
         clip_playing,
         stop_fired,
         play_fired)

    def _get_color(self, track_ele):
        track = track_ele._track
        blinking = False
        color = PColor.OFF
        if track != None:
            has_clip, clip_playing, stop_fired, play_fired = self._track_status(track)
            is_group = track.is_foldable
            if stop_fired or play_fired:
                blinking = True
            if is_group:
                if clip_playing:
                    color = PColor.STOP_G_PLAY
                else:
                    color = PColor.STOP_G_NO_PLAY
            elif clip_playing:
                color = PColor.STOP_PLAY
            elif has_clip:
                color = PColor.STOP_NO_PLAY
            else:
                color = PColor.STOP_NO_CLIPS
        if blinking:
            track_ele._colors = color
        else:
            track_ele._colors = None
        return color[0]

    def notify(self, blink_state):
        nval = blink_state % 2
        for track_ele in self._track_assign.elements:
            track_ele.notify(nval)

    def notify_mono(self, blink_state):
        fval = blink_state % 2
        sval = blink_state / 2
        for track_ele in self._track_assign.elements:
            if track_ele and track_ele._track:
                track = track_ele._track
                has_clip, clip_playing, stop_fired, play_fired = self._track_status(track)
                if not has_clip:
                    track_ele._button.turn_off()
                elif stop_fired or play_fired:
                    if fval == 0:
                        track_ele._button.turn_on()
                    else:
                        track_ele._button.turn_off()
                elif clip_playing:
                    if sval == 0:
                        track_ele._button.turn_on()
                    else:
                        track_ele._button.turn_off()
                else:
                    track_ele._button.turn_on()
            else:
                track_ele._button.turn_off()

    def handle_action(self, value, track):
        if value > 0 and track:
            track.stop_all_clips()

    def set_listener(self, track_ele):
        if track_ele._track:
            track_ele._track.add_playing_slot_index_listener(track_ele._listen_event)
            track_ele._track.add_fired_slot_index_listener(track_ele._listen_event)

    def unbind_listener(self, track_element):
        if track_element._track:
            track_element._track.remove_playing_slot_index_listener(track_element._listen_event)
            track_element._track.remove_fired_slot_index_listener(track_element._listen_event)


class TrackMuteMode(TrackModMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackMuteMode, self).__init__(track_assign, *a, **k)

    def _get_color(self, track_ele):
        track = track_ele._track
        if track == None:
            return OFF_COLOR
        elif track.mute:
            return PColor.MUTE_TRACK[1]
        else:
            return PColor.MUTE_TRACK[0]

    def set_listener(self, track_ele):
        if track_ele._track:
            track_ele._track.add_mute_listener(track_ele._listen_event)

    def unbind_listener(self, track_element):
        if track_element._track:
            track_element._track.remove_mute_listener(track_element._listen_event)

    def handle_action(self, value, track):
        if value > 0 and track:
            track.mute = not track.mute


class TrackXFadeMode(TrackModMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackXFadeMode, self).__init__(track_assign, *a, **k)

    def _get_color(self, track_ele):
        track = track_ele._track
        if track != None and track.mixer_device != None:
            xfade = track.mixer_device.crossfade_assign
            if xfade == 0:
                return PColor.XFADE_A[0]
            elif xfade == 1:
                return PColor.XFADE_BOTH[0]
            elif xfade == 2:
                return PColor.XFADE_B[0]
        return OFF_COLOR

    def notify_mono(self, blink_state):
        fval = blink_state % 2
        sval = blink_state / 2
        for track_ele in self._track_assign.elements:
            if track_ele and track_ele._track:
                xfade = track_ele._track.mixer_device.crossfade_assign
                if xfade == 1:
                    track_ele._button.turn_on()
                elif xfade == 2:
                    if fval == 0:
                        track_ele._button.turn_on()
                    else:
                        track_ele._button.turn_off()
                elif xfade == 0:
                    if sval == 0:
                        track_ele._button.turn_on()
                    else:
                        track_ele._button.turn_off()
            else:
                track_ele._button.turn_off()

    def set_listener(self, track_ele):
        if track_ele._track and track_ele._track.mixer_device:
            track_ele._track.mixer_device.add_crossfade_assign_listener(track_ele._listen_event)

    def unbind_listener(self, track_element):
        if track_element._track and track_element._track.mixer_device:
            track_element._track.mixer_device.remove_crossfade_assign_listener(track_element._listen_event)

    def handle_action(self, value, track):
        if value > 0 and track and track.mixer_device:
            track.mixer_device.crossfade_assign = XFADE_SEQ[track.mixer_device.crossfade_assign]


class TrackSelectMode(TrackModMode):
    __module__ = __name__

    def __init__(self, track_assign, *a, **k):
        super(TrackSelectMode, self).__init__(track_assign, *a, **k)

    def _get_color(self, track_ele):
        track = track_ele._track
        sel_track = self.song().view.selected_track
        if track == None:
            return OFF_COLOR
        elif track == sel_track:
            return PColor.SELECT[0]
        else:
            return PColor.SELECT[1]

    def handle_action(self, value, track):
        if value > 0 and track:
            self.song().view.selected_track = track
            if self.canonical_parent.arm_selected_track:
                arm_exclusive(self.song(), track)

    def on_selected_track_changed(self):
        if self._active:
            for track_ele in self._track_assign.elements:
                track_ele.update()