from cgitb import reset
from matplotlib.cbook import to_filehandle
import pyftdi.i2c as i2c
# class Device(object):
#   # Registers/etc.
#   # __SUBADR1            = 0x02

#   def __init__(self, i2c_controller, address=0x6A, debug=False, easy_mdoe=False):
#     # default slave addr== 1101010xb/0x6A OR 1101011xb/0x6B
#     pass

#   def reset(self):  # BUG
#     pass

#   def restart(self):
#     pass

#   def quickShutdown(self):
#     pass

#   def write(self, reg_add, input_value, doCheck=True):
#     pass

#   def read(self, reg):
#     pass

#   def setServoPulse(self, channel, pulse):
#     pass

import math, time, sys

# import Adafruit_GPIO.I2C as I2C
# i2c = I2C.get_i2c_device(address)
# i2c.write8(0X10, dataToWrite)

    # def write8(self, register, value):
    #     """Write an 8-bit value to the specified register."""
    #     value = value & 0xFF
    #     self._bus.write_byte_data(self._address, register, value)
    #     self._logger.debug("Wrote 0x%02X to register 0x%02X",value, register)

    # def write_byte_data(self, addr, cmd, val):
    #     """Write a byte of data to the specified cmd register of the device."""
    #     assert ( self._device is not None), "Bus must be opened before operations are made against it!"
    #     # Construct a string of data to send with the command register and byte value.

    #     data = bytearray(2)
    #     data[0] = cmd & 0xFF
    #     data[1] = val & 0xFF
    #     # Send the data to the device.
    #     self._select_device(addr)
    #     self._device.write(data)

class LSM6DS3mb:
  # from https://github.com/maxofbritton/Raspberry-Pi-4x4-in-Schools-Project/blob/master/LSM6DS3.py
  # address = 0x6b
  slave = None
  tempvar = 0
  __FIFO_CTRL5 = 0x0A
  __WHO_AM_I = 0x0F

  __CTRL1_XL = 0x10 # Accelerometer controls # [ODR*4,FS*2,BW*2]
  __CTRL2_G = 0x11 # gyroscope, angluar rate sensor control 
  __CTRL3_C = 0x12 # System ctrl 
  __CTRL5_C = 0x14 # Output on/off
  __CTRL6_C = 0x15 # Anglar rate sensor ctrl
  __CTRL9_XL = 0x18 # Output on/off
  __CTRL10_C = 0x19 # Output on/off of gyoscope

  __OUT_TEMP_L = 0x20 # Temp low
  __OUT_TEMP = 0x21
  __OUTX_L_G = 0x22 # Low of Gyroscope X, +1=X_High,+2=Y_low,+4=Z_low
  __OUTX_L_XL = 0x28 # Low of Gyroscope X

  __FIFO_STATUS2 = 0x3B
    
  def __init__(self,i2c_controller,address=0x6b, debug=0, pause=0.8):
    self.i2c = i2c_controller
    self.address = address

    # self.slave = i2c_controller # I2C.get_i2c_device(address)
    self.slave = i2c_controller.get_port( address ) # 0x21 
    
    self.Regs_Angular_acc = [0X22,0X24,0X26] # [X,Y,Yew]_Low
    self.Regs_Linear_acc = [0X28,0X2A,0X2C] # [X,Y,Z]_Low
    self.Regs_Temp = [0X20] # [Temp_Low]

    # Test who am I
    if not self.readReg(self.__WHO_AM_I)-0x69 ==0 : print("Who am I test failed!"); exit()

    # FIFO Bypass mode
    # ...

    # Accelerometer / gyroscope mode controls

    print("Default values: ")
    print('__WHO_AM_I: ',self.readReg(self.__WHO_AM_I))
    print('__CTRL1_XL: ',self.readReg(self.__CTRL1_XL))
    print('__CTRL6_C XL_HM_MODE: ',self.readReg(self.__CTRL6_C))

    print('__CTRL9_XL: ',self.readReg(self.__CTRL9_XL))
    # print('__OUT_TEMP_L: ',self.readReg(self.__OUT_TEMP_L))
    # print('__OUT_TEMP_H: ',self.readReg(self.__OUT_TEMP_L+1))

    # Enable __CTRL9_XL: Linear Acceleration sonsor 
    # Default 0x38h/56d/00111000b  
    print("\n__CTRL9_XL \n\tDefault\t: ",0x38)
    # self.writeReg(self.__CTRL9_XL,0x12)
    self.slave.write(self.__CTRL9_XL,bytearray([self.__CTRL9_XL, 0x38])) # On/off of accelermeter
    print('\tNow\t: ',self.readReg(self.__CTRL9_XL))

    # Enable __CTRL1_XL: Linear Acceleration sonsor setting
    # Default 0x00
    AG_mode = '1010' # OutDataRate 1010 High performance @ 6.66kHz
    AG_mode+= '00'   # FS  11 for +-8g; 00 for +-2g
    AG_mode+= '00'   # BW  Anti-aliasing 
    AG_mode = int(AG_mode,2)

    print("\n__CTRL1_XL \n\tDefault\t: ",0x00,"\t New",AG_mode)
    # self.writeReg(self.__CTRL1_XL,bytearray([AG_mode]))
    to_write = bytearray([self.__CTRL1_XL,AG_mode])
    self.slave.write_to(self.__CTRL1_XL,to_write) # On/off of accelermeter
    print('to_write ',to_write)
    # self.slave.write() # On/off of accelermeter
    # self.slave.write() # On/off of accelermeter
    print('\tNow\t: ',self.readReg(self.__CTRL1_XL))
    
    # self.slave.write(self.__CTRL2_G, bytearray([AG_mode])) # On/off of Gyroscope
    # self.slave.write(self.__CTRL5_C, bytearray([int('01100000',2)]))
    # self.slave.write(self.__CTRL9_XL, bytearray([int('00111000',2)]))


    self.accel_center_x = self.readRawAccel(0)#self.i2c.readS16(0X28)
    self.accel_center_y = self.readRawAccel(1)#self.i2c.readS16(0x2A)
    self.accel_center_z = self.readRawAccel(2)#self.i2c.readS16(0x2C)

  # def write(self, reg_add, input_value, doCheck = True): #Todo
  #   "Writes an 8-bit value to the specified register/address"
    
  #   if doCheck :value_before =  (self.slave.read_from(regaddr=reg_add, readlen=1))[0]#

  #   if isinstance(input_value,int): in_value =  bytearray([input_value]) 
  #   else: in_value = input_value

  #   self.slave.write_to( regaddr= reg_add, out= in_value)
    
  #   if doCheck: # Check
  #     time.sleep(0.1)
  #     value_after =  self.slave.read_from(regaddr=reg_add, readlen=1)[0]# self.read(reg_add)
  #     if (value_after-value_before) == 0:
  #       if input_value == value_after: 
  #         if self.debug: print("\tInputted and saved values are equal, however it is still writted!")
  #       else: 
  #         print("\tValue is changed, however does not mattches the desire value!")
  #         print("\tConsider chaecking the chip datasheet about the correct value for changing")
          
  #     if self.debug: print("\tI2C: Device 0x%02X writted 0x%02X to reg 0x%02X" % (self.address, input_value, reg_add))
  #     return value_after
  #   return in_value
    
  # def read(self, reg):  #Todo
  #   "Read an unsigned byte from the I2C device"
  #   # result = self.slave.read_byte_data(self.address, reg)
  #   result = (self.slave.read_from(regaddr = reg,readlen=1))[0]
  #   # result
  #   if self.debug: print("\tI2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
  #   return result
  

  
  def writeReg(self,reg_addr,dataToWrite):
    # 0xD6 -> DATA
    self.slave.write(bytearray([0xD6,reg_addr,dataToWrite]))
    # self.slave.write(self.reg_addr, bytearray([dataToWrite]))

  def readReg(self,reg_addr):
    res = self.slave.read_from(regaddr = reg_addr,readlen=1)[0]
    return res

  def readFIFOstate(self):
    reg = self.__FIFO_STATUS2
    # accel_bin_L = bin(self.slave.read_from(regaddr = reg,readlen=1)[0])
    # accel_bin_H = bin(self.slave.read_from(regaddr = reg+1,readlen=1)[0])
    # accel_bin = ('0000000'+str(accel_bin_H)[2:])[-8:] + ('0000000'+str(accel_bin_L[0][2:]))[-8:]

  def readRawAccel(self,axis):
    reg = self.Regs_Linear_acc[axis]
    accel_L = self.slave.read_from(regaddr = reg,readlen=1)[0]
    accel_H = self.slave.read_from(regaddr = reg+1,readlen=1)[0]
    acc_int = (accel_H << 8) + accel_L
    if accel_H>>7: acc_int = acc_int - (1<<16)
    return acc_int
  
