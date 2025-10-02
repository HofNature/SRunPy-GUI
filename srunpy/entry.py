"""
Entry Point Module / 入口点模块

This module provides command-line and GUI entry points for the SRunPy application.
本模块为 SRunPy 应用程序提供命令行和 GUI 入口点。
"""

import argparse
import json
import platform
from typing import List, Optional

from srunpy.ip_utils import get_local_ipv4_addresses


def Cli() -> None:
    """
    Command-line interface for SRun authentication.
    SRun 认证的命令行界面。
    """
    from srunpy import SrunClient, __version__

    parser = argparse.ArgumentParser(
        description=f'深澜网关登录器(第三方) 命令行 v{__version__}'
    )
    parser.add_argument(
        '-i', '--info', action="store_true",
        help='显示网关状态 Info'
    )
    parser.add_argument(
        '-l', '--login', action="store_true",
        help='登录网关 Login'
    )
    parser.add_argument(
        '-o', '--logout', action="store_true",
        help='登出网关 Logout'
    )
    parser.add_argument(
        '-u', '--username', default=None,
        help='登录用户名 Username'
    )
    parser.add_argument(
        '-p', '--passwd', default=None,
        help='登录密码 Password'
    )
    parser.add_argument(
        '-g', '--gateway', default=None,
        help='网关地址 Gateway'
    )
    parser.add_argument(
        '-L', '--local-ip', dest='local_ips', action='append',
        help='指定本机IP地址，可多次使用指定多个IP，可使用逗号分隔多个地址'
    )
    parser.add_argument(
        '--list-ips', action='store_true',
        help='列出本机可用IP地址 List local IP addresses'
    )
    args = parser.parse_args()

    def build_client(bind_ip: Optional[str]):
        """Build SrunClient with specified binding IP / 使用指定的绑定 IP 构建 SrunClient"""
        if args.gateway is not None:
            return SrunClient(
                srun_host=args.gateway,
                host_ip=args.gateway,
                client_ip=bind_ip
            )
        return SrunClient(client_ip=bind_ip)

    def list_ips() -> None:
        """List available local IP addresses / 列出可用的本地 IP 地址"""
        ips = get_local_ipv4_addresses()
        print('本机可用IP地址 Local IP addresses:')
        if not ips:
            print('  (未检测到非回环IPv4地址 No non-loopback IPv4 detected)')
        else:
            for ip in ips:
                client = build_client(ip)
                is_available, is_online, online_data = client.is_connected()
                showstr = f'  - {ip} '
                if is_available:
                    showstr += '(网关可用 Available, '
                    if is_online:
                        showstr += '已登录 Online)'
                    else:
                        showstr += '未登录 Offline)'
                else:
                    showstr += '(网关不可用 Unavailable)'
                print(showstr)

    # Process local IP selections / 处理本地 IP 选择
    available_ips = set(get_local_ipv4_addresses())
    selected_ips: List[Optional[str]] = []
    if args.local_ips:
        for item in args.local_ips:
            if item is None:
                continue
            for ip in item.split(','):
                ip = ip.strip()
                if not ip:
                    continue
                if ip.lower() in {'auto', 'default'}:
                    selected_ips.append(None)
                    continue
                if ip in available_ips:
                    selected_ips.append(ip)
                else:
                    print(
                        f'警告: IP地址 {ip} 未在本机检测到，已跳过 '
                        f'Warning: IP {ip} not found locally, skipped'
                    )
    if not selected_ips:
        selected_ips = [None]
    else:
        # Keep user-specified order while removing duplicates
        # 保持用户指定的顺序，同时去除重复
        selected_ips = list(dict.fromkeys(selected_ips))

    # Determine operation mode / 确定操作模式
    mode: Optional[str] = None
    if args.info:
        mode = 'info'
    elif args.login:
        mode = 'login'
    elif args.logout:
        mode = 'logout'
    elif args.list_ips:
        mode = 'list_ips'

    if mode is None:
        print(f'深澜网关登录器(第三方) 命令行 v{__version__}')
        print(f'SrunClient (Third-party) Command Line v{__version__}')
        print('如需设置网关地址,请使用-g参数 Use -g parameter to set gateway address')
        print('如需指定本机IP地址,请使用-L参数 Use -L parameter to specify local IP address')
        print('1. 判断登录状态 Check login status')
        print('2. 登录账号 Login account')
        print('3. 登出账号 Logout account')
        print('4. 列出本机IP地址 List local IP addresses')
        command = input('请输入命令 Enter command:')
        if command == '1':
            mode = 'info'
        elif command == '2':
            mode = 'login'
        elif command == '3':
            mode = 'logout'
        elif command == '4':
            mode = 'list_ips'
        else:
            print('未知操作! Unknown operation!')

    # Execute the selected operation / 执行选定的操作
    if mode is not None:
        if mode == 'info':
            for bind_ip in selected_ips:
                label = bind_ip if bind_ip is not None else '默认(Default)'
                print('\n=== IP:', label, '===')
                try:
                    client = build_client(bind_ip)
                    is_available, is_online, online_data = client.is_connected()
                    print('网络是否可用 Available:', is_available)
                    print('是否已登录 Online:', is_online)
                    if is_online:
                        print('在线信息 Online data:')
                        print(json.dumps(online_data, indent=4, ensure_ascii=False))
                except Exception as exc:
                    print('查询失败 Failed to fetch status:', exc)
        elif mode == 'login':
            if args.username is None:
                username = input('请输入用户名 Username:')
            else:
                username = args.username
            if args.passwd is None:
                import getpass
                passwd = getpass.getpass('请输入密码 Password:')
            else:
                passwd = args.passwd
            for bind_ip in selected_ips:
                label = bind_ip if bind_ip is not None else '默认(Default)'
                print('\n=== IP:', label, '===')
                try:
                    client = build_client(bind_ip)
                    client.login(username, passwd)
                    print('登录成功 Login succeeded')
                except Exception as exc:
                    print('登录失败 Login failed:', exc)
        elif mode == 'logout':
            for bind_ip in selected_ips:
                label = bind_ip if bind_ip is not None else '默认(Default)'
                print('\n=== IP:', label, '===')
                try:
                    client = build_client(bind_ip)
                    client.logout()
                    print('注销成功 Logout succeeded')
                except Exception as exc:
                    print('注销失败 Logout failed:', exc)
        elif mode == 'list_ips':
            list_ips()


