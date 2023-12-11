# Created by Askar @20231211
# Modified in 2023 1211
# based on Askars code of TIADS1115
if __name__=='__main__': # Test codes # Main process
    import os,sys
    import pyftdi.spi as spi
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0,parentdir)

    from lib.GENERALFUNCTIONS import *

from audioop import reverse
import math, time, sys , json

import numpy
from lib.GENERALFUNCTIONS import *

 # PLS follow https://www.ti.com/product/ADS1256

class TiAds1256_01(object): # TODO
    FCLKIN = 7.68E6 # ADS1256 Cristal Freq
    TCLKIN = 1/7.68E6

    WAKEUP = 0x00
    CMD_RDATA = 0x01
    CMD_RREG = 0x10 
    CMD_WREG = 0x50
    CMD_RESET = 0xFE

  
    def __init__(self, spi_controller,cs=0x01,continues_mdoe=False,spi_freq_denom=4,debug=False,): # TODO
        print("Creating New Ti Ads1115_01 I2C slave :",hex(cs))
        self.init_time = time.time()

        self.spi_ch_freq = self.FCLKIN / spi_freq_denom
        # Get a port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 12MHz
        
        self.spi_controller = spi_controller
        # Get a port to an I2C slave device
        self.spi_slave_device = self.spi_controller.get_port(cs=0,mode=1) 
        self.spi_slave_device.set_frequency(self.spi_ch_freq)
        print("SPI Freq:",self.spi_ch_freq)

        self.PGA = 1
        self.cs = cs
        self.debug = debug
        self.continues_mdoe = continues_mdoe

        if (self.debug): 
        # # TODO
        # print("Reseting PCA9685: ",'%#x'%self.address )
        # print("Initial Mode_1 reg value: ",'%#x'%self.read(self.__MODE1))
            pass

        # if hs_mdoe: self.highSpeedMode() # BUG

        print("Ti Ads1256 Device created! initial state:",self.getState(nums_to_read=12))
        print('Initial reseting:')
        self.reset()
        # self.setAmplifier(amp_level=1)
        pass

    def reset(self):
        self.spi_slave_device.exchange([self.CMD_RESET])
        time.sleep(50*self.TCLKIN)
        print("Ti Ads1256 Device reseted")

    def getState(self,addr=0x00,nums_to_read=11,is_show = True):
        nums_to_read += 1
        if nums_to_read < 0:nums_to_read = 1

        to_exchange = [ self.CMD_RREG + addr ,nums_to_read-1]
        self.spi_slave_device.exchange(to_exchange)
        time.sleep(50*self.TCLKIN)
        _data_reg = self.spi_slave_device.exchange([0x00],nums_to_read)
        
        if is_show:
           i = 0
           for _byte in _data_reg:
               print("Addr:",'%#x'%(0x00+i),'Value:','%#x'%_byte,bin(_byte))
               i += 1 

        return _data_reg
    
    def getReg(self,):
       
       pass

    def _decodeReading(self,raw_data):
        _res = (raw_data[0]<<16) + (raw_data[1]<<8) + raw_data[2]
        if not (_res&0x800000)==0: _res = -((_res^0xffffff) +1)
        _res = _res/0x7FFFFF # OR 0xFFFFFFF
        _res = _res * self.PGA
        return _res
    
    def continuesRead(self,):
       
       return []

    def setAmplifier(self, amp_level,): # setPGA
        # Change range depends on the amp_level
        _amp_levels = [1,2,4,8,16,32,64]
        _level_codes = [0b000,0b001,0b010,0b011,0b100,0b101,0b110]

        # Read PGA
        _reading = 1 # TODO Acquire current ADCON reg thorugh RREG cmd
        state_PGA = _reading & 0b00000111 # Final 3 bits

        for _level,_code in zip(_amp_levels,_level_codes):
           if amp_level <= _level: break

        _to_write = (_reading[0] & 0x0001) or _code<<1 # TODO

        # WREG TODO WREG

        # Read and save to self
        if self.getState() == amp_level:
            self.PGA = amp_level
        else: print("PGA setting failed!!")
       

class HW526Angle(TiAds1256_01): # TODO

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


    print("\n\n")
    print('Testing TI ADS115     at',time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()),"")
    
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/0')  
    
    spi_device = spi.SpiController(cs_count=1)
    spi_device.configure(url_0,frequency=7.8E6)
    ads1256_01 = TiAds1256_01(spi_controller=spi_device)

    # angle_sensor_01 = HW526Angle(i2c_device,name="angle_sensor_01") # ....
    print("\nEND\n")
    # angle_sensor_01.selfTest(rounds=5,is_show=True)

    
    # angle_sensor_01.highSpeedTest(512,True)
    # t0 = time.time()
    # while time.time()-t0 < 5: print(angle_sensor_01.readSensors())


 



