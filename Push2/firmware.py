#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/firmware.py
from __future__ import absolute_import, print_function
import fnmatch
import logging
import os
import re
from ableton.v2.base import find_if, first, listenable_property, task
from ableton.v2.control_surface import Component
logger = logging.getLogger(__name__)
WELCOME_STATE_TIME = 2.0
FIRMWARE_PATH = os.path.join(os.path.dirname(__file__), 'firmware')

class FirmwareVersion(object):

    def __init__(self, major = 0, minor = 0, build = 0, *a, **k):
        super(FirmwareVersion, self).__init__(*a, **k)
        self.major = major
        self.minor = minor
        self.build = build

    def __cmp__(self, other):
        if self.major == other.major and self.minor == other.minor and self.build == other.build:
            return 0
        if self.major > other.major or self.major == other.major and self.minor > other.minor or self.major == other.major and self.minor == other.minor and self.build > other.build:
            return 1
        return -1

    def __repr__(self):
        return '<FirmwareVersion %i.%i.%i>' % (self.major, self.minor, self.build)


_firmware_file_prog = re.compile('app_push2_([0-9]+).([0-9]+).([0-9]+).*')

def extract_firmware_version(filename):
    match = _firmware_file_prog.match(filename)
    if match:
        return FirmwareVersion(int(match.group(1)), int(match.group(2)), int(match.group(3)))


class FirmwareUpdateComponent(Component):
    state = listenable_property.managed('welcome')

    def __init__(self, *a, **k):
        super(FirmwareUpdateComponent, self).__init__(is_enabled=False, *a, **k)
        available_firmware_files = self._collect_firmware_files()
        logger.debug('Available firmware files %r', available_firmware_files)
        self._latest_firmware = max(available_firmware_files, key=first)

    def start(self):
        raise self.state == 'welcome' or AssertionError
        self.set_enabled(True)

        def set_state():
            self.state = 'start'

        self._tasks.add(task.sequence(task.wait(WELCOME_STATE_TIME), task.run(set_state)))

    def process_firmware_response(self, data):
        if not self.state == 'start':
            raise AssertionError
            entry = find_if(lambda entry: entry['type'] == 'firmware', data)
            self.state = entry and ('success' if entry['success'] else 'failure')

    def has_newer_firmware(self, major, minor, build):
        return self.provided_version > FirmwareVersion(major, minor, build)

    def _collect_firmware_files(self):
        return filter(lambda x: x[0] is not None, [ (extract_firmware_version(f), f) for f in os.listdir(FIRMWARE_PATH) if fnmatch.fnmatch(f, '*.upgrade') ])

    @property
    def provided_version(self):
        return self._latest_firmware[0]

    @property
    def firmware_file(self):
        return os.path.join(FIRMWARE_PATH, self._latest_firmware[1])

    @property
    def data_file(self):
        return os.path.join(FIRMWARE_PATH, 'FlashData.bin')