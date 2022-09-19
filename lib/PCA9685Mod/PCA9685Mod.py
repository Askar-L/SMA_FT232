import math, time, sys
import pyftdi.i2c as i2c

class PCA9685Mod(object):
  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04

  __MODE1              = 0x00
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
  
  def __init__(self, address=0x40, debug=False,easy_mdoe = False):
    print("New PCA9685 IIC slave created: ",hex(address))
    
    # Instantiate an I2C controller
    i2c_controller = i2c.I2cController()
    # Configure the first interface (IF/1) of the FTDI device as an I2C master
    i2c_controller.configure('ftdi:///1') # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78
    self.i2c_controller = i2c_controller

    self.gpio = i2c_controller.get_gpio()

    # self.FT232_chip = i2c_controller.ftdi()

    
    # Get a port to an I2C slave device
    self.slave = i2c_controller.get_port( address ) # 0x21 
    # self.slave = smbus.SMBus(1)

    self.address = address
    self.debug = debug
    self.osc_clock = 25000000.0
    self.easy_mdoe = easy_mdoe
    # self.initial_values = []
    # self.freqList = [0 for _ in range(10)]
    # self.dutyratioList = [0 for _ in range(10)]
    # self.onoffList = [0 for _ in range(10)]

    self.print_value = False

    if (self.debug): 
      print("Reseting PCA9685: ",'%#x'%self.address )
      print("Initial Mode_1 reg value: ",'%#x'%self.read(self.__MODE1))

  def reset(self): #BUG

      #     The SWRST Call function is defined as the following:
      # 1. A START command is sent by the I2C-bus master.

      # 2. The reserved SWRST I2C-bus address ‘0000 0000’ with the R/W bit set to ‘0’ (write) is
      # sent by the I2C-bus master.

      # 3. The PCA9685 device(s) acknowledge(s) after seeing the General Call address
      # ‘0000 0000’ (00h) only. If the R/W bit is set to ‘1’ (read), no acknowledge is returned to
      # the I2C-bus master.

      # 4. Once the General Call address has been sent and acknowledged, the master sends
      # 1 byte with 1 specific value (SWRST data byte 1):
      # a. Byte 1 = 06h: the PCA9685 acknowledges this value only. If byte 1 is not equal to
      # 06h, the PCA9685 does not acknowledge it.
      # If more than 1 byte of data is sent, the PCA9685 does not acknowledge any more.

      # 5. Once the correct byte (SWRST data byte 1) has been sent and correctly
      # acknowledged, the master sends a STOP command to end the SWRST Call: the
      # PCA9685 then resets to the default value (power-up value) and is ready to be
      # addressed again within the specified bus free time (tBUF).
    print('\n Resetting PCA9685 board:0x%02X'%self.address)
    __SWRST = 0b00000110
    
    print(self.read(__SWRST))

    self.write(0x00,bytearray([0x06]))

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

  def testChannle(self,channel_num):

    if (channel_num<0) or channel_num >15: 
      print("\nIllegal PWM channel: ",channel_num,"\n\tChannel number should in range: [0,15]")
      return False
    else:  
      port = self.__LED0_ON_L + (channel_num)*4
      if self.print_value: print('\nTesting channel: ',channel_num,'; Port: ',port,'/',hex(port))

    # self.sleep(True)
    # self.write(self.__MODE1, 0x11)
   
    self.write(port, 0x99) # ON L
    self.write(port+1, 0x01) # ON H
    self.write(port+2, 0xCC) # LOW L
    self.write(port+3, 0x04) # LOW H
    
    self.write(self.__MODE1, 0x01)

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

  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval =     self.osc_clock/4096    # 25MHz 12-bit
    prescaleval = round(prescaleval/float(freq) )-1

    # if (self.debug):
    print("Setting PWM frequency to %d Hz" % freq)
    print("Estimated pre-scale: %d" % prescaleval)
    
    prescale = prescaleval # math.floor(prescaleval + 0.5)
    
    if (self.debug):      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1)
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    # print("\tOld mode:0x%02X"%oldmode, " Mode to write:0x%02X"%newmode)

    self.slave.write_to( regaddr=self.__MODE1, out=bytearray([newmode])) # go to sleep
    print("\tWritting value: ",prescale,", to prescale reg 0x%02x"%prescale)
    self.slave.write_to( regaddr=self.__PRESCALE, out=bytearray([prescale]) ) # Value
    print("\tBack to awake mode")
    self.slave.write_to( regaddr=self.__MODE1, out=bytearray([oldmode])) # Restart sign


    # self.write(self.__MODE1, newmode,False)        # go to sleep
    # print("\tWritting value: ",prescale,", to prescale reg 0x%02x"%prescale)
    # self.write(self.__PRESCALE, prescale,False)
    # print("\tBack to awake mode")
    # self.write(self.__MODE1, oldmode,False)
    
    # time.sleep(0.005) # 20220729 remove
    # self.write(self.__MODE1, oldmode | 0x80) # Restart sign
  
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
    
    if (self.debug):      print("\tChannel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))

  def setDutyRatioCH(self,channel,duty_ratio,stop_sending=True):

    if not self.easy_mdoe:
      print("Pls use easy mode to Duty Ratio!"); return []
    if (channel<0) or channel >15: 
      print("\nIllegal PWM channel: ",channel,"\n\tShould in range: [0,15]"); return []
    elif duty_ratio<0 or duty_ratio>1:print("\n\n\t\tREALLY?!?! Illegeal DUTY RATIO!! ");return []
    else:  
      port = self.__LED0_ON_L + (channel)*4
      if self.print_value: print('\nTesting channel: ',channel,'; Port: ',channel,'/',hex(channel))
      
      off_time =int((4096-1) * duty_ratio )# [off_time_H,off_time_L] = [0000,off_time(12Bit)]
      
      off_time_b_shortstr= bin(off_time)[2:] # ig: 819/0b1100110011/
      
      len_off_t = len(off_time_b_shortstr)
      if (len_off_t<12) and (len_off_t>0):
        off_time_b = str("0"*(12-len_off_t)) + str(off_time_b_shortstr)
      elif len_off_t == 12: off_time_b = off_time_b_shortstr
      else: print("\n Err!: encoding err inside setChannelDutyRatio when encoding dutyretio in ez mode")
      
      off_time_b = str("0"*(4)) + off_time_b
      len_off_time_b = len(off_time_b)
      if not len_off_time_b == 16:  
        print(off_time_b,"Len:",len_off_time_b)
        print("Err: Encoding err, data not correct"); exit()
      else: 
        off_time_L = int(off_time_b[8:],2)
        off_time_H = int(off_time_b[0:7],2)    
      
      if stop_sending:
        self.slave.write_to( regaddr=port, out=bytearray([0x00]),relax=False ) # Value
        self.slave.write_to( regaddr=port+1, out=bytearray([0x00]),relax=False ) # Value
        self.slave.write_to( regaddr=port+2, out=bytearray([off_time_L]),relax=False ) # Value
        self.slave.write_to( regaddr=port+3, out=bytearray([off_time_H])) # Value
      else:
        # self.slave.write_to( regaddr=port, out=bytearray([0x00]),relax=False ) # Value
        # self.slave.write_to( regaddr=port+1, out=bytearray([0x00]),relax=False ) # Value
        self.slave.write_to( regaddr=port+2, out=bytearray([off_time_L]),relax=False ) # Value
        self.slave.write_to( regaddr=port+3, out=bytearray([off_time_H]),relax=False) # Value
    
    return []

  def setDutyRatioCHS(self,channels,duty_ratio,stop_sending=True): # 20220815
    if len(channels) < 1: print("\nNo target channel!"); return []
    elif len(channels) > 1:
      for _ch in channels[:len(channels)-1]: 
        self.setDutyRatioCH(_ch,duty_ratio,stop_sending=False)
    self.setDutyRatioCH(channels[-1],duty_ratio,stop_sending)    
    return []

  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    freq = 50 #Hz
    period = 1000000 / freq # period (us)
    pulse = int(pulse*4096/20000)        #PWM frequency is 50HZ,the period is 20000us

    print('pulse: ',pulse)
     
    self.setPWM(channel, 0, pulse)
  
  # 手部功能的初级实现！ 后需另外建立lib
  def test_wires(self,channels,dutys,intervals,conf0 = False):
    # [active_duty,sustain_duty,stop_duty] = dutys
    # [burst_interval,sustain_interval,stop_interval] = intervals
    if not len(dutys)==len(intervals): 
      print("\n\nError!\tin test_wires\t"); return []
    if conf0 and not channels[-1]==0 : channels.append(0)

    for _duty,_interval in zip(dutys,intervals) :
        print(channels,_duty,_interval)
        self.setDutyRatioCHS(channels,_duty)
        time.sleep(_interval)
        self.setDutyRatioCHS(channels,0)

