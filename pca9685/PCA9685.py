# Created by Askar based on a gitbuh project
# Modified in 2022 10 14
from ast import Pass
import math, time, sys
from lib.GENERALFUNCTIONS import *

class Pca9685_01(object):
  # Registers/etc.
  __MODE1              = 0x00
  __MODE2              = 0x01

  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  
  # __SWRST              = 0x06
  
  
  __PRESCALE           = 0xFE

  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  
  __LED15_ON_L          = 0x42
  
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  CH_EVEN = [0,2,4,6,8,10,12,14]
  CH_ODD = [1,3,5,7,9,11,13,15]
  CH_ALL = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]



  def __init__(self, i2c_controller,address=0x40,easy_mdoe= True,debug=False,):
    print("Creating New PCA9685 IIC slave :",hex(address))
    
    self.i2c_controller = i2c_controller
    # self.FT232_chip = i2c_controller.ftdi()
    
    # Get a port to an I2C slave device
    self.slave = i2c_controller.get_port( address ) # 0x21 
    
    # self.slave = smbus.SMBus(1)

    self.address = address
    self.debug = debug
    self.osc_clock = 25000000.0
    self.easy_mdoe = easy_mdoe 
    self.OCH_mode = False
    self.AI = False

    
    self.restart()
    self.reset()

    self.setOCH() # # Output change on ack mode
    self.setAI(True)



  def reset(self): #BUG
    i2c_controller = self.i2c_controller
    #     The SWRST Call function is defined as the following:
    # 1. A START command is sent by the I2C-bus master.
    i2c_controller._do_prolog( (self.address << 1) & i2c_controller.HIGH )
    # 2. The reserved SWRST I2C-bus address ‘0000 0000’ with the R/W bit set to ‘0’ (write) is
    # sent by the I2C-bus master.

    # 3. The PCA9685 device(s) acknowledge(s) after seeing the General Call address
    # ‘0000 0000’ (00h) only. If the R/W bit is set to ‘1’ (read), no acknowledge is returned to
    # the I2C-bus master.

    self.write(0x00,bytearray([0x06]),doCheck=False)

    # 4. Once the General Call address has been sent and acknowledged, the master sends
    # 1 byte with 1 specific value (SWRST data byte 1):
    # a. Byte 1 = 06h: the PCA9685 acknowledges this value only. If byte 1 is not equal to
    # 06h, the PCA9685 does not acknowledge it.
    # If more than 1 byte of data is sent, the PCA9685 does not acknowledge any more.

    # 5. Once the correct byte (SWRST data byte 1) has been sent and correctly
    # acknowledged, the master sends a STOP command to end the SWRST Call: the
    # PCA9685 then resets to the default value (power-up value) and is ready to be
    # addressed again within the specified bus free time (tBUF).
    
    
    
    # print(self.read(__SWRST))

    print('\nSucess Reseted PCA9685 board:0x%02X'%self.address)
    self.i2c_controller._do_epilog()
 

    if self.debug: 
      print("Reseting PCA9685: ",'%#x'%self.address )
      print("Initial Mode_1 reg value: ",'%#x'%self.read(self.__MODE1))
      print("Initial Mode_2 reg value: ",'%#x'%self.read(self.__MODE2))

    return []

  def restart(self):
    print('\n Restart PCA9685 board:0x%02X\n  The PWM in regs will be runned from the start'%self.address)
    # 1. Read MODE1 register.
    mode1_data = self.read(self.__MODE1)      
    print("  0x%02X.Mode1_data:0x%02X"%(self.address,mode1_data))

    # 2. Check that bit 7 (RESTART) is a logic 1. If it is, clear bit 4 (SLEEP). 
        # Allow time for oscillator to stabilize (500 us).
    if (mode1_data >>6)==1: 
      mode1_data = self.write(self.__MODE1,mode1_data & 0xEF) # 239=1110 1111

    # 3. Write logic 1 to bit 7 of MODE1 register. All PWM channels will restart and the
    # RESTART bit will clear
    self.slave.write_to( regaddr= self.__MODE1, out=bytearray(mode1_data | 128 ))

    time.sleep(1)
    mode1_data = self.read(self.__MODE1)   
    print('  MODE1 after reset: ',bin(mode1_data))
    # exit()

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

  def testChannle(self,channel_num):

    if (channel_num<0) or channel_num >15: 
      print("\nIllegal PWM channel: ",channel_num,"\n  Channel number should in range: [0,15]")
      return False
    else:  
      port = self.__LED0_ON_L + (channel_num)*4
      if self.debug: print('\nTesting channel: ',channel_num,'; Port: ',port,'/',hex(port))

    # self.sleep(True)
    # self.write(self.__MODE1, 0x11)
   
    self.write(port, 0x99) # ON L
    self.write(port+1, 0x01) # ON H
    self.write(port+2, 0xCC) # LOW L
    self.write(port+3, 0x04) # LOW H
    
    self.write(self.__MODE1, 0x01)
    # time.pause(0.5)
    self.setDutyRatioCH(channel_num,0)

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
          if self.debug: print("  Inputted and saved values are equal, however it is still writted!")
        else: 
          print("  Value is changed, however does not mattches the desire value!")
          print("  Consider chaecking the chip datasheet about the correct value for changing")
          
      # if self.debug: print("  I2C: Device 0x%02X writted 0x%02X to reg 0x%02X" % (self.address, input_value, reg_add))
      return value_after
    return in_value
    
  def read(self, reg): 
    "Read an unsigned byte from the I2C device"
    # result = self.slave.read_byte_data(self.address, reg)
    result = (self.slave.read_from(regaddr = reg,readlen=1))[0]
    # result
    if self.debug: print("  I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result

  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescale_val =     self.osc_clock/4096    # 25MHz 12-bit
    prescale_val = round(prescale_val/float(freq) )-1

    # if (self.debug):
    print("Setting PWM frequency to %d Hz" % freq)
    print("Estimated pre-scale: %d" % prescale_val)
    
    prescale = prescale_val # math.floor(prescaleval + 0.5)
    
    if (self.debug):      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1)
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    # print("  Old mode:0x%02X"%oldmode, " Mode to write:0x%02X"%newmode)

    self.slave.write_to( regaddr=self.__MODE1, out=bytearray([newmode])) # go to sleep
    print("  Writting value: ",prescale,", to prescale reg ",hex(self.__PRESCALE))
    self.slave.write_to( regaddr=self.__PRESCALE, out=bytearray([prescale]) ) # Value
    print("  Back to awake mode")
    self.slave.write_to( regaddr=self.__MODE1, out=bytearray([oldmode])) # Restart sign
    
  def setOCH(self): # updated @20231229
    # Output change on ack mode
 
    # sleep
    oldmode1 = self.read(self.__MODE1)
    newmode1 = (oldmode1 & 0x7F) | 0x10        
    self.slave.write_to( regaddr=self.__MODE1, out=bytearray([newmode1])) # go to sleep

    oldmode2 = self.read(self.__MODE2)
    newmode2 = (oldmode2 | 0x08) # OCH ON/OFF

    # print("  Writting value: ",prescale,", to prescale reg ",hex(self.__PRESCALE))
    self.slave.write_to( regaddr=self.__MODE2, out=bytearray([newmode2]) ) # Value
    # print("  Back to awake mode")

    self.slave.write_to( regaddr=self.__MODE1, out=bytearray([oldmode1])) # Restart sign
    if self.debug:
      print("oldmode2: 0x%02X New:0x%02X" % (oldmode2, self.read(self.__MODE2)) )
    
    current_mode_2 = self.read(self.__MODE2)
    if current_mode_2 & 0x08:
      print(' OCH mode opened.')
      self.OCH_mode = True
      return True 
    else:
      print('\n\nFAILED: OCH mode open failed!\n  OCH mode: Output change on ACK')
      return False

  def setAI(self,is_on):
    # Set Auto Increasment Mode@20231229
    _oldmode1 = self.slave.read_from(self.__MODE1,1)[0]
    _oldmode2 = self.slave.read_from(self.__MODE2,1)[0]
    
    if self.debug: 
      print('-'*20,'Pca9685_01.setAI()')
      print('_oldmode1: ',bin(_oldmode1),'_oldmode2',bin(_oldmode2))

    self.AI = True if (_oldmode1 & 0x20) else False 
    if self.debug: print('AI mode: ',self.AI)

    if  (_oldmode1 & 0x20 ) ^ is_on: # IF NOT SAME
      if is_on:
        _newmode1 = (_oldmode1 | 0x20 ) # AI ON/OFF
      else:
        _newmode1 = (_oldmode1 & 0xDF ) # AI ON/OFF
      self.slave.write_to( regaddr=self.__MODE1, out=bytearray([_newmode1]) ) # Value

      self.AI = True if (self.read(self.__MODE1) & 0x20) else False
      if self.debug: print('_newmode1: ',bin(_newmode1),' now: ',bin(self.read(self.__MODE1)),'self.AI',self.AI)

      if not self.AI ==  is_on:
        print('\n\nFAILED: Failed on setting AI mode:\n  self.AI old:'
              ,bin(_oldmode1),' Cuurent',bin(self.AI))
        exit()
      else: return self.AI

  def getPWMFreq(self):
    cur_prescala = self.read(self.__PRESCALE)
    cur_freq = self.osc_clock/((cur_prescala+1)*4096)
    return cur_freq

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    print(" IN/out: ", self.__LED0_ON_L+4*channel, self.read(self.__LED0_ON_L+4*channel))
    
    print("On: ",on,',',on & 0xFF,' ',on >> 8,'; Off', off)

    self.write(self.__LED0_ON_L+4*channel, on & 0xFF) # & 1111 1111
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    
    if (self.debug):      print("  Channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))

  def setOnTime(self,channel=[_i-1 for _i in range(16)]):
    # NOT ready
    for _ch in channel:
      port = self.__LED0_ON_L + (_ch)*4
      self.slave.write_to( regaddr=port, out=bytearray([0x00]),relax=False ) # Value On time Low
      self.slave.write_to( regaddr=port+1, out=bytearray([0x00]),relax=True ) # Value On time H
      return []
  
  def setDutyRatioCH(self,channel,duty_ratio,relax=True):

    # if not self.easy_mdoe:
    #   print("Pls use easy mode to Duty Ratio!"); return []
    # if (channel<0) or channel >15: 
    #   print("\nIllegal PWM channel: ",channel,"\n  Should in range: [0,15]"); return []
    # elif duty_ratio<0 or duty_ratio>1:
    #   print("\n\n     Illegeal DUTY RATIO!! \nPlease set duty ratio to 0-1"); return []

    
    port = self.__LED0_ON_L + (channel)*4
    # if self.debug: print('\nTesting channel: ',channel,'; Port: ',channel,'/',hex(channel))
    
    off_time =int((4096-1) * duty_ratio )# [off_time_H,off_time_L] = [0000,off_time(12Bit)]
    off_time_L = off_time & 0xFF
    off_time_H = off_time >> 8

    if not self.AI:  
      if relax and (not self.OCH_mode): #
        # self.slave.write_to( regaddr=port, out=bytearray([0x00]),relax=False ) # Value
        # self.slave.write_to( regaddr=port+1, out=bytearray([0x00]),relax=False ) # Value
        self.slave.write_to( regaddr=port+2, out=bytearray([off_time_L]),relax=False ) # Value
        self.slave.write_to( regaddr=port+3, out=bytearray([off_time_H])) # Value
      else:
        # _data =  [0x00,0x00,off_time_L,off_time_H]
        self.slave.write_to( regaddr=port, out=bytearray([0x00]),relax=False ) # Value On time Low
        self.slave.write_to( regaddr=port+1, out=bytearray([0x00]),relax=False ) # Value On time H
        self.slave.write_to( regaddr=port+2, out=bytearray([off_time_L]),relax=False ) # Value
        self.slave.write_to( regaddr=port+3, out=bytearray([off_time_H]),relax=False) # Value
    else:
        _data =  [0x00,0x00,off_time_L,off_time_H]
        self.slave.write_to( regaddr=port, out=bytearray(_data),relax=relax ) 
  
    return []
  
  def setDutyRatioCHS(self,channels,duty_ratio,relax=False): # 20220815

    if len(channels) >= 1:
      if self.OCH_mode:
        for _ch in channels: 
          self.setDutyRatioCH(_ch,duty_ratio,relax=relax)
      else:
        for _ch in channels[:len(channels)-1]: 
          self.setDutyRatioCH(_ch,duty_ratio,relax=False)
        self.setDutyRatioCH(channels[-1],duty_ratio,relax=relax)  
    else :
      self.setDutyRatioCH(channels[-1],duty_ratio,relax=relax)   

    return []

  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    freq = 50 #Hz
    period = 1000000 / freq # period (us)
    pulse = int(pulse*4096/20000)        #PWM frequency is 50HZ,the period is 20000us

    print('pulse: ',pulse)
     
    self.setPWM(channel, 0, pulse)
  
  # 手部功能的初级实现！ 后需另外建立lib
  def test_wires(self,channels,dutys,intervals,is_show = False):
    # [active_duty,sustain_duty,stop_duty] = dutys
    # [burst_interval,sustain_interval,stop_interval] = intervals
    # if not len(dutys)==len(intervals): 
    #   print("\n\nError!  in test_wires  "); return []

    # if conf0 and not channels[-1]==0 : channels.append(0)


    # Open AutoIncreasing mode:
    # self.setAI(True)

    for _duty,_interval in zip(dutys,intervals) :
        if is_show: print("PCA Setting Duty Ratio",channels,_duty,_interval)

        self.setDutyRatioCHS(channels,_duty)

        if is_show: print("DR SET at:", time.time()- RUNTIME,
              " Related to ",time.strftime('%Y:%m:%d %H:%M:%S'
                                           , time.localtime(RUNTIME)) )
        time.sleep(_interval)

        self.setDutyRatioCHS(channels,0)

        if is_show: print("DR OVER at:", time.time()- RUNTIME,
              " Related to ",time.strftime('%Y:%m:%d %H:%M:%S'
                                           , time.localtime(RUNTIME)) )

  def communication_speed_test(self,wire_channles= CH_ALL,cycles=40):

    self.setOCH()
    self.setAI(True)

    t_st =time.time()
    for _ in range(cycles):
      self.setDutyRatioCH(0,1,relax=False)
      self.setDutyRatioCH(0,0,relax=False)
    t_end = time.time()

    print('Single Ch Refreshing : Avg Duration:',(t_end-t_st)/cycles,' Freq: ',cycles/(t_end-t_st))
   
    t_st =time.time()
    for _ in range(cycles):
      self.setDutyRatioCHS(wire_channles,1,relax=False)
      self.setDutyRatioCHS(wire_channles,0,relax=False)

    t_end = time.time()

    print('All Ch Refreshing: Avg Duration:',(t_end-t_st)/cycles,' Freq: ',cycles/(t_end-t_st))
   

    t_st =time.time()
    for _ in range(cycles):
      self.setDutyRatioCHS(wire_channles,1,relax=False)
      self.setDutyRatioCHS(wire_channles,0,relax=False)

    t_end = time.time()

    print('All: Avg Duration:',(t_end-t_st)/cycles,' Freq: ',cycles/(t_end-t_st))