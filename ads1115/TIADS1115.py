# Created by Askar @20221224
# Modified in 2022 1224


from audioop import reverse
import math, time, sys

 # PLS follow https://www.ti.com.cn/product/cn/ADS1115

class TiAds1115_01(object): # TODO
  # Registers/etc. # TODO
  # __SUBADR1            = 0x02
  # __SUBADR2            = 0x03
  
  def __init__(self, i2c_controller,address=0x48,easy_mdoe= True,debug=False,): # TODO
    print("Creating New Ti Ads1115_01 I2C slave :",hex(address))
    
    self.i2c_controller = i2c_controller

    # Get a port to an I2C slave device
    self.slave = i2c_controller.get_port( address ) # 0x48 / 0x49 / 0x4A / 0x4B
    # Addr connection: GND-0x48; VDD-0x49; SDA-0x4A; SCL-0x4B

    self.address = address
    self.debug = debug
    # self.osc_clock = 25000000.0
    self.easy_mdoe = easy_mdoe
 
    self.print_value = False

    if (self.debug): 
      # # TODO
      # print("Reseting PCA9685: ",'%#x'%self.address )
      # print("Initial Mode_1 reg value: ",'%#x'%self.read(self.__MODE1))
      pass
    print("Ti Ads1115 Device created! initial state:",self.getState(is_show=True))
   
    self.setRange()
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
    

    self.startConversion(is_continue=True,data_rate=1000,is_show=is_show)
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

  def readSensors(self,is_show=False):
    _res = []
    _reading =  self.slave.read_from(0x00,readlen=2) 
    _reading = int.from_bytes(_reading, byteorder='big', signed=True) 
    _res.append( _reading )
    if is_show: print("Last conversion res: ",_reading)
    return _res
  
  def startConversion(self,data_rate=128,is_continue=False,is_show=False):
    # Mode 8th bit @ addrt 0x01 [15:0]
    _curr_mode =  self.slave.read_from(0x01,readlen=2) 
    config_regH =_curr_mode[0]; config_regL= _curr_mode[1]

    if is_continue: # Continued mode
      _data_rates = ([860,475,250,128,64,32,16,8]);_data_rates.reverse() # SPS
      _codes = [0x7,0x6,0x5,0x4, 0x3,0x2,0x1,0x0];_codes.reverse()
      for _mode,_code in zip(_data_rates,_codes): 
        if _mode >= data_rate: break
      

      config_regH = _curr_mode[0] & 0b11111110 # MODE -> 0(CONTINUES MODE)
      config_regL = (_curr_mode[1]& 0x1F)|_code<<5

      self.slave.write_to(0x01,out=[ config_regH ,config_regL ])
      self.getState(is_show=True)
    else : # Single shot mode
      self.slave.write_to( regaddr=0x01 , out= [_curr_mode[0] | 0x80,_curr_mode[1]])
      self.readSensors(is_show)
    return []
  
  def setRange(self,maxVoltage = 5): # DONE
    # Change range depends on the 
      # maxVoltage: maxium level of in put analog signal

    _modes = [0.256,0.256,0.256,0.512, 1.024,2.048,4.096,6.144]
    _codes = [0x7,0x6,0x5,0x4, 0x3,0x2,0x1,0x0]
    
    for _mode,_code in zip(_modes,_codes): 
      if maxVoltage <= _mode: break

    _reading =  self.slave.read_from(regaddr = 0x01,readlen=2) 
    _to_write = (_reading[0] & 0x0001) or _code<<1

    self.slave.write_to( regaddr=0x01 , out= [_to_write,_reading[1]] )
   

    pass

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
    _reading =  self.slave.read_from(regaddr = regaddrs[1],readlen=2) 
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
    _reading =  self.slave.read_from(regaddr = regaddrs[2],readlen=2) 
    _reading = int.from_bytes(_reading, byteorder='big', signed=True) 
    if is_show: print("Low threshold:",_reading)
    _res.append( _reading )

    # Case 11:
    _reading =  self.slave.read_from(regaddr = regaddrs[3],readlen=2) 
    _reading = int.from_bytes(_reading, byteorder='big', signed=True) 
    if is_show: print("High threshold:",_reading)
    _res.append( _reading )

    return _res
 
  def read(self, reg): 
    "Read an unsigned byte from the I2C device"
    # result = self.slave.read_byte_data(self.address, reg)
    result = (self.slave.read_from(regaddr = reg,readlen=1))[0]
    # result
    if self.debug: print("\tI2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
 
  def write(self, reg_add, input_value, doCheck = True):
    "Writes an 8-bit value to the specified register/address"
    
    if doCheck :value_before =  (self.slave.read_from(regaddr=reg_add, readlen=1))[0]#

    if isinstance(input_value,int): in_value =  bytearray([input_value]) 
    else: in_value = input_value

    self.slave.write_to( regaddr= reg_add, out= in_value)
    
    if doCheck: # Check
      time.sleep(0.1)
      value_after =  self.slave.read_from(regaddr=reg_add, readlen=1)[0]# self.read(reg_add)
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

class HW526Angle(TiAds1115_01):
  
  def __init__(self, i2c_controller,address=0x48,easy_mdoe= True,debug=False,):
    super(HW526Angle,self).__init__(i2c_controller,address,easy_mdoe,debug)
    self.calibrationData = []
    self.loadCalibration()
    pass
  
  def loadCalibration(self):
    # self.calibrationData = []
    
    
    pass

  def calibrateRange(self,location=[],t_delay=2):

    if len(location) < 2 : print("Location number: ",len(location)," is not enough for calibration"); return []
    raw_resistance = []
    for _location in location:
      # Time delay reqiured here!!!
      _str = "Please press enter after rotate the actuator into:",_location," degree..." 
      input(_str)
      # time.sleep(t_delay)
      _reading = self.readSensors()
      raw_resistance.append(_reading) 
      print(_reading)
    return raw_resistance


if __name__=='__main__': # Test codes # Main process
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0,parentdir)

    import pyftdi.i2c as i2c
    # from pyftdimod import i2c as i2c
    
    print("\n\n")
    print('Testing TI ADS115     at',time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()),"")
    
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1') 
    
    i2c_device = i2c.I2cController()
    i2c_device.configure(url_0,frequency = 1E6)
    # print(i2c_device.frequency, i2c_device.configured )    

    angle_sensor = HW526Angle(i2c_device)
    angle_sensor.selfTest(rounds=5,is_show=True)
    angle_sensor.calibrateRange([90,180,270])
    # adc_device.highSpeedTest(512,True)
 



