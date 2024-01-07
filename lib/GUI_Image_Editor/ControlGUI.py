# -*- coding: utf-8 -*-
import os
from lib.GUI_Image_Editor.ModelImage import ModelImage

class ControlGUI():
    
    def __init__(self, default_path):

        self.dir_path = default_path
        self.ext_keys = {'[Photo]':['.png', '.jpg', '.jpeg', '.JPG', '.PNG'], '[Video]':['.mp4']}
        self.target_files = {}
        self.file_pos_photo = 0
        self.file_pos_video = 0
        self.speed_val = 1
        
        self.clip_sx = 0
        self.clip_sy = 0
        self.clip_ex = 0
        self.clip_ey = 0
        self.canvas  = {}
        self.frame   = {}
                
        self.output_path = os.path.join(default_path,'output')
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            
        # Model Class生成
        self.model = ModelImage(self.output_path)
    
        
    # Common(Private)
    def is_target(self, name, key_list):
        
        valid = False
        for ks in key_list:
            if ks in name:
                valid = True
        
        return valid
    
    
    def get_file(self, command, set_pos=-1):
        
        tab = self.select_tab
        num = len(self.target_files[tab])
        
        if num > 0:
        
            if tab == '[Photo]':
                
                if command == 'prev':
                    self.file_pos_photo -= 1
                    
                elif command == 'next':
                    self.file_pos_photo += 1
                    
                elif command == 'set':
                    self.file_pos_photo = set_pos
                    
                else:   # current
                    self.file_pos_photo = self.file_pos_photo
                
                if self.file_pos_photo < 0:
                    self.file_pos_photo = num -1
                    
                elif self.file_pos_photo >= num:
                    self.file_pos_photo = 0
                    
                cur_pos = self.file_pos_photo
                    
            else: # '[Video]'
            
                if command == 'set':
                    self.file_pos_video = set_pos  
                cur_pos = self.file_pos_video
            
            file_path = os.path.join(self.dir_path, self.target_files[tab][cur_pos])
            print('{}/{} {} '.format(cur_pos, num-1, file_path))
        
        else:
            file_path = 'None'
            print('No files..to support')
        
        return file_path
    
    # Common(Public)
    def InitCanvas(self, window_canvas_dict):
        
        for ks, canvas in window_canvas_dict.items():      
            self.canvas[ks] = canvas
        
        
    def SetTab(self, select_tab):
        
        self.select_tab = select_tab
        
    
    def InitStateMachine(self):
        # (1/0:有効/無効, 0-7:遷移先)
        stm_video = [
            #0:IDLE
            {'dir':(1,1),'set':(0,0),'play':(0,0),'stop':(0,0),'step':(0,0),'speed|bar':(0,0),'cap':(0,0),
             'edit':(0,0),'clip':(0,0),'rect':(0,0),'done':(0,0),'dclick':(0,0),'undo':(0,0),
             'save':(0,0),'drop':(0,0)},
            #1:SET
            {'dir':(1,1),'set':(1,2),'play':(0,1),'stop':(0,1),'step':(0,1),'speed|bar':(0,1),'cap':(0,1),
             'edit':(0,1),'clip':(0,1),'rect':(0,1),'done':(0,1),'dclick':(0,1),'undo':(0,1),
             'save':(0,1),'drop':(0,1)}, 
            #2:STOP    
            {'dir':(1,1),'set':(1,2),'play':(1,3),'stop':(0,2),'step':(1,2),'speed|bar':(1,2),'cap':(1,2),
             'edit':(1,4),'clip':(1,5),'rect':(0,2),'done':(0,2),'dclick':(1,2),'undo':(1,2),
             'save':(1,7),'drop':(0,2)},   
            #3:PLAY    
            {'dir':(0,3),'set':(0,3),'play':(0,3),'stop':(1,2),'step':(0,3),'speed|bar':(1,3),'cap':(0,3),
             'edit':(0,3),'clip':(0,3),'rect':(0,3),'done':(0,3),'dclick':(0,3),'undo':(0,3),
             'save':(0,3),'drop':(0,3)},
            #4:EDIT    
            {'dir':(0,4),'set':(0,4),'play':(0,4),'stop':(0,4),'step':(0,4),'speed|bar':(0,4),'cap':(1,4),
             'edit':(1,4),'clip':(1,5),'rect':(0,4),'done':(0,4),'dclick':(0,4),'undo':(1,2),
             'save':(1,7),'drop':(0,4)},   
            #5:EDIT_CLIP    
            {'dir':(0,5),'set':(0,5),'play':(0,5),'stop':(0,5),'step':(0,5),'speed|bar':(0,5),'cap':(1,5),
             'edit':(0,5),'clip':(1,5),'rect':(1,5),'done':(1,6),'dclick':(0,5),'undo':(1,2),
             'save':(1,7),'drop':(0,5)},    
            #6:EDIT_LOCK    
            {'dir':(0,6),'set':(0,6),'play':(0,6),'stop':(0,6),'step':(0,6),'speed|bar':(0,6),'cap':(1,6),
             'edit':(0,6),'clip':(0,6),'rect':(0,6),'done':(0,6),'dclick':(0,6),'undo':(1,2),
             'save':(1,7),'drop':(0,6)},
            #7:SAVING    
            {'dir':(0,7),'set':(0,7),'play':(0,7),'stop':(0,7),'step':(0,7),'speed|bar':(0,7),'cap':(0,7),
             'edit':(0,7),'clip':(0,7),'rect':(0,7),'done':(0,7),'dclick':(0,7),'undo':(0,7),
             'save':(0,7),'drop':(1,2)},
        ]
        # (1/0:有効/無効, 0-3:遷移先)
        stm_photo = [
            #0:IDLE
            {'dir':(1,1),'set':(0,0),'prev':(0,0),'next':(0,0),'edit':(0,0),'clip':(0,0),'rect':(0,0),
             'done':(0,0),'undo':(0,0),'save':(0,0)},
            #1:SET    
            {'dir':(1,1),'set':(1,1),'prev':(1,1),'next':(1,1),'edit':(1,2),'clip':(1,3),'rect':(0,1),
             'done':(0,1),'undo':(0,1),'save':(0,1)},
            #2:EDIT    
            {'dir':(0,2),'set':(1,1),'prev':(1,1),'next':(1,1),'edit':(1,2),'clip':(1,3),'rect':(0,2),
             'done':(0,2),'undo':(1,1),'save':(1,1)}, 
            #3:EDIT_CLIP    
            {'dir':(0,2),'set':(1,1),'prev':(1,1),'next':(1,1),'edit':(1,3),'clip':(1,3),'rect':(1,3),
             'done':(1,2),'undo':(1,1),'save':(1,1)}, 
        ]
        # State Machine table
        self.state_machine_table = {'[Photo]':stm_photo, '[Video]':stm_video}

        # State table
        state_video      = {'IDLE':0,'SET':1,'STOP':2,'PLAY':3,'EDIT':4,'EDIT_CLIP':5,'EDIT_LOCK':6,'SAVING':7}
        state_photo      = {'IDLE':0,'SET':1,'EDIT':2,'EDIT_CLIP':3}
        self.state_table = {'[Photo]':state_photo, '[Video]':state_video}

        # Initial state
        self.cur_state   = {'[Photo]':state_photo['IDLE'], '[Video]':state_video['IDLE']}
          

    def IsTransferToState(self, command):
       
        tab = self.select_tab
        cur_state = self.cur_state[tab]
        is_valid, next_state = self.state_machine_table[tab][cur_state][command]
        print('state_change:{}, {}->{} @ {}'.format(is_valid, cur_state, next_state, command))
        self.cur_state[tab] = next_state
        res = True if is_valid == 1 else False
        return res  
    
    
    def ForceToState(self, state):
        
        tab = self.select_tab
        next_state = self.state_table[tab][state]
        self.cur_state[tab] = next_state
        

    def SetFilelist(self, dir_path):
                
        self.dir_path = dir_path
        tab = self.select_tab
        target_files = []
        
        file_list = os.listdir(self.dir_path)
        target_ext = self.ext_keys[tab]
        print(tab, target_ext)
        
        for file_name in file_list:
            if self.is_target(file_name, target_ext):
                target_files.append(file_name)        
        
        self.target_files[tab] = target_files

        return self.target_files[tab]


    def GetCurrentFile(self):
        
        tab = self.select_tab
        target_files = self.target_files[tab]
        if len(target_files) > 0:
            file_path = self.get_file('current')
            return os.path.basename(file_path)

        else:
            return 'None'

    
    def DrawRectangle(self, command, pos_y, pos_x):
                
        tab = self.select_tab
        if command == 'clip_start':
            self.clip_sy, self.clip_sx = pos_y, pos_x
            self.clip_ey, self.clip_ex = pos_y+1, pos_x+1
            
        elif command == 'clip_keep':      
            self.clip_ey, self.clip_ex = pos_y, pos_x
            
        elif command == 'clip_end':
            self.clip_ey, self.clip_ex = pos_y, pos_x
            self.clip_sy, self.clip_sx = self.model.GetValidPos(tab, self.clip_sy, self.clip_sx)
            self.clip_ey, self.clip_ex = self.model.GetValidPos(tab, self.clip_ey, self.clip_ex)
            
        if tab == '[Photo]':
            self.model.DrawRectangle(self.canvas['Photo'],  self.clip_sy, self.clip_sx, self.clip_ey, self.clip_ex)
            
        else: # '[Video]'
            self.model.DrawRectangle(self.canvas['Video1'], self.clip_sy, self.clip_sx, self.clip_ey, self.clip_ex)
            self.model.DrawRectangle(self.canvas['Video2'], self.clip_sy, self.clip_sx, self.clip_ey, self.clip_ex)

    
    def Set(self, set_pos, callbacks):
        
        tab = self.select_tab
        if tab == '[Photo]':
            self.model.DeleteRectangle(self.canvas['Photo'])
            file_path = self.get_file('set', set_pos)
            res = self.model.DrawPhoto(file_path, self.canvas['Photo'], 'None')
            
        else: # '[Video]'            
            self.model.DeleteRectangle(self.canvas['Video1'])
            # self.model.DeleteRectangle(self.canvas['Video2'])
            self.video_tag = 'Video1'
            
            file_path = self.get_file('set', set_pos)
            cmd = 'set' if file_path != 'None' else 'unset'
            res = self.model.SetVideo(file_path, self.canvas[self.video_tag], self.video_tag, cmd, callbacks)
            _, self.frame['Video1'] = self.model.GetVideo('status')
            _, self.frame['Video2'] = self.model.GetVideo('status')   
            print('tag, fno1, fno2',self.video_tag, self.frame['Video1'], self.frame['Video2'])
            
        return res
    
        
    def Edit(self, command):
                
        args = {}
        if command == 'clip_done':
            args['sx'], args['sy'] = self.clip_sx, self.clip_sy
            args['ex'], args['ey'] = self.clip_ex, self.clip_ey
        
        tab = self.select_tab
        if tab == '[Photo]':                 
            file_path = self.get_file('current')
            self.model.DrawPhoto(file_path, self.canvas['Photo'], command, args=args)
            
        else: # '[Video]'
            self.play_status, self.frame[self.video_tag] = self.model.GetVideo('status')
            print('tag, fno1, fno2',self.video_tag, self.frame['Video1'], self.frame['Video2'])
            self.model.EditVideo(self.canvas['Video1'], 'Video1', command, self.frame['Video1'], args=args, update=False)
            self.model.EditVideo(self.canvas['Video2'], 'Video2', command, self.frame['Video2'], args=args, update=True)

        
    def Save(self, args=None):
        
        tab = self.select_tab
        if tab == '[Photo]':        
            file_path = self.get_file('current')
            self.model.SavePhoto(file_path)
            
        else: # '[Video]'
            _, self.frame[self.video_tag] = self.model.GetVideo('status')
            file_path = self.get_file('current')
            self.model.SaveVideo(file_path, self.frame['Video1'], self.frame['Video2'], args)
            print('tag, fno1, fno2',self.video_tag, self.frame['Video1'], self.frame['Video2'])
  
    
    def ClearCanvas(self):
        
        tab = self.select_tab
        if tab == '[Photo]':
            self.model.DeleteRectangle(self.canvas['Photo'])
            
        else: # '[Video]'
            self.model.EditVideo(self.canvas['Video1'], 'Video1', 'Undo', self.frame['Video1'])
            self.model.EditVideo(self.canvas['Video2'], 'Video2', 'Undo', self.frame['Video2'])
            self.model.DeleteRectangle(self.canvas['Video1'])
            self.model.DeleteRectangle(self.canvas['Video2'])
            
            
    def Undo(self, command):
        
        tab = self.select_tab
        if tab == '[Photo]':
            file_path = self.get_file('current')
            self.model.DrawPhoto(file_path, self.canvas['Photo'], command)
            
        else: # '[Video]'
            _, self.frame[self.video_tag] = self.model.GetVideo('status')
            print('tag, fno1, fno2',self.video_tag, self.frame['Video1'], self.frame['Video2'])
            self.ClearCanvas()


    # Photo(Public)
    def DrawPhoto(self, command, set_pos=-1):
                
        file_path = self.get_file(command, set_pos)
        self.model.DrawPhoto(file_path, self.canvas['Photo'], 'None')

        
    # Video(Public)
    def InitSpeed(self, speed_text):
        
        self.speed_val = 1
        return speed_text[self.speed_val]    
    
    
    def UpSpeed(self, speed_text):     
        
        self.speed_val += 1
        if self.speed_val >= len(speed_text):
            self.speed_val = 0
        return speed_text[self.speed_val]
    
    
    def SetCanvas(self, select_canvas):

        self.video_tag = select_canvas
        self.play_status, self.frame['Video1'] = self.model.GetVideo('status')
        self.play_status, self.frame['Video2'] = self.model.GetVideo('status')
        print('canvas->{}, play_status:{}, frame:{}'.format(select_canvas, self.play_status, self.frame[select_canvas]))          
            
    
    def GetVideo(self, command):
        
        return self.model.GetVideo(command)       
            
            
    def Video(self, command, set_pos=-1):
        # play/stop/setpos/speed/drop
        res = self.model.Video(self.canvas[self.video_tag], self.video_tag, command)
        return res 
