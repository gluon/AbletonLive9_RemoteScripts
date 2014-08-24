#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Push/HandshakeComponent.py
"""
Component for handling the initialization process of Push.
"""
import Live
from _Framework import Task
from _Framework.SubjectSlot import subject_slot
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Util import NamedTuple
from FirmwareHandling import get_version_number_from_string
from functools import partial
HANDSHAKE_TIMEOUT = 10.0
DONGLE_SIZE = 16

def to_bytes(dongle):
    return tuple([ dongle >> 4 * (7 - index) & 15 for index in xrange(8) ])


def to_integral(dongle):
    length = len(dongle)
    return sum([ long(dongle[index] & 15) << 4 * (length - 1 - index) for index in xrange(length) ])


def make_dongle_message(dongle_prefix, random_generator = Live.Application):
    dongle_one = random_generator.get_random_int(0, 2000000)
    dongle_two = random_generator.get_random_int(2000001, 4000000)
    return (dongle_prefix + (0, DONGLE_SIZE) + to_bytes(dongle_one) + to_bytes(dongle_two) + (247,), (dongle_one, dongle_two))


class HardwareIdentity(NamedTuple):
    """
    Stores the identity of the hardware.
    """
    firmware = None
    serial = None
    manufacturing = None


class HandshakeComponent(ControlSurfaceComponent):
    """
    Component for retrieving the hardware identity and checking that
    it is a Ableton certified device.
    """
    __subject_events__ = ('success', 'failure')
    encryptor = partial(Live.Application.encrypt_challenge, key_index=1)
    _handshake_succeeded = None
    _hardware_identity = None

    def __init__(self, identity_control = None, presentation_control = None, dongle_control = None, dongle = (0, 0), *a, **k):
        super(HandshakeComponent, self).__init__(*a, **k)
        self._identity_control = identity_control
        self._presentation_control = presentation_control
        self._dongle_control = dongle_control
        self._dongle_one, self._dongle_two = dongle
        self._on_identity_value.subject = identity_control
        self._on_dongle_value.subject = dongle_control
        self._identification_timeout_task = self._tasks.add(Task.sequence(Task.wait(HANDSHAKE_TIMEOUT), Task.run(self._do_fail)))
        self._identification_timeout_task.kill()

    @property
    def handshake_succeeded(self):
        """
        This will return None if the handshake process has not
        finished, otherwise True or False.
        """
        return self._handshake_succeeded

    @property
    def hardware_identity(self):
        return self._hardware_identity

    @property
    def firmware_version(self):
        version_bytes = self._hardware_identity.firmware if self._hardware_identity != None else 4 * (0,)
        return get_version_number_from_string(' %d %d %d %d' % version_bytes)

    def on_enabled_changed(self):
        super(HandshakeComponent, self).on_enabled_changed()
        if self._handshake_succeeded == None:
            self._do_fail()

    def _start_handshake(self):
        self._handshake_succeeded = None
        self._identification_timeout_task.restart()
        self._identity_control.enquire_value()

    @subject_slot('value')
    def _on_identity_value(self, value):
        if len(value) == 25:
            if value[9:] == tuple(range(1, 17)):
                self._do_fail(bootloader_mode=True)
            else:
                self._hardware_identity = HardwareIdentity(firmware=value[:4], serial=value[4:8], manufacturing=value[8:25])
                self._presentation_control.enquire_value()
                self._dongle_control.enquire_value()
        else:
            self._do_fail()

    @subject_slot('value')
    def _on_dongle_value(self, value):
        success = False
        if len(value) >= 18:
            result = (to_integral(value[2:10]), to_integral(value[10:18]))
            expected = self.encryptor(self._dongle_one, self._dongle_two)
            success = tuple(expected) == tuple(result)
        if success:
            self._do_succeed()
        else:
            self._do_fail()

    def _do_succeed(self):
        if self._handshake_succeeded == None:
            self._handshake_succeeded = True
            self._identification_timeout_task.kill()
            self.notify_success()

    def _do_fail(self, bootloader_mode = False):
        if self._handshake_succeeded == None:
            self._handshake_succeeded = False
            self._identification_timeout_task.kill()
            self.notify_failure(bootloader_mode)