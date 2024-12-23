#!/bin/bash/python3 

# * Multi Process version
# Class of SMA single finger robot 
# Created by Askar. Liu @ 20221020
# Modified @20230221: Add logger

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


if True: # Experiment settings
    
    DO_PLOT = True
    PLOT_LEN = 1600
    if DO_PLOT: TIME_OUT = 10000
    else: TIME_OUT = 5

    VOT = 12 # Vlots
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
        # i2c_controller.configure()
        i2c_controller.configure('ftdi://ftdi:232h/') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78
        # USB\VID_0403&PID_6014\6&263914d5&0&2
        # USB\VID_0403&PID_6014\6&263914d5&0&1

        print('\n\n')
        lsm6ds3_A = IMUCHIP(i2c_controller,lsm_addr); lsm6ds3_A.reset()
        pca9685_A = PWMGENERATOR(i2c_controller,pca_addr,debug=False); pca9685_A.reset()

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

# Start of program

# Test settings
import pyftdi.ftdi as ftdi
from multiprocessing import  Process

def ctrlProcess(i2c_actuator_controller_URL=[]): # PCA 
    
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
        i2c_device.configure(i2c_actuator_controller_URL)
        actuator_device = PWMGENERATOR(i2c_device,debug=False)
        actuator_device.reset()

    # Set wire initial state
    actuator_device.setPWMFreq(wire_freq) 
    
    # experiment_ICMA(actuator_device) # ICMA
    experiment_SSA(actuator_device)
 
    actuator_device.i2c_controller.close()
    pass
 
def experiment_SSA(actuator_device):

    wire_channles_p = [4,0] # DR[0.09, 1, 0.2, 0.14, 0.1, 0] Duration[1, 0.3, 2, 2, 2, 2]
    dutys_P = [0.1,1,0.25,0] 
    intervals_P = [2,0.2,2,4] 
    
    print_info(dutys_P,intervals_P)
    actuator_device.test_wires(wire_channles_p,dutys_P,intervals_P,conf0=True)

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

def sense_ADS1115(i2c_sensor_controller_URL=[],adc_01=[],do_plot=False,mode=[],lables=[]): # TODO
    print("sense_ADS1115 starts at: ",time.time()- RUNTIME,"s, Related to ",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)) )
    ads_addr = 0x48 # ADS1115 address
    check_interval = int(EXIT_CHECK_FREQ/0.0008)

    if i2c_sensor_controller_URL==[]: adc_01 = findFtdiDevice(ads_addr)
    elif adc_01==[]:
        print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")
        i2c_device = i2c.I2cController()
        i2c_device.configure(i2c_sensor_controller_URL)

    # Modes
    if "Angle_01" in mode:
        adc_01 =ANGLESENSOR(i2c_device,name="angle_sensor_01")
        _url=[]

    elif "Angle_02" in mode:
        adc_01 =ANGLESENSOR(i2c_device,name="angle_sensor_02")
        _url=[]

    elif "Volta" in mode: 
        adc_01 =ANGLESENSOR(i2c_device,name="SSA_defalut")
        _url = CAL_FOLDER + "SSA_defalut" + ".json"
    
    elif "LoadCell" in mode:
        
        adc_01 =ANGLESENSOR(i2c_device,name="Load_cell")
        adc_01.setRange(0) # Minrange
        adc_01 # Going to 差分模式
        _url = CAL_FOLDER + "Load_cell" + ".json"

        pass
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
                    plt.plot(data_np[-PLOT_LEN:,-1],data_np[-PLOT_LEN:,_i],label = lables[_i])
                plt.pause(0.001);plt.ioff()
        pass
    
    adc_01.i2c_controller.close()
    return data

def sensorProcess(mode="Angle_02",i2c_sensor_controller_URL=[],LSM_device=[],do_plot=False): # NONE FIFO Version
    process_start_time = time.time()
    url = i2c_sensor_controller_URL

    print("\nSensorProcess Starts:",process_start_time,"With sensor: ",mode)
    print("\t",process_start_time- RUNTIME,"s after runtime:",time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(RUNTIME)))

    if "Angle" in mode: 
        labels = ['Joint Angle','Time']
        data = sense_ADS1115(url,[],do_plot,mode,labels)
    elif "Load" in mode:
        labels = ['Force','Time']
        data = sense_ADS1115(url,[],do_plot,mode,labels) # LoadCell
        pass
    elif mode =="Volta": 
        labels = ['Voltage','Time']
        data = sense_ADS1115(url,[],do_plot,mode,labels)

    elif mode =="IMU": 
        labels = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']
        data = sensor_LSM6DS3(url,LSM_device,do_plot,labels)
        
    # data = sense_LSM6DS3(i2c_sensor_controller_URL,LSM_device,do_plot)
    # data = sense_FIFO(i2c_sensor_controller_URL,do_plot)
    file_name = mode+time.strftime("_%b%d_%H.%M.%S",time.localtime(RUNTIME))

    saveData(data,file_name,labels)
    saveFigure(data,file_name,labels)

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

    
    # if True: sensorProcess("Angle_02",url_1,[],do_plot) # Calibration Range of rotational encoder

    if True:
        # process_sensor_LoadCell = Process( target= sensorProcess, args=("LoadCell",url_0,[],do_plot)) # LoadCell
        process_sensor_Angle = Process( target= sensorProcess, args=("Volta",url_1,[],do_plot)) # Volta

        # process_sensor_Volta = Process( target= sensorProcess, args=("Angle_02",url_2,[],do_plot)) # Angle_02

        # process_sensor_IMU = Process( target= sensorProcess, args=("IMU",url_2,[],do_plot))
        process_ctrl = Process(target= ctrlProcess,args=(url_0,))
        


        time.sleep(1)
        process_sensor_Angle.start()
        
        # process_sensor_Volta.start()

        # process_sensor_LoadCell.start()

        # process_sensor_IMU.start()
        time.sleep(0.2)
        process_ctrl.start()


    pass 