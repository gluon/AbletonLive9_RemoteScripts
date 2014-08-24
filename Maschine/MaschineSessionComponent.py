#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\MaschineSessionComponent.py
from MIDI_Map import *
from _Framework.InputControlElement import *
from _Framework.ButtonElement import *
from _Framework.SessionComponent import *
from _Framework.SubjectSlot import subject_slot
from ModSceneComponent import ModSceneComponent
from MIDI_Map import *
TRIGG = (36, 10, 127)
TRIGG_DIM = (36, 10, 10)
REC = (0, 127, 127)
REC_DIM = (0, 80, 20)
CLR_REC = (REC, REC)
CLR_TRIGG = (TRIGG, TRIGG)

class MaschineSessionComponent(SessionComponent):
    __module__ = __name__
    __doc__ = 'Session Component for Maschine'
    scene_component_type = ModSceneComponent
    _session_mode = None
    _advance = STEP1
    _matrix = None
    _color_manager = None

    def __init__(self):
        SessionComponent.__init__(self, 4, 4)
        self._mode_button = ButtonElement(False, MIDI_CC_TYPE, 2, 50)
        self._do_matrix_adv_mode.subject = self._mode_button
        self._mode_button.send_value(0, True)
        self._track_banking_increment = 1
        self._c_mode_button = ButtonElement(True, MIDI_CC_TYPE, 2, 90)
        self._change_color_mode.subject = self._c_mode_button
        self._c_mode_button.send_value(0, True)
        self.notify = self.notify_standard
        self.get_color = self.get_color_standard
        self._nav_color_button = self.canonical_parent.create_gated_button(8, 110)
        self._toggle_step_advance.subject = self._nav_color_button
        self._nav_color_button.switch_off()
        self._color_manager = self

    def set_mode(self, mode):
        self._session_mode = mode

    def set_color_manager(self, manager):
        if manager:
            self._color_manager = manager

    @subject_slot('value')
    def _change_color_mode(self, value):
        if value > 0:
            if self.is_color_mode():
                self.set_color_mode(False)
                self._session_mode.refresh()
                self._c_mode_button.send_value(0, True)
            else:
                self.set_color_mode(True)
                self._session_mode.refresh()
                self._c_mode_button.send_value(1, True)

    def set_color_mode(self, colormode):
        if colormode:
            self.notify = self.notify_cmode
            self.get_color = self.get_color_cmode
        else:
            self.notify = self.notify_standard
            self.get_color = self.get_color_standard

    def is_color_mode(self):
        return self.notify == self.notify_cmode

    def start_up(self):
        self.set_enabled(True)

    def update_nav_button(self):
        color = self._advance == STEP4 and COLOR_HUE_NAV4 or COLOR_HUE_NAV
        self._bank_up_button.hue = color
        self._bank_down_button.hue = color
        self._bank_left_button.hue = color
        self._bank_right_button.hue = color
        self._horizontal_banking.update()
        self._vertical_banking.update()

    @subject_slot('value')
    def _toggle_step_advance(self, value):
        if value != 0:
            self.set_step_advance(self._advance == STEP4 and STEP1 or STEP4)

    def switch_step_advance(self):
        self.set_step_advance(self._advance == STEP4 and STEP1 or STEP4)

    def set_step_advance(self, value):
        self._advance = value
        if self._advance == STEP4:
            self._mode_button.send_value(127, True)
            self._nav_color_button.turn_on()
        else:
            self._mode_button.send_value(0, True)
            self._nav_color_button.switch_off()
        self.set_track_banking_increment(self._advance)
        self.update_nav_button()

    def get_step_advance(self):
        return self._advance

    def _link(self):
        pass

    def get_track_offset(self):
        return self._track_offset

    def get_scene_offset(self):
        return self._scene_offset

    def set_matrix(self, matrix):
        self._matrix = matrix

    def set_track_banking_increment(self, increment):
        self._track_banking_increment = increment

    @subject_slot('value')
    def _do_matrix_adv_mode(self, value):
        if not self._mode_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                self._advance = value != 0 and self._advance == STEP1 and STEP4
                self._mode_button.send_value(127, True)
                self._nav_color_button.turn_on()
                self.set_track_banking_increment(STEP4)
            else:
                self._advance = STEP1
                self._mode_button.send_value(0, True)
                self._nav_color_button.switch_off()
                self.set_track_banking_increment(STEP1)

    def update(self):
        SessionComponent.update(self)
        try:
            self._advance
        except AttributeError:
            pass
        else:
            if self._advance == STEP4:
                self._mode_button.send_value(127, True)
            else:
                self._mode_button.send_value(0, True)

    def get_controled_clip_slots(self, clip_slot):
        if clip_slot.controls_other_clips:
            track = clip_slot.canonical_parent
            if track.is_foldable:
                song = self.song()
                index = vindex(song.tracks, track)
                if index >= 0:
                    count = index
                    done = False
                    result = []
                    while not done:
                        count += 1
                        if count == len(song.tracks):
                            done = True
                        else:
                            ctrack = song.tracks[count]

    def get_color_cmode(self, clip_slot):
        if clip_slot == None:
            return PColor.OFF
        color = self.get_color_cmode_base(clip_slot)
        oncolor = color[0]
        offcolor = color[1]
        if clip_slot.has_clip:
            if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                return (oncolor, oncolor)
            elif clip_slot.clip.is_triggered:
                return (oncolor, oncolor)
            elif clip_slot.clip.is_playing:
                return (oncolor, oncolor)
            else:
                return (offcolor, offcolor)
        elif clip_slot.will_record_on_start:
            return CLR_REC
        elif clip_slot.is_playing:
            return PColor.CLIP_GROUP_PLAY
        elif clip_slot.controls_other_clips:
            return PColor.CLIP_GROUP_CONTROL
        elif clip_slot.is_triggered:
            return CLR_TRIGG
        return PColor.OFF

    def get_color_standard(self, clip_slot):
        if not clip_slot:
            return PColor.OFF
        if clip_slot.has_clip:
            if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                if clip_slot.clip.is_triggered:
                    return PColor.CLIP_RECORD_TRIGGER
                else:
                    return PColor.CLIP_RECORD
            if clip_slot.clip.is_playing:
                return PColor.CLIP_PLAY
            elif clip_slot.clip.is_triggered:
                return PColor.CLIP_PLAY_TRIGGER
            else:
                return PColor.CLIP_STOPPED
        elif clip_slot.will_record_on_start:
            return PColor.CLIP_RECORD_TRIGGER
        elif clip_slot.is_playing:
            return PColor.CLIP_GROUP_PLAY
        elif clip_slot.controls_other_clips:
            return PColor.CLIP_GROUP_CONTROL
        elif clip_slot.is_triggered:
            return PColor.CLIP_GROUP_TRIGGER
        return PColor.OFF

    def get_mono_state(self, clip_slot):
        if not clip_slot:
            return (0, 0)
        if clip_slot.has_clip:
            if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                if clip_slot.clip.is_triggered:
                    return (1, 2)
                else:
                    return (1, 1)
            if clip_slot.clip.is_playing:
                return (1, 1)
            elif clip_slot.clip.is_triggered:
                return (1, 2)
            else:
                return (1, 0)
        elif clip_slot.will_record_on_start:
            return (1, 2)
        elif clip_slot.is_playing:
            return (1, 1)
        elif clip_slot.controls_other_clips:
            return (1, 0)
        elif clip_slot.is_triggered:
            return (1, 2)
        return (0, 0)

    def notify_standard(self, blink):
        index = blink / 2
        for scene_index in range(4):
            scene = self.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)._clip_slot
                if clip_slot:
                    button = self._matrix[scene_index][track_index]
                    color = self.get_color_standard(clip_slot)
                    if button != None and clip_slot.has_clip:
                        if clip_slot.clip.is_triggered:
                            button.send_color_direct(color[index])
                    elif clip_slot.is_triggered:
                        button.send_color_direct(color[index])

    def notify_cmode(self, blink):
        sblink = blink / 2
        fblink = blink % 2
        for scene_index in range(4):
            scene = self.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)._clip_slot
                if clip_slot:
                    button = self._matrix[scene_index][track_index]
                    color = self.get_color_cmode_base(clip_slot)
                    if clip_slot.has_clip:
                        if clip_slot.clip.is_recording or clip_slot.clip.will_record_on_start:
                            button.send_color_direct(sblink == 0 and color[0] or REC)
                        elif clip_slot.clip.is_triggered:
                            button.send_color_direct(color[sblink])
                        elif clip_slot.clip.is_playing:
                            button.send_color_direct(color[0])
                        else:
                            button.send_color_direct(color[1])
                    elif clip_slot.will_record_on_start:
                        button.send_color_direct(sblink == 0 and REC or REC_DIM)
                    elif clip_slot.is_playing:
                        button.send_color_direct(PColor.CLIP_GROUP_PLAY[0])
                    elif clip_slot.controls_other_clips:
                        button.send_color_direct(PColor.CLIP_GROUP_CONTROL[0])
                    elif clip_slot.is_triggered:
                        button.send_color_direct(sblink == 0 and TRIGG or TRIGG_DIM)

    def convertToHSB(self, rgb_color):
        return toHSB(rgb_color)

    def get_color_cmode_base(self, clip_slot):
        if clip_slot != None:
            if clip_slot.has_clip:
                rgb = clip_slot.clip.color
                color = self._color_manager.convertToHSB(clip_slot.clip.color)
                return color
            elif clip_slot.controls_other_clips:
                pass
        return PColor.OFF

    def notify_mono(self, blink):
        sblink = blink / 2
        fblink = blink % 2
        for scene_index in range(4):
            scene = self.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)._clip_slot
                button = self._matrix[scene_index][track_index]
                if clip_slot != None:
                    state = self.get_mono_state(clip_slot)
                    if state:
                        val = state[0]
                        bval = state[1]
                        if bval == 0:
                            if val == 1:
                                button.turn_on()
                            else:
                                button.turn_off()
                        elif bval == 1:
                            if sblink == 0:
                                button.turn_on()
                            else:
                                button.turn_off()
                        elif bval == 2:
                            if fblink == 0:
                                button.turn_on()
                            else:
                                button.turn_off()
                    else:
                        button.turn_off()
                else:
                    button.turn_off()

    def on_track_list_changed(self):
        num_tracks = len(self.tracks_to_use())
        new_track_offset = self.track_offset()
        if new_track_offset >= num_tracks:
            new_track_offset = num_tracks - 1
            new_track_offset -= new_track_offset % self._track_banking_increment
        self._reassign_tracks()
        self.set_offsets(new_track_offset, self.scene_offset())

    def update(self):
        SessionComponent.update(self)
        self._bank_up_button.update()
        self._bank_down_button.update()
        self._bank_left_button.update()
        self._bank_right_button.update()

    def _bank_right(self):
        return self.set_offsets(self.track_offset() + self._track_banking_increment, self.scene_offset())

    def _bank_left(self):
        return self.set_offsets(max(self.track_offset() - self._track_banking_increment, 0), self.scene_offset())

    def bank_down(self):
        if self.is_enabled():
            newoff = max(0, self._scene_offset - 1)
            self.set_offsets(self._track_offset, newoff)

    def bank_up(self):
        if self.is_enabled():
            self.set_offsets(self._track_offset, self._scene_offset + 1)

    def bank_left(self):
        if self.is_enabled():
            self.set_offsets(max(0, self._track_offset - 1), self._scene_offset)

    def bank_right(self):
        if self.is_enabled():
            self.set_offsets(self._track_offset + 1, self._scene_offset)

    def _allow_updates(self):
        return True

    def disconnect(self):
        self._matrix = None
        self._mode_button = None
        SessionComponent.disconnect(self)