def Gui(aes_key: Optional[str] = None) -> None:
    """
    Graphical user interface for SRun authentication (Windows only).
    SRun 认证的图形用户界面（仅限 Windows）。

    Args / 参数:
        aes_key: AES encryption key for config storage / 用于配置存储的 AES 加密密钥
    """
    if platform.system() != 'Windows':
        print('此命令仅支持Windows系统 This command is only supported on Windows system')
        return

    from srunpy import GUIBackend, MainWindow, TaskbarIcon, __version__

    parser = argparse.ArgumentParser(
        description=f'深澜网关登录器(第三方) 用户界面 v{__version__}'
    )
    parser.add_argument(
        '--no-auto-open', action="store_true",
        help='不自动打开主界面 Do not open the main window automatically'
    )
    parser.add_argument(
        '--qt', action="store_true",
        help='使用Qt引擎 Use Qt engine'
    )
    args = parser.parse_args()

    if aes_key is not None:
        srunpy = GUIBackend(use_qt=args.qt, aes_key=aes_key)
    else:
        srunpy = GUIBackend(use_qt=args.qt)

    main_window = MainWindow(srunpy, not args.no_auto_open)
    while True:
        TaskbarIcon()
        main_window.start_webview()


def Main() -> None:
    """
    Main entry point - dispatches to CLI or GUI based on OS.
    主入口点 - 根据操作系统分派到 CLI 或 GUI。
    """
    if platform.system() == 'Windows':
        Gui()
    else:
        Cli()


