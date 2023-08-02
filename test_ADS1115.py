from concurrent.futures import process
import os,sys,time

# from pickle import TRUE
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from lib.GENERALFUNCTIONS import *

import pyftdi.ftdi as ftdi
from multiprocessing import  Process

import numpy as np
import pyftdi.i2c as i2c
from matplotlib import pyplot as plt

from lsm6ds3.LSM6DS3 import Lsm6ds3_01 as IMUCHIP
from pca9685.PCA9685 import Pca9685_01 as PWMGENERATOR
from ads1115.TIADS1115 import HW526Angle as ANGLESENSOR

# Experiment settings
if True: 
    MODE = "debug" # "expriment"
    LABELS = ['Voltage' ]

    VOT = 20 # Vlots
    LOAD = 20 # Grams

    # Main derections
    DUTYS_P = [0.09,1,0.4,0.4]# [1,0.2]   # [预热 响应 维持]c 
    INTERVALS_P =[1,0,0,2]# [0.2,1]
    # Reversed derections
    DUTYS_M = [1,0.3,0.3]# [1,0.2]   # [预热 响应 维持]c
    INTERVALS_M =[0.1,2,0.1]# [0.2,1]

    DO_PLOT = True
    if DO_PLOT: TIME_OUT = 10000
    else: TIME_OUT = 5#13

    LABELS = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']
    # LABELS = ['R','Time']
    EXIT_CHECK_FREQ = 1 #S, EXIT check!

    print('Multi process version of SMA finger')
    print(time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    

    act_type = 2
    act_types = {0:"SMA",1:"TSMA",2:"CTSMA"}
    
    print("Expriment data:\n")
    print("\t Expriment MODE:\t",MODE)
    
    print("\t act_type:\t",act_types[act_type])
    
    print("\t DUTYS:    \t",DUTYS_P,"%")
    print("\t INTERVALS:\t",INTERVALS_P,"Sec")

    print("\t VOT: \t",VOT,"Volts")
    print("\t LOAD: \t",LOAD,"Grams")

    print("\t DO_PLOT:\t",DO_PLOT)
    print("\t TIME_OUT:\t",TIME_OUT,"Sec")
    print("\t LABELS:\t",LABELS)
    print("\t EXIT_CHECK_FREQ:\t",EXIT_CHECK_FREQ)

    print("\n\n")

def sense_ADS1115( num_ch=1,i2c_sensor_controller_URL=[],angle_sensor_01=[],do_plot=False): # TODO

    ads_addr = 0x48 # ADS1115 address
    check_interval = int(EXIT_CHECK_FREQ/0.00017)

    if i2c_sensor_controller_URL==[]: angle_sensor_01 = findFtdiDevice(ads_addr)
    elif angle_sensor_01==[]:
        print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL)

        # print("Max freq:",i2c_device.frequency_max)
        # exit()

        # angle_sensor_01 =ANGLESENSOR(i2c_device,name="angle_sensor_01",hs_mode=False)
        adc_01 =ANGLESENSOR(i2c_device,name="SSA_defalut")

        # sensor_device.reset()        
        
    # plt.ion()
    T,A0,A1,A2,A3 = [],[],[],[],[]
    # axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]
    adc_01.setRange(0) # Minrange
    adc_01.startConversion(data_rate=100,is_continue=True,is_show=False)

 
    # while run
    _t=0
 

    data = []

    if DO_PLOT: 
        plt.ion()
        figsize = (12.8,7.2)#(19.2,10.8)
        plt.figure(figsize=figsize)
        plot_counter = 0

    while DO_PLOT:
        reading = adc_01.readSensors(is_show=False)
        reading.append( time.time()- RUNTIME)
        # print(time.time()- RUNTIME)

        data.append( reading ) # 0.021474266052246095 S

        if _t % check_interval ==0: 
           print("\rSensor reading, continued for: ",reading[-1],"s",end='')
           if reading[-1] > TIME_OUT: 
            print("\nSensor reading Over due to time out: ",TIME_OUT);continue_senseing = False
        _t+=1

        if DO_PLOT:
            plot_counter+=1
            if plot_counter == 400:
                plot_counter = 0            
                    
                data_np = np.array(data[-10000:]) # [-800]
 
                plt.clf(); A0.append(_t)
                for _i in range(data_np.shape[1]-1): 
                    plt.plot(data_np[:,-1],data_np[:,_i],label = LABELS[_i])
                    # print(data_np[:,-1],data_np[:,_i],label = LABELS[_i])
                plt.pause(0.001);plt.ioff()
    
    angle_sensor_01.i2c_controller.close()
    return data

def sensorProcess(mode="ADC", num_ch=1, i2c_sensor_controller_URL=[],LSM_device=[],do_plot=False): # NONE FIFO Version
    PROCESSRUNTIME = time.time()
    # print(num_ch);exit()

    print("\nSensorProcess Starts:",PROCESSRUNTIME,"With sensor: ",mode)
    print("OF:",PROCESSRUNTIME-RUNTIME,RUNTIME)

    if mode =="ADC": 
        if num_ch > 0 : 
            LABELS =[]
            for _i in range(num_ch): LABELS.append( 'Joint Angle'+str(_i) )
            LABELS.append('Time')

            data = sense_ADS1115(num_ch,i2c_sensor_controller_URL,[],do_plot)
        else: print("Illegal channle number !!!!:",num_ch);exit()
 
    # file_name = mode+time.strftime("_%b%d_%H.%M",time.localtime(RUNTIME))+str(DUTYS_P)+str(INTERVALS_P)

    # saveData(data,file_name,LABELS)
    # saveFigure(data,file_name,LABELS)

if __name__=='__main__': # Test codes # Main process
 
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/0') 
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/0')
    url_2 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FD/1')

    # MP on
    print("SMA Finger MultiProcess: \nTwo thread with Python threading library")
         # url_PCA,url_LSM,PCA_device,LSM_device = findFtdiAddr()
 

    # mode == "debug"
    # if "debug" in MODE :
    sensorProcess("LoadCell",url_0,[],do_plot=True); exit()        
    # sensorProcess("ADC",1,url_0,[],do_plot=True); exit()        