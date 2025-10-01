#!/usr/bin/python3

from srunpy import SrunClient, PROGRAM_VERSION, WebRoot
from srunpy.ip_utils import get_local_ipv4_addresses

import os
import sys
import time
import json
import base64
import socket
import webview
import pystray
import requests
import threading
import webbrowser
import subprocess
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from PIL import Image
import win32con
import win32api
import win32com.client as client
from win10toast import ToastNotifier
import ctypes
import win32gui
import platform
import uuid

def is_ip_address(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False

def is_domain(address):
    if not is_ip_address(address):
        try:
            ip=socket.gethostbyname(address)
            return True,ip
        except socket.error:
            return False,""
    return False,""

sysToaster = ToastNotifier()


#qt_backend = False
current_pid = os.getpid()
# resource_path = os.path.dirname(os.path.abspath(__file__))
application_path = os.path.abspath(sys.argv[0])
python_path = os.path.abspath(sys.executable)
start_lnk_path = os.path.join(os.path.expandvars(
    r'%APPDATA%'), r'Microsoft\Windows\Start Menu\Programs\Startup', '校园网登陆器.lnk')
appdata_path = os.path.expandvars(r'%APPDATA%')
config_path = os.path.join(appdata_path, 'SRunPy', 'config.json')

def exit_application():
    os._exit(0)


def webbrowser_open(url):
    webbrowser.open(url)


def get_Color_Mode():
    # coding:utf-8
    reg_root = win32con.HKEY_CURRENT_USER
    reg_path = r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
    reg_flags = win32con.KEY_READ | win32con.KEY_WOW64_64KEY
    # 读取键值
    key = win32api.RegOpenKey(reg_root, reg_path, 0, reg_flags)
    value, _ = win32api.RegQueryValueEx(key, "SystemUsesLightTheme")

    # 关闭键
    win32api.RegCloseKey(key)
    return value

def get_Update():
    try:
        response = requests.get(
            "https://api.github.com/repos/HofNature/SRunPy-GUI/releases/latest")
        if response.status_code == 200:
            data = response.json()
            tag_name = data['tag_name']
            if tag_name[1:] > '.'.join(map(str, PROGRAM_VERSION)):
                return True
        return False
    except:
        return False

def load_config(aes_key):
    aes = MyAES(key=aes_key)
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        config = {
            "username": "",
            "password": "",
            "pass_correct": False,
            "srun_host": "gw.buaa.edu.cn",
            "self_service": "zfw.buaa.edu.cn",
            "host_ip": "10.200.21.4",
            "sleeptime": 5,
            "auto_login": False,
            "start_with_windows": False,
            "local_ips": [],
            "active_ip": None,
        }
        with open(config_path, 'w') as f:
            f.write(json.dumps(config, indent=4, ensure_ascii=True))
    else:
        with open(config_path, 'r') as f:
            config = json.load(f)
        if config['password'] != "":
            config['password'] = aes.decode_aes(config['password'].encode())
        if not config.get('pass_correct'):
            config['auto_login'] = False
        config.setdefault('local_ips', [])
        config.setdefault('active_ip', None)
    return config

def reset_config():
    os.remove(config_path)

def save_config(config,aes_key):
    aes = MyAES(key=aes_key)
    config['password'] = aes.encode_aes(config['password']).decode()
    with open(config_path, 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=True))
    config['password'] = aes.decode_aes(config['password'].encode())


def check_lnk():
    return os.path.exists(start_lnk_path)


def delete_lnk():
    if check_lnk():
        os.remove(start_lnk_path)

