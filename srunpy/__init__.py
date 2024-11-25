PROGRAM_VERSION = (1, 0, 6, 8)
__version__ = '.'.join(map(str, PROGRAM_VERSION))

from .html import WebRoot
from .srun import Srun_Py as SrunClient
import platform
if platform.system() == 'Windows':
    from .interface import MainWindow, TaskbarIcon, GUIBackend


print('SrunClient version:', __version__)