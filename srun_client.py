#!/usr/bin/python3

import os
import time
import json
import webview
import pystray
from PIL import Image

from srun_py import Srun_Py


def load_config():
    appdata = os.path.expandvars(r'%APPDATA%')
    config_path = os.path.join(appdata, 'SRunPy', 'config.json')
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        config = {
            "username": "",
            "password": "",
            "srun_host": "gw.buaa.edu.cn",
            "sleeptime": 10
        }
        json.dump(config, open(config_path, 'w'), indent=4, ensure_ascii=True)
    else:
        config = json.load(open(config_path, 'r'))
    return config


def save_config(config):
    appdata = os.path.expandvars(r'%APPDATA%')
    config_path = os.path.join(appdata, 'SRunPy', 'config.json')
    json.dump(config, open(config_path, 'w'), indent=4, ensure_ascii=True)


class TaskbarIcon():
    def __init__(self):
        self.menu = pystray.Menu(
            pystray.MenuItem("打开主界面", self.stop, default=True),
            pystray.MenuItem("退出登陆器", self.exit)
        )
        self.icon = pystray.Icon("SRunPy", Image.open(
            r'html\icons\journey_white.png'), "校园网登陆器", self.menu)
        self.icon.run()

    def stop(self):
        self.icon.stop()

    def exit(self):
        self.icon.stop()
        os._exit(0)


class SRunClient():
    def __init__(self):
        self.refresh_config()

    def refresh_config(self):
        self.config = load_config()
        self.username = self.config['username']
        self.password = self.config['password']
        self.srun_host = self.config['srun_host']
        self.sleeptime = self.config['sleeptime']
        self.srun = Srun_Py(self.srun_host)
    
    def set_config(self, username, password):
        if self.srun_host == "gw.buaa.edu.cn":
            self.config['username'] = username.lower()
        else:
            self.config['username'] = username
        self.config['password'] = password
        save_config(self.config)
        self.refresh_config()

    def get_config(self):
        return self.username, self.password!=""
    
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
            "校园网登陆器", "html/index.html", width=400, height=300, resizable=False)
        self.window.expose(self.srunpy.get_online_data,self.srunpy.login,self.srunpy.logout,self.srunpy.set_config,self.srunpy.get_config)
        webview.start(lambda:self.window.evaluate_js('updateInfo()'), localization=localization, debug=True)


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
