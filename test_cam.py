# Debugged @ 20240711
# Created by Askar.Liu

import cv2
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from lib.GENERALFUNCTIONS import *
import tkinter as tk
import threading,multiprocessing

class exprimentGUI():

    def __init__(self, root,process_share_dict={}, width=[], height=[]):
        super().__init__()
        self.root_window = root
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_width()
        self.process_share_dict = process_share_dict

        if width==[]:    
            self.width = int(screen_width * 0.6)
            self.height = int(screen_height * 0.6)

        self.root_window.geometry( str(self.width)+'x'+str(self.height) )  # 设置窗口大小 
        
        """ 组件容器创建 """
        self.nav_bar_width = 0.04
        self.frame_nav_bar = ttk.Frame(self.root_window,bootstyle="primary") 

        self.frame_nav_bar.place(relx=0,rely=0,relheight=1,relwidth=self.nav_bar_width)

        margin_page_H = 0.01
        self.frame_page = ttk.Frame(self.root_window,) 
        self.frame_page.place( relx = self.nav_bar_width ,rely = margin_page_H,
                              relheight = 1-2*margin_page_H, relwidth=1-self.nav_bar_width)
        # self.page_frame.place(x=self.nav_bar_weidth,rely=0,relheight=1,width=window_width-self.nav_bar_weidth)
        
        cam_num =  1
        self.cap = cv2.VideoCapture(cam_num,cv2.CAP_DSHOW)  #cv2.CAP_DSHOW  CAP_WINRT


        # Declare the width and height in variables
         
        width, height =  1280,720# 1280, 720 # 
        # Set the width and height 
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) 
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        ## Create CAM obj

        cam_name = 'AR0234' # 'OV7251' #  
        if cam_name == 'AR0234': # Aptina AR0234
            fps = 90
            resolution = (1920,1080)# (800,600)#(1920,1200)

        elif cam_name == 'OV7251': # Grayscale
            fps = 120
            resolution = (640,480)
            self.cap.set(cv2.CAP_PROP_CONVERT_RGB,0)

        self.cap.set(3, resolution[0]) 
        self.cap.set(4, resolution[1])
        # Set FPS
        self.cap.set(cv2.CAP_PROP_FPS,fps)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
         
        # image = self.process_share_dict['photo']
        image = cv2.imread(IMG_FOLDER+'1.jpg')
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        self.st_image = image
        photo = ImageTk.PhotoImage(image)  

        self.video_label_0 = tk.Label(self.root_window) #  
        # self.video_label_0.place(relheight=1,relwidth=1)#.pack(expand = "yes")# 
        self.video_label_0.pack(expand=True)

        self.video_label_0.configure(image=photo)
        self.video_label_0.image = photo 

        self.variable_fps = ttk.DoubleVar()
        self.entry_fps = ttk.Entry(textvariable= self.variable_fps,bootstyle='info')    
        # self.entry_fps.configure(state='readonly')
        self.entry_fps.place(relx=0,rely=0,relheight=0.1,relwidth=0.1)#.pack(expand = "yes")# 

        # Save video
        fourcc = 'MJPG' # 'I420'
        video_file_name = 'IMG/video/' +cam_name +'_' +str(time.time()) + '.avi'

        fourcc =  cv2.VideoWriter_fourcc(*fourcc)# XVID I420 3IVD
        self.video_file = cv2.VideoWriter(video_file_name,fourcc,fps,resolution)
        print("Saving Video file:",video_file_name," in ")

        self.thread_it(self.refresh_img)
        self.frame_id = 0
        self.time_cv_st = time.perf_counter()
 

    def refresh_img(self):
        ret, frame_BGR = self.cap.read()
        ret = True

        # frame = self.st_image
        if ret:
            # print(image.shape)
            self.video_file.write(frame_BGR)
            
            # Convert the frame to PIL format
            frame = cv2.cvtColor(frame_BGR, cv2.COLOR_BGR2RGB)

            frame = Image.fromarray(frame)

            # Resize the image to fit the label
            # frame = frame.resize((640, 360)) #640, 360 1280,720
            pass
        
        try:
            # image = self.process_share_dict['photo']
            frame = ImageTk.PhotoImage(frame)  
            self.video_label_0.configure(image=frame)
            self.video_label_0.image = frame    
            self.frame_id += 1

            if self.frame_id>300:
                self.variable_fps.set( (self.frame_id-60) / (time.perf_counter()-self.time_cv_st) )
            else :
                self.variable_fps.set( -1 )
            self.root_window.after(1,self.refresh_img)


        except Exception as err:
            print('Video frame load from thread manager failed:\n ')
            print('Err:',err)
            print('Tring again ... ...')
            self.root_window.after(1,self.refresh_img)

    def thread_it(self, func, *args):
        """ 将函数打包进线程 """
        self.myThread = threading.Thread(target=func, args=args)
        self.myThread.daemon = True
        self.myThread.start()

if __name__ == '__main__':

    print('Running on env: ',sys.version_info)
    root = ttk.Window(hdpi=True,scaling=3,themename='darkly')  # darkly sandstone sandstone
    # process_share_dict['root'] = root

    root.title("Test Cam image")  # 设置窗口标题
    root.geometry('+0+0')
    exprimentGUI(root)
    root.mainloop()