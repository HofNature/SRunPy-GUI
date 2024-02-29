import clr
from tkinter import Tk
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Threading')
from System.Windows.Forms import Control
from System.Threading import Thread,ApartmentState,ThreadStart    

#范例
def main():
    if not have_runtime():#没有webview2 runtime
        install_runtime()
    root=Tk()
    root.title('pywebview for tkinter test')
    root.geometry('1200x600+5+5')

    frame2=WebView2(root,500,500)
    frame2.pack(side='left',padx=1,pady=1,fill='both',expand=True)
    frame2.load_url('https://smart-space.com.cn/')

    root.mainloop()

if __name__ == "__main__":
    t = Thread(ThreadStart(main))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Join()