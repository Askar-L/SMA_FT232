from concurrent.futures import process
import os,sys,time

# from pickle import TRUE
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from lib.GENERALFUNCTIONS import *


# import pyftdi.i2c as i2c
import lib.i2c as i2c

from matplotlib import pyplot as plt

from ads1115.TIADS1115 import HW526Angle as ANGLESENSOR

# Experiment settings
if True: 
    MODE = "debug" # "expriment"

    VOT = 20 # Vlots
    LOAD = 20 # Grams

    # Main derections
    DUTYS_P = [0.09,1,0.4,0.4]# [1,0.2]   # [预热 响应 维持]c 
    INTERVALS_P =[1,0,0,2]# [0.2,1]
    # Reversed derections
    DUTYS_M = [1,0.3,0.3]# [1,0.2]   # [预热 响应 维持]c
    INTERVALS_M =[0.1,2,0.1]# [0.2,1]

    DO_PLOT = False
    if DO_PLOT: TIME_OUT = 10000
    else: TIME_OUT = 5#13

    LABELS = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']
    # LABELS = ['R','Time']
    EXIT_CHECK_FREQ = 1 #S, EXIT check!

    print('Multi process version of SMA finger')
    print(time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    do_plot = DO_PLOT
    

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
    check_interval = int(EXIT_CHECK_FREQ/0.017)

    if i2c_sensor_controller_URL==[]: angle_sensor_01 = findFtdiDevice(ads_addr)
    elif angle_sensor_01==[]:
        print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL,frequency = 1000E3)
        # print("Max freq:",i2c_device.frequency_max)
        # exit()
        # i2c_device.start_HS()
        angle_sensor_01 =ANGLESENSOR(i2c_device,name="angle_sensor_01",hs_mode=False)
        # sensor_device.reset()        
        
    # plt.ion()
    T,A0,A1,A2,A3 = [],[],[],[],[]
    # axis_x,x_list,y_list,z_list,t_list = [],[],[],[],[]

    if not isinstance(angle_sensor_01,ANGLESENSOR):print("Programe err! @ sense_ADS1115, pls check coding!"); exit()

    angle_sensor_01.startConversion(data_rate=100,is_continue=True,is_show=False)

    # # Empty run for 1 sec
    # t0 =  time.clock()
    # while time.clock()-t0 < 0.3: sensor_device.readSensors(1)

    # while run
    num_read_reg = 100

    all_data = []
    angle_sensor_01.slave.read_from(0x00,readlen=2*num_ch,relax=False)
    _i = 0; t_s = time.time()
    while _i < num_read_reg:
        _i += 1
        all_data.append(angle_sensor_01.slave.read_from(0x00,readlen=2*num_ch,relax=False))
    t_end = time.time()
    print("Reg read for ",num_read_reg,",   ",num_read_reg/(t_end-t_s),"Hz")

    print("\nFREQ:",i2c_device._frequency/1000,i2c_device._ck_hd_sta)



    all_data_HS = []
    angle_sensor_01.i2c_controller.start_HS(i2c_sensor_controller_URL)
    angle_sensor_01.slave.read_from(0x00,readlen=2*num_ch,relax=False)
    _i = 0;t_s = time.time()
    while _i < num_read_reg:
        _i += 1
        all_data_HS.append(angle_sensor_01.i2c_controller.read_HS(0x00,readlen=2*num_ch,relax=False))
    t_end = time.time()
    print("Reg read for ",num_read_reg,",   ",num_read_reg/(t_end-t_s),"Hz")
    print("\nFREQ:",i2c_device._frequency/1000,i2c_device._ck_hd_sta)
    print(all_data,all_data_HS)
    # while continue_senseing:

    #     reading = angle_sensor_01.readSensors(num_ch,is_show=False)
    #     reading.append( time.time()- RUNTIME)
    #     all_data.append( reading ) # 0.021474266052246095 S
 
        
    #     # Exit detecting
    #     if _t % check_interval ==0: 
    #        print("\rSensor reading, continued for: ",reading[-1],"s",end='')
    #        if reading[-1] > TIME_OUT: 
    #         print("\nSensor reading Over due to time out: ",TIME_OUT);continue_senseing = False
    #     _t+=1
 
    #     pass
    
    angle_sensor_01.i2c_controller.close()
    return all_data

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
    sensorProcess("ADC",1,url_0,[]); exit() 