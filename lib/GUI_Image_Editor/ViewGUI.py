# -*- coding: utf-8 -*-
import sys,os
import tkinter as tk
from tkinter import ttk, filedialog
from lib.GUI_Image_Editor.ControlGUI import ControlGUI

class ViewGUI():
    
    def __init__(self, window_root, default_path):
        self.window_root = window_root
        # Controller Class生成
        self.control = ControlGUI(default_path)
        
        # 初期化
        self.dir_path         = None
        self.save_dirpath     = {'[Photo]':'None', '[Video]':'None'}
        self.label_rotate     = [' 90°','180°','270°']
        self.label_flip       = ['U/D','L/R']
        self.speed_text       = ['x0.5','x1.0','x2.0','x4.0']
        # set callback for video playback status
        # update_timestamp or update_frameno
        self.update_playstat  = self.update_timestamp

        # サブウィンドウ
        self.window_sub_ctrl1     = tk.Frame(self.window_root, height=300, width=300)
        self.window_sub_ctrl2     = tk.Frame(self.window_root, height=500, width=400)
        
        # Nootebook, Tab生成
        self.window_sub_frame     = tk.Frame(self.window_root, height=590, width=540)
        self.notebook             = ttk.Notebook(self.window_sub_frame)
        self.tab1                 = tk.Frame(self.notebook, height=560, width=500)
        self.tab2                 = tk.Frame(self.notebook, height=560, width=500)
        self.notebook.add(self.tab1, text='[Photo]')
        self.notebook.add(self.tab2, text='[Video]')
        self.notebook.bind('<<NotebookTabChanged>>', self.event_tabchanged)
        #self.notebook.select(self.tab2)
        self.notebook.select(self.tab1)
        self.select_tab           = '[Photo]'
        #self.select_tab           = '[Video]'
        
        
        # Photo[tab1]
        self.window_sub_ctrl3     = tk.Frame(self.tab1,  height=120, width=400)
        self.window_photo_canvas  = tk.Canvas(self.tab1, height=450, width=400, bg='gray')
        # Video[tab2]
        self.window_sub_ctrl4     = tk.Frame(self.tab2,  height=120, width=400)
        self.window_video_canvas1 = tk.Canvas(self.tab2, height=192, width=454, bg='gray')
        self.window_video_canvas2 = tk.Canvas(self.tab2, height=192, width=454, bg='gray')
        self.window_sub_ctrl5     = tk.Frame(self.window_root, height=30, width=400)
        self.window_sub_ctrl6     = tk.Frame(self.window_root, height=60, width=400)
        
        # オブジェクト
        # StringVar(ストリング)生成
        self.str_dir        = tk.StringVar()
        # IntVar生成 
        self.radio_intvar = []
        for n in range(3):
            self.radio_intvar.append(tk.IntVar())
        self.bar_position   = tk.IntVar()
    
        
        # GUIウィジェット・イベント登録
        # ラベル
        label_s3_blk1       = tk.Label(self.window_sub_ctrl3, text='')
        label_s3_blk2       = tk.Label(self.window_sub_ctrl3, text='')
        label_target        = tk.Label(self.window_sub_ctrl1, text='[Files]')

        label_s2_blk1       = tk.Label(self.window_sub_ctrl2, text='')
        label_rotate        = tk.Label(self.window_sub_ctrl2, text='[Rotate]')
        label_flip          = tk.Label(self.window_sub_ctrl2, text='[Flip]')
        label_clip          = tk.Label(self.window_sub_ctrl2, text='[Clip]')
        label_run           = tk.Label(self.window_sub_ctrl2, text='[Final Edit]')

        # label_saveopt       = tk.Label(self.window_sub_ctrl5, text='[Save Option]')
        # label_s5_blk        = tk.Label(self.window_sub_ctrl5, text='')
        # label_ftype         = tk.Label(self.window_sub_ctrl5, text='[EXT]')
        
        label_imgsz         = tk.Label(self.window_sub_ctrl6, text='[H,W]')
        label_fps           = tk.Label(self.window_sub_ctrl6, text='[FPS]')

        # label_msg           = tk.Label(self.window_root,      text='[Message]')
        # self.label_msgtxt   = tk.Label(self.window_root,      text='')
        
        self.label_frame = []
        for n in range(2):
           self.label_frame.append(tk.Label(self.tab2, text=''))
        label_barunit = tk.Label(self.tab2, text='[%]')
        
        # フォルダ選択ボタン生成
        self.button_setdir  = tk.Button(self.window_sub_ctrl1,    text = 'Set Folder', width=10, command=self.event_set_folder) 
        #　テキストエントリ生成
        self.entry_dir      = tk.Entry(self.window_sub_ctrl1,     text = 'entry_dir',  state='readonly',  textvariable=self.str_dir, width=39)
        self.str_dir.set(self.dir_path)
        # コンボBOX生成
        self.combo_file     = ttk.Combobox(self.window_sub_ctrl1, text = 'combo_file', value=[], state='readonly', width=36, postcommand=self.event_updatefile)
        self.combo_file.set('..[select file]')
        self.combo_file.bind('<<ComboboxSelected>>', self.event_selectfile)
        
        #　切替ボタン生成
        button_next         = tk.Button(self.window_sub_ctrl3, text = '>>Next',  width=10,command=self.event_next)
        button_prev         = tk.Button(self.window_sub_ctrl3, text = 'Prev<<',  width=10,command=self.event_prev)
        
        # # クリップボタン生成
        # button_clip_start   = tk.Button(self.window_sub_ctrl2, text = 'Try',     width=5, command=self.event_clip_try)
        # button_clip_done    = tk.Button(self.window_sub_ctrl2, text = 'Done',    width=5, command=self.event_clip_done)
        
        # # Save/Undo/Dropボタン生成
        # button_save         = tk.Button(self.window_sub_ctrl2, text = 'Save',    width=5, command=self.event_save)
        # button_undo         = tk.Button(self.window_sub_ctrl2, text = 'Undo',    width=5, command=self.event_undo)
        # self.button_drop    = tk.Button(self.window_sub_ctrl2, text = 'Drop',    width=5, command=self.event_drop)

        # ラジオボタン生成
        self.ftype      = ['mp4','gif']
        self.rate_resz  = ['1/1','1/2','1/4']
        self.rate_fps   = ['1/1','1/4','1/8']
        radio_ftype = []
        for val, text in enumerate(self.ftype):
            radio_ftype.append(tk.Radiobutton(self.window_sub_ctrl5, text=text, 
                                              value=val, variable=self.radio_intvar[0], command=self.event_ftype))
        self.radio_intvar[0].set(0)   # 0: mp4, 1: gif
        
        radio_imgsz = []
        for val, text in enumerate(self.rate_resz):
            radio_imgsz.append(tk.Radiobutton(self.window_sub_ctrl6, text=text,
                                               value=val, variable=self.radio_intvar[1]))
        self.radio_intvar[1].set(0)   # 0: 1/1, 1: 1/2, 2: 1/4
        
        radio_fps = []
        for val, text in enumerate(self.rate_fps):
            radio_fps.append(tk.Radiobutton(self.window_sub_ctrl6, text=text,
                                             value=val, variable=self.radio_intvar[2]))
        self.radio_intvar[2].set(0)   # 0: 1/2, 1: 1/4, 2: 1/8

        # Video 
        # Slide bar(Scale)
        self.bar_scale      = tk.Scale(self.tab2, from_=0, to_=100, orient='horizontal', resolution=1.0,
                                   variable=self.bar_position, length=400, command=self.event_update_bar)
        self.bar_position.set(0)
        
        # Play/Stop/Stepボタン生成
        self.button_play    = tk.Button(self.window_sub_ctrl4, text = 'Play',    width=7, command=self.event_play)
        self.button_step    = tk.Button(self.window_sub_ctrl4, text = 'Step',    width=7, command=self.event_step)
        self.button_capture = tk.Button(self.window_sub_ctrl4, text = 'Capture', width=7, command=self.event_capture)
        self.button_speed   = tk.Button(self.window_sub_ctrl4, text = self.speed_text[1], width=7, command=self.event_speed)
        
        
        # ボタン生成
        self.btn_rotate = []
        for idx, text in enumerate(self.label_rotate): # 1:rot90 2:rot180 3:rot270
            self.btn_rotate.append(tk.Button(self.window_sub_ctrl2, text=text, width=5, command=self.event_rotate(idx)))
            
        self.btn_flip = []
        for idx, text in enumerate(self.label_flip):   # 1:Flip U/L 2:Flip L/R
            self.btn_flip.append(tk.Button(self.window_sub_ctrl2,  text=text,  width=5, command=self.event_flip(idx)))
        
        # マウスイベント登録
        self.window_photo_canvas.bind   ('<ButtonPress-1>',   self.event_clip_start)
        self.window_photo_canvas.bind   ('<Button1-Motion>',  self.event_clip_keep)
        self.window_photo_canvas.bind   ('<ButtonRelease-1>', self.event_clip_end)
        
        self.window_video_canvas1.bind  ('<Double-Button-1>', self.event_mouse_select1)
        # self.window_video_canvas2.bind  ('<Double-Button-1>', self.event_mouse_select2)
        
        self.window_video_canvas1.bind  ('<ButtonPress-1>',   self.event_clip_start)
        self.window_video_canvas1.bind  ('<Button1-Motion>',  self.event_clip_keep)
        self.window_video_canvas1.bind  ('<ButtonRelease-1>', self.event_clip_end)
        # self.window_video_canvas2.bind  ('<ButtonPress-1>',   self.event_clip_start)
        # self.window_video_canvas2.bind  ('<Button1-Motion>',  self.event_clip_keep)
        # self.window_video_canvas2.bind  ('<ButtonRelease-1>', self.event_clip_end)
        
        
        ## ウィジェット配置
        # サブウィンドウ
        self.window_sub_ctrl1.place     (relx=0, rely=0.75) # file load
        self.window_sub_ctrl2.place     (relx=0.68, rely=0.25)
        self.window_sub_ctrl3.place     (relx=0.30, rely=0.90)
        self.window_sub_ctrl4.place     (relx=0.25, rely=0.93)
        self.window_sub_frame.place     (relx=0.01, rely=0.01)

        self.notebook.place             (relx=0, rely=0)
        # Photo[tab1]
        self.window_photo_canvas.place  (relx=0,  rely=0)
        # Video[tab2]
        self.window_video_canvas1.place (relx=0, rely=0)
        # self.window_video_canvas2.place (relx=0.042, rely=0.44)
        


        # window_sub_ctrl1
        self.button_setdir.grid  (row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.entry_dir.grid      (row=2, column=1, padx=5, pady=5, sticky=tk.W)
        label_target.grid        (row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.combo_file.grid     (row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # window_sub_ctrl2
        label_rotate.grid        (row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.btn_rotate[0].grid  (row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.btn_rotate[1].grid  (row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.btn_rotate[2].grid  (row=3, column=3, padx=5, pady=5, sticky=tk.W)
        
        label_flip.grid          (row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.btn_flip[0].grid    (row=5, column=1, padx=5, pady=5, sticky=tk.W)
        self.btn_flip[1].grid    (row=5, column=2, padx=5, pady=5, sticky=tk.W)

        # label_clip.grid          (row=6, column=1, padx=5, pady=5, sticky=tk.W)
        # button_clip_start.grid   (row=7, column=1, padx=5, pady=5, sticky=tk.W)
        # button_clip_done.grid    (row=7, column=2, padx=5, pady=5, sticky=tk.W)
        label_run.grid           (row=8, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        # button_undo.grid         (row=9, column=1, padx=5, pady=5, sticky=tk.W)
        # button_save.grid         (row=9, column=2, padx=5, pady=5, sticky=tk.W)
        
        # window_sub_ctrl3
        label_s3_blk1.grid       (row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        button_prev.grid         (row=1, column=1, padx=5, pady=5, sticky=tk.E)
        label_s3_blk2.grid       (row=1, column=4, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        button_next.grid         (row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # window_sub_ctrl5
        # label_saveopt.grid       (row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        # label_ftype.grid         (row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        radio_ftype[0].grid      (row=2, column=2, padx=5, pady=5, sticky=tk.EW)
        radio_ftype[1].grid      (row=2, column=3, padx=5, pady=5, sticky=tk.EW)
        # label_s5_blk.grid        (row=2, column=4, padx=5, pady=5, sticky=tk.EW)

        # # window_sub_ctrl6
        # label_imgsz.grid         (row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        # radio_imgsz[0].grid      (row=1, column=2, padx=5, pady=5, sticky=tk.EW)
        # radio_imgsz[1].grid      (row=1, column=3, padx=5, pady=5, sticky=tk.EW)
        # radio_imgsz[2].grid      (row=1, column=4, padx=5, pady=5, sticky=tk.EW)
        # label_fps.grid           (row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        # radio_fps  [0].grid      (row=2, column=2, padx=5, pady=5, sticky=tk.EW)
        # radio_fps  [1].grid      (row=2, column=3, padx=5, pady=5, sticky=tk.EW)
        # radio_fps  [2].grid      (row=2, column=4, padx=5, pady=5, sticky=tk.EW)

        # Video
        # Button
        self.button_play.grid    (row=1, column=1, padx=5, pady=5, sticky=tk.E)
        self.button_step.grid    (row=1, column=2, padx=5, pady=5, sticky=tk.E)
        self.button_capture.grid (row=1, column=3, padx=5, pady=5, sticky=tk.E)
        self.button_speed.grid   (row=1, column=4, padx=5, pady=5, sticky=tk.E)
        #
        self.label_frame[0].place(relx=0.44, rely=0.36)
        self.label_frame[1].place(relx=0.44, rely=0.79)
        label_barunit.place      (relx=0.90, rely=0.85)
        # label_msg.place          (relx=0.69, rely=0.90)
        # self.label_msgtxt.place  (relx=0.70, rely=0.94)
        # Slide bar(Scale)
        self.bar_scale.place     (relx=0.08, rely=0.85)
        
        # Init
        self.save_dirpath['[Photo]'] = default_path
        self.save_dirpath['[Video]'] = default_path
        canvas_dict = {'Photo':self.window_photo_canvas, 
                       'Video1':self.window_video_canvas1, 
                    #    'Video2':self.window_video_canvas2
                       }
        
        self.control.InitCanvas(canvas_dict)
        self.control.SetTab(self.select_tab)
        self.control.SetCanvas('Video1')
        self.control.InitStateMachine()
        self.button_speed['text'] = self.control.InitSpeed(self.speed_text)
        # self.sub_frame5_display()

    
    # # Private
    # def sub_frame5_display(self):
        
    #     if self.select_tab == '[Video]':
    #         self.window_sub_ctrl5.place(relx=0.68, rely=0.68)
    #         self.button_drop.grid(row=9, column=3, padx=5, pady=5, sticky=tk.W)
    #         # [EXT] option: 'gif' ot 'mp4'
    #         arg0 = self.ftype[self.radio_intvar[0].get()]
    #         if arg0 == 'gif':
    #             self.window_sub_ctrl6.place(relx=0.68, rely=0.78)
    #     else:
    #         self.window_sub_ctrl5.place_forget()
    #         self.window_sub_ctrl6.place_forget()
    #         self.button_drop.grid_forget()
    
            
    def get_save_args(self):        
        if self.select_tab == '[Video]':                        
            arg0 = self.ftype[self.radio_intvar[0].get()]
            arg1 = self.rate_resz[self.radio_intvar[1].get()]
            arg2 = self.rate_fps[self.radio_intvar[2].get()]
            args = [arg0,arg1,arg2]
        else: args = []
            
        return args
        
    def clear_message(self):
        # self.label_msgtxt['text'] = ''
        pass        
        
    def display_tab(self):
        self.notebook.tab(self.tab1, state='normal')
        self.notebook.tab(self.tab2, state='normal')
        
    def disable_tab(self):
        # Disable tab which is not selected
        tab = self.tab2 if self.select_tab == '[Photo]' else self.tab1
        self.notebook.tab(tab, state='disabled')
        

    # Event Callback
    # Common
    def event_tabchanged(self, event):
        
        notebook = event.widget
        self.select_tab = notebook.tab(notebook.select(), 'text')
        self.control.SetTab(self.select_tab)
        self.dir_path = self.save_dirpath[self.select_tab]
        self.str_dir.set(self.dir_path)

        self.event_updatefile()
        # self.sub_frame5_display()
        print('{}: {}'.format(sys._getframe().f_code.co_name, self.select_tab))
        
        self.event_selectfile(None)
        
    
    def event_set_folder(self):
        
        if self.control.IsTransferToState('dir'):
            print(sys._getframe().f_code.co_name)
            
            dir_path = self.save_dirpath[self.select_tab]
            self.dir_path = filedialog.askdirectory(initialdir=dir_path, mustexist=True)
            self.str_dir.set(self.dir_path)
            self.combo_file['value'] = self.control.SetFilelist(self.dir_path)
            
            file_name = self.control.GetCurrentFile()
            self.combo_file.set(file_name)
            self.save_dirpath[self.select_tab] = self.dir_path
            print(self.save_dirpath[self.select_tab])
            
            self.event_selectfile(None)

        
    def event_updatefile(self):
        
        if self.control.IsTransferToState('dir'):
            print(sys._getframe().f_code.co_name)
            self.combo_file['value'] = self.control.SetFilelist(self.dir_path)
            file_name = self.control.GetCurrentFile()
            self.combo_file.set(file_name)

        
    def event_selectfile(self, event):
        
        if self.control.IsTransferToState('set'):
            print(sys._getframe().f_code.co_name)
            self.display_tab()
            
            callbacks = None
            if self.select_tab == '[Video]':
                self.button_speed['text'] = self.control.InitSpeed(self.speed_text)
                callbacks = [self.update_playstat, self.update_savestat]
            
            set_pos = self.combo_file.current()
            result  = self.control.Set(set_pos, callbacks)
            if not result:
                self.control.ForceToState('IDLE')
                
            self.clear_message()

        
    def event_rotate(self, idx):

        def check_event():
            if self.control.IsTransferToState('edit'):
                self.disable_tab()
                cmd = 'rotate-' + str(idx+1)
                self.control.Edit(cmd)
                print('{} {} {}'.format(sys._getframe().f_code.co_name, idx, cmd))
                return check_event
            
        return check_event
        
    
    def event_flip(self, idx):
        
        def check_event():
            if self.control.IsTransferToState('edit'):
                self.disable_tab()
                cmd = 'flip-' + str(idx+1)
                self.control.Edit(cmd)
                print('{} {} {}'.format(sys._getframe().f_code.co_name, idx, cmd))
                return check_event
            
        return check_event
        
        
    def event_clip_try(self):
        
        if self.control.IsTransferToState('clip'):
            self.disable_tab()
            print(sys._getframe().f_code.co_name)
        
        
    def event_clip_done(self):
        
        if self.control.IsTransferToState('done'):
            print(sys._getframe().f_code.co_name)
            self.control.Edit('clip_done')
    
    
    def event_clip_start(self, event):
        
        if self.control.IsTransferToState('rect'):
            print(sys._getframe().f_code.co_name, event.x, event.y)
            self.control.DrawRectangle('clip_start', event.y, event.x)
    
        
    def event_clip_keep(self, event):
        
        if self.control.IsTransferToState('rect'):
            self.control.DrawRectangle('clip_keep', event.y, event.x)

        
    def event_clip_end(self, event):
        
        if self.control.IsTransferToState('rect'):
            print(sys._getframe().f_code.co_name, event.x, event.y)
            self.control.DrawRectangle('clip_end', event.y, event.x)
        
        
    def event_save(self):
        
        if self.control.IsTransferToState('save'):
            print(sys._getframe().f_code.co_name)
            
            if self.select_tab == '[Video]':
                self.disable_tab()
            else:
                self.display_tab()
            
            args = self.get_save_args()
            self.control.Save(args=args)

    
    def event_undo(self):
        
        if self.control.IsTransferToState('undo'):
            print(sys._getframe().f_code.co_name)
            self.control.Undo('None')
            self.display_tab()
    
    
    # Photo        
    def event_prev(self):
        
        if self.control.IsTransferToState('prev'):
            self.display_tab()
            print(sys._getframe().f_code.co_name)
            self.control.DrawPhoto('prev')
            file_name = self.control.GetCurrentFile()
            self.combo_file.set(file_name)
         
    def event_next(self):
        
        if self.control.IsTransferToState('next'):
            self.display_tab()
            print(sys._getframe().f_code.co_name)
            self.control.DrawPhoto('next')
            file_name = self.control.GetCurrentFile()
            self.combo_file.set(file_name)


    # Video
    def update_timestamp(self, is_play_status, frame_no, h,m,s, video_tag):
        
        idx = int(video_tag.replace('Video','')) - 1
        if is_play_status:
            self.label_frame[idx]['text']   = 'Time:{:02}:{:02}:{:02}'.format(h,m,s)  
        else:
            self.button_play['text']        = 'Play'
            self.label_frame[0]['text']     = 'Time:{:02}:{:02}:{:02}'.format(h,m,s)
            self.label_frame[1]['text']     = 'Time:{:02}:{:02}:{:02}'.format(h,m,s)
            self.control.ForceToState('STOP')
            
    def update_frameno(self, is_play_status, frame_no, h,m,s, video_tag):
        
        idx = int(video_tag.replace('Video','')) - 1
        if is_play_status:
            self.label_frame[idx]['text']   = 'frame:{}'.format(frame_no)
        else:
            self.button_play['text']        = 'Play'
            self.label_frame[0]['text']     = 'frame:{}'.format(0)
            self.label_frame[1]['text']     = 'frame:{}'.format(0)
            self.control.ForceToState('STOP')
    
    def update_savestat(self, is_save_status, cur_num, total_num):
        
        if is_save_status:
            progress = (cur_num/total_num)*100
            self.label_msgtxt['text'] = '{}/{} Saving.. {:.0f} %'.format(cur_num, total_num, progress)
            
        else:
            self.control.ClearCanvas()
            self.control.ForceToState('STOP')
            self.clear_message()
            self.display_tab()
            
    def event_update_bar(self, val):
        
        if self.control.IsTransferToState('speed|bar'):
            self.bar_position.set(int(val))
            pos = self.bar_position.get()
            print('{} :{}'.format(sys._getframe().f_code.co_name, pos))
            command = 'setpos-' + str(pos)
            self.control.Video(command)
        
        
    def event_mouse_select1(self, event):

        if self.control.IsTransferToState('dclick'):
            x, y = event.x, event.y
            print('{} :(x,y)=({},{})'.format(sys._getframe().f_code.co_name, x, y))
            self.control.SetCanvas('Video1')
        
    
    def event_mouse_select2(self, event):

        if self.control.IsTransferToState('dclick'):
            x, y = event.x, event.y
            print('{} :(x,y)=({},{})'.format(sys._getframe().f_code.co_name, x, y))
            self.control.SetCanvas('Video2')

        
    def event_play(self):

        if self.control.IsTransferToState('play'):
            self.control.Video('play')
            self.button_play['text'] = 'Stop'
            self.clear_message()
            
        elif self.control.IsTransferToState('stop'):
            self.control.Video('stop')
            self.button_play['text'] = 'Play'           
            
        print('{} :{}'.format(sys._getframe().f_code.co_name, self.button_play['text']))
            

    def event_step(self):
        
        if self.control.IsTransferToState('step'):
            print(sys._getframe().f_code.co_name)
            self.control.Video('step')
        
    
    def event_capture(self):
        
        if self.control.IsTransferToState('cap'):
            print(sys._getframe().f_code.co_name)
            self.control.Video('capture')
        
    
    def event_speed(self):
        
        if self.control.IsTransferToState('speed|bar'):
            self.button_speed['text'] = self.control.UpSpeed(self.speed_text)
            print('{} :{}'.format(sys._getframe().f_code.co_name, self.button_speed['text']))
            command = 'speed-' + self.button_speed['text']
            self.control.Video(command)
    
    
    def event_drop(self):
        
        if self.control.IsTransferToState('drop'):
            print(sys._getframe().f_code.co_name)
            self.control.Video('drop')
            
    
    def event_ftype(self):
        
        arg0 = self.ftype[self.radio_intvar[0].get()]
        if arg0 == 'mp4':
            self.window_sub_ctrl6.place_forget()
        else:
            self.window_sub_ctrl6.place(relx=0.68, rely=0.78)


def main():
    
    #　Tk MainWindow 生成
    main_window = tk.Tk()
    
    # Viewクラス生成
    current_dir = os.getcwd()
    print(current_dir)
    ViewGUI(main_window, current_dir)
    
    #　フレームループ処理
    main_window.mainloop()
    

if __name__ == '__main__':
    
    main()

   