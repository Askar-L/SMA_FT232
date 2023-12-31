#!/bin/bash/python3 

# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu @ 20221020
# Modified @20230221: Add logger

# General funcs
import os,sys,time,multiprocessing
import numpy as np
from matplotlib import pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

# Driver funcs
import pyftdi.i2c as i2c

from lsm6ds3.LSM6DS3 import Lsm6ds3_01 as IMUCHIP
from pca9685.PCA9685 import Pca9685_01 as PWMGENERATOR
from ads1115.TIADS1115 import HW526Angle as ANGLESENSOR

from lib.GENERALFUNCTIONS import *
sys.stdout = Logger()
sys.stderr = sys.stdout		# redirect std err, if necessary

# Test settings
import pyftdi.ftdi as ftdi
from multiprocessing import  Process


if True: # Experiment settings
    
    RESTING = 0

    DO_PLOT = False
    if DO_PLOT: TIME_OUT = 10000
    else: TIME_OUT = 20 + RESTING
    VOT = 9 # Vlots
    LOAD = 20 # Grams

    EXIT_CHECK_FREQ = 1 #S, EXIT check!

    print('Multi process version of SMA finger')
    print("Current time",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    print("RUNTIME",time.strftime('%m.%dth,%HH:%MM:%SS .%F', time.localtime(RUNTIME)))
    
    # RUNTIME = time.time()

    do_plot = DO_PLOT
    
    act_type = 2
    act_types = {0:"SMA",1:"TSMA",2:"CTSMA",3:"SSA"}
    
def print_info(dutys_P,intervals_P):

    print("Expriment data:\n")
    print("\t act_type:\t",act_types[act_type])
    
    print("\t DUTYS:    \t",dutys_P,"%")
    print("\t INTERVALS:\t",intervals_P,"Sec")

    print("\t VOT: \t",VOT,"Volts")
    print("\t LOAD: \t",LOAD,"Grams")

    print("\t DO_PLOT:\t",DO_PLOT)
    # print("\t TIME_OUT:\t",TIME_OUT,"Sec")
    # print("\t LABELS:\t",LABELS)
    print("\t EXIT_CHECK_FREQ:\t",EXIT_CHECK_FREQ)

    print("\n\n")

# class SMAfingerMP_01(object):

#     def __init__(self, i2c_controller=i2c.I2cController(),address=0x40, reset = False,debug=False):
#         # print("New PCA9685 IIC slave created: ",hex(address))
        
#         # Address Setting
#         lsm_addr = 0x6b # Gryoscope address
#         pca_addr = 0x40 # PWM device address

#         wire_freq = 1526 # Default PWM freq for wire controling
#         wire_channles = [12,14,0] # [Wire 1; Wire 2;Indicating LED]

#         self.lsm_list, self.pca_list = [],[]
#         # Instantiate an I2C controller
#         i2c_controller = i2c.I2cController() # Create 

#         # Open port
#         # i2c_controller.configure()
#         i2c_controller.configure('ftdi://ftdi:232h/') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78
#         # USB\VID_0403&PID_6014\6&263914d5&0&2
#         # USB\VID_0403&PID_6014\6&263914d5&0&1

#         print('\n\n')
#         lsm6ds3_A = IMUCHIP(i2c_controller,lsm_addr); lsm6ds3_A.reset()
#         pca9685_A = PWMGENERATOR(i2c_controller,pca_addr,debug=False); pca9685_A.reset()

#         self.lsm_list.append(lsm6ds3_A)
#         self.pca_list.append(pca9685_A)

#         # Set wire initial state
#         pca9685_A.setPWMFreq(wire_freq); dutys = [0] # [预热 响应 维持]
#         intervals = [0.1]; pca9685_A.test_wires(wire_channles,dutys,intervals,conf0=True)

#         pass
    
#     def calibrate(self): # 三轴角度校准
#         pass

#     def get_angle(self): # 静态角度获取
#         lsm = self.lsm_list[0]
#         reading = lsm.readSensors(1)
#         print(reading)
#         pass
    
#     def drive_axis(self,dutyRatio,time):
#         # _st = time.time()
#         # self.pca_list[0].
#         pass

#     def to_angle(self,tar_angle): # 到达目标角度
#         # 计算目前角度
#         angle_curr = self.get_angle()
#         return []
#         angle_diff = angle_curr - tar_angle
        
#         accuracy = 0.5 # 角度控制精度

#         while abs(angle_diff) > accuracy:
            
#             if angle_diff > 0: # angle_diff > accuracy
#                 pass
#             else:  # angle_diff < -accuracy
#                 pass

#             # out put pwm # 驱动
#             angle_curr = self.get_angle() # 检测
#             pass
#         pass

# Start of program
 
def showMPTestProcess(i2c_actuator_controller_URL=[],angle_sensor_ID="SNS000",process_share_dict={}):
    while True:
        print(process_share_dict[angle_sensor_ID])
    pass 

def findFtdiDevice(addr): # find corresbonding device 
    device = []
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1')  # ftdi://ftdi:232h:0/1
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/1') 
    # ftdi://ftdi:232h/1 ftdi:///1 'ftdi://ftdi:232h:1'

    # address = os.environ.get('I2C_ADDRESS', '0x50').lower()
    # addr = int(address, 16 if address.startswith('0x') else 10) # into dec
    # # print("\address \t",address)
    # # print("\addr \t",addr)
    
    i2c_device_0 = i2c.I2cController();i2c_device_1 = i2c.I2cController()
    i2c_device_0.configure(url_0,frequency = 400E3)
    i2c_device_1.configure(url_1,frequency = 400E3)
    
    if addr == 0x40: # PCA 
        try: 
            device = PWMGENERATOR(i2c_device_0,addr,debug=False); device.reset()
        except Exception as err: 
            print("\nErr @0x40",err)
            device = PWMGENERATOR(i2c_device_1,addr,debug=False); device.reset()

    elif addr == 0x6b: # Gryoscope address
        try: 
            device =IMUCHIP(i2c_device_0); device.reset()
        except Exception as err:
            print("\nErr @0x6b",err)
            
            device = IMUCHIP(i2c_device_1); device.reset()

    return device

def findFtdiAddr(): 
    # find corresbonding device 
    # https://eblot.github.io/pyftdi/urlscheme.html
    print('Finding correspoonding FTDI addr')
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1')  # ftdi://ftdi:232h:0/1
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/1') 
    # url_2 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FD/1') 

    url_list = [url_0,url_1]

    i2c_addr_PCA = 0x40
    i2c_addr_LSM = 0x6b
    addr_PCA,addr_LSM = [],[]
    _PCA_device,_LSM_device = [],[] 
    device_list = []
    # for _url in url_list: device_list.append(i2c.I2cController())

    # for _device in device_list:
    _device = i2c.I2cController()
    for _url in url_list:
        try:
            _device.configure(_url,frequency = 400E3)
            _PCA_device = PWMGENERATOR(_device); _PCA_device.reset()
            # _PCA_device.testChannle(0)
            addr_PCA = _url
            url_list.remove(_url)
            print("Found PCA addr:",addr_PCA)
            break
        except Exception as err:  continue

    # for _device in device_list:
    for _url in url_list:
        try:
            _device.configure(_url,frequency = 400E3)
            _LSM_device = IMUCHIP(_device); _LSM_device.reset()
            addr_LSM = _url
            url_list.remove(_url)
            print("Found LSM addr:",addr_LSM)
            break
        except Exception as err:  continue
    
    return addr_PCA,addr_LSM,_PCA_device,_LSM_device

def i2c_test():

    usb_tool = ftdi.UsbTools()
    ftdi_devices = usb_tool.find_all( [[1027,24596]])
    # ftdi_devices = usb_tool.find_all([[1027]])
    print("\n",ftdi_devices)

    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1') 
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/1') 
    # s.environ.get('FTDI_DEVICE','USB\VID_0403&PID_6014\6&263914D5&0&2') # ftdi:// [1027][:[24596][:|:0:254|:]] /1

    i2c_device_0 = i2c.I2cController();i2c_device_1 = i2c.I2cController()
    i2c_device_0.configure(url_0,frequency = 400E3)
    i2c_device_0.configure(url_1,frequency = 400E3)

    #Ftdi Addr
    # devices = pyftdi.list_devices()
    # print(devices)
 
    # 'ftdi://{}:{}:{}/{}'.format(idn.vid,idn.pid,idn.sn, idn.address)
    # ftdi://[vendor][:[product][:serial|:bus:address|:index]]/interface
    # ftdi[:232h[: :0:254|:]]/1

    # ftdi://1027:24569:
    # USB\VID_0403&PID_6014\6&263914d5&0&2 
        # ftdi://[VID_0403][:[PID_6014][:serial|:bus:address|:index]]/interface
    # USB\VID_0403&PID_6014\6&263914d5&0&1

    return []


def experiment_actuators(actuator_device): # Actuators Experiment 1
    wire_channles_P = [12,0] # DR[0.09, 1, 0.2, 0.14, 0.1, 0] Duration[1, 0.3, 2, 2, 2, 2]
    # fan_channles = [4,6] 
    
    # Positive derections
    DUTYS_P = [0.4,0]# [1,0.2]   # [预热 响应 维持]c 
    INTERVALS_P =[2,0.1]# [0.2,1]
    
    # # Reversed derections
    # DUTYS_M = [1,0.3]# [1,0.2]   # [预热 响应 维持]c
    # INTERVALS_M =[0.2,2]# [0.2,1]

    print_info(DUTYS_P,INTERVALS_P)
    # actuator_device.test_wires(fan_channles,DUTYS_P,INTERVALS_P,conf0=True)
    
    actuator_device.test_wires(wire_channles_P,DUTYS_P,INTERVALS_P,conf0=True)
    # Extensor direction: DR [1,0.3] Duration [0.2,2]
    # actuator_device.test_wires(wire_channles_M,DUTYS_M,INTERVALS_M,conf0=True)

    pass
 
def sensor_LSM6DS3(i2c_sensor_controller_URL=[],sensor_device=[],do_plot=False,lables=[]): # NONE FIFO Version
    # LABELS = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']

    lsm_addr = 0x6b # Gryoscope address
    check_interval = int(EXIT_CHECK_FREQ/0.001)

    if i2c_sensor_controller_URL==[]: sensor_device = findFtdiDevice(lsm_addr)
    elif sensor_device==[]:
        print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL)
        sensor_device =IMUCHIP(i2c_device)
        sensor_device.reset()        
        sensor_device.setRange()
        
    # plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]
    all_list = [[],[],[],[],[],[],[],[]]
    
    if not isinstance(sensor_device,IMUCHIP):print("Programe err! @ sense_LSM6DS3, pls check coding!"); exit()

    # # Empty run for 1 sec
    # t0 =  time.clock()
    # while time.clock()-t0 < 0.3: sensor_device.readSensors(1)

    # while run
    _t=0
    continue_sensor = True
    # do_plot=True
    if do_plot: 
        plt.ion()
        figsize = (12.8,7.2)#(19.2,10.8)
        plt.figure(figsize=figsize)

    data = []
    if do_plot: plot_counter = 0
    while continue_sensor:
        reading = sensor_device.readSensors(1)
        reading.append(time.time()-RUNTIME)

        data.append( reading ) # 0.021474266052246095 S
        # print(reading)

        if _t % check_interval ==0: 
           print("\rSensor reading, continued for: ",reading[-1],"s",end='')
           if reading[-1] > TIME_OUT: 
            print("\nSensor reading Over due to time out: ",TIME_OUT);continue_sensor = False
        _t+=1

        if do_plot:
            plot_counter+=1
            if plot_counter == 20:
                data_np = np.array(data)
                plot_counter = 0
                plt.clf(); axis_x.append(_t)
                for _i in range(3): 
                    i = _i+1+3
                    # all_list[i].append(data[-1][i])
                    # print()
                    # print(data_np[:,i])
                    plt.plot(data_np[:,-1],data_np[:,i],label = lables[i])
                plt.pause(0.001);plt.ioff()
        pass
    
    sensor_device.i2c_controller.close()
    return data

