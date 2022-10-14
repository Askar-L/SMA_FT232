# This file is to find out how to read sensoe values of LSM6DS3
# import lib.LSM6DS3.lsm6ds3 as LSM6DS3
import time
from matplotlib import pyplot as plt
from lib.LSM6DS3.lsm6ds3 import LSM6DS3mb as LSM6DS3
# sys.path.append("..")

import pyftdi.i2c as i2c

# a = 11<<2;=> 1011->101100;print(a)-->44;exit()
if __name__=='__main__':
    plt.ion()
    # Instantiate an I2C controller
    IIC_device = i2c.I2cController()
    # Configure the first interface (IF/1) of the FTDI device as an I2C master
    IIC_device.configure('ftdi:///1') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78

    print('\n\n')
    lsm_addr = 0x6b
    lsm6ds3 = LSM6DS3(i2c_controller= IIC_device,address= lsm_addr, debug=False,pause=0.8)
    # lsm6ds3.reset()
    
    axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]
    labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z']
    all_list = [[],[],[],[],[],[],[]]
    for t in range(20000):
        axis_x.append(t); plt.clf() 

        st = time.time()      
        res = lsm6ds3.readHighSpeed() # 0.017958402633666992 S
        # print("readWordSpeed: ",res)
        ed = time.time()
        # print("It uses: ",ed-st,"S")
        for _i in range(3): 
            i = _i+1
            all_list[i].append(res[i])
            plt.plot(axis_x,all_list[i],label = labels[i])
        
        # if t%100 == 0: all_list = [[],[],[],[],[],[],[]];axis_x = []
 

            
        # plt.legend()
        plt.pause(0.001); plt.ioff()
        pass
    
    t = 0
    for t in range(20000):
        axis_x.append(t); plt.clf() 
        # angle = lsm6ds3.calcAnglesXY()
        # angle = (int) (angle * 1000)
        
        # temp = lsm6ds3.temp();
        # t_list.append(lsm6ds3.readWord(0x20));plt.plot(axis_x,t_list) # temp
        # y_list.append(temp)

        x_list.append(lsm6ds3.rawAngularRate(0));plt.plot(axis_x,x_list)
        y_list.append(lsm6ds3.rawAngularRate(1));plt.plot(axis_x,y_list)
        z_list.append(lsm6ds3.rawAngularRate(2));plt.plot(axis_x,z_list)
        
        # x_list.append(lsm6ds3.rawLinearAcc(0))
        # y_list.append(lsm6ds3.rawLinearAcc(1))
        # z_list.append(lsm6ds3.rawLinearAcc(2))
            
        
        # plt.plot(axis_x,y_list)
        # plt.plot(axis_x,z_list)
        
        plt.pause(0.001); plt.ioff()
        # exit()
        # import Adafruit_GPIO.I2C as I2C
        # i2c = I2C.get_i2c_device(0x6A)
        # i2c.readS16(0X22)