#   def readAllAccel(self,axis):
#     reg = self.Regs_Linear_acc[axis]
#     data = self.slave.read_from(regaddr = reg,readlen=2)
#     accel_L = data[0]
#     accel_H = data[1]
#     print(data)
#     acc_int = (accel_H << 8) + accel_L
#     if accel_H>>7: acc_int = acc_int - (1<<16)
#     return acc_int

  def read16BitValue(self,reg_L):
    bL = self.slave.read_from(regaddr = reg_L,readlen=1)[0]
    bH = self.slave.read_from(regaddr = reg_L+1,readlen=1)[0]
    bInt = (bH << 8) + bL
    if bH>>7: bInt = bInt - (1<<16)
    return bInt


  def readTemp(self): # self.__OUT_TEMP_L
    # reg_L = self.__OUT_TEMP_L
    # bL = self.slave.read_from(regaddr = reg_L,readlen=1)[0]
    # bH = self.slave.read_from(regaddr = reg_L+1,readlen=1)[0]
    # bInt = (bH << 8) + bL
    # if bH>>7: bInt = bInt - (1<<16)
    # return bInt
    temp = self.read16BitValue(self.__OUT_TEMP_L)
    
    return temp

  def calcAnglesXY(self):
    # Using x y and z from accelerometer, calculate x and y angles
    x_val = 0; y_val = 0; z_val = 0; result = 0
    x2 = 0; y2 = 0; z2 = 0

    x_val = self.readRawAccel(0) - self.accel_center_x
    y_val = self.readRawAccel(1) - self.accel_center_y
    z_val = self.readRawAccel(2) - self.accel_center_z

    x2 = x_val*x_val
    y2 = y_val*y_val
    z2 = z_val*z_val

    result = math.sqrt(y2+z2)
    if (result != 0): result = x_val/result
    accel_angle_x = math.atan(result)
    return accel_angle_x

  def readRawGyroX(self):
      output = self.slave.readS16(0X22)
      return output

  def readFloatGyroX(self):
      output = self.calcGyro(self.readRawGyroX())
      return output

  def calcGyroXAngle(self):
      temp = 0
      temp += self.readFloatGyroX()
      if (temp > 3 or temp < 0): self.tempvar += temp
      return self.tempvar

  def calcGyro(self, rawInput):
      gyroRangeDivisor = 245 / 125  # 500 is the gyro range (DPS)
      output = rawInput * 4.375 * (gyroRangeDivisor) / 1000
      return output
