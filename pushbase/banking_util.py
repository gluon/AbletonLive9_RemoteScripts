#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/banking_util.py
from __future__ import absolute_import, print_function
from math import ceil
from copy import deepcopy
from ableton.v2.base import liveobj_valid
MX_MAIN_BANK_INDEX = -1
BANK_FORMAT = 'Bank %d'
PARAMETERS_KEY = 'Parameters'
MAIN_KEY = 'Main'

def has_bank_count(device):
    if liveobj_valid(device):
        try:
            num_banks = device.get_bank_count()
            return num_banks > 0
        except (AttributeError, RuntimeError):
            pass

    return False


def has_main_bank(device, definitions):
    if has_bank_count(device):
        try:
            main_bank = device.get_bank_parameters(MX_MAIN_BANK_INDEX)
            return bool(main_bank)
        except (AttributeError, RuntimeError):
            return False

    else:
        return MAIN_KEY in definitions.get(device.class_name, {})


def has_bank_names(device, definitions):
    if has_bank_count(device):
        try:
            name = device.get_bank_name(0)
            return bool(name)
        except (AttributeError, RuntimeError):
            return False

    else:
        return bool(definitions.get(device.class_name, {}).keys())


def all_parameters(device):
    if liveobj_valid(device):
        return list(device.parameters[1:])
    return []


def device_bank_count(device, bank_size = 8, definition = None, definitions = None):
    count = 0
    if liveobj_valid(device):
        definition = definition or definitions.get(device.class_name, {})
        if has_bank_count(device):
            count = device.get_bank_count() + int(has_main_bank(device, definitions))
        elif definition:
            count = len(definition.keys())
        else:
            count = int(ceil(float(len(all_parameters(device))) / bank_size))
    return count


def device_bank_definition(device, definitions):
    original_definition = definitions.get(device.class_name, None)
    definition = deepcopy(original_definition) if original_definition is not None else None
    return definition


def device_bank_names(device, bank_size = 8, definitions = None):
    names = []
    if liveobj_valid(device):
        class_name = device.class_name
        if class_name in definitions:
            names = definitions[class_name].keys()
        elif has_bank_count(device) and has_bank_names(device, definitions):
            offset = int(has_main_bank(device, definitions))
            names = [ device.get_bank_name(index - offset) for index in xrange(device_bank_count(device, definitions=definitions)) ]
            if has_main_bank(device, definitions) and not names[0]:
                names[0] = MAIN_KEY
        else:
            bank_count = device_bank_count(device, bank_size=bank_size, definitions=definitions)
            names = [ BANK_FORMAT % (index + 1) for index in xrange(bank_count) ]
    return names


class BankingInfo(object):

    def __init__(self, bank_definitions):
        self._bank_definitions = bank_definitions

    def has_bank_count(self, device):
        return has_bank_count(device)

    def has_main_bank(self, device):
        return has_main_bank(device, definitions=self._bank_definitions)

    def has_bank_names(self, device):
        return has_bank_names(device, definitions=self._bank_definitions)

    def device_bank_count(self, device, **k):
        return device_bank_count(device, definitions=self._bank_definitions, **k)

    def device_bank_definition(self, device):
        return device_bank_definition(device, definitions=self._bank_definitions)

    def device_bank_names(self, device, **k):
        return device_bank_names(device, definitions=self._bank_definitions, **k)