# Created by Askar @20221224
# Modified in 2022 1224
import math, time, sys
import pyftdi.i2c as i2c

# PLS follow https://www.ti.com.cn/product/cn/ADS1115

class TiAds1115_01(object):
  # Registers/etc.
  # __SUBADR1            = 0x02
  # __SUBADR2            = 0x03
  # __SUBADR3            = 0x04

  # __MODE1              = 0x00
  # __PRESCALE           = 0xFE

  # __LED0_ON_L          = 0x06
  # __LED0_ON_H          = 0x07
  # __LED0_OFF_L         = 0x08
  # __LED0_OFF_H         = 0x09
  
  # __LED15_ON_L          = 0x42
  
  # __ALLLED_ON_L        = 0xFA
  # __ALLLED_ON_H        = 0xFB
  # __ALLLED_OFF_L       = 0xFC
  # __ALLLED_OFF_H       = 0xFD
  
  def __init__(self, i2c_controller,address=0x48,easy_mdoe= True,debug=False,):
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
    print("Ti Ads1115 Device created!")
  
  # def test_

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

  def restart(self):
    print('\n Restart PCA9685 board:0x%02X\n\tThe PWM in regs will be runned from the start'%self.address)
    # 1. Read MODE1 register.
    mode1_data = self.read(self.__MODE1)
    # if self.print_value: 
      
    print("\t0x%02X.Mode1_data:0x%02X"%(self.address,mode1_data))

    # 2. Check that bit 7 (RESTART) is a logic 1. If it is, clear bit 4 (SLEEP). 
        # Allow time for oscillator to stabilize (500 us).
    if (mode1_data & 128): 
      mode1_data = self.write(self.__MODE1,mode1_data & 0xEF) # 239=1110 1111
    # 3. Write logic 1 to bit 7 of MODE1 register. All PWM channels will restart and the
    # RESTART bit will clear
    self.slave.write_to( regaddr= self.__MODE1, out=bytearray(mode1_data | 128 ))
    
    pass

  def quickShutdown(self):
    "Two methods can be used to do an orderly shutdown." 
    "Fastest: write logic 1 to bit 4 in register ALL_LED_OFF_H. "
    self.slave.write_to( regaddr= self.__ALLLED_OFF_H, out= bytearray([0x11]) )
    "Method2: write logic 1 to bit 4 in each active PWM channel LEDn_OFF_H register. "
    pass

  def testPort(self,port): # Add by askar @ 20220703
    print('\n---Testing port: ',hex(port), ' In mode: ', hex(self.read(self.__MODE1)))
    
    old_value = self.read(port)
    test_value = old_value + 1
    
    self.write(port, test_value)
    changed_value = self.read(port)
    
    self.write(port, old_value)  
    final_value = self.read(port)

    print("Ori value: ",old_value,'/',hex(old_value),' Input: ',test_value,'/',hex(test_value),
        '\nChanged content: ',changed_value,'Final content: ',final_value)
    pass
 
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
    
  def read(self, reg): 
    "Read an unsigned byte from the I2C device"
    # result = self.slave.read_byte_data(self.address, reg)
    result = (self.slave.read_from(regaddr = reg,readlen=1))[0]
    # result
    if self.debug: print("\tI2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
 

if __name__=='__main__': # Test codes # Main process
    import os
    print("\n\n")
    print('Testing TI ADS115 \n')
    print(time.strftime('%Y:%m:%d %H:%M:%S', time.localtime()))
    # do_plot = 
    url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/1') 
    url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/1')
    url_2 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FD/1')

    url_PCA = url_0
    url_LSM = url_1
    url_ADS = url_2
    if url_PCA==[] or url_LSM==[]:
        print("Failed on finding PCA or LSM device addr:",url_PCA,url_LSM); exit()
    else : print("Found PCA, LSM device @:",url_PCA,url_LSM) 

    i2c_device = i2c.I2cController()
    i2c_device.configure(url_0)
    adc_device = TiAds1115_01(i2c_device)


    exit()
    process_ctrl = Process(target= ctrlProcess,args=(url_PCA,[]))
    process_sensor = Process(target= sensorProcess, args=(url_LSM,[],do_plot))
    





