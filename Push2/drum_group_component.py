#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/drum_group_component.py
from __future__ import absolute_import, print_function
from itertools import ifilter, izip
from ableton.v2.base import flatten, liveobj_valid
from pushbase.device_chain_utils import find_instrument_devices
from pushbase.drum_group_component import DrumGroupComponent as DrumGroupComponentBase, DrumPadCopyHandler as DrumPadCopyHandlerBase
from .decoration import find_decorated_object
from .device_decoration import SimplerDecoratedPropertiesCopier

def find_simplers(chain):
    return ifilter(lambda i: hasattr(i, 'playback_mode'), find_instrument_devices(chain))


def find_all_simplers_on_pad(drum_pad):
    simplers = []
    for chain in drum_pad.chains:
        simplers.append(find_simplers(chain))

    return list(flatten(simplers))


class DrumPadCopyHandler(DrumPadCopyHandlerBase):

    def __init__(self, decorator_factory = None, song = None, *a, **k):
        super(DrumPadCopyHandler, self).__init__(*a, **k)
        self._song = song
        self._decorator_factory = decorator_factory

    def _finish_copying(self, drum_group_device, destination_pad):
        notification_reference = super(DrumPadCopyHandler, self)._finish_copying(drum_group_device, destination_pad)
        if self._source_pad.note != destination_pad.note and len(destination_pad.chains) > 0:
            source_simplers = find_all_simplers_on_pad(self._source_pad)
            destination_simplers = find_all_simplers_on_pad(destination_pad)
            for source, destination in izip(source_simplers, destination_simplers):
                decorated = find_decorated_object(source, self._decorator_factory)
                if decorated:
                    self._copy_simpler_properties(decorated, destination)

        return notification_reference

    def _copy_simpler_properties(self, source_simpler, destination_simpler):
        copier = SimplerDecoratedPropertiesCopier(source_simpler, self._decorator_factory)
        copier.apply_properties(destination_simpler, song=self._song)


class DrumGroupComponent(DrumGroupComponentBase):
    __events__ = ('mute_solo_stop_cancel_action_performed',)

    def __init__(self, tracks_provider = None, device_decorator_factory = None, *a, **k):
        raise tracks_provider is not None or AssertionError
        self._decorator_factory = device_decorator_factory
        super(DrumGroupComponent, self).__init__(*a, **k)
        self.mute_button.color = 'DefaultButton.Transparent'
        self.solo_button.color = 'DefaultButton.Transparent'
        self._tracks_provider = tracks_provider

    def select_drum_pad(self, drum_pad):
        if len(drum_pad.chains) > 0 and self.song.view.selected_track.is_showing_chains:
            self._tracks_provider.scroll_into_view(drum_pad.chains[0])

    def _on_matrix_pressed(self, pad):
        super(DrumGroupComponent, self)._on_matrix_pressed(pad)
        self.notify_mute_solo_stop_cancel_action_performed()

    def _on_selected_drum_pad_changed(self):
        super(DrumGroupComponent, self)._on_selected_drum_pad_changed()
        chain = self._selected_drum_pad.chains[0] if self._selected_drum_pad and len(self._selected_drum_pad.chains) > 0 else None
        if self.song.view.selected_track.is_showing_chains and liveobj_valid(chain):
            self._tracks_provider.set_selected_item_without_updating_view(self._selected_drum_pad.chains[0])

    def delete_drum_pad_content(self, drum_pad):
        self._tracks_provider.synchronize_selection_with_live_view()
        super(DrumGroupComponent, self).delete_drum_pad_content(drum_pad)

    def _make_copy_handler(self, notification_formatter):
        return DrumPadCopyHandler(show_notification=self.show_notification, notification_formatter=notification_formatter, decorator_factory=self._decorator_factory, song=self.song)