#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/model/generation.py
from operator import attrgetter
from functools import partial
from ableton.v2.base import Disconnectable, memoize, SlotManager, Slot, has_event
from .repr import ModelAdapter
from .declaration import custom_property, id_property, is_binding_property_decl, is_list_property_decl, is_list_model_property_decl, is_reference_property_decl, is_view_model_property_decl, view_property, WrongIdPropertyDeclaration, ViewModelsCantContainRefs, UndeclaredReferenceClass

class AdapterAwareSlot(Slot):
    """
    A special Slot-subclass that delegates
    validation checking to the adapters that
    are wrapped around all bindable objects.
    """

    def subject_valid(self, adapter):
        return adapter is not None and adapter.is_valid()


class ModelUpdateNotifier(object):

    def __init__(self, step = None, parent = None, delegate = None):
        raise parent is not None or step is None or AssertionError, (parent, step)
        self._step = step
        self._delegate = delegate
        self.path = [] if self._step is None else parent.path + [self._step]

    def step(self, step):
        return ModelUpdateNotifier(step=step, parent=self, delegate=self._delegate)

    def attribute_changed(self, value):
        if self._delegate:
            self._delegate.attribute_changed(self.path, value)

    def structural_change(self):
        if self._delegate:
            self._delegate.structural_change(self.path)


class WrapperBase(Disconnectable):

    def __init__(self, notifier = ModelUpdateNotifier(), *a, **k):
        super(WrapperBase, self).__init__(*a, **k)
        self._notifier = notifier

    def get(self):
        raise NotImplementedError

    def to_json(self):
        raise NotImplementedError

    def notify(self):
        raise NotImplementedError


class SimpleWrapper(WrapperBase):

    def __init__(self, value, *a, **k):
        super(SimpleWrapper, self).__init__(*a, **k)
        self._value = value

    def to_json(self):
        return self._value

    def get(self):
        return self._value

    def notify(self):
        self._notifier.attribute_changed(self.get())


class NullValueWrapper(SimpleWrapper):

    def notify(self):
        self._notifier.structural_change()


class BoundListWrapper(SlotManager, SimpleWrapper):

    def __init__(self, parent_object, name = None, wrapper = None, notifier = ModelUpdateNotifier(), verify_unique_ids = False, *a, **k):
        raise wrapper is not None or AssertionError
        raise name is not None or AssertionError
        super(BoundListWrapper, self).__init__([], notifier=notifier, *a, **k)
        self.wrapper = wrapper
        self.attrgetter = partial(getattr, parent_object, name)
        self._verify_unique_ids = verify_unique_ids
        self._update_list()
        self._connect(parent_object, name)

    def notify(self):
        self._notifier.structural_change()

    def _update_list(self):
        for value in self._value:
            self.disconnect_disconnectable(value)

        self._value = [ self.wrapper(v, notifier=self._notifier.step(i)) for i, v in enumerate(self.attrgetter()) ]
        for value in self._value:
            self.register_disconnectable(value)

        if not (self._verify_unique_ids and len(self._value) == len(set((item.values['id'].get() for item in self._value)))):
            raise AssertionError, 'BoundListWrapper requires unique ids for items'

    def to_json(self):
        return [ v.to_json() for v in self._value ]

    def _connect(self, parent_object, name):
        if has_event(parent_object, name):
            slot = AdapterAwareSlot(parent_object, lambda *a: self._update_list(), name)
            slot.connect()
            self.register_slot(slot)


class BoundAttributeWrapper(WrapperBase):

    def __init__(self, bound_object, attr_getter = None, *a, **k):
        super(BoundAttributeWrapper, self).__init__(*a, **k)
        raise attr_getter is not None or AssertionError
        self.attrgetter = partial(attr_getter, bound_object)

    def get(self):
        return self.attrgetter()

    def to_json(self):
        return self.attrgetter()

    def notify(self):
        self._notifier.attribute_changed(self.get())


