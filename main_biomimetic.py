 
# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu @ 20231230
# Modified @20231231

# Based on https://cloud.tencent.com/developer/article/2192324

import sys,ctypes
import time
# import tkinter as tk
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
import threading,multiprocessing

from ttkbootstrap import Style
import ttkbootstrap as ttk

class exprimentGUI(object):

    def __init__(self, root_window, width=[], height=[]):
        self.root_window = root_window
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_width()

        if width==[]:    
            self.width = int(screen_width * 1)
            self.height = int(screen_height * 0.8)

        self.root_window.geometry( str(self.width)+'x'+str(self.height) )  # 设置窗口大小 

        """ 点击右上角关闭窗体弹窗事件 """
        # self.root_window.protocol('WM_DELETE_WINDOW', lambda: self.thread_it(self.clos_window))
        
        """ 组件容器创建 """
        
        self.nav_bar_weidth = 120
        self.frame_nav_bar = ttk.Frame(self.root_window,) 

        self.frame_nav_bar.place(relx=0,rely=0,relheight=1,width=self.nav_bar_weidth)

        margin_page_H = 0.02
        self.frame_page = ttk.Frame(self.root_window) 
        self.frame_page.place( x = self.nav_bar_weidth ,rely = margin_page_H,
                              relheight = 1-2*margin_page_H, width=screen_width-self.nav_bar_weidth)
        # self.page_frame.place(x=self.nav_bar_weidth,rely=0,relheight=1,width=window_width-self.nav_bar_weidth)

        # self.thread_it(self.page_1(container_window=self.page_frame))
        self.thread_it(self.page_scale_contoller(container_window=self.frame_page))

    def page_1(self,container_window):
        
        log_frame = tk.Frame(container_window,background="#FF00FF")  
        log_frame.place(relx=0,rely=0,relheight=0.4,relwidth=1)
        
        scale1 = tk.Scale(container_window,label="sc1",
                               length=600,width=60,orient=tk.VERTICAL,
                               from_=0,to=100,resolution=0.5,digits=4,
                               command=self.run_log_print)         
        scale1.place(relx=1,rely=0,relheight=1,relwidth=0.2)

        """ 日志框 """
        run_log = ScrolledText(log_frame, font=('Calibri Light', 20), width=49, height=17)
        run_log.place(relx=0.02,rely=0.02,relheight=0.96,relwidth=0.96)

        runs_button_frame = tk.Frame(container_window) 
        runs_button_frame.place(relx=0,rely=0.4,relheight=0.2,relwidth=0.4)

        """ 操作按钮 """
        butten_1 = tk.Button(runs_button_frame, text='Print', font=('Calibri Light', 20,'bold'), 
                                    fg="white", bg="#1E90FF", width=20,height=1,
                                      command=lambda: self.thread_it(self.print1))
        butten_1.place(relx=0,rely=0,relheight=1,relwidth=0.5)

        butten_2 = tk.Button(runs_button_frame, text='Print', font=('Calibri Light', 20, 'bold'), 
                                    fg="white", bg="#1E90FF", width=25,
                                      command=lambda: self.thread_it(self.print2))
        butten_2.place(relx=0.5,rely=0,relheight=1,relwidth=0.5)

        
        pass
    
    def page_scale_contoller(self,container_window):
        
        log_frame_width = 0.20
        Frame_log = ttk.Frame(container_window)   
        Frame_log.place(relx=0,rely=0,relheight=1,relwidth=log_frame_width)

        frame_scale_butten = ttk.Frame(container_window)   
        margin_scale_butten_W = 0.01
        frame_scale_butten.place(relx = log_frame_width+margin_scale_butten_W,
                                 rely=0,relheight=1,relwidth = 1-log_frame_width-margin_scale_butten_W )

        # Frame scale
        scale_height = 0.8
        frame_scale = ttk.Frame(frame_scale_butten)   
        frame_scale.place(relx=0,rely=0,relheight=scale_height,relwidth=1)


        """ 日志框 """
        margin_log_box = 0.0
        from ttkbootstrap.scrolled import ScrolledText

        self.run_log = ScrolledText (Frame_log,width=49, height=17, autohide=True)
        # self.run_log = ttk.ScrolledText(Frame_log,font=('Calibri Light',20), width=49, height=17,
        #                           highlightthickness=1 )
        self.run_log.place(relx=margin_log_box,rely=margin_log_box,
                           relheight=1-2*margin_log_box,relwidth=1-2*margin_log_box)


        # Scales
        num_scale = 8
        scales = []
        margin_scale_W = margin_scale_butten_W
        margin_scale_H = 0
        a = 1
        self.run_log_print(str(frame_scale.winfo_vrootwidth()))
        # scales_colors = ["#%02x%02x%02x"%(25,255-int((_+1)*255/(num_scale+10)),255) for _ in range(num_scale)]  
        # self.run_log_print(str(scales_colors))

        for _i in range(num_scale):
            self.run_log_print(str(_i))

            scales.append( ttk.Scale(frame_scale,length=200,value=0,orient=ttk.VERTICAL, 
                                     from_=4095,to=0,command=self.run_log_print,variable = a )      )
             
            scales[-1].place(relx = _i/(num_scale), rely = margin_scale_H,
                         relheight=1-2*margin_scale_H, relwidth = 1/(num_scale)-margin_scale_W)
            


        # Frame Butten
        frame_button = ttk.Frame(frame_scale_butten) 
        frame_button.place( relx = 0, rely = scale_height+margin_scale_butten_W,
                           
                    relheight = 1-scale_height-margin_scale_butten_W,relwidth=0.4)

        butten_1 = ttk.Button(frame_button, text='Stop ALL', 
                                    width=20,
                                      command=lambda: self.thread_it(self.print1))
        butten_1.place(relx=0,rely=0,relheight=1,relwidth=0.5)

        butten_2 = ttk.Button(frame_button, text='Print',  
                                     width=25,
                                      command=lambda: self.thread_it(self.print2))
        butten_2.place(relx=0.5,rely=0,relheight=1,relwidth=0.5)

        
        pass

    def thread_it(self, func, *args):
        """ 将函数打包进线程 """
        self.myThread = threading.Thread(target=func, args=args)
        self.myThread .setDaemon(True)  # 主线程退出就直接让子线程跟随退出,不论是否运行完成。
        self.myThread .start()

    def print1(self):
        i = 0
        start_t = time.time()# time.process_time()

        for i in range(201):
            # i += 1
            tip_content = f'第{i}次打印'
            self.run_log_print(message=tip_content)
            if i%100 == 99: 
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
        self.run_log.insert(ttk.END, message+'\n')
        pass     

    def clos_window(self):
        ans = askyesno(title='Exit', message='Exit?', )
        if ans:
            self.root_window.destroy()
            sys.exit()
        else:
            return None


if __name__ == '__main__':


    # ctypes.windll.shcore.SetProcessDpiAwareness(1) #调用api设置成由应用程序缩放
    # ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0) #调用api获得当前的缩放因子
    # root.tk.call('tk', 'scaling', ScaleFactor/100)    #设置缩放因子


    root = ttk.Window(hdpi=False,scaling=2.5)#tk.Tk()# style.master # tk.Tk()

    style = Style(theme='darkly') # darkly sandstone sandstone
    root = style.master
    root.title("Contorl SMA")  # 设置窗口标题

    



    # """ tk界面置顶 """
    # root.attributes("-topmost", 1)

    """ 创建Gui类对象 """
    test_gui = exprimentGUI(root)
    
    """ 初始化GUi组件 """
    root.mainloop()

     