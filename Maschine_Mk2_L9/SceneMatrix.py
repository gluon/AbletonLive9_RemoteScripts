#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\SceneMatrix.py
import Live
from MIDI_Map import *
from _Framework.CompoundComponent import *
from _Framework.ButtonElement import ButtonElement
from SceneElement import SceneElement
from ControlHandler import ControlHandler
from Mk2KnobControl import *

class SceneMatrix:
    __module__ = __name__
    __doc__ = ' Special button class that can be configured with custom on- and off-values '

    def __init__(self, ctrl):
        self.track_offset = 0
        self.scene_offset = 0
        self._scenes = []
        self._control = ctrl
        self.mode = SCENE_MODE_NORMAL
        self.receives_notify = True
        self.control_handler = ControlHandler(ctrl, self)
        self.soloexclusive = True
        self.mutedsolo = False
        for index in range(16):
            self._scenes.append(SceneElement(index, self))

        self._control.song().view.add_selected_track_listener(self._sel_track_changed)

    def notify_scene_mode(self, value):
        if self.receives_notify:
            num_scenes = len(self._scenes)
            for index in range(num_scenes):
                if value == 1:
                    self._scenes[index].eval()
                self._scenes[index].notify(value)

    def update_control_selection(self):
        trindex = self._control.index_in_strip(self.control_handler.track)
        self.control_handler.sel_track_parm_index = trindex

    def mod_track_offset(self, delta):
        nr_of_tracks = len(self._control.song().tracks)
        newoffset = self.track_offset + delta * 16
        if newoffset > -1 and newoffset < nr_of_tracks:
            self.track_offset = newoffset
            self.show_track_control_message(nr_of_tracks)
            self.update()

    def mod_scene_offset(self, delta):
        scenes = self._control.song().scenes
        nr_of_scenes = len(scenes)
        newoffset = self.scene_offset + delta
        if newoffset > -1 and newoffset + 15 < nr_of_scenes:
            self.scene_offset = newoffset
            self.show_scene_control_message(nr_of_scenes)
            self.update()

    def show_scene_control_message(self, nr_of_scenes):
        self._control.show_message('Pads control Scenes ' + str(self.scene_offset + 1) + ' to ' + str(min(nr_of_scenes, self.scene_offset + 16)) + ' in Scene Mode')

    def show_track_control_message(self, nr_of_tracks):
        self._control.show_message('Pads control Tracks ' + str(self.track_offset + 1) + ' to ' + str(min(nr_of_tracks, self.track_offset + 16)))

    def _sel_track_changed(self):
        if self.mode == SCENE_MODE_SELECT:
            self.update()

    def in_main_mode(self):
        if self.mode == SCENE_MODE_NORMAL or self.mode == SCENE_MODE_CONTROL:
            return True
        return False

    def get_element(self, col, row):
        index = (3 - col) * 4 + row
        return self._scenes[index]

    def set_knob_mode(self, mode):
        self._control._master_knob._set_mode(KN2_MODE_GENERAL)

    def set_armsolo_exclusive(self, button):
        if self.soloexclusive:
            self.soloexclusive = False
            self._control.show_message(str('Exclusive Mode Arm/Solo Off'))
            button.send_value(0)
        else:
            self.soloexclusive = True
            self._control.show_message(str('Exclusive Mode Arm/Solo On'))
            button.send_value(100)

    def unbind(self):
        self._control.song().view.remove_selected_track_listener(self._sel_track_changed)
        num_scenes = len(self._scenes)
        for index in range(num_scenes):
            self._scenes[index].disable_color()
            self._scenes[index].force_value(0)
            self._scenes[index].unbind()

    def deassign(self):
        num_scenes = len(self._scenes)
        for index in range(num_scenes):
            self._scenes[index].set_launch_button(None)
            self._scenes[index].set_scene(None)
            self._scenes[index].set_track(None)
            self._scenes[index].eval()

    def assign(self):
        scenes = self._control.song().scenes
        tracks = self._control.song().tracks
        for index in range(16):
            tr_index = index + self.track_offset
            sc_index = index + self.scene_offset
            self._scenes[index].set_launch_button(self._control._button_sequence[index])
            if sc_index < len(scenes):
                self._scenes[index].set_scene(scenes[sc_index])
            else:
                self._scenes[index].set_scene(None)
            if tr_index < len(tracks):
                self._scenes[index].set_track(tracks[tr_index])
            else:
                self._scenes[index].set_track(None)
            self._scenes[index].eval()

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == SCENE_MODE_NORMAL or self.mode == SCENE_MODE_STOP:
            self.receives_notify = True
        else:
            self.receives_notify = False
        num_scenes = len(self._scenes)
        for index in range(num_scenes):
            self._scenes[index].assign_mode(mode)

        if mode == SCENE_MODE_CONTROL and self.control_handler.parm == None:
            trindex = self.control_handler.sel_track_parm_index
            track = self._control._mixer._channel_strips[trindex]._track
            if track != None:
                self.control_handler.track = track
                self.control_handler.reassign_mix_parm()
        self.update()

    def do_solo(self, track_index):
        if self.soloexclusive:
            tracks = self._control.song().tracks
            for index in range(len(tracks)):
                if index != track_index and tracks[index].solo:
                    tracks[index].solo = False

    def do_arm(self, track_index):
        if self.soloexclusive:
            tracks = self._control.song().tracks
            for index in range(len(tracks)):
                if index != track_index and tracks[index].can_be_armed and tracks[index].arm:
                    tracks[index].arm = False

    def eval_matrix(self):
        for index in range(16):
            self._scenes[index].eval()

    def fire_values(self):
        for index in range(16):
            self._scenes[index].set_value()

    def eval_control(self):
        nr_of_tracks = len(self._control.song().return_tracks)
        if self.control_handler.selected_sends_index >= nr_of_tracks:
            self.control_handler.selected_sends_index = nr_of_tracks - 1

    def setSelectedTrack(self, track):
        self._control.song().view.selected_track = track

    def getSelectedTrack(self):
        return self._control.song().view.selected_track

    def update_on_device(self, device):
        if self.mode == SCENE_MODE_CONTROL and self.control_handler.mode == CONTROL_DEVICE:
            self.control_handler.set_device(device)
            self.update()

    def update_on_device_parm_changed(self):
        if self.mode == SCENE_MODE_CONTROL and self.control_handler.mode == CONTROL_DEVICE:
            self.update()

    def disconnect(self):
        num_scenes = len(self._scenes)
        for index in range(num_scenes):
            self._scenes[index].disconnect()

        self.unbind()
        self._scenes = None
        self._control = None
        self.mode = None
        self.receives_notify = None
        self.control_handler.disconnect()
        self.soloexclusive = None
        self.mutedsolo = None
        self.control_handler = None

    def fix_track_offset(self, nr_of_tracks):
        while self.track_offset >= nr_of_tracks:
            self.track_offset -= 16

        self.show_track_control_message(nr_of_tracks)

    def fix_scene_offset(self, nr_of_scenes, show_message = True):
        while self.scene_offset + 15 >= nr_of_scenes and self.scene_offset > 0:
            self.scene_offset -= 1

        if show_message:
            self.show_scene_control_message(nr_of_scenes)

    def update(self, force = False):
        scenes = self._control.song().scenes
        tracks = self._control.song().tracks
        nr_of_tracks = len(tracks)
        nr_of_scenes = len(scenes)
        if self.track_offset < 0:
            self.track_offset = 0
        elif self.track_offset >= nr_of_tracks:
            self.fix_track_offset(nr_of_tracks)
        if self.scene_offset < 0:
            self.scene_offset = 0
        elif self.scene_offset + 15 >= nr_of_scenes:
            self.fix_scene_offset(nr_of_scenes, False)
        self.eval_control()
        for index in range(16):
            tr_index = index + self.track_offset
            sc_index = index + self.scene_offset
            if sc_index < nr_of_scenes:
                self._scenes[index].set_scene(scenes[sc_index])
            else:
                self._scenes[index].set_scene(None)
            if tr_index < nr_of_tracks:
                self._scenes[index].set_track(tracks[tr_index])
            else:
                self._scenes[index].set_track(None)
            self._scenes[index].eval()
            self._scenes[index].set_value(force)