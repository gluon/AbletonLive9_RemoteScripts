#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/base/slot.py
"""
Family of classes for maintaining connections with optional subjects.
"""
from __future__ import absolute_import, print_function
from itertools import izip, repeat, chain
from functools import partial, wraps
from .disconnectable import Disconnectable, CompoundDisconnectable
from .signal import Signal
from .util import instance_decorator, monkeypatch, monkeypatch_extend, NamedTuple, mixin

class SlotError(Exception):
    pass


class Event(NamedTuple):
    name = None
    doc = ''
    signal = Signal
    override = False


class listenable_property_base(object):

    def set_property_name(self, name):
        pass


class listenable_property(listenable_property_base, property):

    def setter(self, func):
        return listenable_property(self.fget, func)

    @classmethod
    def managed(cls, default_value):
        return _managed_listenable_property(default_value=default_value)


class _managed_listenable_property(listenable_property_base):

    def __init__(self, default_value = None, *a, **k):
        super(_managed_listenable_property, self).__init__(*a, **k)
        self._default_value = default_value
        self._property_name = None
        self._member_name = None

    def set_property_name(self, property_name):
        self._property_name = property_name
        self._member_name = '__listenable_property_%s' % property_name

    def _get_value(self, obj):
        raise self._member_name is not None or AssertionError('Cannot get member for managed listenable property. Listenable property might be used without inheriting from Subject.')
        return getattr(obj, self._member_name, self._default_value)

    def __get__(self, obj, owner):
        return self._get_value(obj)

    def __set__(self, obj, value):
        if value != self._get_value(obj):
            setattr(obj, self._member_name, value)
            getattr(obj, 'notify_%s' % self._property_name)(value)


def add_event(cls, event_name_or_event):
    if isinstance(event_name_or_event, str):
        event = Event(name=event_name_or_event)
    else:
        event = event_name_or_event
    raise callable(event.signal) or AssertionError
    signal_attr = '_' + event.name + '_signal'

    def get_signal(self):
        try:
            return getattr(self, signal_attr)
        except AttributeError:
            signal = event.signal(sender=self)
            setattr(self, signal_attr, signal)
            return signal

    kwargs = dict({'doc': event.doc,
     'override': event.override})

    @monkeypatch(cls, (event.name + '_has_listener'), **kwargs)
    def has_method(self, slot):
        return get_signal(self).is_connected(slot)

    @monkeypatch(cls, ('add_' + event.name + '_listener'), **kwargs)
    def add_method(self, slot, identify_sender = False, *a, **k):
        sender = self if identify_sender else None
        return get_signal(self).connect(slot, sender=sender, *a, **k)

    @monkeypatch(cls, ('remove_' + event.name + '_listener'), **kwargs)
    def remove_method(self, slot):
        return get_signal(self).disconnect(slot)

    @monkeypatch(cls, ('notify_' + event.name), **kwargs)
    def notify_method(self, *a, **k):
        return get_signal(self)(*a, **k)

    @monkeypatch(cls, ('clear_' + event.name + '_listeners'), **kwargs)
    def clear_method(self):
        return get_signal(self).disconnect_all()

    @monkeypatch(cls, (event.name + '_listener_count'), **kwargs)
    def listener_count_method(self):
        return get_signal(self).count

    @monkeypatch_extend(cls)
    def disconnect(self):
        get_signal(self).disconnect_all()


def validate_subject_interface(subject, event_name):
    if not callable(getattr(subject, 'add_' + event_name + '_listener', None)):
        raise SlotError('Subject %s missing "add" method for event: %s' % (subject, event_name))
    if not callable(getattr(subject, 'remove_' + event_name + '_listener', None)):
        raise SlotError('Subject %s missing "remove" method for event: %s' % (subject, event_name))
    if not callable(getattr(subject, event_name + '_has_listener', None)):
        raise SlotError('Subject %s missing "has" method for event: %s' % (subject, event_name))


def has_event(subject, event_name):
    return callable(getattr(subject, 'add_' + event_name + '_listener', None)) and callable(getattr(subject, 'remove_' + event_name + '_listener', None)) and callable(getattr(subject, event_name + '_has_listener', None))