class BoundObjectWrapper(SlotManager, SimpleWrapper):

    def __init__(self, bound_object, wrappers = None, adapter = None, *a, **k):
        if not adapter is not None:
            raise AssertionError
            raise wrappers is not None or AssertionError
            bound_object = adapter(bound_object) if bound_object != None else None
            super(BoundObjectWrapper, self).__init__(bound_object, *a, **k)
            self.wrappers = wrappers
            self.values = {}
            bound_object is not None and self.register_disconnectable(bound_object)
            for name in wrappers.keys():
                self._update_wrapper(name)

        self.connect()

    def notify(self):
        self._notifier.structural_change()

    def to_json(self):
        if self._value is not None and self._value.is_valid():
            res = {}
            for name, wrapper in self.values.iteritems():
                res[name] = wrapper.to_json()

            return res

    def _update_wrapper(self, name):
        if name in self.values:
            self.disconnect_disconnectable(self.values[name])
        self.values[name] = self.wrappers[name](self._value, notifier=self._notifier.step(name))
        self.register_disconnectable(self.values[name])

    def _property_changed(self, name, *_a):
        self._update_wrapper(name)
        attr = self.values[name]
        attr.notify()

    def connect(self):
        for name in self.wrappers.keys() if self._value else []:
            if has_event(self._value, name):
                slot = AdapterAwareSlot(self._value, partial(self._property_changed, name), name)
                slot.connect()
                self.register_slot(slot)


class DeferredWrapper(WrapperBase):

    def __init__(self, parent, name, bound_object_wrapper, *a, **k):
        super(DeferredWrapper, self).__init__(*a, **k)
        value = getattr(parent, name)
        if value is None:
            self._value = NullValueWrapper(None, notifier=self._notifier.step(name))
        else:
            self._value = bound_object_wrapper(value, *a, **k)

    def get(self):
        return self._value.get()

    def to_json(self):
        return self._value.to_json()

    def disconnect(self):
        self._value.disconnect()

    def notify(self):
        self._value.notify()


class NotifyingList(WrapperBase):

    def __init__(self, value, wrapper = None, *a, **k):
        super(NotifyingList, self).__init__(*a, **k)
        raise wrapper is not None or AssertionError
        raise value is not None or AssertionError
        self.wrapper = wrapper
        self.data = [ self.wrapper(item, notifier=self._notifier.step(i)) for i, item in enumerate(value) ]

    def notify(self):
        self._notifier.structural_change()

    def disconnect(self):
        super(NotifyingList, self).disconnect()
        for child in self.data:
            child.disconnect()

    def append(self, value):
        self.data.append(self.wrapper(value))
        self.notify()

    def to_json(self):
        return [ item.to_json() for item in self.data ]

    def to_list(self):
        return [ i.get() for i in self.data ]

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.data)

    def __setitem__(self, index, value):
        if not isinstance(index, slice):
            index = slice(index, index + 1)
            value = [value]
        own_values = [ v.get() for v in self.data[index] ]
        if own_values != value:
            for old_item in self.data[index]:
                old_item.disconnect()

            self.data[index] = [ self.wrapper(item) for item in value ]
            self.notify()

    def get(self):
        return self


def _generate_model_mixin_property(name):

    def fget(self):
        return self.data[name].get()

    def fset(self, value):
        if self.data[name].get() != value:
            self.data[name].disconnect()
            notifier = self._notifier.step(name)
            self.data[name] = self.wrappers[name](value, notifier=notifier)
            self.data[name].notify()

    return property(fget, fset)


class ModelMixin(WrapperBase):
    wrappers = {}

    def __init__(self, *a, **k):
        super(ModelMixin, self).__init__(*a, **k)
        self.data = {}
        for name, wrapper in self.wrappers.iteritems():
            value = self.default_data[name]
            self.data[name] = wrapper(value, notifier=self._notifier.step(name))

        for name, child in self.children.iteritems():
            self.data[name] = child(notifier=self._notifier.step(name))

    def disconnect(self):
        super(ModelMixin, self).disconnect()
        for child in self.data.values():
            child.disconnect()

    def to_json(self):
        return dict(((name, obj.to_json()) for name, obj in self.data.iteritems()))

    def get(self):
        return self


