# %load ../0_Hello/main.py
from kivy.app import App
from kivy.clock import Clock

from kivy.core.window import Window
from kivy.utils import get_color_from_hex

import time,kivy

class ClockApp(App):
    # 当运行main.py文件时，Kivy自动调用clock.kv。类名是ClockApp，.kv文件名就是clock，类名小写并去掉App。
    # def __init__(self, **kwargs):
    #     # super().__init__(**kwargs)
    #     pass

    def update_time(self, nap):
        cur_t = time.process_time()
        self.root.ids.time1.text = str( ( cur_t ))


    def on_start(self):
        Clock.schedule_interval(self.update_time, 0)

if __name__ == "__main__":

    Window.clearcolor = get_color_from_hex("#101216")

    # while True:
    #     cur_t = time.process_time()
    #     print(cur_t)

    ClockApp().run()
 