def create_desktop_lnk(qt_backend=False):
    no_cmd_path=os.path.join(os.path.dirname(application_path), 'srunpy-gui.exe')
    if python_path != application_path and os.path.exists(python_path) and os.path.basename(application_path).endswith(".exe") and os.path.exists(no_cmd_path):
        desktop_lnk=os.path.join(os.path.expandvars(r'%USERPROFILE%'), 'Desktop', '校园网登陆器.lnk')
        if os.path.exists(desktop_lnk):
            os.remove(desktop_lnk)
        shell = client.Dispatch('Wscript.Shell')
        link = shell.CreateShortCut(desktop_lnk)
        link.TargetPath = no_cmd_path
        #link.Arguments = ' --no-auto-open'
        if qt_backend:
            link.Arguments += ' --qt'
        link.IconLocation = os.path.join(WebRoot, 'icons/logo.ico')+',0'
        link.save()
    else:
        print("非EntryPoint启动，无法创建桌面快捷方式")

def create_lnk(qt_backend=False):
    delete_lnk()
    shell = client.Dispatch('Wscript.Shell')
    link = shell.CreateShortCut(start_lnk_path)
    no_cmd_path=os.path.join(os.path.dirname(application_path), 'srunpy-gui.exe')
    if python_path == application_path or not os.path.exists(python_path):
        link.TargetPath = application_path
        link.Arguments = ' --no-auto-open'
        link.IconLocation = application_path+',0'
    elif os.path.exists(python_path) and os.path.basename(application_path).endswith(".exe") and os.path.exists(no_cmd_path):
        link.TargetPath = no_cmd_path
        link.Arguments = ' --no-auto-open'
        link.IconLocation = os.path.join(
            WebRoot, 'icons/logo.ico')+',0'
    else:
        link.TargetPath = python_path
        link.Arguments = '"'+application_path+'" --no-auto-open'
        link.IconLocation = os.path.join(
            WebRoot, 'icons/logo.ico')+',0'
    if qt_backend:
        link.Arguments += ' --qt'
    link.save()


class MyAES:
    def __init__(self, key):
        self.key = key.encode()

    def __add_to_16(self, text):
        """ 如果string不足16位则用空格补齐16位 """
        if len(text.encode()) % 16:
            add = 16 - (len(text.encode()) % 16)
        else:
            add = 0
        text += ("\0" * add)
        return text.encode()

    def encode_aes(self, text):
        cryptos = AES.new(key=self.key, mode=AES.MODE_ECB)
        cipher_text = cryptos.encrypt(self.__add_to_16(text))
        # 由于AES加密后的字符串不一定是ascii字符集，所以转为16进制字符串
        return b2a_hex(cipher_text)

    def decode_aes(self, text):
        cryptos = AES.new(key=self.key, mode=AES.MODE_ECB)
        plain_text = cryptos.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip("\0")


class TaskbarIcon():
    def __init__(self):
        self.menu = pystray.Menu(
            pystray.MenuItem("打开主界面", self.stop, default=True),
            pystray.MenuItem("退出登陆器", self.exit)
        )
        try:
            if get_Color_Mode() == 0:
                icon_path = r'icons\journey_white.png'
            else:
                icon_path = r'icons\journey.png'
        except:
            icon_path = r'icons\logo.png'
        self.icon = pystray.Icon("SRunPy", Image.open(
            os.path.join(WebRoot, icon_path)), "校园网登陆器", self.menu)
        self.icon.run()

    def stop(self):
        self.icon.stop()

    def exit(self):
        self.icon.stop()
        os._exit(0)


