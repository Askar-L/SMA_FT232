# -*- coding: utf-8 -*-
import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk, ImageOps
import cv2

import threading

class ModelImage():
    
    def __init__(self, output_path, ImageType='Photo+Video'):
         
        self.ImageType = ImageType
        self.edit_img = None
        self.original_img = None
        self.canvas_w = 0
        self.canvas_h = 0
        self.cap = None
        self.play_status = False
        self.cur_frame = 0
        self.lock = threading.Lock()
        self.video_img = None
        self.interval_limit = 21
        self.output_path = output_path
       
    # Common(Private)
    def set_image_layout(self, canvas, image):
        
        self.canvas_w = canvas.winfo_width()
        self.canvas_h = canvas.winfo_height()
        self.rate_wh = self.canvas_w/self.canvas_h
        
        h, w = image.height, image.width
        rate_wh = w / h
        self.h, self.w = h, w
        if rate_wh < self.rate_wh:
            self.resize_h = self.canvas_h
            self.resize_w = int(w * (self.canvas_h/h))
            self.pad_x = (self.canvas_w - self.resize_w) // 2
            self.pad_y = 0
            
        else:
            self.resize_w = self.canvas_w
            self.resize_h = int(h * (self.canvas_w/w))
            self.pad_y = (self.canvas_h - self.resize_h) // 2
            self.pad_x = 0
        
        
    def get_correct_values(self, rate, sy, sx, ey, ex):

        mod_sx = int(min(sx, ex)*rate)
        mod_sy = int(min(sy, ey)*rate)
        mod_ex = int(max(sx, ex)*rate)
        mod_ey = int(max(sy, ey)*rate)
        ch, cw = mod_ey - mod_sy, mod_ex - mod_sx

        return mod_sy, mod_sx, ch, cw

    
    def get_original_coords(self, h, w, args):
        
        sy, sx, ey, ex = args['sy'], args['sx'], args['ey'], args['ex']
        rate_wh = w / h
        
        if rate_wh < self.rate_wh:
            rate = h/self.canvas_h
            x_spc = self.pad_x*rate
            sy, sx, ch, cw = self.get_correct_values(rate, sy, sx, ey, ex)
            sx = sx - x_spc
            sx = int(max(sx, 0))
            sx = int(min(sx, w))
            
        else:
            rate = w/self.canvas_w
            y_spc = self.pad_y*rate
            sy, sx, ch, cw = self.get_correct_values(rate, sy, sx, ey, ex)        
            sy = sy - y_spc
            sy = int(max(sy, 0))
            sy = int(min(sy, h))

        return sy, sx, ch, cw
    
    
    def edit_image_proc(self, np_img, command, args={}):        
        
        if 'flip-1' in command: # U/L
            np_img = np.flip(np_img, axis=0)
            
        elif 'flip-2' in command: # L/R
            np_img = np.flip(np_img, axis=1)

        elif 'rotate-' in command: # 1:rot90 2:rot180 3:rot270
            cmd = int(command.replace('rotate-', ''))
            np_img = np.rot90(np_img, cmd)
            
        elif command == 'clip_done':
            h, w = np_img[:,:,0].shape
            sy, sx, ch, cw = self.get_original_coords(h, w, args)
            np_img = np_img[sy:sy+ch, sx:sx+cw,:]
            self.edit_args = (sy, sx, ch, cw)         
        
        elif command == 'clip_save':
            sy, sx, ch, cw = self.edit_args
            np_img = np_img[sy:sy+ch, sx:sx+cw,:]
            
        return np_img
        
    
    def edit_image_command(self, orginal_image, edit_image, command, args={}):
        
        if edit_image != None:
            img = edit_image
        else:
            img = orginal_image.copy()
        
        np_img = np.array(img)
        np_img = self.edit_image_proc(np_img, command, args=args)
        
        return Image.fromarray(np_img)

    # Common(Public) 
    def GetValidPos(self, select_tab, pos_y, pos_x):
        
        rate_wh = self.resize_w / self.resize_h
        
        if rate_wh < self.rate_wh:
            valid_pos_y = pos_y
            valid_pos_x = max(pos_x, self.pad_x)
            valid_pos_x = min(valid_pos_x, self.canvas_w - self.pad_x)
            
        else:
            valid_pos_x = pos_x
            valid_pos_y = max((pos_y, self.pad_y))
            valid_pos_y = min(valid_pos_y, self.canvas_h - self.pad_y)

        return valid_pos_y, valid_pos_x
  
   
    def DrawRectangle(self, canvas, clip_sy, clip_sx, clip_ey, clip_ex):
        
        if canvas.gettags('clip_rect'):
            canvas.delete('clip_rect')
            
        canvas.create_rectangle(clip_sx, clip_sy, clip_ex, clip_ey, outline='red', tag='clip_rect')
        
    
    def DeleteRectangle(self, canvas):
        
        if canvas.gettags('clip_rect'):
            canvas.delete('clip_rect')
           
            
    # Photo(Public)     
    def DrawPhoto(self, file_path, canvas, command, args={}):
        
        if canvas.gettags('Photo'):
            canvas.delete('Photo')
        
        result = False
        if file_path != 'None':
            
            if self.edit_img != None and command != 'None':
                img = self.edit_img
                
            else:
                self.clear_command_list()
                img = Image.open(file_path)
                self.original_img = img
                self.edit_img = None
                self.set_image_layout(canvas, self.original_img)
            
            if command != 'None':
                img = self.edit_image_command(self.original_img, self.edit_img, command, args=args)
                self.edit_img = img
                self.set_image_layout(canvas, self.edit_img)
    
            pil_img = ImageOps.pad(img, (self.canvas_w, self.canvas_h))
            self.tk_img = ImageTk.PhotoImage(image=pil_img)
            canvas.create_image(self.canvas_w/2, self.canvas_h/2, image=self.tk_img, tag='Photo')
            result = True
            
        return result
    
    
    def SavePhoto(self, fname):
        
        if self.edit_img != None:
            name, ext = os.path.splitext(fname)
            dt = datetime.now()
            fpath = name + '_' + dt.strftime('%H%M%S') + '.png'

            self.edit_img.save(fpath)
            print("Saved: {}".format(fpath))
            
    
    # Video(Private)
    def get_cur_time(self, sec):
        
        sec_time = int(sec)
        m = int(sec_time/60)
        h = int(sec_time/3600)
        s = sec_time - 3600*h - 60*m
        return h,m,s
    
    
    def draw_video(self, canvas, target_img, canvas_tag):
        
        canvas_w_video = canvas.winfo_width()
        canvas_h_video = canvas.winfo_height()
        
        img_conv = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)             
        self.img_conv = Image.fromarray(img_conv)
        pil_img = ImageOps.pad(self.img_conv, (canvas_w_video, canvas_h_video))
        self.tk_video[canvas_tag] = ImageTk.PhotoImage(image=pil_img)
        
        self.delete_video(canvas, canvas_tag)
        canvas.create_image(canvas_w_video/2, canvas_h_video/2, image=self.tk_video[canvas_tag], tag=canvas_tag)
    
        
    def delete_video(self, canvas, canvas_tag):
        
        if canvas.gettags(canvas_tag):
            canvas.delete(canvas_tag)

        
    def loop_video(self, loop=True):
        
        if loop and self.ret:
            self.vid = self.canvas_video.after(self.interval, self.loop_video)

        self.ret, self.video_img = self.cap.read()
        if self.ret:
            self.draw_video(self.canvas_video, self.video_img, self.canvas_tag)
            self.play_status = True
            self.cur_frame += 1
            h,m,s = self.get_cur_time(self.cur_frame/self.fps)
            self.cb_playing(self.play_status, self.cur_frame, h,m,s, self.canvas_tag)

        else:
            self.cur_frame = 0
            self.play_status = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame)
            h,m,s = self.get_cur_time(self.cur_frame/self.fps)
            self.cb_playing(self.play_status, self.cur_frame, h,m,s, self.canvas_tag)
        
        return self.ret
    
    
    def set_interval(self, speed):
        
        with self.lock:
            self.interval = int(self.base_tick*speed)
            if self.interval < self.interval_limit:
                self.interval = self.interval_limit

    
    def save_capture(self):
        
        file_path = '{}/{:05}.png'.format(self.output_path, self.cur_frame)        
        self.img_conv.save(file_path)
        print("Saved: {}".format(file_path))
        
    
    def edit_video(self, frame, command_list, args):
        
        edit_np_video = np.array(frame).copy()
        for cmd in command_list:
            edit_np_video = self.edit_image_proc(edit_np_video, cmd, args=args)
            
        return edit_np_video
    
    
    def is_equel(self, cmd, last_cmd):
        
        result = False
        for k_cmd in ['rotate-', 'flip-1', 'flip-2', 'clip_']:
            if k_cmd in cmd:
                if k_cmd in last_cmd:
                    result = True
                    break
            
        return result
    
    
    def get_cmd_keyval(self, cmd):
        
        key = 'None'
        for k_cmd in ['rotate', 'flip-1', 'flip-2', 'clip']:
            if k_cmd in cmd:
                key = k_cmd
                break                
        
        val = 1
        if 'rotate-' in cmd:
            val = int(cmd.replace('rotate-',''))
            
        return key, val
    
    
    def get_cmdpack(self, cmd_dict, cmd):
        
        flip_UB_keys = ['None', 'flip-1']
        flip_LR_keys = ['None', 'flip-2']
        ROT_keys     = ['None', 'rotate-1', 'rotate-2', 'rotate-3']
        
        cmd_pack = cmd
        for ks, val in cmd_dict.items():
            if ks == 'rotate':
                idx = val % len(ROT_keys)
                cmd_pack = ROT_keys[idx]
            elif ks == 'flip-1':
                idx = val % len(flip_UB_keys)
                cmd_pack = flip_UB_keys[idx]
            elif ks == 'flip-2':
                idx = val % len(flip_LR_keys) 
                cmd_pack = flip_LR_keys[idx]
            elif ks == 'clip':
                cmd_pack = 'clip_save'
            
        return cmd_pack
    
        
    def create_command_list(self):

        cont_dict = {}
        edit_command_list = []
        self.all_command_list.append('None')
        
        for idx, cmd in enumerate(self.all_command_list):
            
            if idx == 0:
                ks_cmd, val = self.get_cmd_keyval(cmd)
                cont_dict[ks_cmd] = val
                last_cmd = cmd
                
            else:
                
                if self.is_equel(cmd, last_cmd):                  
                    ks_cmd, val = self.get_cmd_keyval(cmd)
                    cont_dict[ks_cmd] += val
                    last_cmd = cmd
                    
                else:           
                    pack_cmd = self.get_cmdpack(cont_dict, cmd)
                    edit_command_list.append(pack_cmd)
                    cont_dict = {}
                    ks_cmd, val = self.get_cmd_keyval(cmd)
                    cont_dict[ks_cmd] = val
                    last_cmd = cmd
       
        self.edit_command_list = [cmd for cmd in edit_command_list if cmd != 'None']
    
        
    def clear_command_list(self):
    
        self.edit_command_list = []
        self.edit_args = {}
        self.all_command_list = []
        
    
    # Video(Public)
    def SetVideo(self, fname, canvas, canvas_tag, command, callbacks):
        
        result = False
        if command == 'set':
            print('Video/', command)
            if self.cap != None:
                self.cap.release()
                
            self.cap = cv2.VideoCapture(fname)
            self.frame_num = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.base_tick = int(1000/self.fps)
            self.cur_frame = 0
            self.speed = 1.0
            self.set_interval(self.speed)
            print(fname, self.frame_num, self.fps, self.base_tick, self.interval)
            
            self.canvas_video = canvas
            self.canvas_tag = canvas_tag
            self.tk_video = {}
            self.video_edit_imgs = {'Video1':None, 'Video2':None}
            self.clear_command_list()
            self.cb_playing = callbacks[0]
            self.cb_playing(False, 0, 0,0,0, self.canvas_tag)
            self.cb_saving  = callbacks[1]
            
            self.ret, self.video_img = self.cap.read()
            if self.ret:
                self.set_image_layout(self.canvas_video, Image.fromarray(self.video_img))  
                self.draw_video(self.canvas_video, self.video_img, self.canvas_tag)
                self.cur_frame += 1
                self.edit_h = self.h
                self.edit_w = self.w
                result = True
        
        elif command == 'unset':
            print('Video/', command)
            if self.cap != None:
                self.cap.release()
                
            self.cap = None
            self.frame_num = 0
            self.fps = 0
            self.base_tick = 0
            self.cur_frame = 0
            self.speed = 1.0
            self.set_interval(self.speed)
            print(fname, self.frame_num, self.fps, self.base_tick, self.interval)
            
            self.canvas_video = canvas
            self.canvas_tag = canvas_tag
            self.tk_video = {}
            self.video_edit_imgs = {'Video1':None, 'Video2':None}
            self.clear_command_list()
            self.cb_playing = callbacks[0]
            self.cb_playing(False, 0, 0,0,0, 'Video1')
            self.cb_playing(False, 0, 0,0,0, 'Video2')
            self.cb_saving  = None
            
            self.delete_video(canvas, 'Video1')
            self.delete_video(canvas, 'Video2')
            
        return result
            
            
    def GetVideo(self, command):
            
        if command == 'status': 
            info1, info2 = self.play_status, self.cur_frame
        elif command == 'property':
            info1, info2 = self.frame_num, self.fps
        elif command == 'frame':
            info1, info2 = self.frame_num, self.cur_frame
            
        return info1, info2
        
    
    def Video(self, canvas, canvas_tag, command, args=None):
        
        res = True
        self.canvas_video = canvas
        self.canvas_tag   = canvas_tag
        
        if command == 'play':            
            res = self.loop_video()
            print('Video/', command, self.play_status)
                    
        elif command == 'step':
            self.loop_video(loop=False)
            
        elif command == 'stop':
            print('Video/', command, self.vid)
            self.canvas_video.after_cancel(self.vid)
            self.play_status = False
        
        elif 'setpos' in command:
            num = command.replace('setpos-','')
            with self.lock:                
                self.cur_frame = int(self.frame_num*(int(num)/100))
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame)
            print('Video/', command, self.cur_frame, num)
            
        elif 'speed' in command:
            val = command.replace('speed-x','')
            self.speed = 1/float(val)
            self.set_interval(self.speed)
            print('Video/', command, self.speed, self.interval)
            
        elif command == 'capture':
           self.save_capture()
           print('Video/', command)
           
        elif command == 'drop':
            print('Video/', command, self.sid)
            self.canvas_video.after_cancel(self.sid)
            self.save_status = False
            self.complete_save_video()
            self.clear_save_video()
            self.clear_command_list()
            self.cb_saving(self.save_status, self.save_num, self.edit_num)
        
        elif command == 'reset':
            self.cap.release()
            self.cap = None
            self.play_status = False
            
        else:
            print('Video/None')
            
        return res

    
    def EditVideo(self, canvas, canvas_tag, command, edit_frame, args=None, update=False):
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, edit_frame)
        ret, frame = self.cap.read()
        if ret:           

            if command != 'Undo':
    
                if self.video_edit_imgs[canvas_tag] != None:
                    edit_img = np.array(self.video_edit_imgs[canvas_tag])
                else:
                    edit_img = frame
           
                edit_img = self.edit_video(edit_img, [command], args) 
                self.draw_video(canvas, edit_img, canvas_tag)
                self.video_edit_imgs[canvas_tag] = Image.fromarray(edit_img)
        
                if update:
                    pil_img = self.video_edit_imgs[canvas_tag]
                    self.set_image_layout(canvas, pil_img)
                    self.edit_h = pil_img.height
                    self.edit_w = pil_img.width
                    self.all_command_list.append(command)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame)
                    
            else: # Undo
                self.draw_video(canvas, frame, canvas_tag)
                self.set_image_layout(canvas, Image.fromarray(frame))
                self.video_edit_imgs[canvas_tag] = None
                self.all_command_list = []      
                
        else:
            print('cap_read:', ret)
            


    def SaveVideo(self, fname, frame_1, frame_2, save_args):          
        # Set frames to save
        fno_sp = min(frame_1, frame_2)
        fno_ep = max(frame_1, frame_2)
        if fno_sp == fno_ep:
            fno_ep += 1
        
        self.cap_save = cv2.VideoCapture(fname)
        self.cap_save.set(cv2.CAP_PROP_POS_FRAMES, fno_sp)
        self.edit_num = fno_ep - fno_sp
        self.save_num = 0
        print(f'fno_sp:{fno_sp} fno_ep:{fno_ep} save_num:{self.save_num}')

        # Create file_path
        name, ext = os.path.splitext(fname)
        self.file_path = '{}_frame{}_{}.{}'.format(name, fno_sp, fno_ep, save_args[0])
        # Create edit commands(Minimal)
        self.create_command_list()
        # Pre-Process for save video
        self.save_ftype = save_args[0]
        self.prepare_save_video(save_args)
            
        self.save_status = True
        print(self.save_ftype, self.resz_rate, self.skip_rate)
        # start save_video_thread
        self.sid = self.canvas_video.after(20, self.save_video_thread)
    
    
    def save_video_thread(self):
        
        if self.save_num < self.edit_num:
            ret, frame = self.cap_save.read()
            if ret:
                # Edit frame
                img_cnv = self.edit_video(frame, self.edit_command_list, None)
                # Save 1frame
                self.save_video_frame(img_cnv)
                # View callback
                self.cb_saving(self.save_status, self.save_num, self.edit_num)
                # update save frame
                self.save_num += 1
                
                if self.save_status:
                    # start save_video_thread
                    self.sid = self.canvas_video.after(20, self.save_video_thread)
        
        else:
            # Complete saving
            self.complete_save_video()
            self.clear_save_video()
            self.clear_command_list()
            self.save_status = False
            # View callback
            self.cb_saving(self.save_status, self.save_num, self.edit_num)


    def prepare_save_video(self, save_args):

        if self.save_ftype == 'mp4':
            # Open Video Writer
            video_format = cv2.VideoWriter_fourcc(*'mp4v') 
            self.video   = cv2.VideoWriter(self.file_path, video_format, self.fps, (self.edit_w, self.edit_h))
            self.skip_rate  = 1
            self.resz_rate  = 1

        else: # gif
            # For gif save
            self.pil_images = []
            self.resz_rate  = int(save_args[1][2])  # '1/X' -> int('X')
            self.skip_rate  = int(save_args[2][2])  #' 1/X' -> int('X')


    def save_video_frame(self, img_cnv):
       
        if self.save_ftype == 'mp4':
            self.video.write(img_cnv)
        
        else: # Save gif list
            if self.save_num % self.skip_rate == 0:
                img_cnv = cv2.cvtColor(img_cnv, cv2.COLOR_BGR2RGB)
                img_cnv = Image.fromarray(img_cnv).resize((self.edit_w//self.resz_rate, self.edit_h//self.resz_rate), resample=Image.BICUBIC)
                self.pil_images.append(img_cnv)


    def complete_save_video(self):

        if self.save_ftype == 'mp4':
            self.video.release()
            
            if self.save_status:
                print("Saved: {}".format(self.file_path))
            else:
                # remove file if choosed to drop
                os.remove(self.file_path)

        else: # gif
            if self.save_status:
                self.pil_images[0].save(self.file_path, save_all = True, append_images=self.pil_images[1:], duration=200, loop=0)
                print("Saved: {}".format(self.file_path))
    

    def clear_save_video(self):
        
        if self.cap_save != None:
            self.cap_save.release()
            self.cap_save = None

