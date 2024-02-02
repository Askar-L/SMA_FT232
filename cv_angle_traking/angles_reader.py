# %%
import cv2,time,os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class AngleTracker(object): # TODO
   
    def __init__(self, ): # TODO
        # colors_name = ["blue", "pink", "green", "yellow"]

        self.color_mode = 0 # 0: Lab,1: Rgb

        if self.color_mode ==0: # Lab
            self.maker_tolerance_L = 30#int(0.08 * 255)
            self.maker_tolerance_a = 20# int(0.09 * 255)# red -> green
            self.maker_tolerance_b = 25# int(0.09 * 255)# Yellow -> Blue
        else : # RGB
            self.maker_tolerance_L = int(0.5 * 255)
            self.maker_tolerance_a = int(0.2 * 255)# red -> green
            self.maker_tolerance_b = int(0.2 * 255)# Yellow -> Blue

        # self.marker_rangers = [ #[Low Lhigh alow ahigh blow bhigh]] #  SC02
        #                [ [100,255],[150,180],[100,150]], # Marker A
        #                [ [130,155],[100,200],[20,80]], # Marker B
        #                [ [180,220],[55,85],[100,180]], # Marker C
        #                [ [150,215],[80,100],[90,110]], # Marker D 
        #                 ]
        self.marker_rangers = [ #[Low Lhigh alow ahigh blow bhigh]] # SC01
                       [ [100,220],[160,220],[60,160]], # Marker A
                       [ [100,215],[70,190],[30,80]], # Marker B
                       [ [180,210],[55,85],[120,180]], # Marker C
                       [ [150,235],[80,90],[100,120]], # Marker D 
                        ]
        # self.marker_rangers = [ #[Low Lhigh alow ahigh blow bhigh]] # Default
        #                [ [0,255],[140,170],[160,255]], # Marker A
        #                [ [0,255],[175,255],[0,80]], # Marker B
        #                [ [0,255],[110,120],[130,180]], # Marker C
        #                [ [0,255],[80,120],[90,110]], # Marker D 
        #                 ]
        self._point_counter = 0
        self.num_maker_sets = 4
        self.maker_position_frame0 = []
        for _ in range(self.num_maker_sets):self.maker_position_frame0.append([0,0])

        pass
        
    def add_text_to_frame(self,frame, text, position=(30, 30), font=cv2.FONT_HERSHEY_DUPLEX, font_scale=0.2, color=(0, 255, 0), thickness=2):
           # Add text overlay into video frame
        """
        Add text to a frame.

        Parameters:
        - frame (numpy.ndarray): Input frame.
        - text (str): Text to be added to the frame.
        - position (tuple): Position of the text (x, y).
        - font (int): Font type. FONT_HERSHEY_PLAIN FONT_HERSHEY_SIMPLEX
        - font_scale (float): Font scale.
        - color (tuple): Text color (B, G, R).
        - thickness (int): Text thickness.

        Returns:
        - numpy.ndarray: Frame with added text.
        """
        frame_with_text = frame.copy()
        cv2.putText(frame_with_text, text, position, font, font_scale, color, thickness)
        return frame_with_text

    def calculate_angle(self,line1, line2):
        # Convert lines to numpy arrays
        line1 = np.array(line1)
        line2 = np.array(line2)

        # Calculate the vectors corresponding to the lines
        vector1 = line1[1] - line1[0]
        vector2 = line2[1] - line2[0]

        # Calculate the dot product and cross product of the vectors
        dot_product = np.dot(vector1, vector2)
        cross_product = np.cross(vector1, vector2)

        # Calculate the magnitudes of the vectors
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)

        # Calculate the cosine of the angle between the vectors
        cosine_theta = dot_product / (magnitude1 * magnitude2)

        # Determine the sign of the dot product to determine the direction
        if dot_product > 0:
            angle_radians = np.arccos(cosine_theta)
            # Convert the angle to degrees
            angle_degrees = 180 - np.degrees(angle_radians)
            # Adjust angle for the cross product sign
            if cross_product < 0:
                angle_degrees = 360 - angle_degrees
        else:
            angle_radians = np.arccos(cosine_theta)
            # Convert the angle to degrees
            angle_degrees = np.degrees(angle_radians)

        return angle_degrees
    
    @staticmethod
    def calculate_vector(point1, point2):
        return np.array(point2) - np.array(point1)

    def segment_marker_by_color_Maros(self,frame_tmp):
        # Input must be a frame in the cielab color model from the OpenCV function

        # Extract color channels
        L_channel = frame_tmp[:, :, 0]
        a_channel = frame_tmp[:, :, 1]
        b_channel = frame_tmp[:, :, 2]

        # Color segmentation using NumPy array operations
        marker_blue = (a_channel > 140) & (a_channel < 170) & (b_channel > 160)
        marker_pink = (a_channel > 175) & (b_channel < 80)
        marker_green = (a_channel < 120) & (b_channel > 130)
        marker_yellow = (a_channel > 80) & (a_channel < 120) & (b_channel > 90) & (b_channel < 110)

        return marker_blue, marker_pink, marker_green, marker_yellow

    def segment_marker_by_color(self,frame_tmp): # Askar.L
        # Input must be a frame in the cielab color model from the OpenCV function
        num_maker_sets = 4
        # Extract color channels
        L_channel = frame_tmp[:, :, 0] # lightness
        a_channel = frame_tmp[:, :, 1] # red -> green
        b_channel = frame_tmp[:, :, 2] # Yellow -> Blue

        marker_rangers = self.marker_rangers
        markers_masks = []
        
        # print(marker_rangers)
        for i in range(num_maker_sets):# Color segmentation using NumPy array operations
            _mask =( 
                (L_channel > marker_rangers[i][0][0]) & (L_channel < marker_rangers[i][0][1]) &
                (a_channel > marker_rangers[i][1][0]) & (a_channel < marker_rangers[i][1][1]) &
                (b_channel > marker_rangers[i][2][0]) & (b_channel < marker_rangers[i][2][1]) )
            
            markers_masks.append( _mask )
        
        if True:
            mask_in_one = np.vstack((markers_masks[0],markers_masks[1],markers_masks[2],markers_masks[3]))
            # mask_in_one = np.vstack((markers_masks[2]))
            # print("!!!!:",type(_mask))
            cv2.namedWindow("Mask",cv2.WINDOW_KEEPRATIO)
            # while True:
            cv2.imshow("Mask",255*np.uint8(mask_in_one))         
            cv2.waitKey(1)
            # if cv2.waitKey(1) & 0xFF == 27: break
            # cv2.destroyWindow("Mask")
                
        return markers_masks

    def acquire_marker_color(self,frame): #TODO
        marker_rangers_old = self.marker_rangers
        marker_rangers = []

        num_marker_sets = self.num_maker_sets
        cv2.namedWindow(cv_choose_wd_name, cv2.WINDOW_KEEPRATIO)
        cv2.setMouseCallback(cv_choose_wd_name, tracker.mouse_event)

        if self.color_mode == 0:
            frame_to_segment = cv2.cvtColor(frame, cv2.COLOR_RGB2Lab)
        else: frame_to_segment = frame

        # frame = add_text_to_frame(frame,'Please choose',position=(40, 50),color=(255, 255,255),font_scale=1)
        cv2.putText(frame, 'Choose '+ str(num_marker_sets)+' position for the marker', (40, 50), cv2.FONT_HERSHEY_DUPLEX,
                    1, (255, 255,255), thickness =1)
        cv2.putText(frame, 'Press Esc after finish', (40, 80), cv2.FONT_HERSHEY_DUPLEX,
                    1, (255, 255,255), thickness =1)
        
        while not frame is None:
            cv2.imshow('Choose', frame)
            if cv2.waitKey(1) & 0xFF == 27: break

        for _i,_pos in enumerate(self.maker_position_frame0):
            # Get color dara from lab img
            # print(_pos) # [413, 277]
            # print(frame_cielab[_pos[1]][_pos[0]]) # [143 181 109]
            # Cal tolerance range
            upper_limit = frame_to_segment[_pos[1]][_pos[0]] + [self.maker_tolerance_L, self.maker_tolerance_a, self.maker_tolerance_b]  
            lower_limit = frame_to_segment[_pos[1]][_pos[0]] - [self.maker_tolerance_L, self.maker_tolerance_a, self.maker_tolerance_b]
            # print(upper_limit,lower_limit);exit() # [146 171  82] [122 147  58]
            marker_rangers_ch = []
            # Save to variable
            for _j in range(3):
                marker_rangers_ch.append([lower_limit[_j],upper_limit[_j]])
                # self.marker_rangers[_i][_j:_j+1] = [lower_limit[_j],upper_limit[_j]]
                # self.marker_rangers[_i][_j+1] = 
            pass
            marker_rangers.append(marker_rangers_ch)

        print(marker_rangers)
        self.marker_rangers = marker_rangers
        
        cv2.destroyWindow("Choose")
        
        return marker_rangers 
    
    def mouse_event(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            _meassage = str(self._point_counter) + ":%d,%d" % (x, y) # _point_counter
            cv2.circle(frame, (x, y), 1, (255, 255, 255), thickness = -1)
            cv2.putText(frame, _meassage, (x, y), cv2.FONT_HERSHEY_PLAIN,
                        1.0, (255, 255, 255), thickness = 1)
            cv2.imshow("Choose", frame)
            # self. = x
            self.maker_position_frame0[self._point_counter] = [x,y]
            self._point_counter = self._point_counter + 1 if self._point_counter < self.num_maker_sets-1 else 0
            # print(self.maker_position_frame0)
        return []

    def store_video(self,frames, output_path, fps):
        # Function to store the video with updated frames
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G') # Win
        # fourcc = cv2.VideoWriter_fourcc(*'x264')# # 'avc1' # Mac
        print('fourcc built')
        height, width, _ = frames[0].shape
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for frame in frames:out.write(frame)
        out.release()

    def extract_angle(self, frame, swap):
        # Convert the input frame to the CIELAB color space
        cielab_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2Lab)

        # Segment markers by color in the CIELAB color space
        [marker_blue, marker_pink, marker_green, marker_yellow] = self.segment_marker_by_color(cielab_frame)
        # marker_blue, marker_pink, marker_green, marker_yellow = segment_marker_by_color(cielab_frame)


        # Create a stack of masks for each color marker
        masks = np.stack([marker_blue, marker_pink, marker_green, marker_yellow], axis=0)

        # Define color names for visualization
        colors_name = ["blue", "pink", "green", "yellow"]

        # Initialize a list to store points per frame
        point_per_frame = []

        # Set the line padding value
        line_pad = 5  # Adjust this value as needed

        # Initialize the direction vector for the first line
        direction_vector_0_1 = None
        # Iterate over each color marker
        try:
            for mask, thr, color, color_name, direction_vector in zip(
                    masks, threshold_area_size, colors, colors_name, [direction_vector_0_1, None, None, None]        ):
                # Convert the mask to uint8
                
                mask = np.uint8(mask) # True/False -> 0/1
        
                # Find connected components in the mask
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

                # Filter regions based on area threshold
                filtered_regions = [index for index, stat in enumerate(stats[1:]) if stat[4] >= thr]

                # Initialize a list to store points per mask
                point_per_mask = []

                # Iterate over filtered regions in the mask
                for idx, index in enumerate(filtered_regions):
                    # Access region properties from the stats array
                    left, top, width, height, area = stats[index + 1]

                    # Calculate the centroid
                    centroid_x, centroid_y = int(left + width / 2), int(top + height / 2)

                    # Append the centroid to the list of points for the mask
                    point_per_mask.append((centroid_x, centroid_y))
                

                # Visualize circles for each point in the mask
                for idx, point in enumerate(point_per_mask):
                    cv2.circle(frame, (point[0], point[1]), radius=idx * 10, color=color, thickness=5)

                # Visualize circles for each point with increased radius
                for idx, point in enumerate(point_per_mask):
                    cv2.circle(frame, (point[0], point[1]), radius=idx * 10 + 10, color=color, thickness=5)

                # print(point_per_mask)
                # If direction vector is not initialized, calculate it from the first two points
                if direction_vector is None:
                    direction_vector = self.calculate_vector(point_per_mask[1], point_per_mask[0])

                # Calculate points for the line based on the direction vector and line padding
                point1 = (int(point_per_mask[1][0] - line_pad * direction_vector[0]),
                        int(point_per_mask[1][1] - line_pad * direction_vector[1]), )
                
                point2 = (int(point_per_mask[0][0] + line_pad * direction_vector[0]),
                        int(point_per_mask[0][1] + line_pad * direction_vector[1]), )

                # Visualize the line connecting the two points
                cv2.line(frame, point1, point2, color, 3)

                # Append the points for the current mask to the list of points per frame
                point_per_frame.append(point_per_mask)
        
        except Exception:
            print(color_name,' Failed!')
            return frame,[],[],[]

        # Calculate angles between consecutive lines
        angle_0 = self.calculate_angle(point_per_frame[0], point_per_frame[1])
        angle_1 = self.calculate_angle(point_per_frame[1], point_per_frame[2])
        angle_2 = self.calculate_angle(point_per_frame[2], point_per_frame[3])

        # Add text annotations to the frame with calculated angles
        frame = self.add_text_to_frame(frame, "ANGLE 0: {}".format(int(angle_0)), position=(1000, 810), font_scale=0.5, thickness=2, color=(255, 255, 0))
        frame = self.add_text_to_frame(frame, "ANGLE 1: {}".format(int(angle_1)), position=(1000, 830), font_scale=0.5, thickness=2, color=(255, 255, 0))
        frame = self.add_text_to_frame(frame, "ANGLE 2: {}".format(int(angle_2)), position=(1000, 850), font_scale=0.5, thickness=2, color=(255, 255, 0))

        return frame, angle_0, angle_1, angle_2


