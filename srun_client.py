#!/usr/bin/python3

from srun_py import Srun_Py
import os
import sys
import time
import pickle
import webview
import pystray
import requests
import threading
import webbrowser
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from PIL import Image
import win32con
import win32api
import win32com.client as client
from win10toast import ToastNotifier

sysToaster = ToastNotifier()
PROGRAM_VERSION = (1, 0, 1, 0)

resource_path = os.path.dirname(os.path.abspath(__file__))
application_path = os.path.abspath(sys.argv[0])
python_path = os.path.abspath(sys.executable)
start_lnk_path = os.path.join(os.path.expandvars(
    r'%APPDATA%'), r'Microsoft\Windows\Start Menu\Programs\Startup', '校园网登陆器.lnk')


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

def load_config():
    aes = MyAES(key="dj26Dh47useoUI28")
    appdata = os.path.expandvars(r'%APPDATA%')
    config_path = os.path.join(appdata, 'SRunPy', 'config.bin')
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        config = {
            "username": "",
            "password": "",
            "srun_host": "gw.buaa.edu.cn",
            "sleeptime": 5,
            "auto_login": False,
            "start_with_windows": False
        }
        pickle.dump(config, open(config_path, 'wb'))
    else:
        config = pickle.load(open(config_path, 'rb'))
        if config['password'] != "":
            config['password'] = aes.decode_aes(config['password'])
    return config


def save_config(config):
    aes = MyAES(key="dj26Dh47useoUI28")
    appdata = os.path.expandvars(r'%APPDATA%')
    config_path = os.path.join(appdata, 'SRunPy', 'config.bin')
    config['password'] = aes.encode_aes(config['password'])
    pickle.dump(config, open(config_path, 'wb'))
    config['password'] = aes.decode_aes(config['password'])


def check_lnk():
    return os.path.exists(start_lnk_path)


def delete_lnk():
    if check_lnk():
        os.remove(start_lnk_path)


def create_lnk():
    delete_lnk()
    shell = client.Dispatch('Wscript.Shell')
    link = shell.CreateShortCut(start_lnk_path)
    if python_path == application_path:
        link.TargetPath = application_path
        link.Arguments = ' --no-auto-open'
        link.IconLocation = application_path+',0'
    else:
        link.TargetPath = python_path
        link.Arguments = '"'+application_path+'" --no-auto-open'
        link.IconLocation = os.path.join(
            resource_path, 'html/icons/journey.ico')+',0'

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
                icon_path = r'html\icons\journey_white.png'
            else:
                icon_path = r'html\icons\journey.png'
        except:
            icon_path = r'logo.png'
        self.icon = pystray.Icon("SRunPy", Image.open(
            os.path.join(resource_path, icon_path)), "校园网登陆器", self.menu)
        self.icon.run()

    def stop(self):
        self.icon.stop()

    def exit(self):
        self.icon.stop()
        os._exit(0)


class SRunClient():
    def __init__(self):
        self.auto_login_thread = None
        self.isUptoDate = False
        self.hasDoneUpdate = False
        def check_update():
            self.isUptoDate = get_Update()
        threading.Thread(target=check_update).start()
        self.refresh_config()

    def refresh_config(self):
        self.config = load_config()
        self.username = self.config['username']
        self.password = self.config['password']
        self.srun_host = self.config['srun_host']
        self.sleeptime = self.config['sleeptime']
        self.auto_login = self.config['auto_login']
        self.start_with_windows = self.config['start_with_windows']
        self.srun = Srun_Py(self.srun_host)
        if self.start_with_windows:
            create_lnk()
        else:
            delete_lnk()
        if self.auto_login:
            if self.auto_login_thread is None or not self.auto_login_thread.is_alive():
                self.auto_login_thread = threading.Thread(
                    target=self.auto_login_deamon)
                self.auto_login_thread.start()

    def set_config(self, username, password):
        if username != "":
            if self.srun_host == "gw.buaa.edu.cn":
                self.config['username'] = username.lower()
            else:
                self.config['username'] = username
        if password != "":
            self.config['password'] = password
        save_config(self.config)
        self.refresh_config()

    def set_start_with_windows(self, start_with_windows):
        self.config['start_with_windows'] = start_with_windows
        save_config(self.config)
        self.refresh_config()

    def set_auto_login(self, auto_login):
        self.config['auto_login'] = auto_login
        save_config(self.config)
        self.refresh_config()

    def get_config(self):
        return self.username, self.password != "", self.auto_login, self.start_with_windows, self.isUptoDate, self.hasDoneUpdate
    
    def do_update(self,open=False):
        if open:
            webbrowser.open("https://github.com/HofNature/SRunPy-GUI/releases/latest")
        self.hasDoneUpdate = True

    def auto_login_deamon(self):
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
                    else:
                        sysToaster.show_toast(
                            "校园网登陆器", "自动登陆失败", duration=5, threaded=True)
                except:
                    sysToaster.show_toast(
                        "校园网登陆器", "自动登陆失败", duration=5, threaded=True)
            if self.auto_login:
                time.sleep(self.sleeptime)
            else:
                break

    def login(self):
        try:
            return self.srun.login(self.username, self.password)
        except:
            return False

    def logout(self):
        try:
            return self.srun.logout()
        except:
            return False

    def get_online_data(self):
        try:
            return self.srun.is_connected()
        except:
            return False, False, {}


class MainWindow():
    def __init__(self, srunpy, open_window=True):
        self.srunpy = srunpy
        self.window = None
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
            "校园网登陆器", os.path.join(resource_path, "html/index.html"), width=400, height=300, resizable=False)
        self.window.expose(self.srunpy.get_online_data, self.srunpy.login, self.srunpy.logout, self.srunpy.set_config,
                           self.srunpy.get_config, webbrowser_open, exit_application, self.srunpy.set_start_with_windows, self.srunpy.set_auto_login, self.srunpy.do_update)
        webview.start(lambda: self.window.evaluate_js(
            'updateInfo()'), localization=localization, debug=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='校园网登陆器')
    parser.add_argument('--no-auto-open', action="store_true", help='不自动打开主界面')
    args = parser.parse_args()
    srunpy = SRunClient()
    main_window = MainWindow(srunpy, not args.no_auto_open)
    while True:
        TaskbarIcon()
        main_window.start_webview()
