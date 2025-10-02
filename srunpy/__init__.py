"""
SRunPy - Third-party Srun Gateway Authentication Client
深澜网关第三方认证客户端

This package provides functionality to authenticate with Srun gateway systems.
本包提供深澜网关系统的认证功能。
"""

import platform
from typing import Tuple

# Version information / 版本信息
PROGRAM_VERSION: Tuple[int, int, int, int] = (1, 0, 8, 3)
__version__: str = '.'.join(map(str, PROGRAM_VERSION))

# Import core components / 导入核心组件
from .html import WebRoot
from .srun import Srun_Py as SrunClient

# Import Windows-specific components / 导入 Windows 特定组件
if platform.system() == 'Windows':
    from .interface import MainWindow, TaskbarIcon, GUIBackend

print('SrunClient version:', __version__)