#!/bin/bash/python3 

# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu @ 20221020

# if __name__=='__main__': # Test codes
from concurrent.futures import process
from logging import exception
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import numpy as np
import pyftdi.i2c as i2c
from matplotlib import pyplot as plt
import time,pyftdi

from multiprocessing import Queue

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
        i2c_controller.configure('ftdi://ftdi:232h/1') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78

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
        reading = lsm.readSensors()
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

def test_dual_ftdi(): # 
    ctrl_ftdi = 0
    sens_ftdi = 1

    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:'+ctrl_ftdi+'/1') # ftdi://ftdi:232h/1 ftdi:///1 'ftdi://ftdi:232h:1'
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:'+sens_ftdi+'/1') # ftdi://ftdi:232h/1 ftdi:///1 'ftdi://ftdi:232h:1'
    print("\nURL 0 \t",url_0)
    print("\nURL 1 \t",url_1)

    address = os.environ.get('I2C_ADDRESS', '0x50').lower()
    addr = int(address, 16 if address.startswith('0x') else 10) # into dec
    print("\address \t",address)
    print("\addr \t",addr)
    
    i2c_device_0 = i2c.I2cController();i2c_device_1 = i2c.I2cController()
    i2c_device_0.configure(url_0,frequency = 400E3)
    i2c_device_1.configure(url_1,frequency = 400E3)
    
    return []

def ctrlProcess(i2c_url):
    print("\nCtrlProcess Starts")
    # Address Setting
    pca_addr = 0x40 # PWM device address

    wire_freq = 1000 # PWM freq for wire controling
    wire_channles = [12,14,0] # [Wire 1; Wire 2;Indicating LED]

    # Instantiate an I2C controller
    i2c_actuator_controller = i2c.I2cController() # Create 
    # Open port
    i2c_actuator_controller.configure(i2c_url,frequency = 400E3)

    actuator_device = PCA(i2c_actuator_controller,pca_addr,debug=False); actuator_device.reset()

    # Set wire initial state
    actuator_device.setPWMFreq(wire_freq)
    dutys = [0.1] # [预热 响应 维持]
    intervals = [1]
    actuator_device.test_wires(wire_channles,dutys,intervals,conf0=True)
    
    pass

def sensorProcess(i2c_url,do_plot=False):
    print("\nSzensorProcess Starts")

    lsm_addr = 0x6b # Gryoscope address

    check_freq = 2 #S
    check_interval = int(check_freq/0.17)

    i2c_sensor_controller = i2c.I2cController()    
    i2c_sensor_controller.configure(i2c_url,frequency = 400E3)
    sensor_device = LSM(i2c_sensor_controller); sensor_device.reset()

    # plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]; all_list = [[],[],[],[],[],[],[]]
    labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z']

    data = []
    continue_sensor = True;stop_signal = False

    # test run 
    data.append(sensor_device.readHighSpeed(0,7)) # 0.021474266052246095 S
    # print("_res:",_res)

    # while run
    _t=0
    time_out = 1000
    while continue_sensor:
        data.append(sensor_device.readHighSpeed()) # 0.021474266052246095 S

        if _t % check_interval ==0: stop_signal: continue_sensor = False
        elif _t>time_out: continue_sensor = False

        _t+=1        
        if do_plot:
            plt.clf(); axis_x.append(_t)
            for _i in range(3): 
                i = _i+1
                all_list[i].append(data[-1][i])
                plt.plot(axis_x,all_list[i],label = labels[i])
            plt.pause(0.001); plt.ioff()
        pass
    
    # process end here

from multiprocessing import  Process
if __name__=='__main__': # Test codes # Main process
    print("\n\n")
    print('Multi process version of SMA finger')
    # test_dual_ftdi()

    #Ftdi Addr
    url_0 = "ftdi://ftdi:232h:0/1"
    url_1 = "ftdi://ftdi:232h:1/1"
    # ctrlProcess(url_0)
    # sensorProcess(url_1)

    # MP on
    print("Two thread with Python threading library")

    process_ctrl = Process(target= ctrlProcess,args=(url_0,))
    do_plot = True
    process_sensor = Process(target= sensorProcess, args=(url_1,do_plot))

    process_sensor.start()
    time.sleep(1)
    process_ctrl.start()
    time.sleep(1)
    process_ctrl.join()
    time.sleep(1)
    process_sensor.join()

    exit()
    finger = SMAfingerMP_01()
