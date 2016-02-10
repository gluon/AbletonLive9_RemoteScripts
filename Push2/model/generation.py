#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/model/generation.py
from __future__ import absolute_import, print_function
from hashlib import md5
from contextlib import contextmanager
from collections import namedtuple
from operator import attrgetter
from functools import partial
from ableton.v2.base import Disconnectable, SlotManager, Slot, has_event
from .repr import ModelAdapter
from .declaration import ViewModelsCantContainRefs, ViewModelCantContainListModels, UndeclaredReferenceClass, ModelVisitor

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
        raise parent is not None or step is None or AssertionError((parent, step))
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

        if self._verify_unique_ids:
            raise len(self._value) == len(set((item.values['id'].get() for item in self._value))) or AssertionError('BoundListWrapper requires unique ids for items')

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


ClassInfo = namedtuple('ClassInfo', ['class_',
 'd',
 'default_data',
 'wrappers',
 'children'])

@contextmanager
def pushpop(collection, item):
    collection.append(item)
    yield item
    collection.pop()


class BindingModelVisitor(ModelVisitor):

    def __init__(self, decl2class, references, name2class):
        self._class_stack = []
        self._decl2class = decl2class
        self._references = references
        self._name2class = name2class

    @property
    def current_class_info(self):
        return self._class_stack[-1]

    @contextmanager
    def __call__(self, class_info):
        self._class_stack.append(class_info)
        yield class_info
        self._class_stack.pop()

    def visit_binding_class(self, class_):
        if class_ not in self._decl2class:
            with self(ClassInfo(class_=class_, d=None, default_data=None, wrappers={}, children=None)) as ci:
                super(BindingModelVisitor, self).visit_binding_class(class_)
                self._decl2class[class_] = partial(BoundObjectWrapper, wrappers=ci.wrappers, adapter=class_.__dict__.get('ADAPTER', ModelAdapter))
                self._name2class[class_.__name__] = self._decl2class[class_]
        return self._decl2class[class_]

    def visit_value_property(self, name, decl):
        super(BindingModelVisitor, self).visit_value_property(name, decl)
        self.current_class_info.wrappers[name] = partial(BoundAttributeWrapper, attr_getter=attrgetter(name))

    def visit_id_property(self, name, decl):
        super(BindingModelVisitor, self).visit_id_property(name, decl)
        self.current_class_info.wrappers[name] = partial(BoundAttributeWrapper, attr_getter=decl.id_attribute_getter)

    def visit_binding_property(self, name, decl):
        super(BindingModelVisitor, self).visit_binding_property(name, decl)
        self.current_class_info.wrappers[name] = make_bound_child_wrapper(name=name, wrapper=self._decl2class[decl.property_type])

    def visit_value_list_property(self, name, decl, value_type):
        super(BindingModelVisitor, self).visit_value_list_property(name, decl, value_type)
        self.current_class_info.wrappers[name] = partial(BoundListWrapper, name=name, wrapper=SimpleWrapper, verify_unique_ids=False)

    def visit_complex_list_property(self, name, decl, value_type):
        super(BindingModelVisitor, self).visit_complex_list_property(name, decl, value_type)
        self.current_class_info.wrappers[name] = partial(BoundListWrapper, name=name, wrapper=self._decl2class[value_type], verify_unique_ids=False)

    def visit_custom_property(self, name, decl):
        super(BindingModelVisitor, self).visit_custom_property(name, decl)
        self.current_class_info.wrappers[name] = decl.wrapper_class

    def visit_list_model_property(self, name, decl, value_type):
        super(BindingModelVisitor, self).visit_list_model_property(name, decl, value_type)
        self.current_class_info.wrappers[name] = partial(BoundListWrapper, name=name, wrapper=self._decl2class[value_type], verify_unique_ids=True)

    def visit_reference_property(self, name, decl):
        super(BindingModelVisitor, self).visit_reference_property(name, decl)
        self._references.append(partial(self._resolve_reference, decl.property_type.class_name, self.current_class_info.wrappers, name, self._name2class))

    def visit_reference_list_property(self, name, decl, reference_name):
        self._references.append(partial(self._resolve_reference_list, decl.property_type.property_type.class_name, self.current_class_info.wrappers, name, self._name2class))

    @staticmethod
    def _resolve_reference(class_name, wrappers, name, decl2class):
        generated_class = decl2class[class_name]
        wrappers[name] = partial(DeferredWrapper, name=name, bound_object_wrapper=generated_class)

    @staticmethod
    def _resolve_reference_list(class_name, wrappers, name, decl2class):
        generated_class = decl2class[class_name]
        wrappers[name] = partial(BoundListWrapper, name=name, wrapper=generated_class, verify_unique_ids=False)


