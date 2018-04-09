import functools
import abc
import sys
from collections import OrderedDict
from enum import Enum
from contextlib import contextmanager

import log
from . import module

_ModuleLogger = log.getLogger('cip.core')

class Param:
    def __init__(self, *args, **kwargs):
        #assert(len(args) > 0, 'Arguments are necessery at least one.')
        self.ArgNames = args
        self.Help = kwargs.get('help', '')
        self.VerboseHelp = kwargs.get('verbose', '')
        self.DefaultValue = kwargs.get('default', None)
        self.IsRequired = kwargs.get('required', False)
        self.Type = kwargs.get('type', str)

    def __repr__(self):
        return '<Param: {}, {}>'.format(
            self.ArgNames[0],
            'Requirement parameter' if self.IsRequired else 'default=' + str(self.DefaultValue)
            )

    def getArguments(self):
        return self.ArgNames

    def getArgumentName(self):
        return self.ArgNames[0]

    def getHelp(self):
        return self.Help

    def getVerboseHelp(self):
        return self.VerboseHelp # if self.VerboseHelp != '' else self.Help

    def getDefaultValue(self):
        return self.DefaultValue

    def isRequired(self):
        return self.IsRequired

    def getType(self):
        return self.Type

# ---------------------------------------------------------------
# Decorators for implementation of procedure.
# ---------------------------------------------------------------

def command(name, namespace, help, verbose=''):
    def _command(klass):
        m = module.getModule(namespace)
        m.append(name, klass)

        klass.Namespace = namespace
        klass.Name = name
        klass.Help = help
        klass.Verbose = verbose
        if '_ReservedParams' not in klass.__dict__ or klass._ReservedParams is None:
            klass._ReservedParams = list()
        
        if issubclass(klass, IWriter):
            klass = param('image', help='Image to be saved', default='@temp')(klass)
            klass = param('filename', help='Name of file', required=True)(klass)
        elif issubclass(klass, IReader):
            klass = param('filename', help='Name of file to be loaded', required=True)(klass)
        elif issubclass(klass, IProcessor):
            klass = param('image', help='Name of file to be loaded', default='@temp')(klass)

        return klass
    return _command

def param(*names, help='', verbose='', required=False, default=None, type=str):
    def _param(klass):
        if '_ReservedParams' not in klass.__dict__ or klass._ReservedParams is None:
            klass._ReservedParams = list()
        klass._ReservedParams.append(Param(*names, help=help, verbose=verbose, required=required, default=default, type=type))
        return klass
    return _param

def prior(klass):
    if '_Prior' not in klass.__dict__ or not klass._Prior:
        klass._Prior = True
    return klass

def str2bool(string):
    string = string.lower()
    if string in ('true', 'on'):
        return True
    elif string in ('false', 'off'):
        return False
    raise ValueError('String is not valid. ({})'.format(string))

# ---------------------------------------------------------------
# Decorators for image processing.
# ---------------------------------------------------------------

def rgb(func):
    @functools.wraps(func)
    def _rgb(image, *args, **kwargs):
        assert len(squeeze_shape(image.shape)) == 2
        return func(image, *args, **kwargs)
    return _rgb

# ---------------------------------------------------------------
# Iterfaces of processing
# ---------------------------------------------------------------

class IFunction:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def apply(self, *args, **kwargs):
        raise NotImplementedError()

class IReader:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def read(self, filename, *args, **kwargs):
        raise NotImplementedError()
        
class IWriter:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def write(self, filename, image, *args, **kwargs):
        raise NotImplementedError()
        
class IProcessor:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def process(self, image, *args, **kwargs):
        raise NotImplementedError()

    def isBatchProcessable(self):
        return False

# ---------------------------------------------------------------
# Manager classes for application
# ---------------------------------------------------------------

class VariableManager:
    def __init__(self):
        self.Stack = list()
        self.Variables = dict()
    
    def __iter__(self):
        return iter(self.Variables)

    def push(self, value):
        self.Stack.append(value)
        self.Variables['@temp'] = value

    def pop(self):
        obj = self.Stack[-1]
        del self.Stack[-1]
        return obj

    def get(self, name):
        return self.Variables[name]

    def as_value(self, name, position = -1):
        self.Variables[name] = self.Stack[position]
        del self.Stack[position]

    def rename(self, old_name, new_name):
        self.Variables[new_name] = self.Variables[old_name]
        del self.Variables[old_name]

    def deleteTemp(self):
        del self.Variables['@temp']

