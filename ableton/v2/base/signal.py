#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/base/signal.py
from __future__ import absolute_import, print_function
from functools import partial
from .util import find_if, nop

def default_combiner(results):
    for _ in results:
        pass


class Slot(object):

    def __init__(self, callback = None, *a, **k):
        super(Slot, self).__init__(*a, **k)
        self.callback = callback

    def __call__(self, *a, **k):
        return self.callback(*a, **k)

    def __eq__(self, other):
        return id(self) == id(other) or self.callback == other


class IdentifyingSlot(Slot):

    def __init__(self, sender = None, *a, **k):
        super(IdentifyingSlot, self).__init__(*a, **k)
        self.sender = sender

    def __call__(self, *a, **k):
        self.callback(*(a + (self.sender,)), **k)


class Signal(object):
    """
    A signal object implements the observer pattern.  It can be
    connected to any number of slots (i.e. callbacks). Whenever the
    signal is called, all the slots are called.
    
    The return value of this function will depend on the combiner.
    The combiner takes a generator of slot results and returns a
    value.  The slots whose results are not evaluated are not called.
    """

    def __init__(self, combiner = default_combiner, sender = None, *a, **k):
        super(Signal, self).__init__(*a, **k)
        self._slots = []
        self._combiner = combiner

    def connect(self, slot, in_front = False, sender = None):
        """
        Connects the signal to the slot. Does nothing if the slot is
        already connected. Returns the wrapper object that is used as
        a slot.
        
        If 'in_front' is True, the slot will be put first, meaning it
        will be called before previously registered slots (by default
        it is put last).
        
        If 'sender' is not None, it will be passed as last ordinal
        parameter to the slot when the signal is dispatched.
        """
        if not callable(slot):
            raise AssertionError
            if slot not in self._slots:
                slot = IdentifyingSlot(sender, slot) if sender is not None else Slot(slot)
                in_front and self._slots.insert(0, slot)
            else:
                self._slots.append(slot)
        else:
            slot = find_if(lambda x: x == slot, self._slots)
        return slot

    def disconnect(self, slot):
        if slot in self._slots:
            self._slots.remove(slot)

    def disconnect_all(self):
        self._slots = []

    @property
    def count(self):
        return len(self._slots)

    def is_connected(self, slot):
        return slot in self._slots

    def __call__(self, *a, **k):
        return self._combiner(_slot_notification_generator(self._slots, a, k))


def _slot_notification_generator(slots, args, kws):
    for slot in slots:
        yield slot(*args, **kws)


def short_circuit_combiner(slot_results):
    return find_if(nop, slot_results)


short_circuit_signal = partial(Signal, short_circuit_combiner)