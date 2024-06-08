# This file is to find out how to read sensoe values of LSM6DS3

# import lib.LSM6DS3.lsm6ds3 as LSM6DS3
sys.path.append("..")

import time
import numpy as np
from matplotlib import pyplot as plt
from lib.LSM6DS3.lsm6ds3 import LSM6DS3mb as LSM6DS3
import lib.PCA9685.pca9685 as PCA9685

import pyftdi.i2c as i2c

if __name__=='__main__':
        
    lsm_addr = 0x6b; pca_addr = 0x40

    wire_freq = 1000

    wire_channles = [12,14,0]

    # Instantiate an I2C controller
    i2c_controller = i2c.I2cController()

    # Configure the first interface (IF/1) of the FTDI device as an I2C master
    i2c_controller.configure('ftdi:///1') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78


    print('\n\n')

    lsm6ds3 = LSM6DS3(i2c_controller,lsm_addr,False,pause=0.8); lsm6ds3.reset()
    pca9685 = PCA9685.Device(i2c_controller,pca_addr,False,easy_mdoe=True); pca9685.reset()
    
    # Set wire initial state
    pca9685.setPWMFreq(wire_freq); dutys = [0] # [预热 响应 维持]
    intervals = [0.1]; pca9685.test_wires(wire_channles,dutys,intervals,conf0=True)

    plt.ion()
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]; all_list = [[],[],[],[],[],[],[]]
    labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z']

    reading_time=[]
    for t in range(100): # time step
        axis_x.append(t); plt.clf() 

        st = time.time()      
        res = lsm6ds3.readHighSpeed() # 0.021474266052246095 S
        # ed = time.time()
        reading_time.append(time.time()-st)

    print(np.mean(reading_time))
    exit()