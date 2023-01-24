#!/bin/bash/python3 

# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu @ 20221020
# Modified @20230115

# if __name__=='__main__': # Test codes
from asyncore import read
from concurrent.futures import process
from logging import exception
import os,sys
from pickle import TRUE
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import numpy as np
import pyftdi.i2c as i2c
from matplotlib import pyplot as plt
import time

from lsm6ds3.LSM6DS3 import Lsm6ds3_01 as LSM
from pca9685.PCA9685 import Pca9685_01 as PCA
# import PCA9685.pca9685 as PCA9685

class SMAfingerMP_01(object):

    def __init__(self, i2c_controller=i2c.I2cController(),address=0x40, reset = False,debug=False):
        # print("New PCA9685 IIC slave created: ",hex(address))
        
        # Address Setting
        lsm_addr = 0x6b # Gryoscope address
        pca_addr = 0x40 # PWM device address

        wire_freq = 1000 # PWM freq for wire controling
        wire_channles = [12,14,0] # [Wire 1; Wire 2;Indicating LED]

        self.lsm_list, self.pca_list = [],[]
        # Instantiate an I2C controller
        i2c_controller = i2c.I2cController() # Create 

        # Open port
        # pyftdi
        # i2c_controller.configure()
        i2c_controller.configure('ftdi://ftdi:232h/') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78
        # USB\VID_0403&PID_6014\6&263914d5&0&2
        # USB\VID_0403&PID_6014\6&263914d5&0&1

        print('\n\n')
        lsm6ds3_A = LSM(i2c_controller,lsm_addr); lsm6ds3_A.reset()
        pca9685_A = PCA(i2c_controller,pca_addr,debug=False); pca9685_A.reset()

        self.lsm_list.append(lsm6ds3_A)
        self.pca_list.append(pca9685_A)

        # Set wire initial state
        pca9685_A.setPWMFreq(wire_freq); dutys = [0] # [预热 响应 维持]
        intervals = [0.1]; pca9685_A.test_wires(wire_channles,dutys,intervals,conf0=True)

        pass
    
    def calibrate(self): # 三轴角度校准
        pass

    def get_angle(self): # 静态角度获取
        lsm = self.lsm_list[0]
        reading = lsm.readSensors(1)
        print(reading)
        pass
    
    def drive_axis(self,dutyRatio,time):
        # _st = time.time()
        # self.pca_list[0].

        pass

    def to_angle(self,tar_angle): # 到达目标角度
        # 计算目前角度
        angle_curr = self.get_angle()
        return []
        angle_diff = angle_curr - tar_angle
        
        accuracy = 0.5 # 角度控制精度

        while abs(angle_diff) > accuracy:
            
            if angle_diff > 0: # angle_diff > accuracy
                pass
            else:  # angle_diff < -accuracy
                pass

            # out put pwm # 驱动
            angle_curr = self.get_angle() # 检测
            pass
        pass

    def a(self): pass

# process end here
import pyftdi.ftdi as ftdi
from multiprocessing import  Process

DUTYS =  [1,0.2]   # [预热 响应 维持]c
INTERVALS = [0.2,1]
DO_PLOT = False
if DO_PLOT: TIME_OUT = 10000
else: TIME_OUT = 10
FIG_FOLDER = "./IMG/"
RUNTIME = time.localtime()

LABELS = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']

