#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/PadSensitivity.py
from itertools import repeat
from _Framework import Task
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Util import find_if, second, lazy_attribute, nop, NamedTuple
from .Sysex import to_bytes

class PadParameters(NamedTuple):
    """
    Describes the properties of pad parameters.
    """
    off_threshold = 0
    on_threshold = 0
    gain = 0
    curve1 = 0
    curve2 = 0
    name = ''

    def __str__(self):
        return self.name

    @lazy_attribute
    def sysex_bytes(self):
        return to_bytes(self.off_threshold, 4) + to_bytes(self.on_threshold, 4) + to_bytes(self.gain, 8) + to_bytes(self.curve1, 8) + to_bytes(self.curve2, 8)


def pad_parameter_sender(global_control, pad_control):
    """
    Sends the sensitivity parameters for a given pad, or all pads (pad
    == None) over the given ValueControl.
    """

    def do_send(parameters, pad = None):
        if pad != None:
            pad_control.send_value((pad,) + parameters.sysex_bytes)
        else:
            global_control.send_value(parameters.sysex_bytes)

    return do_send


class PadUpdateComponent(ControlSurfaceComponent):
    """
    Sets a set of parameters for different pads.  It keeps a set of
    profiles, and maps a profile to each pad.  It caches all
    modifications to the pad profiles, updating later optimally.
    
    The all_pads parameter contains the pads identifiers.
    
    The parameter_sender is a function that is used to update the
    pads. It takes the parameters as first value and a second optional
    value indicating the pad to update, or None to update all possible
    pads.
    """

    def __init__(self, all_pads = tuple(), parameter_sender = nop, default_profile = PadParameters(), update_delay = 0, *a, **k):
        raise find_if(lambda pad: pad < 0 or pad > 63, all_pads or []) == None or AssertionError
        super(PadUpdateComponent, self).__init__(*a, **k)
        self.parameter_sender = parameter_sender
        self._all_pads = set(all_pads)
        self._modified_pads = set(all_pads)
        self._profiles = {'default': default_profile}
        self._profile_for = dict(zip(all_pads, repeat('default')))
        self._profile_count = {'default': len(all_pads)}
        self._update_task = self._tasks.add(Task.sequence(Task.wait(update_delay), Task.run(self._update_modified)))
        self._update_task.restart()

    def set_profile(self, profile_id, parameters):
        self._profiles[profile_id] = parameters
        self._profile_count.setdefault(profile_id, 0)
        affected = [ k for k, v in self._profile_for.iteritems() if v == profile_id ]
        self._add_modified_pads(affected)

    def get_profile(self, profile_id):
        return self._profiles[profile_id]

    def set_pad(self, pad, new_profile):
        if not pad in self._all_pads:
            raise AssertionError
            raise new_profile in self._profile_count or AssertionError
            old_profile = self._profile_for[pad]
            old_profile != new_profile and self._add_modified_pads([pad])
            self._profile_for[pad] = new_profile
            self._profile_count[old_profile] -= 1
            self._profile_count[new_profile] += 1

    def update(self):
        super(PadUpdateComponent, self).update()
        self._add_modified_pads(self._all_pads)
        self._update_modified()

    def _update_modified(self):
        if not (self.is_enabled() and self._modified_pads and sum(self._profile_count.itervalues()) == len(self._all_pads)):
            raise AssertionError
            largest_profile, largest_count = max(self._profile_count.iteritems(), key=second)
            if len(self._all_pads) - largest_count + 1 < len(self._modified_pads):
                self.parameter_sender(self._profiles[largest_profile])
                for pad in self._all_pads:
                    profile = self._profile_for[pad]
                    if profile != largest_profile:
                        self.parameter_sender(self._profiles[profile], pad)

            else:
                for pad in self._modified_pads:
                    self.parameter_sender(self._profiles[self._profile_for[pad]], pad)

            self._modified_pads.clear()
        self._update_task.kill()

    def _add_modified_pads(self, pads):
        self._modified_pads.update(pads)
        self._update_task.restart()