def sense_LSM_FIFO(i2c_sensor_controller_URL=[],do_plot=False): #  FIFO Version
    lsm_addr = 0x6b # Gryoscope address
    check_interval = int(EXIT_CHECK_FREQ/0.017)

    if i2c_sensor_controller_URL==[]:
        sensor_device = findFtdiDevice(lsm_addr)
    else: 
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL,frequency = 400E3)
        sensor_device =IMUCHIP(i2c_device);sensor_device.reset()        

    # plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]
    all_list = [[],[],[],[],[],[],[],[]]
    
    # # Empty run for 1 sec
    # t0 =  time.clock()
    # while time.clock()-t0 < 0.3: sensor_device.readSensors(1)

    # while run
    _t=0
    continue_sensor = True
    # do_plot=True
    if do_plot: 
        plt.ion()
        figsize = (12.8,7.2)#(19.2,10.8)
        plt.figure(figsize=figsize)

    data = []
 
    while continue_sensor:
        reading = sensor_device.readSensors(0)
        reading.append(time.clock()-RUNTIME)

        data.append( reading ) # 0.021474266052246095 S
        # print(reading)

        if _t % check_interval ==0: 
           print("\rSensor reading, continued for: ",reading[-1],"s",end='')
           if reading[-1] > TIME_OUT: 
            print("\nSensor reading Over due to time out: ",TIME_OUT);continue_sensor = False
        _t+=1

        if do_plot:
            plt.clf(); axis_x.append(_t)
            for _i in range(3): 
                i = _i+1
                all_list[i].append(data[-1][i])
                plt.plot(axis_x,all_list[i],label = LABELS[i])
            plt.pause(0.001); plt.ioff()
        pass
    
    sensor_device.i2c_controller.close()
    return data

