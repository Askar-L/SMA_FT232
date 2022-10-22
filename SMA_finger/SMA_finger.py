# Class of SMA single finger robot
# Created by Askar. Liu @ 20221014

# if __name__=='__main__': # Test codes
from operator import contains
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import numpy as np
import pyftdi
import pyftdi.i2c as i2c
from matplotlib import pyplot as plt
import time

from lsm6ds3.LSM6DS3 import Lsm6ds3_01 as LSM
from pca9685.PCA9685 import Pca9685_01 as PCA
# import PCA9685.pca9685 as PCA9685

class SMAfinger_01(object):

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
        pyftdi
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

def test():
    # print(os.environ.items())
    # ftdi_devices = []
    # for _item in os.environ.items():
    #     print(_item)
    #     # if _item.index('ftdi'): ftdi_devices.append(_item)
    #     pass
    # print('ftdi_devices: ',ftdi_devices)

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
    slave = i2c_device.get_port(addr)
    gpio = i2c_device.get_gpio()
    gpio.set_direction(0x0010, 0x0010)
    gpio.write(0)
    gpio.write(1<<4)
    gpio.write(0)
    slave.write([0x12, 0x34])
    gpio.write(0)
    gpio.write(1<<4)
    gpio.write(0)

if __name__=='__main__': # Test codes
    test()
    exit()
    finger = SMAfinger_01()

    finger.lsm_list[0].changeRange(2,2000)
    finger.to_angle(90)

    plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]; all_list = [[],[],[],[],[],[],[]]
    labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z']
    
    for t in range(400): # time step
        axis_x.append(t)
        [temp,LA_reading,AR_reading] = finger.lsm_list[0].readSensors()
        y_list.append(LA_reading[0])
    
    plt.plot(axis_x,y_list,label = labels[1])
    plt.pause(0.001)
    print('OK')
    # time.sleep(1000)
    exit()

    for t in range(10000): # time step
        axis_x.append(t); plt.clf() 
        [temp,LA_reading,AR_reading] = finger.lsm_list[0].readSensors()
        y_list.append(LA_reading[0])
        plt.plot(axis_x,y_list,label = labels[1])
        plt.pause(0.001); plt.ioff()

    pass
    # plt.ion()
    # axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]; all_list = [[],[],[],[],[],[],[]]
    # labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z']

    # for t in range(10000): # time step
    #     axis_x.append(t); plt.clf() 

    #     res = LSM.readHighSpeed() # 0.021474266052246095 S
    #     # print("It uses: ",ed-st,"S")
    #     for _i in range(3): 
    #         i = _i+1
    #         all_list[i].append(res[i])
    #         plt.plot(axis_x,all_list[i],label = labels[i])
    #     plt.pause(0.001); plt.ioff()
    #     pass