class SubjectMeta(type):

    @staticmethod
    def collect_listenable_properties(dct):
        return filter(lambda item: isinstance(item[1], listenable_property_base), dct.iteritems())

    def __new__(cls, name, bases, dct):
        listenable_properties = SubjectMeta.collect_listenable_properties(dct)
        for property_name, obj in listenable_properties:
            obj.set_property_name(property_name)

        events = dct.get('__events__', [])
        property_events = [ event_name for event_name, obj in listenable_properties ]
        has_events = events or property_events
        if has_events and 'disconnect' not in dct:
            dct['disconnect'] = lambda self: super(cls, self).disconnect()
        cls = super(SubjectMeta, cls).__new__(cls, name, bases, dct)
        raise not has_events or hasattr(cls, 'disconnect') or AssertionError
        for lst in chain(events, property_events):
            add_event(cls, lst)

        return cls


class Subject(Disconnectable):
    """
    Base class that installs the SubjectMeta metaclass
    """
    __metaclass__ = SubjectMeta


class SerializableListenablePropertiesMeta(SubjectMeta):

    def __new__(cls, name, bases, dct):
        listenable_properties = SubjectMeta.collect_listenable_properties(dct)

        def getstate(self):
            data = super(generated_class, self).__getstate__()
            data.update(dict(((property_name, getattr(self, property_name)) for property_name, _ in listenable_properties)))
            return data

        def setstate(self, data):
            for k, v in data.iteritems():
                setattr(self, k, v)

        dct['__getstate__'] = getstate
        dct['__setstate__'] = setstate
        generated_class = super(SerializableListenablePropertiesMeta, cls).__new__(cls, name, bases, dct)
        return generated_class


class SerializableListenablePropertiesBase(Subject):

    def __getstate__(self):
        return dict()

    def __setstate__(self, data):
        pass


class SerializableListenableProperties(SerializableListenablePropertiesBase):
    """
    Installs a meta class, that generates __getstate__ and __setstate__ for
    serializing all listenable properties.
    """
    __metaclass__ = SerializableListenablePropertiesMeta


class SlotManager(CompoundDisconnectable):
    """
    Holds references to a number of slots. Disconnecting it clears all
    of them and unregisters them from the system.
    """

    def register_slot(self, *a, **k):
        slot = a[0] if a and isinstance(a[0], Slot) else Slot(*a, **k)
        self.register_disconnectable(slot)
        return slot

    def register_slot_manager(self, *a, **k):
        manager = a[0] if a and isinstance(a[0], SlotManager) else SlotManager(*a, **k)
        self.register_disconnectable(manager)
        return manager


class Slot(Disconnectable):
    """
    This class maintains the relationship between a subject and a
    listener callback. As soon as both are non-null, it connects the
    listener the given 'event' of the subject and release the connection
    when any of them change.
    
    The finalizer of the object also cleans up both parameters and so
    does the __exit__ override, being able to use it as a context
    manager with the 'with' clause.
    
    Note that 'event' is a string with canonical identifier for the
    listener, i.e., the subject should provide the methods:
    
      add_[event]_listener
      remove_[event]_listener
      [event]_has_listener
    
    Note that the connection can already be made manually before the
    subject and listener are fed to the slot.
    """
    _extra_kws = {}
    _extra_args = []

    def __init__(self, subject = None, listener = None, event = None, extra_kws = None, extra_args = None, *a, **k):
        super(Slot, self).__init__(*a, **k)
        if not event:
            raise AssertionError
            self._event = event
            if extra_kws is not None:
                self._extra_kws = extra_kws
            self._extra_args = extra_args is not None and extra_args
        self._subject = None
        self._listener = None
        self.subject = subject
        self.listener = listener

    def subject_valid(self, subject):
        return subject != None

    def disconnect(self):
        """
        Disconnects the slot clearing its members.
        """
        self.subject = None
        self.listener = None
        super(Slot, self).disconnect()

    def connect(self):
        if not self.is_connected and self.subject_valid(self._subject) and self._listener != None:
            add_method = getattr(self._subject, 'add_' + self._event + '_listener')
            all_args = tuple(self._extra_args) + (self._listener,)
            try:
                add_method(*all_args, **self._extra_kws)
            except RuntimeError:
                pass

    def soft_disconnect(self):
        """
        Disconnects the listener from the subject keeping their
        values.
        """
        if self.is_connected and self.subject_valid(self._subject) and self._listener != None:
            all_args = tuple(self._extra_args) + (self._listener,)
            remove_method = getattr(self._subject, 'remove_' + self._event + '_listener')
            try:
                remove_method(*all_args)
            except RuntimeError:
                pass

    @property
    def is_connected(self):
        all_args = tuple(self._extra_args) + (self._listener,)
        connected = False
        try:
            connected = bool(self.subject_valid(self._subject) and self._listener != None and getattr(self._subject, self._event + '_has_listener')(*all_args))
        except RuntimeError:
            pass

        return connected

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, subject):
        if subject != self._subject:
            if self.subject_valid(subject):
                validate_subject_interface(subject, self._event)
            self.soft_disconnect()
            self._subject = subject
            self.connect()

    def _get_listener(self):
        return self._listener

    def _set_listener(self, listener):
        if listener != self._listener:
            self.soft_disconnect()
            self._listener = listener
            self.connect()

    listener = property(_get_listener, _set_listener)


