#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/SpecialChanStripComponent.py
from _Framework.Util import flatten
from _Framework import Task
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.InputControlElement import ParameterSlot
from _Framework.TrackArmState import TrackArmState
from MessageBoxComponent import Messenger
from consts import MessageBoxText
import consts
import Live
TRACK_FOLD_DELAY = 0.5
TRACK_PARAMETER_NAMES = ('Volume', 'Pan', 'Send A', 'Send B', 'Send C', 'Send D', 'Send E', 'Send F', 'Send G', 'Send H', 'Send I', 'Send J', 'Send K', 'Send L')

def param_value_to_graphic(param, graphic):
    if param != None:
        param_range = param.max - param.min
        graph_range = len(graphic) - 1
        value = int((param.value - param.min) / param_range * graph_range)
        graphic_display_string = graphic[value]
    else:
        graphic_display_string = ' '
    return graphic_display_string


class SpecialChanStripComponent(ChannelStripComponent, Messenger):
    """
    Channel strip component with press & hold mute solo and stop
    buttons
    """

    def __init__(self, *a, **k):
        super(SpecialChanStripComponent, self).__init__(*a, **k)
        self.empty_color = 'Option.Unused'
        self._invert_mute_feedback = True
        self._duplicate_button = None
        self._selector_button = None
        self._delete_handler = None
        self._track_parameter_name_sources = [ DisplayDataSource(' ') for _ in xrange(14) ]
        self._track_parameter_data_sources = [ DisplayDataSource(' ') for _ in xrange(14) ]
        self._track_parameter_graphic_sources = [ DisplayDataSource(' ') for _ in xrange(14) ]
        self._on_return_tracks_changed.subject = self.song()
        self._on_selected_track_changed.subject = self.song().view
        self._fold_task = self._tasks.add(Task.sequence(Task.wait(TRACK_FOLD_DELAY), Task.run(self._do_fold_track))).kill()
        self._cue_volume_slot = self.register_disconnectable(ParameterSlot())
        self._track_state = self.register_disconnectable(TrackArmState())
        self._on_arm_state_changed.subject = self._track_state

    def set_delete_handler(self, delete_handler):
        self._delete_handler = delete_handler

    def set_volume_control(self, control):
        if control:
            control.mapping_sensitivity = consts.CONTINUOUS_MAPPING_SENSITIVITY
        super(SpecialChanStripComponent, self).set_volume_control(control)

    def set_pan_control(self, control):
        if control:
            control.mapping_sensitivity = consts.CONTINUOUS_MAPPING_SENSITIVITY
        super(SpecialChanStripComponent, self).set_pan_control(control)

    def set_send_controls(self, controls):
        if controls != None:
            for control in controls:
                if control:
                    control.mapping_sensitivity = consts.CONTINUOUS_MAPPING_SENSITIVITY

        super(SpecialChanStripComponent, self).set_send_controls(controls)

    def set_cue_volume_control(self, control):
        if control:
            control.mapping_sensitivity = consts.CONTINUOUS_MAPPING_SENSITIVITY
        self._cue_volume_slot.control = control

    def set_duplicate_button(self, duplicate_button):
        self._duplicate_button = duplicate_button

    def set_selector_button(self, selector_button):
        self._selector_button = selector_button

    def track_parameter_data_sources(self, index):
        return self._track_parameter_data_sources[index]

    def track_parameter_graphic_sources(self, index):
        return self._track_parameter_graphic_sources[index]

    def track_parameter_name_sources(self, index):
        return self._track_parameter_name_sources[index]

    def get_track(self):
        return self._track

    def set_track(self, track):
        self._track_state.set_track(track)
        super(SpecialChanStripComponent, self).set_track(track)
        self._update_track_listeners()
        self._update_parameter_name_sources()
        self._update_parameter_values()

    @subject_slot('arm')
    def _on_arm_state_changed(self):
        if self.is_enabled() and self._track:
            self._update_track_button()

    @subject_slot('return_tracks')
    def _on_return_tracks_changed(self):
        self._update_track_listeners()
        self._update_parameter_name_sources()
        self._update_parameter_values()

    @subject_slot('selected_track')
    def _on_selected_track_changed(self):
        self.on_selected_track_changed()

    def on_selected_track_changed(self):
        self._update_track_listeners()
        self._update_track_name_data_source()
        self._update_track_button()

    def _update_track_button(self):
        if self.is_enabled() and self._select_button != None:
            if self._track == None:
                self._select_button.set_light(self.empty_color)
            elif self._track.can_be_armed and (self._track.arm or self._track.implicit_arm):
                if self._track == self.song().view.selected_track:
                    self._select_button.set_light('Mixer.ArmSelected')
                else:
                    self._select_button.set_light('Mixer.ArmUnselected')
            elif self._track == self.song().view.selected_track:
                self._select_button.turn_on()
            else:
                self._select_button.turn_off()

    def _update_track_listeners(self):
        mixer = self._track.mixer_device if self._track else None
        sends = mixer.sends if mixer and self._track != self.song().master_track else ()
        cue_volume = mixer.cue_volume if self._track == self.song().master_track else None
        self._cue_volume_slot.parameter = cue_volume
        self._on_volume_value_changed.subject = mixer and mixer.volume
        self._on_panning_value_changed.subject = mixer and mixer.panning
        self._on_sends_value_changed.replace_subjects(sends)

    def _update_parameter_name_sources(self):
        num_params = self._track and len(self._track.mixer_device.sends) + 2
        for index, source in enumerate(self._track_parameter_name_sources):
            if index < num_params:
                source.set_display_string(TRACK_PARAMETER_NAMES[index])
            else:
                source.set_display_string(' ')

    def _update_track_name_data_source(self):
        if self._track_name_data_source:
            if self._track != None:
                selected = self._track == self.song().view.selected_track
                prefix = consts.CHAR_SELECT if selected else ''
                self._track_name_data_source.set_display_string(prefix + self._track.name)
            else:
                self._track_name_data_source.set_display_string(' ')

    @property
    def _is_deleting(self):
        return self._delete_handler and self._delete_handler.is_deleting

    def _select_value(self, value):
        if self.is_enabled() and self._track:
            if value and self._duplicate_button and self._duplicate_button.is_pressed():
                self._do_duplicate_track(self._track)
            elif value and self._is_deleting:
                self._do_delete_track(self._track)
            elif value and self._shift_pressed:
                self._do_toggle_arm(exclusive=False)
            else:
                self._select_value_without_modifier(value)

    def _mute_value(self, value):
        if self.is_enabled() and self._track != None:
            if not self._mute_button.is_momentary() or value != 0:
                if self._is_deleting:
                    self._delete_handler.delete_clip_envelope(self._track.mixer_device.track_activator)
                else:
                    super(SpecialChanStripComponent, self)._mute_value(value)

    def _do_toggle_arm(self, exclusive = False):
        if self._track.can_be_armed:
            self._track.arm = not self._track.arm
            if exclusive and (self._track.implicit_arm or self._track.arm):
                for track in self.song().tracks:
                    if track.can_be_armed and track != self._track:
                        track.arm = False

    def _select_value_without_modifier(self, value):
        if value and self.song().view.selected_track == self._track:
            self._do_toggle_arm(exclusive=self.song().exclusive_arm)
        else:
            super(SpecialChanStripComponent, self)._select_value(value)
        if value and self._track.is_foldable and self._select_button.is_momentary():
            self._fold_task.restart()
        else:
            self._fold_task.kill()

    def _do_delete_track(self, track):
        try:
            track_index = list(self.song().tracks).index(track)
            name = track.name
            self.song().delete_track(track_index)
            self.show_notification(MessageBoxText.DELETE_TRACK % name)
        except RuntimeError:
            self.expect_dialog(MessageBoxText.TRACK_DELETE_FAILED)
        except ValueError:
            pass

    def _do_duplicate_track(self, track):
        try:
            track_index = list(self.song().tracks).index(track)
            self.song().duplicate_track(track_index)
            self.show_notification(MessageBoxText.DUPLICATE_TRACK % track.name)
        except Live.Base.LimitationError:
            self.expect_dialog(MessageBoxText.TRACK_LIMIT_REACHED)
        except RuntimeError:
            self.expect_dialog(MessageBoxText.TRACK_DUPLICATION_FAILED)
        except ValueError:
            pass

    def _do_select_track(self, track):
        pass

    def _do_fold_track(self):
        if self.is_enabled() and self._track != None and self._track.is_foldable:
            self._track.fold_state = not self._track.fold_state

    @subject_slot('value')
    def _on_volume_value_changed(self):
        if self.is_enabled() and self._track != None:
            param = self._track.mixer_device.volume
            text = self._track_parameter_data_sources[0]
            graph = self._track_parameter_graphic_sources[0]
            text.set_display_string(str(param))
            graph.set_display_string(param_value_to_graphic(param, consts.GRAPH_VOL))

    @subject_slot('value')
    def _on_panning_value_changed(self):
        if self.is_enabled() and self._track != None:
            param = self._track.mixer_device.panning
            text = self._track_parameter_data_sources[1]
            graph = self._track_parameter_graphic_sources[1]
            text.set_display_string(str(param))
            graph.set_display_string(param_value_to_graphic(param, consts.GRAPH_PAN))

    @subject_slot_group('value')
    def _on_sends_value_changed(self, send):
        if self.is_enabled() and self._track != None and self._track != self.song().master_track and send in list(self._track.mixer_device.sends):
            index = list(self._track.mixer_device.sends).index(send) + 2
            text = self._track_parameter_data_sources[index]
            graph = self._track_parameter_graphic_sources[index]
            text.set_display_string(str(send))
            graph.set_display_string(param_value_to_graphic(send, consts.GRAPH_VOL))

    def _update_parameter_values(self):
        for source in flatten(zip(self._track_parameter_data_sources, self._track_parameter_graphic_sources)):
            source.set_display_string(' ')

        self._on_volume_value_changed()
        self._on_panning_value_changed()
        if self._track and self._track != self.song().master_track:
            map(self._on_sends_value_changed, self._track.mixer_device.sends)