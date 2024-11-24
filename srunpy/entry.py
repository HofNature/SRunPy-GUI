import argparse
import json
import platform

def Cli():
    from srunpy import SrunClient,  __version__
    parser = argparse.ArgumentParser(description='深澜网关登录器(第三方) 命令行 v'+__version__)
    parser.add_argument('-i', '--info', action="store_true", help='显示网关状态 Info')
    parser.add_argument('-l', '--login', action="store_true", help='登录网关 Login')
    parser.add_argument('-o', '--logout', action="store_true", help='登出网关 Logout')
    parser.add_argument('-u', '--username', default=None, help='登录用户名 Username')
    parser.add_argument('-p', '--passwd', default=None, help='登录密码 Password')
    parser.add_argument('-g', '--gateway', default=None, help='网关地址 Gateway')
    args = parser.parse_args()
    mode=None
    if args.info:
        mode = 'info'
    elif args.login:
        mode = 'login'
    elif args.logout:
        mode = 'logout'
    if mode is None:
        print('深澜网关登录器(第三方) 命令行 v'+__version__)
        print('SrunClient (Third-party) Command Line v'+__version__)
        print('1. 判断登录状态 Check login status')
        print('2. 登录账号 Login account')
        print('3. 登出账号 Logout account')
        command = input('请输入命令 Enter command:')
        if command == '1':
            mode = 'info'
        elif command == '2':
            mode = 'login'
        elif command == '3':
            mode = 'logout'
        else:
            print('未知操作! Unknown operation!')
    if mode is not None:
        if args.gateway is not None:
            srun_client = SrunClient(srun_host=args.gateway,host_ip=args.gateway)
        else:
            srun_client = SrunClient()
        if mode == 'info':
            is_available, is_online, online_data = srun_client.is_connected()
            print('网络是否可用 Available:', is_available)
            print('是否已登录 Online:', is_online)
            if is_online:
                print('在线信息 Online data:')
                print(json.dumps(online_data, indent=4, ensure_ascii=False))
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
            srun_client.login(username, passwd)
        elif mode == 'logout':
            srun_client.logout()

def Gui():
    if platform.system() != 'Windows':
        print('此命令仅支持Windows系统 This command is only supported on Windows system')
        return
    from srunpy import GUIBackend, MainWindow, TaskbarIcon, __version__
    parser = argparse.ArgumentParser(description='深澜网关登录器(第三方) 用户界面 v'+__version__)
    parser.add_argument('--no-auto-open', action="store_true", help='不自动打开主界面 Do not open the main window automatically')
    parser.add_argument('--qt', action="store_true", help='使用Qt引擎 Use Qt engine')
    args = parser.parse_args()
    srunpy = GUIBackend(use_qt=args.qt)
    main_window = MainWindow(srunpy, not args.no_auto_open)
    while True:
        TaskbarIcon()
        main_window.start_webview()

def Main():
    # 判断操作系统
    if platform.system() == 'Windows':
        Gui()
    else:
        Cli()