class ViewModelVisitor(ModelVisitor):

    def __init__(self, *a, **k):
        super(ViewModelVisitor, self).__init__(*a, **k)
        self._class_stack = []
        self._decl2class = {}
        self._name2class = {}
        self._references = []

    def resolve_references(self):
        for r in self._references:
            try:
                r()
            except KeyError:
                raise UndeclaredReferenceClass

    @property
    def current_class_info(self):
        return self._class_stack[-1]

    @contextmanager
    def __call__(self, class_info):
        self._class_stack.append(class_info)
        yield class_info
        self._class_stack.pop()

    def visit_viewmodel_class(self, class_):
        with self(ClassInfo(class_=class_, d={}, default_data={}, wrappers={}, children={})) as ci:
            super(ViewModelVisitor, self).visit_viewmodel_class(class_)
            ci.d['default_data'] = ci.default_data
            ci.d['wrappers'] = ci.wrappers
            ci.d['children'] = ci.children
            generated_class = type('P2' + class_.__name__, (ModelMixin,), ci.d)
            self._decl2class[class_] = generated_class
            return generated_class

    def visit_binding_class(self, class_):
        BindingModelVisitor(self._decl2class, self._references, self._name2class).visit_class(class_)

    def visit_value_property(self, name, decl):
        super(ViewModelVisitor, self).visit_value_property(name, decl)
        ci = self.current_class_info
        ci.d[name] = _generate_model_mixin_property(name)
        ci.default_data[name] = decl.default_value
        ci.wrappers[name] = SimpleWrapper

    def visit_view_model_property(self, name, decl):
        super(ViewModelVisitor, self).visit_view_model_property(name, decl)
        ci = self.current_class_info
        ci.d[name] = _generate_model_mixin_property(name)
        ci.children[name] = self._decl2class[decl.property_type]

    def visit_value_list_property(self, name, decl, value_type):
        super(ViewModelVisitor, self).visit_value_list_property(name, decl, value_type)
        ci = self.current_class_info
        ci.d[name] = _generate_model_mixin_property(name)
        ci.default_data[name] = []
        ci.wrappers[name] = partial(NotifyingList, wrapper=SimpleWrapper)

    def visit_binding_property(self, name, decl):
        super(ViewModelVisitor, self).visit_binding_property(name, decl)
        ci = self.current_class_info
        ci.d[name] = _generate_model_mixin_property(name)
        ci.default_data[name] = None
        ci.wrappers[name] = self._decl2class[decl.property_type]

    def visit_complex_list_property(self, name, decl, value_type):
        super(ViewModelVisitor, self).visit_complex_list_property(name, decl, value_type)
        ci = self.current_class_info
        ci.d[name] = _generate_model_mixin_property(name)
        ci.default_data[name] = []
        ci.wrappers[name] = partial(NotifyingList, wrapper=self._decl2class[value_type])

    def visit_reference_property(self, name, decl):
        raise ViewModelsCantContainRefs

    def visit_list_model_property(self, name, decl, value_type):
        raise ViewModelCantContainListModels


class ModelFingerprintVisitor(ModelVisitor):

    def __init__(self, class_):
        self._fingerprint = None
        self._class2proplist = {}
        self._property_prints = []
        self.visit_class(class_)

    @property
    def property_prints(self):
        return self._property_prints[-1]

    @property
    def fingerprint(self):
        if self._fingerprint is None:
            self._fingerprint = ';'.join(('%s(%s)' % (classname, ','.join(property_prints)) for classname, property_prints in sorted(self._class2proplist.iteritems(), key=lambda item: item[0])))
        return self._fingerprint

    def visit_class(self, class_):
        with pushpop(self._property_prints, []) as property_prints:
            super(ModelFingerprintVisitor, self).visit_class(class_)
            self._class2proplist[class_.__name__] = property_prints

    def visit_id_property(self, *_a):
        self.property_prints.append('id')

    def visit_value_property(self, name, decl):
        super(ModelFingerprintVisitor, self).visit_value_property(name, decl)
        self.property_prints.append('%s:%s' % (name, decl.property_type.__name__))

    def visit_view_model_property(self, name, decl):
        super(ModelFingerprintVisitor, self).visit_view_model_property(name, decl)
        self.property_prints.append('%s:%s' % (name, decl.property_type.__name__))

    def visit_value_list_property(self, name, decl, property_type):
        super(ModelFingerprintVisitor, self).visit_value_list_property(name, decl, property_type)
        self.property_prints.append('%s:listof(%s)' % (name, property_type.__name__))

    def visit_list_model_property(self, name, decl, property_type):
        super(ModelFingerprintVisitor, self).visit_list_model_property(name, decl, property_type)
        self.property_prints.append('%s:listmodel(%s)' % (name, property_type.__name__))


def generate_model_fingerprint(cls):
    return md5(ModelFingerprintVisitor(cls).fingerprint).hexdigest()


def generate_mrs_model(cls):
    visitor = ViewModelVisitor()
    root_class = visitor.visit_viewmodel_class(cls)
    visitor.resolve_references()
    root_class.__fingerprint__ = generate_model_fingerprint(cls)
    return root_class