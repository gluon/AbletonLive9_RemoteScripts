#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Serato/Serato.py
from __future__ import with_statement
import Live
import libInterprocessCommsAPIPython
from PySCAClipControl import PySCAClipControl
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialSessionComponent import SpecialSessionComponent
from SpecialDeviceComponent import SpecialDeviceComponent

def fixed_value(value):
    """ Small utility function to extract fixed float values from integers """
    return float(value) / 65536L


NUM_SCENES = 8
NUM_TRACKS = 8
NUM_PARAMS = 8
CLIP_EVENTS = (libInterprocessCommsAPIPython.kAbletonClipControlEventClipPlayedDown, libInterprocessCommsAPIPython.kAbletonClipControlEventClipPlayedReleased)
SCENE_EVENTS = (libInterprocessCommsAPIPython.kAbletonClipControlEventScenePlayedDown, libInterprocessCommsAPIPython.kAbletonClipControlEventScenePlayedReleased)

class Serato(ControlSurface):

    def __init__(self, c_instance):
        publish_in_cs_list = True
        ControlSurface.__init__(self, c_instance, not publish_in_cs_list)
        self._device_selection_follows_track_selection = True
        with self.component_guard():
            self._matrix = None
            self._session = None
            self._mixer = None
            self._device = None
            self._scene_launch_buttons = None
            self._track_arm_buttons = None
            self._track_solo_buttons = None
            self._track_mute_buttons = None
            self._track_stop_buttons = None
            self._track_select_buttons = None
            self._device_on_off_button = None
            self._shift_button = None
            self._serato_interface = PySCAClipControl()
            self._serato_interface.PySCA_InitializeClipControl()
            self._setup_session_control()
            self._setup_mixer_control()
            self._setup_device_control()
            self._session.set_mixer(self._mixer)
            self.set_highlighting_session_component(self._session)

    def disconnect(self):
        ControlSurface.disconnect(self)
        self._serato_interface.PySCA_DeinitializeClipControl()
        self._serato_interface = None

    def connect_script_instances(self, instanciated_scripts):
        """ Called by the Application as soon as all scripts are initialized.
            You can connect yourself to other running scripts here, as we do it
            connect the extension modules (MackieControlXTs).
        """
        for control_surface in self._control_surfaces():
            control_surface_session = control_surface.highlighting_session_component()
            if control_surface_session:
                self._session.sync_to(control_surface_session)
                self._on_track_list_changed()
                break

    def build_midi_map(self, midi_map_handle):
        pass

    def update_display(self):
        ControlSurface.update_display(self)
        while self._serato_interface.PySCA_HasIncomingEvent():
            new_event = self._serato_interface.PySCA_GetIncomingEvent()
            if not self._handle_session_event(new_event):
                if not self._handle_mixer_event(new_event):
                    if not self._handle_device_event(new_event):
                        print 'Unhandled Event: ' + str(new_event)

    def _setup_session_control(self):
        is_momentary = True
        self._session = SpecialSessionComponent(NUM_TRACKS, NUM_SCENES)
        self._session.set_serato_interface(self._serato_interface)
        self._matrix = ButtonMatrixElement()
        self._scene_launch_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 0) for index in range(NUM_SCENES) ]
        self._track_stop_buttons = [ ButtonElement(not is_momentary, MIDI_NOTE_TYPE, 0, 0) for index in range(NUM_TRACKS) ]
        stop_all_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 0)
        self._session.set_stop_all_clips_button(stop_all_button)
        self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
        for scene_index in range(NUM_SCENES):
            scene = self._session.scene(scene_index)
            button_row = []
            scene.set_launch_button(self._scene_launch_buttons[scene_index])
            scene.set_index(scene_index)
            scene.set_serato_interface(self._serato_interface)
            for track_index in range(NUM_TRACKS):
                button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 0)
                button_row.append(button)
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(button)
                clip_slot.set_serato_interface(self._serato_interface)

            self._matrix.add_row(tuple(button_row))

    def _setup_mixer_control(self):
        is_momentary = True
        self._mixer = SpecialMixerComponent(NUM_TRACKS)
        self._mixer.set_serato_interface(self._serato_interface)
        self._mixer.master_strip().set_serato_interface(self._serato_interface)
        self._track_arm_buttons = []
        self._track_solo_buttons = []
        self._track_mute_buttons = []
        self._track_select_buttons = []
        self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 0)
        for track in range(NUM_TRACKS):
            strip = self._mixer.channel_strip(track)
            strip.set_serato_interface(self._serato_interface)
            self._track_arm_buttons.append(ButtonElement(not is_momentary, MIDI_NOTE_TYPE, 0, 0))
            self._track_solo_buttons.append(ButtonElement(not is_momentary, MIDI_NOTE_TYPE, 0, 0))
            self._track_mute_buttons.append(ButtonElement(not is_momentary, MIDI_NOTE_TYPE, 0, 0))
            self._track_select_buttons.append(ButtonElement(not is_momentary, MIDI_NOTE_TYPE, 0, 0))
            strip.set_arm_button(self._track_arm_buttons[-1])
            strip.set_solo_button(self._track_solo_buttons[-1])
            strip.set_mute_button(self._track_mute_buttons[-1])
            strip.set_select_button(self._track_select_buttons[-1])
            strip.set_shift_button(self._shift_button)

    def _setup_device_control(self):
        is_momentary = True
        self._device_on_off_button = ButtonElement(not is_momentary, MIDI_NOTE_TYPE, 0, 0)
        self._device = SpecialDeviceComponent()
        self._device.set_serato_interface(self._serato_interface)
        self._device.set_parameter_controls(tuple([ SliderElement(MIDI_CC_TYPE, 0, 0) for index in range(NUM_PARAMS) ]))
        self._device.set_on_off_button(self._device_on_off_button)
        self.set_device_component(self._device)

    def _handle_session_event(self, event):
        result = False
        if event.type in CLIP_EVENTS:
            value = 127 * int(event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventClipPlayedDown)
            track_index = event.key1 - 1
            scene_index = event.key2 - 1
            if track_index in range(NUM_TRACKS) and scene_index in range(NUM_SCENES):
                self._matrix.get_button(track_index, scene_index).receive_value(value)
            result = True
        elif event.type in SCENE_EVENTS:
            value = 127 * int(event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventScenePlayedDown)
            scene_index = event.key1 - 1
            if scene_index in range(NUM_SCENES):
                self._scene_launch_buttons[scene_index].receive_value(value)
            result = True
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlMatrixSizeChanged:
            new_width = event.key1
            new_height = event.key2
            self._session.set_size(new_width, new_height)
            result = True
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlMatrixOffsetChanged:
            x_increment = event.key1
            y_increment = event.key2
            self._session.move_by(x_increment, y_increment)
            result = True
        return result

    def _handle_mixer_event(self, event):
        result = True
        track_index = event.key1 - 1
        value = event.key2
        if event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackMasterGainChange:
            self._mixer.master_strip().set_track_volume(fixed_value(value))
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventMasterTrackStopped:
            self.song().stop_all_clips()
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventMasterTrackSelect:
            self.song().view.selected_track = self.song().master_track
        else:
            result = track_index in range(NUM_TRACKS) and self._handle_strip_event(event)
        return result

    def _handle_strip_event(self, event):
        result = True
        track_index = event.key1 - 1
        value = event.key2
        if value == 0:
            self._shift_button.receive_value(127)
        if event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackSolo:
            self._track_solo_buttons[track_index].receive_value(127)
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackRecord:
            self._track_arm_buttons[track_index].receive_value(127)
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackActive:
            self._track_mute_buttons[track_index].receive_value(127)
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackStopped:
            self._track_stop_buttons[track_index].receive_value(127)
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackSelect:
            self._track_select_buttons[track_index].receive_value(127)
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackGainChange:
            self._mixer.channel_strip(track_index).set_track_volume(fixed_value(value))
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackSendAChange:
            self._mixer.channel_strip(track_index).set_send(0, fixed_value(value))
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventTrackSendBChange:
            self._mixer.channel_strip(track_index).set_send(1, fixed_value(value))
        else:
            result = False
        self._shift_button.receive_value(0)
        return result

    def _handle_device_event(self, event):
        result = True
        if event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventDeviceValueChanged:
            self._device.set_parameter_value(event.key1 - 1, fixed_value(event.key2))
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventDeviceActivate:
            self._device_on_off_button.receive_value(127)
        elif event.type == libInterprocessCommsAPIPython.kAbletonClipControlEventDeviceFocusMove:
            self._move_device_focus(event.key1)
        else:
            result = False
        return result

    def _move_device_focus(self, increment):
        if not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain'):
            self.application().view.show_view('Detail')
            self.application().view.show_view('Detail/DeviceChain')
        else:
            modifier_pressed = True
            direction = Live.Application.Application.View.NavDirection.left
            if increment > 0:
                direction = Live.Application.Application.View.NavDirection.right
            self.application().view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)