def sense_ADS1115(i2c_sensor_controller_URL=[],adc_01=[],do_plot=False,mode=[],lables=[],
                  sensor_ID="ADC000",process_share_dict={}): # TODO
    print("sense_ADS1115 starts at: ",time.time()- RUNTIME,"s, Related to ",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)) )
    ads_addr = 0x48 # ADS1115 address
    check_interval = int(EXIT_CHECK_FREQ/0.0008)

    if i2c_sensor_controller_URL==[]: adc_01 = findFtdiDevice(ads_addr)
    elif adc_01==[]:
        print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL)

    if "Angle" in mode:
        adc_01 =ANGLESENSOR(i2c_device,name="angle_sensor_01")
        _url=[]

    elif "Volta" in mode: 
        adc_01 =ANGLESENSOR(i2c_device,name="SSA_defalut")
        _url = DATA_FOLDER + "SSA_defalut" + ".json"

        # sensor_device.reset()        
    # mode
    adc_01.loadCalibration(_url) # BUG!!!! TODO

    T,A0,A1,A2,A3 = [],[],[],[],[]
    # if not isinstance(angle_sensor_01,ANGLESENSOR):print("Programe err! @ sense_ADS1115, pls check coding!"); exit() 

    adc_01.startConversion(data_rate=860,is_continue=True,is_show=False)    
    # # Empty run for 1 sec
    # t0 =  time.clock()
    # while time.clock()-t0 < 0.3: sensor_device.readSensors(1) 

    # while run
    _t=0
    continue_senseing = True
    # do_plot=True
    if do_plot: 
        plt.ion()
        figsize = (12.8,7.2)#(19.2,10.8)
        plt.figure(figsize=figsize)

    data = []
    if do_plot: plot_counter = 0

    # temp_i = 0
    while continue_senseing:
        reading = adc_01.readSensors(is_show=False)
        reading.append( time.time()- RUNTIME)

        data.append( reading ) # 0.021474266052246095 S
        process_share_dict[sensor_ID] = reading
        # print(temp_i,process_share_dict[sensor_ID]);temp_i += 1

        # process_share_dict.update({sensor_ID:reading})


        if _t % check_interval ==0: 
           print("\rSensor reading, continued for: ",reading[-1],"s",end='')
           if reading[-1] > TIME_OUT: 
            print("\nSensor reading Over due to time out: ",TIME_OUT);continue_senseing = False
        _t+=1

        if do_plot:
            plot_counter+=1
            if plot_counter == 20:
                plot_counter = 0                
                data_np = np.array(data)

                plt.clf(); A0.append(_t)
                for _i in range(data_np.shape[1]-1): 
                    plt.plot(data_np[-800:,-1],data_np[-800:,_i],label = lables[_i])
                plt.pause(0.001);plt.ioff()
        pass
    
    adc_01.i2c_controller.close()
    return data

