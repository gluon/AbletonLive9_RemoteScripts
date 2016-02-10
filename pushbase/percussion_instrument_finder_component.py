#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/percussion_instrument_finder_component.py
from __future__ import absolute_import, print_function
import Live
from itertools import chain
from ableton.v2.base import Subject, listens_group, liveobj_changed, liveobj_valid
from ableton.v2.control_surface import Component
from .device_chain_utils import find_instrument_devices, find_instrument_meeting_requirement

class PercussionInstrumentFinderComponent(Component, Subject):
    """
    Looks in the hierarchy of devices of the selected track, looking
    for the first available drum-rack or sliced simpler (depth-first),
    updating as the device list changes.
    """
    __events__ = ('instrument',)
    _drum_group = None
    _simpler = None

    def __init__(self, device_parent = None, *a, **k):
        raise liveobj_valid(device_parent) or AssertionError
        super(PercussionInstrumentFinderComponent, self).__init__(*a, **k)
        self._device_parent = None
        self.device_parent = device_parent

    @property
    def drum_group(self):
        """
        The latest found drum rack.
        """
        return self._drum_group

    @property
    def sliced_simpler(self):
        """
        The latest found simpler in slicing mode.
        """
        return self._simpler

    def _get_device_parent(self):
        """
        The currently observed track.
        """
        return self._device_parent

    def _set_device_parent(self, device_parent):
        if liveobj_changed(self._device_parent, device_parent):
            self._device_parent = device_parent
            self.update()

    device_parent = property(_get_device_parent, _set_device_parent)

    @listens_group('devices')
    def __on_devices_changed(self, chain):
        self.update()

    @listens_group('chains')
    def __on_chains_changed(self, chain):
        self.update()

    @listens_group('playback_mode')
    def __on_slicing_changed(self, _simpler):
        self.update()

    def update(self):
        super(PercussionInstrumentFinderComponent, self).update()
        if self.is_enabled():
            self._update_listeners()
            self._update_instruments()

    def _update_listeners(self):
        device_parent = self.device_parent
        devices = list(find_instrument_devices(device_parent))
        racks = filter(lambda d: d.can_have_chains, devices)
        simplers = filter(lambda d: hasattr(d, 'playback_mode'), devices)
        chains = list(chain([device_parent], *[ d.chains for d in racks ]))
        self.__on_chains_changed.replace_subjects(racks)
        self.__on_devices_changed.replace_subjects(chains)
        self.__on_slicing_changed.replace_subjects(simplers)

    def _update_instruments(self):
        drum_group = find_drum_group_device(self.device_parent)
        simpler = find_sliced_simpler(self.device_parent)
        do_notify = liveobj_changed(drum_group, self._drum_group) or liveobj_changed(simpler, self._simpler)
        self._drum_group = drum_group
        self._simpler = simpler
        if do_notify:
            self.notify_instrument()


def find_drum_group_device(track_or_chain):
    """
    Looks up recursively for a drum_group device in the track.
    """
    requirement = lambda i: i.can_have_drum_pads
    return find_instrument_meeting_requirement(requirement, track_or_chain)


def find_sliced_simpler(track_or_chain):
    """
    Looks up recursively for a sliced simpler device in the track.
    """
    requirement = lambda i: getattr(i, 'playback_mode', None) == Live.SimplerDevice.PlaybackMode.slicing
    return find_instrument_meeting_requirement(requirement, track_or_chain)