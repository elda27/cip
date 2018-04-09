import os
import os.path

def getApplicationLocalDir():
    if os.name == 'nt':
        return os.path.join(os.environ.get('LOCALAPPDATA'), 'gip')
    else:
        return os.path.join(os.environ.get('HOME'), '.gip')

def getLogDir():
    return os.path.join(getApplicationLocalDir(), 'log')