def sensorProcess(mode="Angle",i2c_sensor_controller_URL=[],LSM_device=[],
                  do_plot=False,sensor_ID="SNS000",save_data = True,process_share_dict={}): # NONE FIFO Version
    PROCESSRUNTIME = time.time()
    url = i2c_sensor_controller_URL

    print("\nSensorProcess Starts:",PROCESSRUNTIME,"With sensor: ",mode)
    print("\t",PROCESSRUNTIME- RUNTIME,"s after runtime:",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)))

    if mode =="Angle": 
        labels = ['Joint Angle','Time'];figure_mode = 'Single'
        data = sense_ADS1115(url,[],do_plot,mode,labels,sensor_ID,process_share_dict)

    elif mode =="Volta": 
        labels = ['Voltage','Time']; figure_mode = 'Single'
        data = sense_ADS1115(url,[],do_plot,mode,labels,sensor_ID,process_share_dict)

    elif mode =="IMU": 
        labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']
        data = sensor_LSM6DS3(url,LSM_device,do_plot,labels)
        figure_mode = 'Double'
        # data = sense_LSM6DS3(i2c_sensor_controller_URL,LSM_device,do_plot)
        # data = sense_FIFO(i2c_sensor_controller_URL,do_plot)

    if save_data:
        file_name = mode+time.strftime("_%b%d_%H.%M.%S",time.localtime(RUNTIME))

    # saveData(data,file_name,labels)
    # saveFigure(data,file_name,labels,figure_mode=figure_mode)

