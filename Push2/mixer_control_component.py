#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/mixer_control_component.py
from __future__ import absolute_import, print_function
from contextlib import contextmanager
from functools import partial
from itertools import izip, izip_longest
from math import ceil
from ableton.v2.base import clamp, depends, listens, liveobj_valid, NamedTuple
from ableton.v2.control_surface.control import control_list, ButtonControl
from ableton.v2.control_surface.mode import ModesComponent
from pushbase.mapped_control import MappedControl
from .real_time_channel import RealTimeDataComponent
from .item_lister_component import SimpleItemSlot
MIXER_SECTIONS = ('Volumes', 'Pans')
SEND_SECTIONS = ['A Sends',
 'B Sends',
 'C Sends',
 'D Sends',
 'E Sends',
 'F Sends',
 'G Sends',
 'H Sends',
 'I Sends',
 'J Sends',
 'K Sends',
 'L Sends']
SEND_LIST_LENGTH = 5
SEND_MODE_NAMES = ['send_slot_one',
 'send_slot_two',
 'send_slot_three',
 'send_slot_four',
 'send_slot_five']

class MixerSectionDescription(NamedTuple):
    view = None
    parameter_name = None


class MixerControlComponent(ModesComponent):
    __events__ = ('items', 'selected_item')
    controls = control_list(MappedControl)
    cycle_sends_button = ButtonControl(color='DefaultButton.Off')

    @depends(tracks_provider=None, real_time_mapper=None, register_real_time_data=None)
    def __init__(self, view_model = None, tracks_provider = None, real_time_mapper = None, register_real_time_data = None, *a, **k):
        raise liveobj_valid(real_time_mapper) or AssertionError
        raise view_model is not None or AssertionError
        raise tracks_provider is not None or AssertionError
        super(MixerControlComponent, self).__init__(*a, **k)
        self._send_offset = 0
        self.real_time_meter_handlers = [ RealTimeDataComponent(channel_type='meter', real_time_mapper=real_time_mapper, register_real_time_data=register_real_time_data, is_enabled=False) for _ in xrange(8) ]
        self._track_provider = tracks_provider
        self._on_return_tracks_changed.subject = self.song
        self._on_mode_changed.subject = self
        self._mixer_section_view = None
        self._mixer_sections = []
        self._selected_view = view_model.volumeControlListView
        self._parameter_getter = lambda x: None
        self._setup_modes(view_model)
        self.selected_mode = 'volume'
        self._selected_item = ''
        self._items = []
        self._on_return_tracks_changed()
        self._update_mixer_sections()
        self._on_items_changed.subject = self._track_provider
        self._on_selected_item_changed.subject = self._track_provider

    def _setup_modes(self, view_model):
        self._add_mode('volume', view_model.volumeControlListView, lambda mixer: mixer.volume, additional_mode_contents=self.real_time_meter_handlers)
        self._add_mode('panning', view_model.panControlListView, lambda mixer: mixer.panning)

        def add_send_mode(index):
            self._add_mode(SEND_MODE_NAMES[index], view_model.sendControlListView, lambda mixer: (mixer.sends[self._send_offset + index] if len(mixer.sends) > self._send_offset + index else None))

        for i in xrange(SEND_LIST_LENGTH):
            add_send_mode(i)

    def _add_mode(self, mode, view, parameter_getter, additional_mode_contents = []):
        description = MixerSectionDescription(view=view, parameter_getter=parameter_getter)
        self.add_mode(mode, additional_mode_contents + [partial(self._set_mode, description)])
        mode_button = self.get_mode_button(mode)
        mode_button.mode_selected_color = 'MixerControlView.SectionSelected'
        mode_button.mode_unselected_color = 'MixerControlView.SectionUnSelected'

    def on_enabled_changed(self):
        super(MixerControlComponent, self).on_enabled_changed()
        self._selected_view.visible = self.is_enabled()
        self._update_mixer_sections()
        if not self.is_enabled():
            self._update_realtime_ids()

    def set_mixer_section(self, mixer_section):
        self._mixer_section_view = mixer_section
        if self._mixer_section_view:
            self._mixer_section_view.model.mode = 'Global'
            self._update_mixer_sections()

    @property
    def number_sends(self):
        return len(self._track_provider.selected_item.mixer_device.sends)

    def _set_mode(self, description):
        self._selected_view.visible = False
        self._selected_view = description.view
        self._parameter_getter = description.parameter_getter
        self._update_controls(self._parameter_getter, self._selected_view)
        self._selected_view.visible = True

    @listens('selected_mode')
    def _on_mode_changed(self, selected_mode):
        if selected_mode in SEND_MODE_NAMES:
            index = SEND_MODE_NAMES.index(selected_mode)
            self._selected_item = SEND_SECTIONS[clamp(index + self._send_offset, 0, self.number_sends - 1)]
        else:
            self._selected_item = MIXER_SECTIONS[1] if selected_mode == 'panning' else MIXER_SECTIONS[0]
        self.notify_selected_item()

    @listens('return_tracks')
    def _on_return_tracks_changed(self):
        with self._updating_send_offset_mode_selection():
            self._update_mode_selection()
            new_send_offset = max(0, int(ceil(float(self.number_sends) / float(SEND_LIST_LENGTH) - 1) * SEND_LIST_LENGTH))
            if new_send_offset < self._send_offset:
                self._send_offset = new_send_offset

    @listens('items')
    def _on_items_changed(self):
        self._update_controls(self._parameter_getter, self._selected_view)

    @listens('selected_item')
    def _on_selected_item_changed(self):
        if self.number_sends <= SEND_LIST_LENGTH:
            self._send_offset = 0
        self._update_mode_selection()
        self._update_mixer_sections()
        self._update_buttons(self.selected_mode)

    def _update_mode_selection(self):
        number_sends = self.number_sends
        if self.selected_mode in SEND_MODE_NAMES:
            index = SEND_MODE_NAMES.index(self.selected_mode)
            if index + self._send_offset >= number_sends and number_sends > 0:
                self.selected_mode = SEND_MODE_NAMES[number_sends % SEND_LIST_LENGTH - 1]
            elif index == 0 and number_sends == 0:
                self.selected_mode = 'panning'

    def _update_mixer_sections(self):
        if self.is_enabled():
            position = max(self._send_offset, 0)
            pos_range = min(self.number_sends - position, SEND_LIST_LENGTH)
            mixer_section_names = list(MIXER_SECTIONS) + SEND_SECTIONS[position:position + pos_range]
            self._mixer_sections = [ SimpleItemSlot(name=name) for name in mixer_section_names ]
            if self.number_sends > SEND_LIST_LENGTH:
                self._mixer_sections.extend([SimpleItemSlot()] * (8 - len(self._mixer_sections)))
                self._mixer_sections[7] = SimpleItemSlot(icon='page_right.svg')
            self.notify_items()
            if self.selected_mode in SEND_MODE_NAMES:
                index = SEND_MODE_NAMES.index(self.selected_mode)
                self._selected_item = SEND_SECTIONS[index + self._send_offset]
                self.notify_selected_item()

    @property
    def items(self):
        return self._mixer_sections

    @property
    def selected_item(self):
        return self._selected_item

    def _update_controls(self, parameter_getter, control_view):
        parameters = self._get_parameter_for_tracks(parameter_getter)
        control_view.parameters = parameters
        self._update_realtime_ids()
        for control, parameter in izip_longest(self.controls, parameters):
            control.mapped_parameter = parameter

    def _update_realtime_ids(self):
        mixables = self._track_provider.items
        for handler, mixable in izip(self.real_time_meter_handlers, mixables):
            handler.set_data(mixable.mixer_device if liveobj_valid(mixable) else None)

    def _get_parameter_for_tracks(self, parameter_getter):
        tracks = self._track_provider.items
        self.controls.control_count = len(tracks)
        return map(lambda t: (parameter_getter(t.mixer_device) if t else None), tracks)

    def mode_can_be_used(self, mode):
        return mode not in SEND_MODE_NAMES or SEND_MODE_NAMES.index(mode) + self._send_offset < self.number_sends

    def _update_buttons(self, selected_mode):
        for name in self._mode_map.iterkeys():
            self.get_mode_button(name).enabled = self.mode_can_be_used(name)

        self.cycle_sends_button.enabled = self.number_sends > SEND_LIST_LENGTH

    @cycle_sends_button.pressed
    def cycle_sends_button(self, button):
        button.color = 'MixerControlView.SectionSelected'

    @cycle_sends_button.released
    def cycle_sends_button(self, button):
        button.color = 'MixerControlView.SectionUnSelected'
        self._cycle_send_offset()

    def _cycle_send_offset(self):
        with self._updating_send_offset_mode_selection():
            new_offset = self._send_offset + SEND_LIST_LENGTH
            self._send_offset = new_offset if new_offset < self.number_sends else 0
            if self.selected_mode in SEND_MODE_NAMES:
                self.selected_mode = SEND_MODE_NAMES[0]

    @contextmanager
    def _updating_send_offset_mode_selection(self):
        yield
        self._update_mixer_sections()
        self._update_buttons(self.selected_mode)
        self._update_controls(self._parameter_getter, self._selected_view)