def Build() -> None:
    """
    Build standalone executable using Nuitka (Windows only).
    使用 Nuitka 构建独立可执行文件（仅限 Windows）。
    """
    if platform.system() != 'Windows':
        print('此命令仅支持Windows系统 This command is only supported on Windows system')
        return

    try:
        import nuitka  # noqa: F401
    except ImportError:
        print('请先安装依赖 Please install dependencies')
        print('你可以使用以下命令 You can use the following command')
        print('pip install srunpy[build]')
        return

    parser = argparse.ArgumentParser(
        description='编译为独立可执行文件 Compile to standalone executable'
    )
    parser.add_argument(
        '--path', default=None,
        help='输出文件夹路径 Output folder path'
    )
    parser.add_argument(
        '--default_key', action="store_true",
        help='使用默认密钥 Use default key'
    )
    parser.add_argument(
        '--icon', default=None,
        help='图标路径 Icon path'
    )
    parser.add_argument(
        '--version', default=None,
        help='版本号 Version'
    )
    parser.add_argument(
        '--company', default=None,
        help='公司名称 Company name'
    )
    parser.add_argument(
        '--product', default=None,
        help='产品名称 Product name'
    )
    parser.add_argument(
        '--description', default=None,
        help='文件描述 File description'
    )
    args = parser.parse_args()

    import os
    import random
    import string
    import sys

    python_path = os.path.abspath(sys.executable)
    if python_path.endswith('pythonw.exe'):
        python_path = os.path.join(os.path.dirname(python_path), 'python.exe')
    if not os.path.exists(python_path):
        print('未找到Python解释器 Not found Python interpreter')
        return

    # Get output path / 获取输出路径
    if args.path is not None:
        path = args.path
    else:
        desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')
        default_path = os.path.join(desktop_path, 'SrunPy')
        print('请输入输出文件夹路径 Please enter the output folder path')
        path = input(f'[{default_path}]')
        if path == '':
            path = default_path

    # Create output directory / 创建输出目录
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        res = input(
            '文件夹已存在,是否覆盖? The folder already exists, '
            'do you want to overwrite? (Y/n)'
        )
        if res.lower() == 'n':
            return

    # Generate entry point file / 生成入口点文件
    aes_key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    with open(os.path.join(path, 'SRunClient.py'), 'w', encoding='utf-8') as f:
        f.write("from srunpy.entry import Gui\n")
        if args.default_key:
            f.write("Gui()\n")
        else:
            f.write(f"Gui('{aes_key}')\n")

    # Compile / 编译
    from srunpy import WebRoot, __version__
    os.chdir(path)

    # Set compilation parameters / 设置编译参数
    if args.icon is not None and os.path.exists(args.icon):
        icon_path = args.icon
    else:
        icon_path = os.path.join(WebRoot, 'icons/logo.ico')

    if args.version is not None:
        file_version = args.version
        product_version = args.version
    else:
        file_version = __version__
        product_version = __version__

    if args.company is not None:
        company_name = args.company
    else:
        company_name = 'HopeOFNature'

    if args.product is not None:
        product_name = args.product
    else:
        product_name = 'SRun Authenticator'

    if args.description is not None:
        file_description = args.description
    else:
        file_description = 'SRun Authenticator'

    execute = [
        python_path, '-m', 'nuitka', '--lto=no',
        '--standalone', 'SRunClient.py',
        f'--include-data-dir="{WebRoot}"=srunpy/html',
        '--windows-console-mode=attach',
        f'--windows-icon-from-ico="{icon_path}"',
        f'--file-version="{file_version}"',
        f'--product-version="{product_version}"',
        f'--company-name="{company_name}"',
        f'--product-name="{product_name}"',
        f'--file-description="{file_description}"'
    ]

    print('编译中 Compiling')
    print(' '.join(execute))
    os.system(' '.join(execute))

    exe_path = os.path.join(path, 'SRunClient.dist', 'SRunClient.exe')
    if not os.path.exists(exe_path):
        print('编译失败,请查看错误信息 Compile failed, please check the error message')
        return
    else:
        print('编译完成 Compile completed')
        if not args.default_key:
            print(
                '建议删除SRunClient.py文件以保护密钥 '
                'It is recommended to delete the SRunClient.py file to protect the key'
            )
        print('请在以下路径查看可执行文件 Please check the executable file in the following path')
        print(os.path.abspath(exe_path))
        res = input('是否立即启动程序? Whether to start the program immediately? (Y/n)')
        if res.lower() == 'n':
            return
        # Start program in background and exit / 后台启动程序并退出
        os.system('start ' + exe_path)
        return

