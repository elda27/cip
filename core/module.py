import os
import abc
import importlib
import log
from functools import wraps

_ModuleLogger = log.getLogger('module')

class ModuleManager:
    def __init__(self, modules = []):
        self.Modules = dict()
        for module in modules:
            self.append(module)
    
    def solve(self, namespace):
        _ModuleLogger.debug('Solve module:{}, {}'.format(namespace, namespace in self.Modules))
        if namespace not in self.Modules:
            raise KeyError('Unknown module "{}"'.format(namespace))
        return self.Modules[namespace]

    def modules(self):
        return list(self.Modules.values())

    def append(self, module, namespace = None):
        if namespace is None:
            namespace = module.getNamespace()
        self.Modules[namespace] = module

_ModuleManager = ModuleManager()

def getModule(namespace):
    return _ModuleManager.solve(namespace)

def getModules():
    return _ModuleManager.modules()

def module(name):
    def _module(klass):
        @wraps(klass)
        def _klass(*args, **kwargs):
            m = klass(*args, **kwargs)
            _ModuleManager.append(m, name)
            return m
        return _klass
    return _module

class Module:
    def __init__(self, namespace):
        self.Namespace = namespace
        _ModuleManager.append(self)
        self.Procedures = dict()

    def getNamespace(self):
        return self.Namespace

    def append(self, name, klass):
        assert(name not in self.Procedures)
        self.Procedures[name] = klass

    def enumerateCommands(self):
        return self.Procedures.keys()

    def getProcedure(self, name):
        if name in self.Procedures:
            return self.Procedures[name]
        return None

    def createProcedure(self, name):
        _ModuleLogger.debug('Create procedure:{}, {}'.format(name, name in self.Procedures))
        tp = self.getProcedure(name)
        return tp() if tp is not None else None
