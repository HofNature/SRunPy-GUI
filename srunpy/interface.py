#!/usr/bin/python3

from srunpy import SrunClient, PROGRAM_VERSION, WebRoot

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
        except Exception as e:
            print(str(e))
            reset_config()
            self.refresh_config()
            return
        if self.srun_host == "":
            self.srun = SrunClient(self.host_ip, self.host_ip)
        else:
            self.srun = SrunClient(self.srun_host, self.host_ip)
        if self.start_with_windows:
            create_lnk(qt_backend=self.qt_backend)
        else:
            delete_lnk()
        if self.auto_login:
            if self.auto_login_thread is None or not self.auto_login_thread.is_alive():
                self.auto_login_thread = threading.Thread(
                    target=self.auto_login_deamon)
                self.auto_login_thread.start()

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

    def get_config(self):
        return self.username, self.password != "", self.auto_login, self.start_with_windows, self.isUptoDate, self.hasDoneUpdate, self.srun_host if self.srun_host != "" else self.host_ip, self.self_service
    
    def do_update(self,open=False):
        if open:
            webbrowser.open("https://github.com/HofNature/SRunPy-GUI/releases/latest")
        self.hasDoneUpdate = True

    def start_self_service(self):
        is_available, is_online, data = self.srun.is_connected()
        if is_online:
            if "user_name" in data:
                username = data["user_name"]
            else:
                username = self.username
            data = base64.standard_b64encode(f"{username}:{username}".encode()).decode()
            webbrowser.open(f"http://{self.self_service}/site/sso?data={data}")
        else:
            webbrowser.open(f"http://{self.self_service}")

    def set_srun_host(self, srun_host, self_service):
        # 判断地址是域名还是ip
        domain, ip = is_domain(srun_host)
        if domain:
            self.config['srun_host'] = srun_host
            self.config['host_ip'] = ip
        elif is_ip_address(srun_host):
            self.config['srun_host'] = ""
            self.config['host_ip'] = srun_host
        else:
            return False
        self.config['self_service'] = self_service
        save_config(self.config,self.aes_key)
        self.refresh_config()
        del self.srun
        if self.srun_host == "":
            self.srun = SrunClient(self.host_ip, self.host_ip)
        else:
            self.srun = SrunClient(self.srun_host, self.host_ip)
        return True
    
    def auto_login_deamon(self):
        login_failed_count = 0
        while self.auto_login:
            try:
                is_available, is_online, _ = self.srun.is_connected()
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

    def login(self):
        try:
            success = self.srun.login(self.username, self.password)
        except:
            success = False
        if success and not self.pass_correct:
            self.config['pass_correct'] = True
            save_config(self.config,self.aes_key)
            self.refresh_config()
        return success

    def logout(self):
        try:
            return self.srun.logout()
        except:
            return False

    def get_online_data(self,hope=None):
        try:
            for i in range(5):
                is_available, is_online, data = self.srun.is_connected()
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
        self.window.expose(self.srunpy.get_online_data, self.srunpy.login, self.srunpy.logout, self.srunpy.set_config,
                           self.srunpy.get_config, webbrowser_open, exit_application, self.srunpy.set_start_with_windows, self.srunpy.set_auto_login, self.srunpy.do_update,self.srunpy.start_self_service,self.srunpy.set_srun_host)
        if self.srunpy.qt_backend:
            webview.start(lambda: self.window.evaluate_js(
                'updateInfo()'), localization=localization, debug=False, gui='qt', icon=self.icon_path)
        else:
            webview.start(lambda: self.window.evaluate_js(
                'updateInfo()'), localization=localization, debug=False)