class CallableSlotMixin(object):
    """
    Use this Mixin to turn slot like interfaces into a
    'callable'.  The call operator will be forwarded to the
    slot.
    """

    def __init__(self, function = None, *a, **k):
        super(CallableSlotMixin, self).__init__(*a, **k)
        self.function = function

    def __call__(self, *a, **k):
        return self.function(*a, **k)


class SlotGroup(SlotManager):
    """
    A slot that connects a given listener to many subjects.
    """
    listener = None
    _extra_kws = None
    _extra_args = None

    def __init__(self, listener = None, event = None, extra_kws = None, extra_args = None, *a, **k):
        super(SlotGroup, self).__init__(*a, **k)
        self.listener = listener
        self._event = event
        if listener is not None:
            self.listener = listener
        if extra_kws is not None:
            self._extra_kws = extra_kws
        if extra_args is not None:
            self._extra_args = extra_args

    def replace_subjects(self, subjects, identifiers = repeat(None)):
        self.disconnect()
        for subject, identifier in izip(subjects, identifiers):
            self.add_subject(subject, identifier=identifier)

    def add_subject(self, subject, identifier = None):
        if identifier is None:
            identifier = subject
        listener = self._listener_for_subject(identifier)
        self.register_slot(subject, listener, self._event, self._extra_kws, self._extra_args)

    def remove_subject(self, subject):
        slot = self.find_disconnectable(lambda x: x.subject == subject)
        self.disconnect_disconnectable(slot)

    def has_subject(self, subject):
        return self.find_disconnectable(lambda x: x.subject == subject) != None

    def _listener_for_subject(self, identifier):
        return lambda *a, **k: self.listener and self.listener(*(a + (identifier,)), **k)


class MultiSlot(SlotManager, Slot, CallableSlotMixin):
    """
    A slot that takes a string describing the path to the event to listen to.
    It will make sure that any changes to the elements of this path notify the given
    listener and will follow the changing subjects.
    """

    def __init__(self, subject = None, listener = None, event = None, extra_kws = None, extra_args = None, function = None, *a, **k):
        self._original_listener = listener
        self._slot_subject = None
        self._nested_slot = None
        super(MultiSlot, self).__init__(event=event[0], listener=self._event_fired, subject=subject, function=function, extra_kws=extra_kws, extra_args=extra_args)
        if len(event) > 1:
            self._nested_slot = self.register_disconnectable(MultiSlot(event=event[1:], listener=listener, function=function, extra_kws=extra_kws, extra_args=extra_args))
            self._update_nested_subject()

    @property
    def subject(self):
        return super(MultiSlot, self).subject

    @subject.setter
    def subject(self, subject):
        try:
            super(MultiSlot, MultiSlot).subject.fset(self, subject)
        except SlotError:
            if self._nested_slot == None:
                raise 
        finally:
            self._slot_subject = subject
            self._update_nested_subject()

    def _event_fired(self, *a, **k):
        self._update_nested_subject()
        self._original_listener(*a, **k)

    def _update_nested_subject(self):
        if self._nested_slot != None:
            self._nested_slot.subject = getattr(self._slot_subject, self._event) if self.subject_valid(self._slot_subject) else None


def listens(events, *a, **k):

    @instance_decorator
    def decorator(self, method):
        raise isinstance(self, SlotManager) or AssertionError
        function = partial(method, self)
        event_list = events.split('.')
        num_events = len(event_list)
        event = event_list if num_events > 1 else events
        base_class = MultiSlot if num_events > 1 else Slot
        slot = wraps(method)(mixin(base_class, CallableSlotMixin)(event=event, extra_kws=k, extra_args=a, listener=function, function=function))
        self.register_slot(slot)
        return slot

    return decorator


class CallableSlotGroup(SlotGroup, CallableSlotMixin):
    pass


def listens_group(event, *a, **k):

    @instance_decorator
    def decorator(self, method):
        raise isinstance(self, SlotManager) or AssertionError
        function = partial(method, self)
        slot = wraps(method)(CallableSlotGroup(event=event, extra_kws=k, extra_args=a, listener=function, function=function))
        self.register_slot_manager(slot)
        return slot

    return decorator