class GUIBackend():
    def __init__(self,use_qt=False,aes_key="dj26Dh47useoUI28"):
        if use_qt:
            try:
                import webview.platforms.qt
            except ImportError:
                print("无法导入Qt库，请使用pip install srumpy[qt]安装")
                print("Failed to import Qt library, please use pip install srumpy[qt] to install")
                use_qt = False
        self.aes_key = aes_key
        self.qt_backend = use_qt
        self.auto_login_thread = None
        self.srun_clients = {}
        self.active_ip = None
        self.isUptoDate = False
        self.hasDoneUpdate = False
        def check_update():
            self.isUptoDate = get_Update()
        threading.Thread(target=check_update).start()
        self.refresh_config()
        if 'process_id' in self.config and self.config['process_id'] != current_pid:
            subprocess.call("start /B taskkill /f /pid "+str(self.config['process_id']),shell=True)
        if 'process_id' not in self.config:
            try:
                create_desktop_lnk(qt_backend=self.qt_backend)
            except:
                pass
        self.config["process_id"] = current_pid
        save_config(self.config,aes_key)

    def refresh_config(self):
        try:
            self.config = load_config(self.aes_key)
            self.username = self.config['username']
            self.password = self.config['password']
            self.pass_correct = self.config['pass_correct']
            self.srun_host = self.config['srun_host']
            self.host_ip = self.config['host_ip']
            self.self_service = self.config['self_service']
            self.sleeptime = self.config['sleeptime']
            self.auto_login = self.config['auto_login']
            self.start_with_windows = self.config['start_with_windows']
            self.local_ips = self.config.get('local_ips', [])
            self.active_ip = self.config.get('active_ip')
        except Exception as e:
            print(str(e))
            reset_config()
            self.refresh_config()
            return
        self._rebuild_clients()
        self._ensure_active_ip()
        self.srun = self.get_client()
        if self.start_with_windows:
            create_lnk(qt_backend=self.qt_backend)
        else:
            delete_lnk()
        if self.auto_login:
            if self.auto_login_thread is None or not self.auto_login_thread.is_alive():
                self.auto_login_thread = threading.Thread(
                    target=self.auto_login_deamon)
                self.auto_login_thread.start()

    def _create_client(self, client_ip):
        if self.srun_host == "":
            return SrunClient(self.host_ip, self.host_ip, client_ip=client_ip)
        return SrunClient(self.srun_host, self.host_ip, client_ip=client_ip)

    def _rebuild_clients(self):
        self.srun_clients = {}
        ip_list = []
        seen = set()

        def append_ip(value):
            if value not in seen:
                ip_list.append(value)
                seen.add(value)

        append_ip(None)
        if self.local_ips:
            for ip in self.local_ips:
                append_ip(ip)
        if not ip_list:
            ip_list = [None]
        for ip in ip_list:
            try:
                self.srun_clients[ip] = self._create_client(ip)
            except Exception as exc:
                print(f"初始化IP {ip or '默认'} 失败: {exc}")
        if not self.srun_clients:
            self.srun_clients[None] = self._create_client(None)

    def _ensure_active_ip(self):
        if not self.srun_clients:
            self.active_ip = None
            return
        if self.active_ip not in self.srun_clients:
            self.active_ip = next(iter(self.srun_clients.keys()))
            self.config['active_ip'] = self.active_ip
            save_config(self.config,self.aes_key)

    def get_client(self, ip=None):
        if not self.srun_clients:
            return None
        if ip in self.srun_clients:
            return self.srun_clients[ip]
        if ip is None and None in self.srun_clients:
            return self.srun_clients[None]
        if self.active_ip in self.srun_clients:
            return self.srun_clients[self.active_ip]
        return next(iter(self.srun_clients.values()))

    def _update_gateway_only(self, srun_host, self_service):
        domain, ip_addr = is_domain(srun_host)
        if domain:
            self.config['srun_host'] = srun_host
            self.config['host_ip'] = ip_addr
        elif is_ip_address(srun_host):
            self.config['srun_host'] = ""
            self.config['host_ip'] = srun_host
        else:
            return False
        self.config['self_service'] = self_service
        return True

    def _update_local_ip_selection(self, selected_ips, active_ip):
        if selected_ips is None:
            return
        normalized = []
        available = set(get_local_ipv4_addresses())
        for ip in selected_ips:
            if ip in (None, "", "null"):
                normalized.append(None)
            elif ip in available:
                normalized.append(ip)
        if normalized:
            ordered = []
            for ip in normalized:
                if ip not in ordered:
                    ordered.append(ip)
            normalized = ordered
        else:
            normalized = []
        self.config['local_ips'] = normalized
        if normalized:
            if active_ip in normalized:
                self.config['active_ip'] = active_ip
            else:
                self.config['active_ip'] = normalized[0]
        else:
            self.config['active_ip'] = None

    def set_config(self, username, password):
        if username != "" and username != self.config['username']:
            if self.srun_host == "gw.buaa.edu.cn":
                self.config['username'] = username.lower()
            else:
                self.config['username'] = username
            self.pass_correct=False
        if password != "" and password != self.config['password']:
            self.config['password'] = password
            self.pass_correct=False
        save_config(self.config,self.aes_key)
        self.refresh_config()

    def set_start_with_windows(self, start_with_windows):
        self.config['start_with_windows'] = start_with_windows
        save_config(self.config,self.aes_key)
        self.refresh_config()

    def set_auto_login(self, auto_login):
        if auto_login and not self.auto_login and not self.pass_correct:
            return False
        else:
            self.config['auto_login'] = auto_login
            save_config(self.config,self.aes_key)
            self.refresh_config()
            return True

    def set_active_client_ip(self, ip):
        target = ip if ip not in (None, "", "null") else None
        if target not in self.srun_clients:
            return False
        self.active_ip = target
        self.config['active_ip'] = target
        save_config(self.config,self.aes_key)
        self.srun = self.get_client()
        return True

    def get_config(self):
        return (
            self.username,
            self.password != "",
            self.auto_login,
            self.start_with_windows,
            self.isUptoDate,
            self.hasDoneUpdate,
            self.srun_host if self.srun_host != "" else self.host_ip,
            self.self_service,
            self.active_ip,
            self.local_ips,
        )

    def get_ip_settings(self):
        return {
            "available": get_local_ipv4_addresses(),
            "selected": self.local_ips,
            "active": self.active_ip,
            "gateway": self.srun_host if self.srun_host != "" else self.host_ip,
            "self_service": self.self_service,
        }

    def update_ip_settings(self, settings):
        gateway = settings.get('gateway', self.srun_host if self.srun_host != "" else self.host_ip)
        self_service = settings.get('self_service', self.self_service)
        selected = settings.get('selected')
        active = settings.get('active')
        return self.set_srun_host(gateway, self_service, selected, active)
    
    def do_update(self,open=False):
        if open:
            webbrowser.open("https://github.com/HofNature/SRunPy-GUI/releases/latest")
        self.hasDoneUpdate = True

    def start_self_service(self, ip=None):
        client = self.get_client(ip)
        if client is None:
            webbrowser.open(f"http://{self.self_service}")
            return
        is_available, is_online, data = client.is_connected()
        if is_online:
            if "user_name" in data:
                username = data["user_name"]
            else:
                username = self.username
            data = base64.standard_b64encode(f"{username}:{username}".encode()).decode()
            webbrowser.open(f"http://{self.self_service}/site/sso?data={data}")
        else:
            webbrowser.open(f"http://{self.self_service}")

    def set_srun_host(self, srun_host, self_service, selected_ips=None, active_ip=None):
        if not self._update_gateway_only(srun_host, self_service):
            return False
        self._update_local_ip_selection(selected_ips, active_ip)
        save_config(self.config,self.aes_key)
        self.refresh_config()
        return True
    
    def auto_login_deamon(self):
        login_failed_count = 0
        while self.auto_login:
            client = self.get_client()
            if client is None:
                time.sleep(self.sleeptime)
                continue
            try:
                is_available, is_online, _ = client.is_connected()
            except:
                is_available, is_online = False, False
            if is_available and not is_online:
                try:
                    if self.login():
                        sysToaster.show_toast(
                            "校园网登陆器", "自动登陆成功", duration=5, threaded=True)
                        login_failed_count = 0
                    else:
                        sysToaster.show_toast(
                            "校园网登陆器", "自动登陆失败", duration=5, threaded=True)
                        login_failed_count += 1
                except:
                    sysToaster.show_toast(
                        "校园网登陆器", "自动登陆失败", duration=5, threaded=True)
                    login_failed_count += 1
            if self.auto_login:
                time.sleep(self.sleeptime)
                if login_failed_count > 3:
                    sysToaster.show_toast(
                        "校园网登陆器", "自动登陆失败次数过多，请检查账号密码", duration=180, threaded=True)
                    time.sleep(60*(login_failed_count-3))
            else:
                break

    def login(self, ip=None):
        client = self.get_client(ip)
        if client is None:
            return False
        try:
            success = client.login(self.username, self.password)
        except:
            success = False
        if success and not self.pass_correct:
            self.config['pass_correct'] = True
            save_config(self.config,self.aes_key)
            self.refresh_config()
        return success

    def logout(self, ip=None):
        client = self.get_client(ip)
        if client is None:
            return False
        try:
            return client.logout()
        except:
            return False

    def get_online_data(self, ip=None, hope=None):
        client = self.get_client(ip)
        if client is None:
            return False, False, {}
        try:
            for _ in range(5):
                is_available, is_online, data = client.is_connected()
                if hope is None or is_online == hope:
                    break
                time.sleep(0.2)
            return is_available, is_online, data
        except:
            return False, False, {}


