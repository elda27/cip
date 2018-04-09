import cv2

import core
import imageio
import env
import arguments
from core import command, param, module, str2bool
import log

_module_namespace = 'cv'
_module = core.module.Module(_module_namespace)
_ModuleLogger = log.getLogger('builtin.cv')

@command('canny', _module_namespace,
         help = 'Canny detector for edge detection'
        )
@param('th1', help='Lower threshold',  type=int, default=20)
@param('th2', help='Higher threshold', type=int, default=40)
class Canny(core.Processor):
    def process(self, image, th1, th2):
        return cv2.Canny(image, th1, th2)