def make_bound_child_wrapper(name = None, wrapper = None):

    def apply_wrapper(bound_object, name = None, wrapper = None, notifier = None):
        return wrapper(getattr(bound_object, name), notifier=notifier)

    return partial(apply_wrapper, name=name, wrapper=wrapper)


def generate_mrs_model(cls):
    name2bound_class = {}
    references = []

    def lookp_class_by_name(name):
        try:
            return name2bound_class[name]
        except KeyError as e:
            raise UndeclaredReferenceClass(e)

    @memoize
    def _generate_mrs_model(cls):
        d = {}
        default_data = {}
        wrappers = {}
        children = {}

        @memoize
        def binding_wrapper(cls):
            raise cls.__name__ not in name2bound_class or AssertionError
            name2bound_class[cls.__name__] = cls
            wrappers = {}
            adapter = cls.__dict__.get('ADAPTER', ModelAdapter)
            for name, decl in cls.__dict__.iteritems():
                if name == 'id' and not isinstance(decl, id_property):
                    raise WrongIdPropertyDeclaration(cls)
                if isinstance(decl, custom_property):
                    wrappers[name] = decl.wrapper_class
                elif isinstance(decl, view_property):
                    if is_reference_property_decl(decl):

                        def resolve_reference(decl, wrappers, name):
                            wrappers[name] = partial(DeferredWrapper, name=name, bound_object_wrapper=binding_wrapper(lookp_class_by_name(decl.property_type.class_name)))

                        references.append(partial(resolve_reference, decl, wrappers, name))
                    elif is_list_property_decl(decl):
                        is_list_model = is_list_model_property_decl(decl)
                        if is_reference_property_decl(decl.property_type):

                            def resolve_reference(decl, wrappers, name):
                                wrappers[name] = partial(BoundListWrapper, name=name, wrapper=binding_wrapper(lookp_class_by_name(decl.property_type.class_name)), verify_unique_ids=is_list_model)

                            references.append(partial(resolve_reference, decl.property_type, wrappers, name))
                        else:
                            wrapper = binding_wrapper(decl.property_type.property_type) if is_binding_property_decl(decl.property_type) else SimpleWrapper
                            wrappers[name] = partial(BoundListWrapper, name=name, wrapper=wrapper, verify_unique_ids=is_list_model)
                    elif is_binding_property_decl(decl):
                        wrappers[name] = make_bound_child_wrapper(name=name, wrapper=binding_wrapper(decl.property_type))
                    else:
                        wrappers[name] = partial(BoundAttributeWrapper, attr_getter=attrgetter(name))
                elif isinstance(decl, id_property):
                    wrappers[name] = partial(BoundAttributeWrapper, attr_getter=decl.id_attribute_getter)

            return partial(BoundObjectWrapper, wrappers=wrappers, adapter=adapter)

        for name, decl in cls.__dict__.iteritems():
            if isinstance(decl, view_property):
                d[name] = _generate_model_mixin_property(name)
                if is_reference_property_decl(decl):
                    raise ViewModelsCantContainRefs
                elif is_binding_property_decl(decl):
                    default_data[name] = None
                    wrappers[name] = binding_wrapper(decl.property_type)
                elif is_view_model_property_decl(decl):
                    children[name] = generate_mrs_model(decl.property_type)
                elif is_list_property_decl(decl):
                    default_data[name] = []
                    wrapper = binding_wrapper(decl.property_type.property_type) if is_binding_property_decl(decl.property_type) else SimpleWrapper
                    wrappers[name] = partial(NotifyingList, wrapper=wrapper)
                else:
                    default_data[name] = decl.default_value
                    wrappers[name] = SimpleWrapper

        d['default_data'] = default_data
        d['wrappers'] = wrappers
        d['children'] = children
        return type('P2' + cls.__name__, (ModelMixin,), d)

    model_class = _generate_mrs_model(cls)
    for refdecl in references:
        refdecl()

    return model_class