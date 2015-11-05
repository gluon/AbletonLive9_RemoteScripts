#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/pushbase/device_chain_utils.py
import Live
from itertools import imap, chain
from functools import partial
from ableton.v2.base import find_if

def is_first_device_on_pad(device, drum_pad):
    return find_if(lambda pad: pad.chains and pad.chains[0].devices and pad.chains[0].devices[0] == device, drum_pad.canonical_parent.drum_pads)


def find_instrument_devices(track_or_chain):
    """
    Returns a list with all instruments from a track or chain.
    """
    instrument = find_if(lambda d: d.type == Live.Device.DeviceType.instrument, track_or_chain.devices)
    if instrument:
        if not instrument.can_have_drum_pads and instrument.can_have_chains:
            return chain([instrument], *imap(find_instrument_devices, instrument.chains))
        return [instrument]
    return []


def find_instrument_meeting_requirement(requirement, track_or_chain):
    instrument = find_if(lambda d: d.type == Live.Device.DeviceType.instrument, track_or_chain.devices)
    if instrument:
        if requirement(instrument):
            return instrument
        elif instrument.can_have_chains:
            recursive_call = partial(find_instrument_meeting_requirement, requirement)
            return find_if(bool, imap(recursive_call, instrument.chains))