def ctrlProcess(i2c_actuator_controller_URL=[],angle_sensor_ID="SNS000",process_share_dict={}): # PCA 
    
    PROCESSRUNTIME = time.time()
    print("\nCtrlProcess Starts:",PROCESSRUNTIME)
    print("\t",PROCESSRUNTIME- RUNTIME,"s after runtime:",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)))
    
    # Address Setting
    pca_addr = 0x40 # PWM device address
    wire_freq = 1526 # PWM freq for wire controling
    # wire_channles = [12,0] # [Wire 1; Wire 2;Indicating LED]

    # # Instantiate an I2C controller
    # i2c_actuator_controller = i2c.I2cController() # Create 
    # # Open port
    # i2c_actuator_controller.configure(i2c_url)
    actuator_device=[] 
    # actuator_device = PCA(i2c_actuator_controller,pca_addr,debug=False); actuator_device.reset()
    if i2c_actuator_controller_URL==[]:
        print('Empty input of i2c_actuator_controller_URL, finding URL')
        actuator_device = findFtdiDevice(pca_addr)
    elif actuator_device==[]: 
        i2c_device = i2c.I2cController()
        # print(i2c_actuator_controller_URL)
        i2c_device.configure(i2c_actuator_controller_URL) # On IIC 
        actuator_device = PWMGENERATOR(i2c_device,debug=False) # Link PCA9685
        actuator_device.reset()

    # Set wire initial state
    actuator_device.setPWMFreq(wire_freq) 
    experiment_actuators(actuator_device)     
    actuator_device.i2c_controller.close()
    pass 

