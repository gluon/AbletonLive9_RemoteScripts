#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/SubjectSlot.py
"""
Family of classes for maintaining connections with optional subjects.
"""
from __future__ import absolute_import
from itertools import izip, repeat
from functools import partial, wraps
from .Disconnectable import Disconnectable, CompoundDisconnectable
from .Signal import Signal
from .Util import instance_decorator, monkeypatch, monkeypatch_extend, NamedTuple, mixin

class SubjectSlotError(Exception):
    pass


class SubjectEvent(NamedTuple):
    """
    Description of a subject event
    """
    name = None
    doc = ''
    signal = Signal
    override = False


def subject_add_event(cls, event_name_or_event):
    if isinstance(event_name_or_event, str):
        event = SubjectEvent(name=event_name_or_event)
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


def setup_subject(cls, listeners):
    for lst in listeners:
        subject_add_event(cls, lst)


class SubjectMeta(type):

    def __new__(cls, name, bases, dct):
        events = dct.get('__subject_events__', [])
        if events and 'disconnect' not in dct:
            dct['disconnect'] = lambda self: super(cls, self).disconnect()
        cls = super(SubjectMeta, cls).__new__(cls, name, bases, dct)
        raise not events or hasattr(cls, 'disconnect') or AssertionError
        setup_subject(cls, events)
        return cls


class Subject(Disconnectable):
    """
    Base class that installs the SubjectMeta metaclass
    """
    __metaclass__ = SubjectMeta


class SlotManager(CompoundDisconnectable):
    """
    Holds references to a number of slots. Disconnecting it clears all
    of them and unregisters them from the system.
    """

    def register_slot(self, *a, **k):
        slot = a[0] if a and isinstance(a[0], SubjectSlot) else SubjectSlot(*a, **k)
        self.register_disconnectable(slot)
        return slot

    def register_slot_manager(self, *a, **k):
        manager = a[0] if a and isinstance(a[0], SlotManager) else SlotManager(*a, **k)
        self.register_disconnectable(manager)
        return manager


class SubjectSlot(Disconnectable):
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
        super(SubjectSlot, self).__init__(*a, **k)
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

    def disconnect(self):
        """
        Disconnects the slot clearing its members.
        """
        self.subject = None
        self.listener = None
        super(SubjectSlot, self).disconnect()

    def _check_subject_interface(self, subject):
        if not callable(getattr(subject, 'add_' + self._event + '_listener', None)):
            raise SubjectSlotError('Subject %s missing "add" method for event: %s' % (subject, self._event))
        if not callable(getattr(subject, 'remove_' + self._event + '_listener', None)):
            raise SubjectSlotError('Subject %s missing "remove" method for event: %s' % (subject, self._event))
        if not callable(getattr(subject, self._event + '_has_listener', None)):
            raise SubjectSlotError('Subject %s missing "has" method for event: %s' % (subject, self._event))

    def connect(self):
        if not self.is_connected and self._subject != None and self._listener != None:
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
        if self.is_connected and self._subject != None and self._listener != None:
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
            connected = bool(self._subject != None and self._listener != None and getattr(self._subject, self._event + '_has_listener')(*all_args))
        except RuntimeError:
            pass

        return connected

    def _get_subject(self):
        return self._subject

    def _set_subject(self, subject):
        if subject != self._subject:
            if subject != None:
                self._check_subject_interface(subject)
            self.soft_disconnect()
            self._subject = subject
            self.connect()

    subject = property(_get_subject, _set_subject)

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
    Use this Mixin to turn subject-slot like interfaces into a
    'callable'.  The call operator will be forwarded to the
    subjectslot.
    """

    def __init__(self, function = None, *a, **k):
        super(CallableSlotMixin, self).__init__(*a, **k)
        self.function = function

    def __call__(self, *a, **k):
        return self.function(*a, **k)


class SubjectSlotGroup(SlotManager):
    """
    A subject slot that connects a given listener to many subjects.
    """
    listener = None
    _extra_kws = None
    _extra_args = None

    def __init__(self, listener = None, event = None, extra_kws = None, extra_args = None, *a, **k):
        super(SubjectSlotGroup, self).__init__(*a, **k)
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


class MultiSubjectSlot(SlotManager, SubjectSlot):
    """
    A subject slot that takes a string describing the path to the event to listen to.
    It will make sure that any changes to the elements of this path notify the given
    listener and will follow the changing subjects.
    """

    def __init__(self, subject = None, listener = None, event = None, extra_kws = None, extra_args = None, *a, **k):
        self._original_listener = listener
        self._slot_subject = None
        self._nested_slot = None
        super(MultiSubjectSlot, self).__init__(event=event[0], listener=self._event_fired, subject=subject, extra_kws=extra_kws, extra_args=extra_args)
        if len(event) > 1:
            self._nested_slot = self.register_disconnectable(MultiSubjectSlot(event=event[1:], listener=listener, subject=subject, extra_kws=extra_kws, extra_args=extra_args))
            self._update_nested_subject()

    def _get_subject(self):
        return super(MultiSubjectSlot, self)._get_subject()

    def _set_subject(self, subject):
        try:
            super(MultiSubjectSlot, self)._set_subject(subject)
        except SubjectSlotError:
            if self._nested_slot == None:
                raise 
        finally:
            self._slot_subject = subject
            self._update_nested_subject()

    subject = property(_get_subject, _set_subject)

    def _event_fired(self, *a, **k):
        self._update_nested_subject()
        self._original_listener(*a, **k)

    def _update_nested_subject(self):
        if self._nested_slot != None:
            self._nested_slot.subject = getattr(self._slot_subject, self._event) if self._slot_subject != None else None


def subject_slot(events, *a, **k):

    @instance_decorator
    def decorator(self, method):
        raise isinstance(self, SlotManager) or AssertionError
        function = partial(method, self)
        event_list = events.split('.')
        num_events = len(event_list)
        event = event_list if num_events > 1 else events
        base_class = MultiSubjectSlot if num_events > 1 else SubjectSlot
        slot = wraps(method)(mixin(base_class, CallableSlotMixin)(event=event, extra_kws=k, extra_args=a, listener=function, function=function))
        self.register_slot(slot)
        return slot

    return decorator


class CallableSubjectSlotGroup(SubjectSlotGroup, CallableSlotMixin):
    pass


def subject_slot_group(event, *a, **k):

    @instance_decorator
    def decorator(self, method):
        raise isinstance(self, SlotManager) or AssertionError
        function = partial(method, self)
        slot = wraps(method)(CallableSubjectSlotGroup(event=event, extra_kws=k, extra_args=a, listener=function, function=function))
        self.register_slot_manager(slot)
        return slot

    return decorator