def ctrlProcess(i2c_actuator_controller_URL=[],actuator_device=[]): # PCA 
    
    print("\nCtrlProcess Starts")
    # Address Setting
    pca_addr = 0x40 # PWM device address

    wire_freq = 1000 # PWM freq for wire controling
    wire_channles = [12,14,0] # [Wire 1; Wire 2;Indicating LED]

    # # Instantiate an I2C controller
    # i2c_actuator_controller = i2c.I2cController() # Create 
    # # Open port
    # i2c_actuator_controller.configure(i2c_url)

    # actuator_device = PCA(i2c_actuator_controller,pca_addr,debug=False); actuator_device.reset()
    if i2c_actuator_controller_URL==[]:
        print('Empty input of i2c_actuator_controller_URL, finding URL')
        actuator_device = findFtdiDevice(pca_addr)
    elif actuator_device==[]: 
        i2c_device = i2c.I2cController()
        # print(i2c_actuator_controller_URL)
        i2c_device.configure(i2c_actuator_controller_URL)
        actuator_device = PCA(i2c_device,debug=False)
        actuator_device.reset()

    # Set wire initial state
    actuator_device.setPWMFreq(wire_freq)
    
    # dutys = [0.1] # [预热 响应 维持]
    # intervals = [1]
    # actuator_device.test_wires(wire_channles,dutys,intervals,conf0=True)
    
    # experiment
    experiment_0(actuator_device,wire_channles)
    actuator_device.i2c_controller.close()
    pass

def experiment_0(actuator_device,wire_channles):
    dutys = DUTYS # [预热 响应 维持]
    intervals = INTERVALS
    actuator_device.test_wires(wire_channles,dutys,intervals,conf0=True)
    pass

def sense_LSM6DS3(i2c_sensor_controller_URL=[],sensor_device=[],do_plot=False): # NONE FIFO Version
    lsm_addr = 0x6b # Gryoscope address
    check_freq = 0.4 #S, EXIT check!
    check_interval = int(check_freq/0.017)

    if i2c_sensor_controller_URL==[]: sensor_device = findFtdiDevice(lsm_addr)
    elif sensor_device==[]:
        print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL)
        sensor_device =LSM(i2c_device)
        sensor_device.reset()        
        
    # plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]
    all_list = [[],[],[],[],[],[],[],[]]
    
    if not isinstance(sensor_device,LSM):print("Programe err! @ sense_LSM6DS3, pls check coding!"); exit()
    # Empty run for 1 sec
    t0 =  time.clock()
    sensor_device.changeRange()
    while time.clock()-t0 < 0.3: sensor_device.readSensors(1)

    # while run
    _t=0
    continue_sensor = True
    # do_plot=True
    if do_plot: plt.ion()
    figsize = (12.8,7.2)#(19.2,10.8)
    plt.figure(figsize=figsize)

    data = []
    t0 =  time.clock()
    # data.append(sensor_device.readSensors(1)); data[-1].append(t0)
    if do_plot: plot_counter = 0
    while continue_sensor:
        reading = sensor_device.readSensors(1)
        reading.append(time.clock()-t0)

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
                    plt.plot(data_np[:,-1],data_np[:,i],label = LABELS[i])
                plt.pause(0.001);plt.ioff()
        pass
    
    sensor_device.i2c_controller.close()
    return data

def sense_FIFO(i2c_sensor_controller_URL=[],do_plot=False): #  FIFO Version
    lsm_addr = 0x6b # Gryoscope address
    check_freq = 0.4 #S, EXIT check!
    check_interval = int(check_freq/0.017)

    if i2c_sensor_controller_URL==[]:
        sensor_device = findFtdiDevice(lsm_addr)
    else: 
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL,frequency = 400E3)
        sensor_device =LSM(i2c_device);sensor_device.reset()        

    # plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]
    all_list = [[],[],[],[],[],[],[],[]]
    
    # Empty run for 1 sec
    t0 =  time.clock()
    sensor_device.changeRange()
    while time.clock()-t0 < 0.3: sensor_device.readSensors(1)

    # while run
    _t=0
    continue_sensor = True
    # do_plot=True
    if do_plot: plt.ion()
    figsize = (12.8,7.2)#(19.2,10.8)
    plt.figure(figsize=figsize)

    data = []
    t0 =  time.clock()
    # data.append(sensor_device.readSensors(1)); data[-1].append(t0)

    while continue_sensor:
        reading = sensor_device.readSensors(1)
        reading.append(time.clock()-t0)

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