def pid_to(target_angle,get_angle,apply_DR):
    from simple_pid import PID
    import math
    # ratio = 0.02
    (k_p, k_i, k_d) = (160,40,4) # (6,2.8,1) #(160,40,4)#(20,20,4)#(16,20.5,0.28)# (3.8,10,0.1)#Extensor (2.8,4,0.02) Flexor(2.5,2.35,0.068) # (60,80,4) *0.02 (160,80,3)
    T_exp = 10
    R_exp = 0
    print("\n\nWith PID parameters:", (k_p, k_i, k_d))
    print("PID following: sin wave of T=",T_exp,' Amplitude: ',R_exp,' degree of mean: ',target_angle)
    DR_limit = 100/2
    limit_DR =  (-DR_limit,DR_limit)                    
    durance = TIME_OUT -0.5
    
    # P调大，反应速度快了，但是出现了超调，指针出现抖动，
    # I调大，在原来基础上，误差变小了
    # D调大，反应速度慢了，但是抖动消失了，且指针存在一定误差（没和下面对准）
    # 初始PWM占空比和目标角度
    dutyRatio = 0  # 读取到当前的PWM 占空比 # (个人习惯)占空比 此处采用DR(dutyRatio)
    
    contorller = PID(k_p, k_i, k_d,sample_time=1/1200,output_limits= limit_DR) # # 创建PID控制器
    contorller.setpoint = target_angle

    time_st = time.time()
    ctrl_DR_history = []
    
    while True: # abs(current_angle - target_angle) > 0.05
        current_t = time.time()- RUNTIME
        current_angle = get_angle()  # 获取当前角度
        
        if current_t < RESTING: current_target = current_angle + current_t*5
        else: current_target = target_angle + R_exp * math.sin( (2*math.pi)*current_t/T_exp)

        contorller.setpoint = current_target
        # current_DR = pid_pwm_control(contorller,current_angle, target_angle, current_DR, k_p, k_i, k_d,output_limits)# 调整PWM占空比  
        pid_output = contorller(current_angle)            # 计算PID控制输出

        # dutyRatio =  max(limit_DR[0], min(limit_DR[1], pid_output)) # 确保PWM占空比保持在给定范围内 pid_output*output_limits*0.01 #
        
        apply_DR(pid_output) # 打印出来PWM/实际系统中是应用在系统里
        # print(f"Current Angle: {current_angle:.2f}°, PWM Duty Cycle: {current_DR:.2f}%")
        # print("Adjusting, Tar: ",target_angle," Cur delta:",current_angle-target_angle," DR: ",pid_output)
        if not (current_t < durance): break
        ctrl_DR_history.append([current_angle,pid_output,current_target,current_t]) # pid_output*100/(limit_DR[1])

    apply_DR(0)
    return ctrl_DR_history

