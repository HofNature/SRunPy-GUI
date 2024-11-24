PROGRAM_VERSION = (1, 0, 6, 2)
__version__ = '.'.join(map(str, PROGRAM_VERSION))

from .html import WebRoot
from .srun import Srun_Py as SrunClient
from .interface import MainWindow, TaskbarIcon, GUIBackend


print('SrunClient version:', __version__)