class ParamSolver:
    def __init__(self, params):
        self.Params = params

    def solve(self, token):
        args = token.args()
        kwargs = token.kwargs()
        #assert len(args) < len(self.Params), 'Number of arguments must be least than number of parameters.'

        solved_args = args
        solved_kwargs = dict()
        params = list(reversed(self.Params))
        for param in params[len(args):]:
            cands = [ (param.getArgumentName(), kwargs[arg]) for arg in param.getArguments() if arg in kwargs ]
            if len(cands) == 0:
                if param.isRequired():
                    raise AttributeError('Required argument is not set. {}'.format(param))
                else:
                    solved_kwargs[param.getArgumentName()] = param.getDefaultValue()
            else:
                key, value = cands[0]
                solved_kwargs[key] = value

        return solved_args, solved_kwargs

    def displayHelp(self, proc_name, formatter = None):
        args = ' '.join([ '<{}>'.format(param.getArgumentName()) for param in self.Params ])
        print(proc_name + ' ' + args + '\n')
        for param in self.Params:
            print('  {}: {}'.format(', '.join(param.getArguments()), param.getHelp()), end=' ')
            if param.isRequired():
                print('(Require)')
            else:
                default_value = param.getDefaultValue()
                if default_value is None:
                    print('')
                else:
                    print('(default:{})'.format(default_value))
        print('\n')

# ---------------------------------------------------------------
# Application features
# ---------------------------------------------------------------

class Application:
    Instance_ = None
    def __init__(self):
        pass
    
    def __new__(cls):
        if not hasattr(cls, 'Instance_') or cls.Instance_ is None:
            cls.Instance_ = super().__new__(cls)
            cls.Instance_.Variables = VariableManager()
            cls.Instance_.UsingModules = list()
        return cls.Instance_

    def exec(self, proc, arg_token):
        args, kwargs = ParamSolver(proc._ReservedParams).solve(arg_token)
        args, kwargs = self.solveVariables(*args, **kwargs)
        value = proc(*args, **kwargs)
        if value is not None:
            self.Variables.push(value)

    def exit(self):
        sys.exit()

    def getProcedure(self, namespace, proc_name):
        proc = None
        if namespace == '':
            for m in self.UsingModules: # Search from using modules.
                module = self.solve(m)
                proc = module.getProcedure(proc_name)
                if proc is not None:
                    break
            if proc is None: # Search proc from builtin module.
                module = self.solve(namespace)
                proc = module.getProcedure(proc_name)
        else: # Search from loaded modules.
            module = self.solve(namespace)
            proc = module.getProcedure(proc_name)
        return proc

    def createProcedure(self, namespace, proc_name):
        return self.getProcedure(namespace, proc_name)()

    def solve(self, name):
        if len(name) > 0 and name[0] == '@':
            if name not in self.Variables:
                raise AttributeError('Unknown variable: ' + name)
            return self.Variables.get(name)
        else:
            return module.getModule(name)

    def solveVariables(self, *args, **kwargs):
        for i, arg in enumerate(args):
            if isinstance(arg, str) and arg[0] == '@' and arg in self.Variables:
                args[i] = self.Variables.get(arg)
        
        for key, value in kwargs.items():
            if isinstance(value, str) and value[0] == '@' and value in self.Variables:
                kwargs[key] = self.Variables.get(value)
                
        return args, kwargs

# ---------------------------------------------------------------
# Procedure classes
# ---------------------------------------------------------------

class Procedure:
    def __init__(self):
        self.ParentApplication = Application()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass
        
    def setApplication(self, app = Application()):
        self.ParentApplication = app

    @property
    def app(self):
        return self.ParentApplication

    def __call__(self, *args, **kwargs):
        if isinstance(self, IFunction):
            self.apply(*args, **kwargs)
            return None
        elif isinstance(self, IProcessor):
            return self.process(*args, **kwargs)
        elif isinstance(self, IReader):
            return self.read(*args, **kwargs)
        elif isinstance(self, IWriter):
            self.write(*args, **kwargs)
            return None

class Reader(Procedure, IReader):
    pass
class Writer(Procedure, IWriter):
    pass
class Processor(Procedure, IProcessor):
    pass
class Function(Procedure, IFunction):
    pass