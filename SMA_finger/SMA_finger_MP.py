#!/bin/bash/python3 

# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu  
 

# General funcs
import os,sys,time,multiprocessing
import numpy as np
from matplotlib import pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

# Driver funcs
from pyftdimod import i2c as i2c


from lsm6ds3.LSM6DS3 import Lsm6ds3_01 as IMUCHIP
from pca9685.PCA9685 import Pca9685_01 as PWMGENERATOR
from ads1115.TIADS1115 import HW526Angle as ANGLESENSOR

from lib.GENERALFUNCTIONS import *


# Test settings
import pyftdimod.ftdi as ftdi

#import pyftdi.ftdi as ftdi
from multiprocessing import  Process


if True: # Experiment settings
    
    RESTING = 0

    DO_PLOT = False
    if DO_PLOT: TIME_OUT = 10000
    else: TIME_OUT = 20 + RESTING
    VOT = 9 # Vlots
    LOAD = 20 # Grams

    EXIT_CHECK_FREQ = 0.5 #S, EXIT check!

    print('Multi process version of SMA finger')
    print("Current time",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    print("RUNTIME",time.strftime('%m.%dth,%HH:%MM:%SS .%F', time.localtime(RUNTIME)))
    
    # RUNTIME = time.perf_counter()

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
 
 
def experiment_bio_01(actuator_device): # Actuators Experiment 1
    # wire_channles_P = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    # DUTYS_P = [0.01,0]
    # INTERVALS_P = [0.5,0]
    # actuator_device.test_wires(wire_channles_P,DUTYS_P,INTERVALS_P,is_show=True)

    wire_channles_P = actuator_device.CH_EVEN

    flexsion_ch = [0x0,0x2]
    extension_ch = [0x8,0xA,0xC]
    adduction_ch = [0x6]
    abducsion_ch = [0x4]

    # Positive derections  
    DUTYS_P_unit = [1,0]# [1,0.2]   # [预热 响应 维持]c 
    INTERVALS_P_unit =[2,6]# [0.2,1]
    DUTYS_P,INTERVALS_P = [],[]
    num_cycles = 1

    for _ in range(num_cycles):
        DUTYS_P.extend(DUTYS_P_unit)
        INTERVALS_P.extend(INTERVALS_P_unit)

    print_info(DUTYS_P,INTERVALS_P)
    
    to_activated =[]
    to_activated.extend(flexsion_ch)
    to_activated.extend(adduction_ch)
    to_activated.extend([0x08])

    actuator_device.test_wires(to_activated,DUTYS_P,INTERVALS_P,is_show=False)


def ctrlProcess(i2c_actuator_controller_URL=[],angle_sensor_ID="SNS000",process_share_dict={}): # PCA 
    
    PROCESSRUNTIME = time.time()
    print("\nCtrlProcess Starts:")
    print("",PROCESSRUNTIME- RUNTIME,"s after runtime:",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)))
    
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
        i2c_device.configure(i2c_actuator_controller_URL,frequency = 3E6,
                            rdoptim=True,clockstretching=True) # On IIC      
        actuator_device = PWMGENERATOR(i2c_device,debug=False) # Link PCA9685
        # i2c_device.write()

    # Set wire initial state
    actuator_device.setPWMFreq(wire_freq) 

    print("Connection established: ",actuator_device)
    return actuator_device 

if __name__=='__main__': # Test codes # Main process
    sys.stdout = Logger()
    sys.stderr = sys.stdout		# redirect std err, if necessary

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
        
        # process_sensor_ADC = multiprocessing.Process( target= sensorProcess, args=("Angle",url_1,[],do_plot,'ADC001',False,process_share_dict))
        # process_sensor_ADC = Process( target= sensorProcess, args=("Volta",url_Sensor,[],do_plot))
        # process_sensor_IMU = Process( target= sensorProcess, args=("IMU",url_2,[],do_plot))

        process_ctrl = multiprocessing.Process(target= ctrlProcess,args=(url_0,'ADC001',process_share_dict))     

        # process_ctrl = multiprocessing.Process(target= pidProcess,args=(url_0,'ADC001',process_share_dict))     

        # process_sensor_ADC.start()
        # process_sensor_IMU.start()

        # time.sleep(0.6)
        process_ctrl.start()

        # process_sensor_ADC.join()


    pass