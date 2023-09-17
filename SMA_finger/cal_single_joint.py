
# General funcs
import os,sys,time
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


import pyftdi.ftdi as ftdi
from multiprocessing import  Process

if True: # Experiment settings
    
    DO_PLOT = False
    if DO_PLOT: TIME_OUT = 10000
    else: TIME_OUT = 10

    VOT = 9 # Vlots
    LOAD = 10 # Grams

    EXIT_CHECK_FREQ = 1 #S, EXIT check!

    print('Multi process version of SMA finger')
    print("Current time",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    print("RUNTIME",time.strftime('%m.%dth,%HH:%MM:%SS .%F', time.localtime(RUNTIME)))
    
    # RUNTIME = time.time()

    do_plot = DO_PLOT
    
    act_type = 2
    act_types = {0:"SMA",1:"TSMA",2:"CTSMA",3:"SSA"}

def sense_ADS1115(i2c_sensor_controller_URL=[],adc_01=[],do_plot=False,mode=[],lables=[]): # TODO
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
    while continue_senseing:
        reading = adc_01.readSensors(is_show=False)
        reading.append( time.time()- RUNTIME)
        # print(time.time()- RUNTIME)

        data.append( reading ) # 0.021474266052246095 S
        # print(reading)

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


def sensorProcess(mode="Angle",i2c_sensor_controller_URL=[],LSM_device=[],do_plot=False): # NONE FIFO Version
    PROCESSRUNTIME = time.time()
    url = i2c_sensor_controller_URL

    print("\nSensorProcess Starts:",PROCESSRUNTIME,"With sensor: ",mode)
    print("\t",PROCESSRUNTIME- RUNTIME,"s after runtime:",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)))

    if mode =="Angle": 
        labels = ['Joint Angle','Time']
        data = sense_ADS1115(url,[],do_plot,mode,labels)

    elif mode =="Volta": 
        labels = ['Voltage','Time']
        data = sense_ADS1115(url,[],do_plot,mode,labels)
 
        
    # data = sense_LSM6DS3(i2c_sensor_controller_URL,LSM_device,do_plot)
    # data = sense_FIFO(i2c_sensor_controller_URL,do_plot)
    file_name = mode+time.strftime("_%b%d_%H.%M.%S",time.localtime(RUNTIME))

    saveData(data,file_name,labels)
    saveFigure(data,file_name,labels)

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


    sensorProcess("Angle",url_1,[],DO_PLOT)
    
    pass