#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/parameter_slot_description.py
from __future__ import absolute_import
from ableton.v2.base import find_if, listens_group, liveobj_valid, Subject, SlotManager
RESULTING_NAME_KEY = 'ResultingName'
CONDITION_NAME_KEY = 'ConditionName'
CONDITIONS_LIST_NAME_KEY = 'ConditionsListName'
PREDICATE_KEY = 'Predicate'
OPERAND_NAME_KEY = 'Operand'
AND = 'and'
OR = 'or'

def find_parameter(name, host):
    parameters = host.parameters if host != None else []
    return find_if(lambda p: p.original_name == name, parameters)


class ParameterSlotDescription(Subject, SlotManager):
    """
    Description class that allows chosing a parameter (name) based on
    the values of other parameters. To retrieve the chosen parameter name
    turn the slot into a string.
    
    Examples:
      - slot = use('A').if_parameter('B').has_value('1.0')
      - slot = use('A').if_parameter('B').has_value('1.0').else_use('C')
      - slot = use('A').if_parameter('B').has_value('1.0')                       .and_parameter('C').has_value('0.5').else_use('D')
      - parameter_name = str(slot)
    """
    __events__ = ('content',)

    def __init__(self, *a, **k):
        super(ParameterSlotDescription, self).__init__(*a, **k)
        self._parameter_host = None
        self._default_parameter_name = ''
        self._conditions = []
        self._cached_content = None

    def _calc_content(self):
        content = self._default_parameter_name
        for condition in self._conditions:
            result = True
            for subcond in condition[CONDITIONS_LIST_NAME_KEY]:
                result = eval('%s %s %s' % (result, subcond[OPERAND_NAME_KEY], subcond[PREDICATE_KEY](find_parameter(subcond[CONDITION_NAME_KEY], self._parameter_host))))
                if not result:
                    continue

            if result:
                content = condition[RESULTING_NAME_KEY]
                break

        return content

    @listens_group('value')
    def __on_condition_value_changed(self, _parameter):
        new_content = self._calc_content()
        if new_content != self._cached_content:
            self._cached_content = new_content
            self.notify_content()

    def set_parameter_host(self, host):
        self._parameter_host = host
        self._cached_content = self._calc_content()
        params_names = set()
        for c in self._conditions:
            params_names.update([ cond[CONDITION_NAME_KEY] for cond in c[CONDITIONS_LIST_NAME_KEY] ])

        self.__on_condition_value_changed.replace_subjects([ find_parameter(name, self._parameter_host) for name in params_names ])

    def if_parameter(self, parameter_name):
        self._conditions.append({RESULTING_NAME_KEY: self._default_parameter_name,
         CONDITIONS_LIST_NAME_KEY: [{CONDITION_NAME_KEY: parameter_name,
                                     OPERAND_NAME_KEY: AND}]})
        self._default_parameter_name = ''
        return self

    def chain_condition(self, operand, parameter_name):
        raise len(self._conditions) > 0 and len(self._conditions[-1][CONDITIONS_LIST_NAME_KEY]) > 0 and not self._default_parameter_name or AssertionError
        self._conditions[-1][CONDITIONS_LIST_NAME_KEY].append({CONDITION_NAME_KEY: parameter_name,
         OPERAND_NAME_KEY: operand})
        return self

    def and_parameter(self, parameter_name):
        return self.chain_condition(AND, parameter_name)

    def or_parameter(self, parameter_name):
        return self.chain_condition(OR, parameter_name)

    def _add_condition_predicate(self, predicate):
        raise len(self._conditions) > 0 and PREDICATE_KEY not in self._conditions[-1][CONDITIONS_LIST_NAME_KEY][-1] or AssertionError
        self._conditions[-1][CONDITIONS_LIST_NAME_KEY][-1][PREDICATE_KEY] = predicate

    def has_value(self, value):
        self._add_condition_predicate(lambda p: str(p) == value)
        return self

    def is_available(self, value):
        self._add_condition_predicate(lambda p: liveobj_valid(p) == value)
        return self

    def else_use(self, parameter_name):
        self._default_parameter_name = parameter_name
        return self

    def __str__(self):
        return self._cached_content


def use(parameter_name):
    return ParameterSlotDescription().else_use(parameter_name)