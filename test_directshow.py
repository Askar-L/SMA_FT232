import cv2
import time
import threading
from collections import deque
import concurrent.futures

class AsyncVideoSaver:
    def __init__(self, filename, fourcc, fps, frame_size):
        self.filename = filename
        self.fourcc = fourcc
        self.fps = fps
        self.frame_size = frame_size
        self.frame_queue = deque()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=32)
        self.out = cv2.VideoWriter(self.filename, self.fourcc, self.fps, self.frame_size)

    def save_frame_batch(self, frames):
        for frame in frames:
            self.out.write(frame)

    def add_frame(self, frame):
        self.frame_queue.append(frame)
        if len(self.frame_queue) >= 10:
            frames_to_save = list(self.frame_queue)
            self.frame_queue.clear()
            self.executor.submit(self.save_frame_batch, frames_to_save)

    def finalize(self):
        if self.frame_queue:
            self.save_frame_batch(list(self.frame_queue))
        self.executor.shutdown(wait=True)
        self.out.release()


def main():
    # 使用OpenCV通过DirectShow捕获视频
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # 使用DirectShow接口
    target_fps = 90
    cap.set(cv2.CAP_PROP_FPS, target_fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 20)  # 设置缓冲区大小

    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Target FPS: {target_fps}, Actual FPS: {actual_fps}")
    resolution = (1280,720)#q(800,600)# (800,600)#(1920,1200) (1280,720)#
    width, height = resolution

    cap.set(3, resolution[0]) 
    cap.set(4, resolution[1])
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    filename = "./img/video/"+time.strftime("%Y%m%d-%H%M%S") + '.avi'
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    saver = AsyncVideoSaver(filename, fourcc, target_fps, frame_size)

    frame_times = deque(maxlen=30)
    previous_time = time.time()
    fps_display_interval = 1
    fps_last_display_time = time.time()
    fps = 0
    frame_count = 0


    # 配置外部触发模式，假设相机SDK提供了类似的接口
    # 假设使用相机的DirectShow属性设置触发模式和源
    cap.set(cv2.CAP_PROP_TRIGGER, 1)  # 启用外部触发
    # cap.set(cv2.CAP_PROP_TRIGGER_SOURCE, 0)  # 设置触发源，假设为0表示外部触发


    while True:
        if True:
            current_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            frame_times.append(current_time)
            frame_count += 1
            if len(frame_times) > 1:
                fps = len(frame_times) / (frame_times[-1] - frame_times[0])

            if current_time - fps_last_display_time >= fps_display_interval:
                fps_last_display_time = current_time
                fps_text = f'FPS: {int(fps)}'
            else:
                fps_text = "None"

            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            if frame_count % int(actual_fps // 20) == 0:
                cv2.imshow('frame', frame)

            saver.add_frame(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    saver.finalize()

if __name__ == "__main__":
    main()