def sensorProcess(i2c_sensor_controller_URL=[],LSM_device=[],do_plot=False): # NONE FIFO Version

    print("\nSensorProcess Starts")

    if DO_PLOT:
        data = sense_LSM6DS3(i2c_sensor_controller_URL,LSM_device,do_plot)
    else:
        data = sense_LSM6DS3(i2c_sensor_controller_URL,LSM_device,do_plot)
        # data = sense_FIFO(i2c_sensor_controller_URL,do_plot)
        saveData(data,LABELS)
        saveFigure(data,LABELS)
    return []

def saveData(data,labels):
    file_url=FIG_FOLDER+ time.strftime("_%b%d_%H.%M",RUNTIME)+str(DUTYS)+str(INTERVALS)  +'.csv'

    header = str(labels).replace("'",'').replace("]",'').replace("[",'')

    np.savetxt(file_url,data, fmt='%.18e', delimiter=',', 
        newline='\n', header=header, footer='', comments='# ', encoding=None)

    pass

def saveFigure(data,labels,show_img=False):
    data_np = np.array(data)
    plt.clf() 
    plt.subplot(2,1,1)
    for _i in range(3): 
        i = _i+1
        plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
    plt.legend()

    plt.subplot(2,1,2)
    for _i in range(3): 
        i = _i+4
        plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
    plt.legend()
    
    file_name = time.strftime("_%b%d_%H.%M",RUNTIME)+str(DUTYS)+str(INTERVALS)  +'.pdf'
    print("Figure saving as: ",FIG_FOLDER+file_name)
    # plt.margins(0,0)
    plt.savefig(FIG_FOLDER+file_name,dpi=1000,bbox_inches = 'tight',pad_inches=0.1)

    if show_img: plt.show()
 
def findFtdiDevice(addr): # find corresbonding device 
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
            device = PCA(i2c_device_0,addr,debug=False); device.reset()
        except Exception as err: 
            print("\nErr @0x40",err)
            device = PCA(i2c_device_1,addr,debug=False); device.reset()

    elif addr == 0x6b: # Gryoscope address
        try: 
            device =LSM(i2c_device_0); device.reset()
        except Exception as err:
            print("\nErr @0x6b",err)
            
            device = LSM(i2c_device_1); device.reset()

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
            _PCA_device = PCA(_device); _PCA_device.reset()
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
            _LSM_device = LSM(_device); _LSM_device.reset()
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

if __name__=='__main__': # Test codes # Main process
    print("\n\n")
    print('Multi process version of SMA finger')
    print(time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    do_plot = DO_PLOT
 
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1') 
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/1')

    # url_PCA,url_LSM,PCA_device,LSM_device = findFtdiAddr()
    url_PCA = url_0
    url_LSM = url_1

    if url_PCA==[] or url_LSM==[]:
        print("Failed on finding PCA or LSM device addr:",url_PCA,url_LSM); exit()
    else : print("Found PCA, LSM device @:",url_PCA,url_LSM) 

    process_ctrl = Process(target= ctrlProcess,args=(url_PCA,[]))
    process_sensor = Process(target= sensorProcess, args=(url_LSM,[],do_plot))
    
    # print(url_PCA,url_LSM);exit()
    # case = 1
    # # i2c_device_0,i2c_device_1 = test_dual_ftdi()

    # # MP on
    # print("Two thread with Python threading library")
    # if case == 1:
    #     process_ctrl = Process(target= ctrlProcess,args=(url_0,))
    #     process_sensor = Process(target= sensorProcess, args=(url_1,do_plot))
    # else:
    #     process_ctrl = Process(target= ctrlProcess,args=(url_1,))
    #     process_sensor = Process(target= sensorProcess, args=(url_0,do_plot))


    process_sensor.start(); time.sleep(1)
    process_ctrl.start()

    # process_sensor.join();time.sleep(1)
    
    # process_ctrl.join()

    
    # exit()
    # finger = SMAfingerMP_01()
