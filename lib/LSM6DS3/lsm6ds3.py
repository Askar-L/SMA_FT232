# Created by Askar 
# Modified in 2022 10 14

from base64 import b16encode
from cgitb import reset
from matplotlib.cbook import to_filehandle
import pyftdi.i2c as i2c
import math, time, sys

# import Adafruit_GPIO.I2C as I2C
# i2c = I2C.get_i2c_device(address)
# i2c.write8(0X10, dataToWrite)

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

  __OUTX_L_G = 0x22 # Angular rate sensor outpout reg (first low)
  # +1=X_High,+2=Y_low,+4=Z_low

  # X Y Z: Pitch,Roll,Yaw
  __OUTX_L_XL = 0x28 # Linear Acc sensor outpout reg (first low)

  __FIFO_STATUS2 = 0x3B
    
  def __init__(self,i2c_controller,address=0x6b, debug=0, pause=0.8):
    self.i2c = i2c_controller
    self.address = address

    # self.slave = i2c_controller # I2C.get_i2c_device(address)
    self.slave = i2c_controller.get_port( address ) # 0x21 
    
    self.Regs_Angular_acc = [0X22,0X24,0X26] # [X,Y,Yew]_Low
    self.Regs_Linear_acc = [0X28,0X2A,0X2C] # [X,Y,Z]_Low
    self.Regs_Temp = [0X20] # [Temp_Low]
    self.reset()

    # FIFO Bypass mode    # ...

    # Accelerometer / gyroscope mode controls

    # self.slave.write(self.__CTRL2_G, bytearray([AG_mode])) # On/off of Gyroscope
    # self.slave.write(self.__CTRL9_XL, bytearray([int('00111000',2)]))

    # self.accel_center_x = self.rawLinearAcc(0)#self.i2c.readS16(0X28)
    # self.accel_center_y = self.rawLinearAcc(1)#self.i2c.readS16(0x2A)
    # self.accel_center_z = self.rawLinearAcc(2)#self.i2c.readS16(0x2C)
    pass

  # def read(self, reg):  #Todo
  #   "Read an unsigned byte from the I2C device"
  #   # result = self.slave.read_byte_data(self.address, reg)
  #   result = (self.slave.read_from(regaddr = reg,readlen=1))[0]
  #   # result
  #   if self.debug: print("\tI2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
  #   return result
    
  def writeReg(self,reg_addr,dataToWrite):
    # 0xD6 -> DATA
    # to_write = 
    self.slave.write_to(reg_addr,bytearray([dataToWrite])) # On/off of accelermeter

  def readReg(self,reg_addr):
    res = self.slave.read_from(regaddr = reg_addr,readlen=1)[0]
    return res
  
  def reset(self):  
    self.writeReg(self.__CTRL3_C,0b00000101)
    
    # Test who am I
    if not self.readReg(self.__WHO_AM_I)-0x69 ==0 : print("Who am I test failed!"); exit()

    print("Default values: ")
    print('__CTRL1_XL: ',self.readReg(self.__CTRL1_XL))
    print('__CTRL6_C XL_HM_MODE: ',self.readReg(self.__CTRL6_C))

    # self.slave.write(self.__CTRL5_C, int('11100000',2)) # Not neccesary

    # Enable __CTRL9_XL: Linear Acceleration sonsor   # Not neccesary
    # Default 0x38h/56d/00111000b  
    # print("\n__CTRL9_XL \n\tDefault\t: ",0x38)
    # self.slave.write(self.__CTRL9_XL, 0x38) # On/off of accelermeter
    # print('\tNow\t: ',self.readReg(self.__CTRL9_XL))

    # Setting __CTRL1_XL: Linear Acceleration sensor setting
    # Default 0x00
    AG_mode = '1010' # OutDataRate 1010 High performance @ 6.66kHz
    AG_mode+= '00'   # FS  11 for +-8g; 00 for +-2g
    AG_mode+= '00'   # BW  Anti-aliasing 
    AG_mode = int(AG_mode,2)

    print("\n__CTRL1_XL \n\tDefault\t: ",0x00,"\t New",AG_mode)
    self.slave.write_to(self.__CTRL1_XL,bytearray([AG_mode]))
    # self.writeReg(self.__CTRL1_XL,AG_mode)
    print('\tNow\t: ',self.readReg(self.__CTRL1_XL))
    
    # Enable __CTRL2_G: Angular rate sensor setting
    AG_mod = '1000' + '10'+'0' + '0'
    self.slave.write_to(self.__CTRL2_G,bytearray([AG_mode]))
 
  def readWord(self,reg_L):
    b16 = self.slave.read_from(regaddr = reg_L,readlen=2)
    bL = b16[0];bH = b16[1]
    bInt = (bH << 8) + bL
    if bH>>7: bInt = bInt - (1<<16)
    return bInt

  def rawLinearAcc(self,axis):
    reg = self.Regs_Linear_acc[axis]
    accel_L = self.slave.read_from(regaddr = reg,readlen=1)[0]
    accel_H = self.slave.read_from(regaddr = reg+1,readlen=1)[0]
    acc_int = (accel_H << 8) + accel_L
    if accel_H>>7: acc_int = acc_int - (1<<16)
    return acc_int

  def rawAngularRate(self,axis):
    reg = self.Regs_Angular_acc[axis]
    accel_L = self.slave.read_from(regaddr = reg,readlen=1)[0]
    accel_H = self.slave.read_from(regaddr = reg+1,readlen=1)[0]
    acc_int = (accel_H << 8) + accel_L
    if accel_H>>7: acc_int = acc_int - (1<<16)
    return acc_int
  
  def decode(self,input):
    output = []
    for _item in input:
      _value_dec = _item
      if _item>>15: _value_dec = _item - (1<<16)
      output.append(_value_dec)

    return output

  def readHighSpeed(self): # TODO
    len_load = 7
    retry_load_max = 5

    hex_raw = []   
    while not len(hex_raw) == len_load*2:
      if retry_load_max <= 0: print("Failed when loading:",len_load,"*2 bytes data.");break
      hex_raw = self.slave.read_from(self.__OUT_TEMP_L,len_load*2)
    if not retry_load_max == 5: print("\n\nAlert!: lsm6ds3.readHighSpeed() retired ",5-retry_load_max,'times.')
    # print(hex_raw,len(hex_raw))

    # print(hex_raw[::2]) # Odd 
    # print(hex_raw[1::2]) # Even
    # print(hex_raw,hex_raw<<8,(hex_raw<<8)>>8)

    # words = list(map(lambda x, y: x + y<<8, hex_raw[::2], hex_raw[1::2]))
    
    i = 0; output = []
    for _byte in hex_raw:
      if i%2 == 1: # 偶数项 H 高位
        output[-1] += (_byte<<8)
        if (_byte >>7) ==1:  output[-1] -= (1<<16) 
      else: output.append(_byte)
      i += 1

    # output = []
    # for _item in words:
    #   _value_dec = _item
    #   if _item>>15==1: 
    #     print(_item)
    #     _value_dec = _item - (1<<16)
    #   output.append(_value_dec)
    return output

  def temp(self): return self.readWord(self.__OUT_TEMP_L) # self.__OUT_TEMP_L

  # NOT ready functions
  def calcAnglesXY(self):
    # Using x y and z from accelerometer, calculate x and y angles
    x_val = 0; y_val = 0; z_val = 0; result = 0
    x2 = 0; y2 = 0; z2 = 0

    x_val = self.rawLinearAcc(0) - self.accel_center_x
    y_val = self.rawLinearAcc(1) - self.accel_center_y
    z_val = self.rawLinearAcc(2) - self.accel_center_z

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

  def readFIFOstate(self):
    reg = self.__FIFO_STATUS2
    # accel_bin_L = bin(self.slave.read_from(regaddr = reg,readlen=1)[0])
    # accel_bin_H = bin(self.slave.read_from(regaddr = reg+1,readlen=1)[0])
    # accel_bin = ('0000000'+str(accel_bin_H)[2:])[-8:] + ('0000000'+str(accel_bin_L[0][2:]))[-8:]