# %%
if __name__ == '__main__':
    import os,sys
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0,parentdir)

    from lib.GENERALFUNCTIONS import *

    # Constants
    ## For styling
    colors = [(255,0,0), (127,0,255), (0,127,0), (0,127,255)]
    line_padding = [0.7, 1.5,1.5,1.5]

    font_scale = 1
    text_position_cnt = (100, 100)
    text_position_time = (100, 120)
    
    video_name = "sc01.mp4"
    video_path = DATA_FOLDER + video_name #"../IMG_7102.MOV"
    output_folder_video = DATA_FOLDER + video_name.split('.')[0] +'/'# "../output/video"
    output_folder_csv = output_folder_video #"../output/csv"
    
    if not os.path.exists(output_folder_video):
        os.makedirs(output_folder_video)

    ## For algorithm tuning
    # Are for optime
    kernel = np.ones((5,5),np.uint8)
    threshold_area_size = [80, 20, 10, 40]
    frame_shift = 500
    set_fps = 150 # I dont know if its work

    tracker = AngleTracker()
    # Main logic
    cap = cv2.VideoCapture(video_path) 
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_shift)
    cap.set(cv2.CAP_PROP_FPS, set_fps)


    if not cap.isOpened():
        print("Error: Could not open the video file.")
        exit()

    # Create a window to display the frames
    cv_preview_wd_name = 'Video Preview'
    cv_choose_wd_name = 'Choose'

    cv2.namedWindow(cv_preview_wd_name, cv2.WINDOW_KEEPRATIO)


    measure = [] # for storing angles
    frames_to_store = []
    cnt = frame_shift # for storing frame count

    # Videos capture cycles
    while True:
        strt = time.time()
        ret, frame = cap.read()
        if not ret: break

        # if not cnt %10 ==0 :
        #     cnt += 1;continue
        # else: print(cnt)
        # if cnt > 3000:break
        
        if cnt==frame_shift:
            tracker.acquire_marker_color(frame)
            # cnt +=1

        frame, angle_0, angle_1, angle_2  = tracker.extract_angle(frame, False)
        # # Use the original frame instead of creating a copy
        # try: frame, angle_0, angle_1, angle_2  = tracker.extract_angle(frame, False)
        # except Exception as err: continue
        # if frame is None: continue
        # cv2.imshow('Video Preview', frame)

        # Add text to the frame
        frame = tracker.add_text_to_frame(frame, str(cnt), position=text_position_cnt, font_scale=font_scale)

        # Calculate and add time information
        end = time.time()
        frame = tracker.add_text_to_frame(frame, str(end - strt), position=text_position_time, font_scale=font_scale)
        measure.append([cnt, angle_0,angle_1,angle_2])
        
        frames_to_store.append(frame.copy())
        cnt += 1

        # print(cnt)
        cv2.imshow('Video Preview', frame)
        if cv2.waitKey(1) & 0xFF == 27: # cv2.waitKey(1000) & 0xFF == ord('q')
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\nFinished video extraction")

    ## Store processed video
    # Store the video with updated frames
    output_video_path = os.path.join(output_folder_video,f"{video_name.split('.')[0]}_extracted.mp4")  # Set the desired output video path
    tracker.store_video(frames_to_store, output_video_path, set_fps)

    ## Store csv - raw_angles
    df_angle = pd.DataFrame(data=measure, columns=["frame", "angle_0", "angle_1", "angle_2"])
    df_angle["time"] = df_angle["frame"] / set_fps
    df_angle.to_csv(os.path.join(output_folder_csv,f"{video_name.split('.')[0]}_extracted.csv"), index=False)
    # df_angle
