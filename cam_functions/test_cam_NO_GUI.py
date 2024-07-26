# Debugged @ 20240713
# Created by Askar.Liu
if __name__=='__main__': # Test codes # Main process
    import os,sys
    # import pyftdi.spi as spi
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0,parentdir)

    from lib.GENERALFUNCTIONS import *

import cv2
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from lib.GENERALFUNCTIONS import *
import tkinter as tk
from collections import deque
import concurrent.futures
 

class AsyncVideoSaver:
    def __init__(self, filename, fourcc, fps, frame_size):
        self.filename = filename
        self.fourcc =  fourcc  # XVID I420 3IVD
        self.fps = fps
        self.frame_size = frame_size
        self.maxlen = 30
        self.frame_queue = deque()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        self.out = cv2.VideoWriter(self.filename, cv2.VideoWriter_fourcc(*fourcc), self.fps, self.frame_size)

        print("Saving Video file:",video_file_name," in ")

    def save_frame_batch(self, frames):
        for frame in frames:
            # _frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            self.out.write(frame)

    def add_frame(self, frame):
        self.frame_queue.append(frame)
        
        if len(self.frame_queue) >= self.maxlen-2:  # 批量处理
            frames_to_save = list(self.frame_queue)
            self.frame_queue.clear()
            self.executor.submit(self.save_frame_batch, frames_to_save)

    def finalize(self):
        if self.frame_queue:
            self.save_frame_batch(list(self.frame_queue))
        self.executor.shutdown(wait=True)
        self.out.release()

if __name__ == "__main__":

    print('Running on env: ',sys.version_info)
    
    ## Create CAM obj
    cam_num =  2
    
    is_lighting = True
    is_recod_video = True    
    cam_name = 'AR0234' # 'OV7251' #  
    
    cap = cv2.VideoCapture(cam_num,cv2.CAP_DSHOW)  #cv2.CAP_DSHOW  CAP_WINRT
    if cam_name == 'AR0234': # Aptina AR0234
        target_fps = 90
        resolution =  (1600,1200)#(1920,1200)#q(800,600)# (800,600)#(1920,1200) (1280,720)#
        width, height = resolution

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0]) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        # Set FPS
        cap.set(cv2.CAP_PROP_FPS,target_fps)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # 'I420'
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # 设置缓冲区大小为2
        
        if is_lighting:            # 曝光控制
            # 设置曝光模式为手动
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # 0.25表示手动模式，0.75表示自动模式
            cap.set(cv2.CAP_PROP_GAIN, 0)  # 调整增益值，具体范围取决于摄像头
            cap.set(cv2.CAP_PROP_EXPOSURE, -11)  # 设置曝光值，负值通常表示较短的曝光时间
        else:            
            cap.set(cv2.CAP_PROP_GAIN, 0)  # 调整增益值，具体范围取决于摄像头
            cap.set(cv2.CAP_PROP_EXPOSURE, -3)  # 设置曝光值，负值通常表示较短的曝光时间
        # Save video
        fourcc = 'X264'#'MJPG' # 'I420' X264

    elif cam_name == 'OV7251': # Grayscale
        target_fps = 120
        resolution =  (640,480) # (640,480)
        width, height = resolution
        # cap.set(cv2.CAP_PROP_CONVERT_RGB,0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0]) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        # Set FPS
        cap.set(cv2.CAP_PROP_FPS,target_fps)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # 'I420'
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # 设置缓冲区大小为2
        
        # # 曝光控制
        cap.set(cv2.CAP_PROP_GAIN, -0.5)  # 调整增益值，具体范围取决于摄像头
        cap.set(cv2.CAP_PROP_EXPOSURE, -20)  # 设置曝光值，负值通常表示较短的曝光时间

        fourcc = 'MJPG' 

    elif cam_name == 'Oneplus':
       
        target_fps = 480
        resolution = (1280,720) #q(800,600)# (800,600)#(1920,1200) (1280,720)#
        width, height = resolution 
        cap = cv2.VideoCapture(2)
 
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0]) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        # Set FPS
        cap.set(cv2.CAP_PROP_FPS,target_fps)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # 'I420'
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # 设置缓冲区大小为2
        
        # 曝光控制
        cap.set(cv2.CAP_PROP_GAIN, 4)  # 调整增益值，具体范围取决于摄像头
        cap.set(cv2.CAP_PROP_EXPOSURE, -10)  # 设置曝光值，负值通常表示较短的曝光时间

        fourcc = 'X264'

        pass


    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Target FPS: {target_fps}, Actual FPS: {actual_fps}")
    if fourcc == 'MJPG':
        video_file_name = 'IMG/video/' +cam_name +'_' + time.strftime("%m%d-%H%M%S")  + '.avi'
    elif fourcc == 'X264':
        video_file_name = 'IMG/video/' +cam_name +'_' + time.strftime("%m%d-%H%M%S")  + '.mp4'
    elif fourcc == 'XVID':
        video_file_name = 'IMG/video/' +cam_name +'_' + time.strftime("%m%d-%H%M%S")  + '.avi'

    if is_recod_video: saver = AsyncVideoSaver(video_file_name, fourcc, target_fps, resolution)
    frame_id = 0
    time_cv_st = time.perf_counter()
    
    # 初始化时间戳队列
    frame_times = deque(maxlen=30)  # 保持最近30帧的时间戳
  
    # Video Loop
    while True:
        cur_time = time.perf_counter()
        ret, frame_raw = cap.read()

        if ret:
            if is_recod_video: saver.add_frame(frame_raw)
            # Convert the frame to PIL format
            # frame = cv2.cvtColor(frame_BGR, cv2.COLOR_BGR2RGB)
            # frame = Image.fromarray(frame)

            # Resize the image to fit the label
            # frame = frame.resize((640, 360)) #640, 360 1280,720
            pass
        else: continue
        frame_id += 1
        frame_times.append(cur_time)

        if True: #frame_id % int(actual_fps // 20) == 0:  # 每示两次
 
            if frame_id>30: cur_fps = len(frame_times) / (frame_times[-1] - frame_times[0])
            else : cur_fps = -1

            cv2.putText(frame_raw, f'Time: {time.strftime("%Y%m%d-%H%M%S")},{frame_times[-1] }', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame_raw, f'Current Frame {frame_id}; FPS: {int(cur_fps)}', (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('frame', frame_raw)  # 显示图像
            

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按'q'键退出
                break

 
cap.release()
cv2.destroyAllWindows()
if is_recod_video: saver.finalize()
