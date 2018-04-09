#from core.plugin import BuiltinModule
import core
import imageio
import env
import arguments
from core import command, param, module, str2bool, prior
import log

_module_namespace = ''
_module = core.module.Module(_module_namespace)
_ModuleLogger = log.getLogger('builtin.nameless')

@command('load', _module_namespace, 
    help='Load image from URI.', 
    verbose='Supported format is following:\n' + str(imageio.formats)
    )
class ImageReader(core.Reader):
    def __init__(self):
        super().__init__()

    def read(self, filename):
        img = imageio.imread(filename)
        _ModuleLogger.info('Loaded image information is following: Shape,{}'.format(img.shape))
        #img = image.createImage(img)
        return img
    

@command('save', _module_namespace, 
    help='Save image to URI.', 
    verbose='Supported format is following:\n' + str(imageio.formats)
    )
class ImageWriter(core.Writer):
    def __init__(self):
        super().__init__()

    def write(self, filename, image, *args, **kwargs):
        assert image is not None
        _ModuleLogger.info('To be written image information is following:'
                           'Filename;{} / Shape;{}'.format(filename, image.shape))
        imageio.imwrite(filename, image)

@command('opendir', _module_namespace, 
    help='Open the directory corresponding the GIP.', 
    verbose='Supported name of directories are following:\n'
            '  log  : Containing log directory'
    )
@param('name', help='Name of directory.', required=True)
class OpenDir(core.Function):
    NAME_TO_DIR = {
        'log': env.getLogDir()
    }
    def __init__(self):
        super().__init__()

    def apply(self, name):
        if name not in OpenDir.NAME_TO_DIR:
            raise AttributeError('Name of director is neccesary any one of ' + str(OpenDir.NAME_TO_DIR))
        print(r'''
Currently not supported open the directory by the file manager.
To open the directoy is the following:
{}'''.format(OpenDir.NAME_TO_DIR[name]))


@command('help', _module_namespace, 
    help='Display help strings.'
    )
@param('name', help='The command name to be displayed help.', default=None)
@param('verbose', help='To be displayed verbose help.', default=False, type=str2bool)
@prior
class PrintHelp(core.Function):
    def __init__(self):
        super().__init__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.app.exit()
        return True

    def apply(self, name, verbose):
        if name is not None:
            # Print verbose help as a procedure.
            self._printVerboseHelp(name, verbose)
        else:
            # Print help string as modules.
            for m in module.getModules():
                self._printModuleCommands(m)
    
    def _printModuleCommands(self, module):
        commands = module.enumerateCommands()
        namespace = module.getNamespace()
        if not namespace:
            print('Core features:')
        else:
            print(namespace + ':')
        length_list = [ len(c) for c in commands ]
        max_length = max(length_list)
        for c, l in zip(commands, length_list):
            tp = module.getProcedure(c)
            print('  {}{}:{}'.format(c, ' ' * (max_length - l + 1), tp.Help))

    def _printVerboseHelp(self, cmd, verbose):
        parser = arguments.ArgumentsParser()
        parser.parse([cmd + ':'])
        token = parser.tokens()[0]
        module = self.app.solve(token.namespace())
        proc = module.createProcedure(token.operation())
        if proc is None:
            print('"{}" is unknown command.'.format(cmd))
        else:
            arg_list = [ '<{}>'.format(param.getArgumentName()) for param in reversed(proc._ReservedParams) ]
            help_list = [ 
                param.getHelp() + (' (Requirement)' 
                    if param.isRequired() 
                    else ' (default: {})'.format(param.getDefaultValue())
                    ) 
                        for param in reversed(proc._ReservedParams) 
                    
                ]
            print('{}: {}\n'.format(proc.Name, proc.Help))
            print('Usage: {}: {}'.format(proc.Name, ', '.join(arg_list)))
            for arg, help_str in zip(arg_list, help_list):
                print('  {}: {}'.format(arg, help_str))
            
            if verbose:
                print('\n' + proc.Verbose)

@command('as', _module_namespace, 
    help='Declare the name of object.',
    verbose='If source is empty, the source will be the top of stack.'
    )
@param('name', help='The name of declaration.', required=True)
@param('source', help='The source object will replace the name.', default=None)
@param('pos', help='The depth of stack will declare the name.', type=int, default=0)
class AsVariable(core.Function):
    def __init__(self):
        super().__init__()
    
    def apply(self, name, source, pos):
        if name == '' or name[0] != '@':
            raise AttributeError('The name must begin with "@". (input:{})'.format(name))
        if source is None:
            pos = -(pos + 1) # Variables are managed by list so the index should be reversed.
            self.app.Variables.as_value(name, pos)
        else:
            if source not in self.app.Variables:
                raise AttributeError('Unknown source object "{}" applying "as"'.format(source))
            if name in self.app.Variables:
                _ModuleLogger.warning('Duplicating target name "{}" applying "as".'.format(name))
            self.app.Variables.rename(source, name)
            

@command('using', _module_namespace, 
    help='To solve the module without namespace.',
    )
@param('name', help='The namespace of module will solve operation without namespace.', required=True)
class UsingModule(core.Function):
    def __init__(self):
        super().__init__()
    
    def apply(self, name):
        self.app.UsingModules.append(name)

@command('e', _module_namespace, 
    help='Exit before command processing.',
    )
@param('name', help='The namespace of module will solve operation without namespace.', required=True)
@prior
class UsingModule(core.Function):
    def __init__(self):
        super().__init__()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.app.exit()
        return True

    def apply(self, name):
        pass
