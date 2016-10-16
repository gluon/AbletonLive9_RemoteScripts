#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/base/dependency.py
"""
Dependency injection framework.

The framework provides lously coupled passing of dependencies from
providers to the objects that require them.

Dependencies are identified by keys, that are valid Python
identifiers.  Dependencies are provided via accessor functions, that
in general will be called whenever they are needed.
"""
from __future__ import absolute_import, print_function
from functools import wraps
from .util import union
__all__ = ('inject', 'depends', 'dependency')

class DependencyError(Exception):
    pass


class InjectionRegistry(object):

    def __init__(self, parent = None, *a, **k):
        super(InjectionRegistry, self).__init__(*a, **k)
        self._key_registry = {}

    def register_key(self, key, injector):
        self._key_registry.setdefault(key, []).append(injector)

    def unregister_key(self, key, injector):
        self._key_registry[key].remove(injector)
        if not self._key_registry[key]:
            del self._key_registry[key]

    def clear(self):
        self._key_registry = {}

    def get(self, key, default = None):
        try:
            return self._key_registry[key][-1].provides[key]
        except KeyError:
            return default


_global_injection_registry = InjectionRegistry()

def get_dependency_for(name, default = None):
    accessor = _global_injection_registry.get(name, default)
    if accessor is not None:
        return accessor()
    raise DependencyError('Required dependency %s not provided' % name)


class dependency(object):
    """
    Data descriptor that provides a given dependency looking as an
    attribute.  The depedency is specified as a keyword parameter,
    whose value can be a default accessor or None.  The attribute only
    tries to fetch the dependency on deman when needed.  Example::
    
         class HttpServer(object):
             connection_port = dependency(http_port = const(80))
    
         server = HttpServer()
         assert server.connection_port == 80
         with inject(connection_port = const(8000)).everywhere():
             assert server.connection_port == 8000
    """

    def __init__(self, **k):
        raise len(k) == 1 or AssertionError
        self._dependency_name, self._dependency_default = k.items()[0]

    def __get__(self, _, cls = None):
        return get_dependency_for(self._dependency_name, self._dependency_default)


def depends(**dependencies):
    """
    Decorates a method where dependencies are passed as keyword
    parameters.  Dependencies are specified as keywords with an
    optional accessor function or None if required.  Dependencies can
    be injected or passed directly as keyword parameters.  Example::
    
        class HttpServer(object):
            @depends(http_port = const(80))
            def listen(http_port = None):
                print "Listening on", http_port
    
        server = HttpServer()
        server.listen()
        server.listen(http_port = 8000)
        with inject(http_port = const(8000)).everywhere():
            server.listen()
    
    Produces the output::
    
        Listening on port 80
        Listening on port 8000
        Listening on port 8000
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*a, **explicit):
            deps = dict([ (k, get_dependency_for(k, v)) for k, v in dependencies.iteritems() if k not in explicit ])
            return func(*a, **union(deps, explicit))

        return wrapper

    return decorator


class Injector(object):

    @property
    def provides(self):
        return {}

    def register(self):
        pass

    def unregister(self):
        pass

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, *a):
        self.unregister()


class RegistryInjector(Injector):

    def __init__(self, provides = None, registry = None, *a, **k):
        super(RegistryInjector, self).__init__(*a, **k)
        self._provides_dict = provides
        self._registry = registry

    @property
    def provides(self):
        return self._provides_dict

    def register(self):
        registry = self._registry
        for k in self._provides_dict:
            registry.register_key(k, self)

    def unregister(self):
        registry = self._registry
        for k in self._provides_dict:
            registry.unregister_key(k, self)


class InjectionFactory(object):

    def __init__(self, provides = None, *a, **k):
        super(InjectionFactory, self).__init__(*a, **k)
        self._provides_dict = provides

    def everywhere(self):
        return RegistryInjector(provides=self._provides_dict, registry=_global_injection_registry)

    into_object = NotImplemented
    into_class = NotImplemented


def inject(**k):
    """
    Inject returns a InjectorFactory that can generate Injectors to
    inject the provided keys at different levels.  The values to
    inject are specified as keyword parameters mapping keys to given
    nullary callables that will be used to access the dependency when
    needed.
    """
    return InjectionFactory(k)