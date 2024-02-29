#!/usr/bin/python3

import os
import clr
import time
import json
import tkinter
import pystray
from PIL import Image

from System.Threading import Thread,ApartmentState,ThreadStart  
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
 

from srun_py import Srun_Py

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Threading')

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
    def __init__(self, callback=None):
        self.menu = pystray.Menu(
            pystray.MenuItem("打开主界面", callback, default=True),
            pystray.MenuItem("退出登陆器", self.exit)
        )
        self.icon = pystray.Icon("SRunPy", Image.open(
            r'html\icons\journey_white.png'), "校园网登陆器", self.menu)
        self.icon.run()

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

    def start_webview(self, on_loaded=None):
        if self.window is not None:
            return
        
        if not have_runtime():#没有webview2 runtime
            install_runtime()
        
        def create_window():
            def close_window():
                self.window.destroy()
                self.window = None
            self.window = tkinter.Tk()
            self.window.title("校园网登陆器")
            self.window.geometry("800x600")
            self.window.iconbitmap(r'html\icons\journey.ico')
            self.window.protocol("WM_DELETE_WINDOW", close_window)
            frame=WebView2(self.window,500,500)
            frame.pack(side='left',padx=0,pady=0,fill='both',expand=True)
            frame.load_url(os.path.abspath(r'html\index.html'))
            self.window.mainloop()
            
        t = Thread(ThreadStart(create_window))
        t.ApartmentState = ApartmentState.STA
        t.Start()



if __name__ == "__main__":
    config = load_config()
    srunpy = SRunClient()
    main_window = MainWindow(srunpy)
    icon = TaskbarIcon(lambda: main_window.start_webview())
    while True:
        time.sleep(config['sleeptime'])