def pidProcess(i2c_actuator_controller_URL=[],angle_sensor_ID="SNS000",process_share_dict={}): # PCA 
    PROCESSRUNTIME = time.time()
    print("\nCtrlProcess Starts:",PROCESSRUNTIME)
    print("\t",PROCESSRUNTIME- RUNTIME,"s after runtime:",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)))
    mode = 'PID'; labels = ['Angle','DutyRatio','Target','Time']

    # Address Setting
    pca_addr = 0x40 # PWM device address
    wire_freq = 1526 # PWM freq for wire controling
    actuator_device=[] 
    if i2c_actuator_controller_URL==[]:
        print('Empty input of i2c_actuator_controller_URL, finding URL')
        actuator_device = findFtdiDevice(pca_addr)
    elif actuator_device==[]: 
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_actuator_controller_URL) # On IIC 
        actuator_device = PWMGENERATOR(i2c_device,debug=False) # Link PCA9685
        actuator_device.reset()

    # current_angle = process_share_dict[angle_sensor_ID]
    # Set wire initial state
    actuator_device.setPWMFreq(wire_freq) 
 
    def get_angle(): return process_share_dict[angle_sensor_ID][0]
    
    def apply_DR(DR=0):
        DR = DR*0.01
        wire_channles_P = [12,0]
        wire_channles_N = [14,0]
        fan_channles_P = [4]
        fan_channles_N = [6]

        fan_max = 1/2 #0.55
        DR_middle = 0

        if DR > DR_middle: # Upper activation # Positive 
            actuator_device.setDutyRatioCHS(wire_channles_N,0,stop_sending=False)
            # actuator_device.setDutyRatioCHS(fan_channles_N,fan_max,stop_sending=False)
            # actuator_device.setDutyRatioCHS(fan_channles_P,0,stop_sending=False)
            actuator_device.setDutyRatioCHS(wire_channles_P,DR-DR_middle)

        elif DR < DR_middle: # Lower activation # Negative
            actuator_device.setDutyRatioCHS(wire_channles_P,0,stop_sending=False)
            # actuator_device.setDutyRatioCHS(fan_channles_P,fan_max,stop_sending=False)
            # actuator_device.setDutyRatioCHS(fan_channles_N,0,stop_sending=False)
            actuator_device.setDutyRatioCHS(wire_channles_N,-DR)

        elif DR == DR_middle: # # None activation 

            actuator_device.setDutyRatioCHS(wire_channles_P,0,stop_sending=False)
            actuator_device.setDutyRatioCHS(wire_channles_N,0,stop_sending=False)
            actuator_device.setDutyRatioCHS(fan_channles_P,fan_max,stop_sending=False)
            actuator_device.setDutyRatioCHS(fan_channles_N,fan_max)
            # actuator_device.setDutyRatioCHS(wire_channles_N,0)
            pass
            ###

    # Ctrl part
    ctrl_DR_history = []

    target_angle = 0 #40
    ctrl_DR_history.extend( pid_to(target_angle,get_angle,apply_DR) )
    actuator_device.i2c_controller.close()

    # Final figures
    file_name = mode+time.strftime("_%b%d_%H.%M.%S",time.localtime(RUNTIME))

    saveData(ctrl_DR_history,file_name,labels)
    saveFigure(ctrl_DR_history,file_name,labels,figure_mode='Single')

    pass 


if __name__=='__main__': # Test codes # Main process
    
    # Log experiment details
        # console recoder
        # data logger
        # expriment setting log  

    # Start of IIC comunication
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/0') 
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/0')
    url_2 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FD/1')
    url_3 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FC/1')

    # MP on
    print("SMA Finger MultiProcess: \nTwo thread with Python threading library")
         # url_PCA,url_LSM,PCA_device,LSM_device = findFtdiAddr()

    case = 0
    if case == 1: url_Control = url_1; url_Sensor = url_0
    else: url_Control = url_0; url_Sensor = url_1

    # # i2c_device_0,i2c_device_1 = test_dual_ftdi()
    if url_Control==[] or url_Sensor==[]:
        print("Failed on finding USB FT232H device addr:",url_Control,url_Sensor); exit()
    else : print("Found USB FT232H device @:",url_Control,url_Sensor) 


    with multiprocessing.Manager() as process_manager:
        process_share_dict = process_manager.dict()
        angle_sensor_ID = 'ADC001'
        
        process_sensor_ADC = multiprocessing.Process( target= sensorProcess, args=("Angle",url_1,[],do_plot,'ADC001',False,process_share_dict))
        # process_sensor_ADC = Process( target= sensorProcess, args=("Volta",url_Sensor,[],do_plot))
        # process_sensor_IMU = Process( target= sensorProcess, args=("IMU",url_2,[],do_plot))

        # process_ctrl = multiprocessing.Process(target= ctrlProcess,args=(url_0,'ADC001',process_share_dict))     

        process_ctrl = multiprocessing.Process(target= pidProcess,args=(url_0,'ADC001',process_share_dict))     

        process_sensor_ADC.start()
        # process_sensor_IMU.start()

        # time.sleep(0.6)
        process_ctrl.start()

        process_sensor_ADC.join()


    pass