#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/model/declaration.py


class ModelDeclarationException(Exception):
    pass


class WrongIdPropertyDeclaration(ModelDeclarationException):
    pass


class ViewModelsCantContainRefs(ModelDeclarationException):
    pass


class UndeclaredReferenceClass(ModelDeclarationException):
    pass


def is_view_model_property_decl(decl):
    try:
        return ViewModel in decl.property_type.__mro__
    except AttributeError:
        return False


def is_list_property_decl(decl):
    return isinstance(decl.property_type, listof)


def is_list_model_property_decl(decl):
    return isinstance(decl.property_type, listmodel)


def is_binding_property_decl(decl):
    try:
        return Binding in decl.property_type.__mro__
    except AttributeError:
        return False


def is_reference_property_decl(decl):
    return isinstance(decl.property_type, ref)


def is_value_property_type(decl):
    return decl.property_type in (int,
     long,
     float,
     unicode,
     str,
     bool)


class property_declaration(object):
    pass


class view_property(property_declaration):
    sentinel = object()

    def __init__(self, property_type, default_value = sentinel, *a, **k):
        super(view_property, self).__init__(*a, **k)
        self.property_type = property_type
        self.default_value = default_value
        raise default_value is not self.sentinel or is_view_model_property_decl(self) or is_list_property_decl(self) or is_binding_property_decl(self) or is_reference_property_decl(self) or AssertionError

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.property_type)

    def visit(self, name, visitor):
        visitor.visit_view_property(name, self)


class custom_property(view_property):

    def __init__(self, property_type, wrapper_class = None, *a, **k):
        raise wrapper_class is not None or AssertionError
        super(custom_property, self).__init__(property_type=property_type, *a, **k)
        self.wrapper_class = wrapper_class


class id_property(property_declaration):
    property_type = int
    default_value = -1

    @staticmethod
    def id_attribute_getter(obj):
        if hasattr(obj, '__id__'):
            return unicode(obj.__id__)
        elif hasattr(obj, '_live_ptr'):
            return unicode(obj._live_ptr)
        return unicode(id(obj))

    def visit(self, name, visitor):
        visitor.visit_id_property(name, self)


class listof(object):

    def __init__(self, property_type, *a, **k):
        super(listof, self).__init__(*a, **k)
        self.property_type = property_type

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.property_type)


class listmodel(listof):
    pass


class ModelVisitor(object):

    def visit_class(self, class_):
        for name, decl in class_.__dict__.iteritems():
            if isinstance(decl, property_declaration):
                decl.visit(name, self)

    def visit_id_property(self, name, decl):
        pass

    def visit_view_property(self, name, decl):
        if is_value_property_type(decl):
            self.visit_value_property(name, decl)
        elif is_view_model_property_decl(decl):
            self.visit_view_model_property(name, decl)
        elif is_list_property_decl(decl):
            self.visit_list_property(name, decl)

    def visit_value_property(self, name, decl):
        pass

    def visit_view_model_property(self, name, decl):
        self.visit_class(decl.property_type)

    def visit_list_property(self, name, decl):
        if is_value_property_type(decl.property_type):
            self.visit_value_list_property(name, decl, decl.property_type.property_type)
        elif is_list_model_property_decl(decl):
            self.visit_list_model_property(name, decl, decl.property_type.property_type)
        elif is_view_model_property_decl(decl.property_type):
            self.visit_complex_list_property(name, decl, decl.property_type.property_type)
        else:
            raise Exception('Invalid property declaration')

    def visit_value_list_property(self, name, decl, value_type):
        pass

    def visit_list_model_property(self, name, decl, value_type):
        self.visit_class(value_type)

    def visit_complex_list_property(self, name, decl, value_type):
        self.visit_class(value_type)


class ModelMeta(type):

    def visit(cls, visitor):
        visitor.visit_class(cls)


class ViewModel(object):
    __metaclass__ = ModelMeta


class Binding(ViewModel):
    pass


class ref(object):

    def __init__(self, class_name, *a, **k):
        super(ref, self).__init__(*a, **k)
        self.class_name = class_name