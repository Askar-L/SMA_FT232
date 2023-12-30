 
# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu @ 20231230
# Modified @20231231

# Based on https://cloud.tencent.com/developer/article/2192324

import sys,ctypes
import time
import tkinter as tk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
import threading,multiprocessing

from ttkbootstrap import Style


class exprimentGUI(object):

    def __init__(self, root_window, width=[], height=[]):
        self.root_window = root_window
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        if width==[]:    
            self.width = int(screen_width * 0.6)
            self.height = int(screen_height * 0.6)

        self.root_window.geometry( str(self.width)+'x'+str(self.height) )  # 设置窗口大小 1080x720

        """ 点击右上角关闭窗体弹窗事件 """
        self.root_window.protocol('WM_DELETE_WINDOW', lambda: self.thread_it(self.clos_window))

        """ 组件容器创建 """
        self.log_frame = tk.Frame(self.root_window)  # 创建存放日志组件的容器
        self.log_frame.grid(padx=20, pady=0, row=1, column=0, sticky=tk.W)
        self.runs_button_frame = tk.Frame(self.root_window)  # 创建存放日志组件的容器
        self.runs_button_frame.grid(padx=20, pady=0, row=2, column=0, sticky=tk.W)

        """ 日志框 """
        self.run_log = ScrolledText(self.log_frame, font=('等线', 10), width=69, height=17)
        self.run_log.grid(padx=20, pady=5, row=0, column=0)

        """ 操作按钮 """
        self.start_run1 = tk.Button(self.runs_button_frame, text='Print', font=('Calibri Light', 20,'bold'), 
                                    fg="white", bg="#1E90FF", width=25,
                                      command=lambda: self.thread_it(self.print1))
        self.start_run1.grid(padx=20, pady=0, row=0, column=1)

        self.start_run2 = tk.Button(self.runs_button_frame, text='Print', font=('Calibri Light', 20, 'bold'), 
                                    fg="white", bg="#1E90FF", width=25,
                                      command=lambda: self.thread_it(self.print2))
        self.start_run2.grid(padx=35, pady=0, row=0, column=2)

    def thread_it(self, func, *args):
        """ 将函数打包进线程 """
        self.myThread = threading.Thread(target=func, args=args)
        self.myThread .setDaemon(True)  # 主线程退出就直接让子线程跟随退出,不论是否运行完成。
        self.myThread .start()

    def print1(self):
        i = 0
        start_t = time.time()# time.process_time()

        for i in range(501):
            # i += 1
            tip_content = f'第{i}次打印'
            self.run_log_print(message=tip_content)
            if i%100 == 0: 
                currunt_t = time.time()# time.process_time()
                
                _massage = f'Freq: {i/(currunt_t - start_t)}'
                self.run_log_print(message= _massage)
    
        self.run_log_print(message='打印完成')

    def print2(self):
        for i in range(100, 200):
            tip_content = f'第{i}次打印2'
            self.run_log_print(message=tip_content)
            time.sleep(0.05)  # 睡眠
        self.run_log_print(message='打印完成')

    def run_log_print(self, message):
        self.run_log.config(state=tk.NORMAL)
        self.run_log.insert(tk.END, "\n" + message + "\n")
        self.run_log.see(tk.END)
        self.run_log.update()
        self.run_log.config(state=tk.DISABLED)

    def clos_window(self):
        ans = askyesno(title='Exit', message='Exit?', )
        if ans:
            self.root_window.destroy()
            sys.exit()
        else:
            return None


if __name__ == '__main__':
    """ 把button方法打包进线程 现实运行不卡顿 """

    """ 实例化出一个父窗口 """
    style = Style(theme='darkly')

    root = style.master # tk.Tk()

    #调用api设置成由应用程序缩放
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    #调用api获得当前的缩放因子
    ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
    #设置缩放因子
    root.tk.call('tk', 'scaling', ScaleFactor/75)

    root.title("Contorl SMA")  # 设置窗口标题

    # """ tk界面置顶 """
    # root.attributes("-topmost", 1)

    """ 创建Gui类对象 """
    test_gui = exprimentGUI(root)
    
    """ 初始化GUi组件 """
    root.mainloop()

     