# Created by Askar @20221224
# Modified in 2022 1224


from audioop import reverse
import math, time, sys , json

import numpy
from lib.GENERALFUNCTIONS import *

 # PLS follow https://www.ti.com.cn/product/cn/ADS1115

class TiAds1115_01(object): # TODO
  # Registers/etc. # TODO
  # __SUBADR1            = 0x02
  # __SUBADR2            = 0x03
  
  def __init__(self, i2c_controller,address=0x48,hs_mdoe=False,easy_mdoe= True,debug=False,): # TODO
    print("Creating New Ti Ads1115_01 I2C slave :",hex(address))
    self.init_time = time.time()

    self.i2c_controller = i2c_controller

    # Get a port to an I2C slave device
    self.slave = i2c_controller.get_port( address ) # 0x48 / 0x49 / 0x4A / 0x4B
    # Addr connection: GND-0x48; VDD-0x49; SDA-0x4A; SCL-0x4B

    self.address = address
    self.debug = debug
 
    if (self.debug): 
      # # TODO
      # print("Reseting PCA9685: ",'%#x'%self.address )
      # print("Initial Mode_1 reg value: ",'%#x'%self.read(self.__MODE1))
      pass

    # if hs_mdoe: self.highSpeedMode() # BUG

    print("Ti Ads1115 Device created! initial state:",self.getState(is_show=True))
      
    self.setRange(maxVoltage=3.3)
    pass

  def selfTest(self,rounds=100,is_show=False):
    print("*"*20,"Conversion speed test start here")

    self.startConversion(is_continue=False)
    t_start = time.time()
    for _i in range(rounds):
      self.startConversion(is_continue=False,is_show=is_show)
      self.readSensors(False)
    t_end = time.time()
    print(-t_start+t_end,"S used for", rounds," times of conversion through full iic calling")
    print((-t_start+t_end)/rounds," for AVG")
    

    self.startConversion(is_continue=True,data_rate=860,is_show=is_show)
    t_start = time.time()
    for _i in range(rounds): self.readSensors(is_show=is_show)
    t_end = time.time()
    print(-t_start+t_end,"S used for", rounds," times of conversion through full iic calling")
    print((-t_start+t_end)/rounds," for AVG")
    return []

  def highSpeedTest(self,rounds=100,is_show=False):
    self.startConversion(is_continue=True)
    # self.startConversion(is_continue=True)

    histroy=[]
    t_start = time.time()
    for _i in range(rounds):
      histroy.append(self.readSensors(is_show))
    t_end = time.time()
    print(-t_start+t_end,"S used for", rounds," times of conversion through full iic calling")
    print((-t_start+t_end)/rounds," for AVG")

    return histroy

  def readSensors(self,num_ch=1,is_show=False):
    _res = []
    _reading =  self.slave.read_from(0x00,readlen=2*num_ch,relax=False) #####! Undergoing!!!!!!!
    # print(_reading)

    # print("_reading:",_reading)

    if num_ch ==1 : 
      int_reading = int.from_bytes(_reading, byteorder='big', signed=True) 
      _res.append( int_reading )
    else:      # Seprate each 2-bytes
      for _i in range(num_ch):
        int_reading = int.from_bytes(_reading[_i*2:_i*2+2], byteorder='big', signed=True) 
        _res.append( int_reading )

    if is_show: print("Last conversion res: ",_reading)
    return _res
  
  def startConversion(self,data_rate=860,is_continue=False,is_show=False):
    # Mode 8th bit @ addrt 0x01 [15:0]
    _curr_mode =  self.slave.read_from(0x01,readlen=2,relax=False) 
    config_regH =_curr_mode[0]; config_regL= _curr_mode[1]

    if is_continue: # Continued mode
      if not data_rate == 860:
        _data_rates = ([860,475,250,128,64,32,16,8]);_data_rates.reverse() # SPS
        _codes = [0x7,0x6,0x5,0x4, 0x3,0x2,0x1,0x0];_codes.reverse()
        for _mode,_code in zip(_data_rates,_codes): 
          if _mode >= data_rate: break
      else : _code = 0x7

      config_regH = _curr_mode[0] & 0b11111110 # MODE -> 0(CONTINUES MODE)
      config_regL = (_curr_mode[1]& 0x1F)|_code<<5

      self.slave.write_to(0x01,out=[ config_regH ,config_regL],relax=True)
      # self.write()
      self.getState(is_show=True)
    else : # Single shot mode
      self.slave.write_to( regaddr=0x01 , out= [_curr_mode[0] | 0x80,_curr_mode[1]])
      self.readSensors(is_show)
    return []
  
  def setRange(self,maxVoltage = 3.3): # DONE
    # Change range depends on the 
      # maxVoltage: maxium level of in put analog signal

    _modes = [0.256,0.256,0.256,0.512, 1.024,2.048,4.096,6.144]
    _codes = [0x7,0x6,0x5,0x4, 0x3,0x2,0x1,0x0]
    for _mode,_code in zip(_modes,_codes): 
      if maxVoltage <= _mode: break

    _reading =  self.slave.read_from(regaddr = 0x01,readlen=2,relax=False) 
    _to_write = (_reading[0] & 0x0001) or _code<<1

    self.slave.write_to( regaddr=0x01 , out= [_to_write,_reading[1]] )
    

  def getState(self,Point=00,is_show= False):
    regaddrs = [0x00,0x01,0x02,0x03]
    _res = []
    """ 7:2	Reserved 0 ;1:0	P[1:0]
    00 : Conversion register;01 : Config register; 10 : Lo_thresh register; 11 : Hi_thresh register """

    # Case 00:  
    """ The 16-bit Conversion register contains the result of the last conversion in binary two's complement format. 
        Following power-up, the Conversion register is cleared to 0, and remains 0 until the first conversion is completed.    """
    _reading =  self.slave.read_from(regaddr = regaddrs[0],readlen=2) 
    _reading = int.from_bytes(_reading, byteorder='big', signed=True) 
    _res.append( _reading )
    if is_show: print("Last conversion res: ",_reading)

    # Case 01:  
    """9.6.3 Config Register (P[1:0] = 1h) [reset = 8583h]
    The 16-bit Config register is used to control the operating mode, 
    input selection, data rate, full-scale range, and comparator modes."""
    _reading =  self.slave.read_from(regaddr = regaddrs[1],readlen=2,relax=False) 
    if is_show: 
      print("Opearting state: ",(_reading[0] & 0x80) >>7)
      print("Input multiplexer state: ",str(_reading[0]>>4 & 0x07) )
      print("PGA state: ",str(_reading[0] & 0b1110) )
      print("MODE : ",str(_reading[0] & 0b1) )

      print("Date Rate: ",bin( _reading[1]>>5) )
      print("Comparator mode: ",bin( _reading[1]>>4 &0b1) )
      print("Comparator polarity: ",bin( _reading[1] &0b1000) )
      print("Latching Comparator: ",bin( _reading[1] &0b100) )
      print("Comparator queue and disable: ",bin( _reading[1] &0b11) )
    
    _res.append( _reading )

    # Case 10:
    _reading =  self.slave.read_from(regaddr = regaddrs[2],readlen=2,relax=False) 
    _reading = int.from_bytes(_reading, byteorder='big', signed=True) 
    if is_show: print("Low threshold:",_reading)
    _res.append( _reading )

    # Case 11:
    _reading =  self.slave.read_from(regaddr = regaddrs[3],readlen=2,relax=False) 
    _reading = int.from_bytes(_reading, byteorder='big', signed=True) 
    if is_show: print("High threshold:",_reading)
    _res.append( _reading )

    return _res
 
  def read(self, reg): 
    "Read an unsigned byte from the I2C device"
    # result = self.slave.read_byte_data(self.address, reg)
    result = (self.slave.read_from(regaddr = reg,readlen=1,relax=False))[0]
    # result
    if self.debug: print("\tI2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
 
  def write(self, reg_add, input_value, doCheck = True):
    "Writes an 8-bit value to the specified register/address"
    
    if doCheck :value_before =  (self.slave.read_from(regaddr=reg_add, readlen=1,relax=False))[0]#

    if isinstance(input_value,int): in_value =  bytearray([input_value]) 
    else: in_value = input_value

    self.slave.write_to( regaddr= reg_add, out= in_value)
    
    if doCheck: # Check
      time.sleep(0.1)
      value_after =  self.slave.read_from(regaddr=reg_add, readlen=1,relax=False)[0]# self.read(reg_add)
      if (value_after-value_before) == 0:
        if input_value == value_after: 
          if self.debug: print("\tInputted and saved values are equal, however it is still writted!")
        else: 
          print("\tValue is changed, however does not mattches the desire value!")
          print("\tConsider chaecking the chip datasheet about the correct value for changing")
          
      if self.debug: print("\tI2C: Device 0x%02X writted 0x%02X to reg 0x%02X" % (self.address, input_value, reg_add))
      return value_after
    return in_value
  
  
  # NOT READY AREA!!!

  def reset(self): #BUG
    """
      The ADS111x reset on power-up and set all the bits in the Config register to the respective default settings. 
      The ADS111x enter a power-down state after completion of the reset process. 
      The device interface and digital blocks are active, but no data conversions are performed. 
      The initial power-down state of the ADS111x relieves systems with 
        tight power-supply requirements from encountering a surge during power-up.

      The ADS111x respond to the I2C general-call reset commands. 
      When the ADS111x receive a general call reset command (06h), 
          an internal reset is performed as if the device is powered-up.
    """
    __SWRST = 0b00000110 # general call reset command (06h)
    
    print(self.read(__SWRST))

    self.write(0x00,bytearray([0x06]))
    print('\nSucess Reseted Ti Ads1115 board:0x%02X'%self.address)
    return []

  def highSpeedMode(self):
    """
      To activate high-speed mode, send a special address byte of 00001xxx following the START condition, 
      where xxx are bits unique to the Hs-capable master. This byte is called the Hs master code, 
      and is different from normal address bytes; the eighth bit does not indicate read/write status. 
      The ADS111x do not acknowledge this byte; the I2C specification prohibits acknowledgment of the Hs master code. 
      Upon receiving a master code, the ADS111x switch on Hs mode filters, and communicate at up to 3.4 MHz. 
      The ADS111x switch out of Hs mode with the next STOP condition.

      For more information on high-speed mode, consult the I2C specification.
    """
    send = 0b00001000 + 0b111
    # print(send);exit()
    try:  
      # self.i2c_controller._do_write(out=send)    
      self.i2c_controller.write(self.address,out=send,relax=False )
    except Exception as err: pass
    return []

class HW526Angle(TiAds1115_01):

  def __init__(self, i2c_controller,address=0x48,easy_mdoe= True,hs_mode=False, debug=False,name=[]):
    # from lib.GENERALFUNCTIONS import *
    super(HW526Angle,self).__init__(i2c_controller,address,hs_mode,easy_mdoe,debug)
    # self.i2c_controller = i2c_controller
    self.calibrationData = []
    self.name = name
    self.calib_file_url = CAL_FOLDER + name + ".json"
    print("HW526:self.calib_file_url",self.calib_file_url)

    self.loadCalibration()
    pass
  
  def loadCalibration(self,url=[]):
    
    if not url:
      url = self.calib_file_url
    print("Loading calibration data from:",url)

    try:
      # JSON到字典转化
      _cali_file = open(url, 'r')
      _cali_data = json.load(_cali_file)
      print(type(_cali_data),_cali_data)
      self.model_k = _cali_data["a1"]
      self.model_b = _cali_data["a0"]
      if len(_cali_data) ==0: raise Exception("")        
      else: print("\tSuccessfully load calibration data!:",self.model_k,self.model_b,"\n")

    except Exception as Err: 
      print("\tErr occurs when loading calibration json file, Please calibrate angle sensor: ",self.name)
      self.calibrateRange()
 

  def calibrateRange(self,angles=[90,270],t_delay=2):
    print("Calibration starts, ",len(angles)," angles reqiured")
    if len(angles) < 2 : print("Location number: ",len(angles)," is not enough for calibration"); return []
    raw_R = []

    for _location in angles:
      # Time delay reqiured here!!!
      _str = "\t Press enter after rotate the actuator into:\t"+str(_location)+" degree..." 
      input(_str)
      _reading = super(HW526Angle,self).readSensors() # self.readSensors()
      raw_R.append(_reading) 
      print("\t",_reading)

    # Cal calibration ?
    if len(angles) == 2:
      raw_R = numpy.array(raw_R)
      angles = numpy.array(angles)

      k = float( (angles[0]-angles[1])/ (raw_R[0]-raw_R[1]) )
      b = float(angles[0] - k*raw_R[0])
      print("Sensor outputs model: angle =",k,"x + ",b)
      model = {"a0":b,"a1":k} 
      # y = (raw_R[0]-raw_R[1])*(x -xs[0])/(xs[1]-xs[0]) + raw_R[1]

    # Save Raw Data and model
    info_json = json.dumps(model,sort_keys=False, indent=4, separators=(',', ': '))
    f = open(self.calib_file_url, 'w')
    f.write(info_json)
    
    self.model_b = b
    self.model_k = k
    return raw_R

  # Undergoing
  def readSensors(self,num_ch=1 ,is_show=False):
    _reading = super(HW526Angle,self).readSensors(num_ch,is_show) 
    res = []
    for _res in _reading: res.append( _res * self.model_k + self.model_b)
    return res

if __name__=='__main__': # Test codes # Main process
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0,parentdir)

    import pyftdi.i2c as i2c
    # from pyftdimod import i2c as i2c
    from lib.GENERALFUNCTIONS import *

    print("\n\n")
    print('Testing TI ADS115     at',time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()),"")
    
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1') 
    
    i2c_device = i2c.I2cController()
    i2c_device.configure(url_0,frequency = 1E6)
    # print(i2c_device.frequency, i2c_device.configured )    

    angle_sensor_01 = HW526Angle(i2c_device,name="angle_sensor_01")
    print("\n\n\n")
    # angle_sensor_01.selfTest(rounds=5,is_show=True)

    
    angle_sensor_01.highSpeedTest(512,True)
    t0 = time.time()
    while time.time()-t0 < 5: print(angle_sensor_01.readSensors())


 