class MainWindow():
    def __init__(self, srunpy, open_window=True):
        self.srunpy = srunpy
        self.window = None
        if self.srunpy.qt_backend:
            self.icon_path = os.path.join(WebRoot, r'icons\logo.png')
        if open_window:
            self.start_webview()

    def start_webview(self):
        if len(webview.windows) > 0:
            print('window exists')
            return
        localization = {
            'global.quitConfirmation': u'确定关闭?',
        }
        self.window = webview.create_window(
            "校园网登陆器", os.path.join(WebRoot, "index.html"), width=400, height=300, resizable=False)
        self.window.expose(
            self.srunpy.get_online_data,
            self.srunpy.login,
            self.srunpy.logout,
            self.srunpy.set_config,
            self.srunpy.get_config,
            webbrowser_open,
            exit_application,
            self.srunpy.set_start_with_windows,
            self.srunpy.set_auto_login,
            self.srunpy.do_update,
            self.srunpy.start_self_service,
            self.srunpy.set_srun_host,
            self.srunpy.get_ip_settings,
            self.srunpy.update_ip_settings,
            self.srunpy.set_active_client_ip,
        )
        def after_window_created():
            if platform.system() == "Windows":
                # Ensure process is DPI aware so we can get the real DPI
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

                # wait briefly for the window to appear and get its HWND by title
                hwnd = None
                random_title = uuid.uuid4().hex
                self.window.set_title(random_title)
                for _ in range(20):
                    hwnd = win32gui.FindWindow(None, random_title)
                    if hwnd:
                        break
                    time.sleep(0.05)
                self.window.set_title("校园网登陆器")
                if hwnd:
                    # get DPI for the window (fall back to screen DPI)
                    try:
                        user32 = ctypes.windll.user32
                        get_dpi = getattr(user32, "GetDpiForWindow", None)
                        if get_dpi:
                            dpi = get_dpi(hwnd)
                        else:
                            # fallback: get device DPI
                            gdi32 = ctypes.windll.gdi32
                            hdc = user32.GetDC(0)
                            LOGPIXELSX = 88
                            dpi = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
                            user32.ReleaseDC(0, hdc)
                    except Exception:
                        dpi = 96

                    scale = float(dpi) / 96.0

                    # original logical size used when creating the window
                    logical_w, logical_h = 400, 300
                    new_w = int(logical_w * scale)
                    new_h = int(logical_h * scale)

                    # keep current position, only resize
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    win32gui.SetWindowPos(hwnd, None, left, top, new_w, new_h, win32con.SWP_NOZORDER)
                    
            self.window.evaluate_js('updateInfo()')
        if self.srunpy.qt_backend:
            webview.start(after_window_created, localization=localization, debug=False, gui='qt', icon=self.icon_path)
        else:
            webview.start(after_window_created, localization=localization, debug=True)
