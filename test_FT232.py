# from test import test_FT232HQ

# https://eblot.github.io/pyftdi/api/index.html


# Run: set BLINKA_FT232H=1 ; OR :  $env:BLINKA_FT232H=1 ; Before USE


# import usb
# import usb.util
# dev = usb.core.find(idVendor=0x0403, idProduct=0x6014)
# print(dev)
from ast import Pass
from itertools import cycle
import time,os

url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/0') 
import pyftdi.i2c as ftdii2c
# from pyftdi.ftdi import Ftdi
# import pyftdi.gpio as Gpio

if False:
    
    
    gpio = Gpio.GpioAsyncController()

    output_pins = 0 #0b01110110

    gpio.configure( url_0, direction= output_pins ) # 0111 0110

    
    # read whole port
    pins = gpio.read()
    print(pins & ~output_pins) 
    # ignore output values (optional)
    pins &= ~gpio.direction
    gpio.close()

    exit()

if True:
    # use I2C feature
    i2c = ftdii2c.I2cController()
    # configure the I2C feature, and predefines the direction of the GPIO pins
    i2c.configure('ftdi:///1', direction=0x78)
    gpio = i2c.get_gpio()

    output_pins = 0b11111000
    gpio.set_direction( output_pins, output_pins )
    
    # read whole port
    pins = gpio.read()
    print("pins: ",pins)

    # # clearing out I2C bits (SCL, SDAo, SDAi)
    # pins &= 0x07
    # # set AD4
    # pins |= 1 << 4

    # update GPIO output
    t_start = time.time()
    for _i  in range(1000):
        gpio.write(0b00000000)
        gpio.write(output_pins)
    t_end = time.time()
    print(t_end-t_start)
    exit()


if True:
    

    i2c_sensor_controller_URL = url_0
    print("Configuring device ",str(i2c_sensor_controller_URL)," for experiment")

    i2c_device = ftdii2c.I2cController()

    output_pins = 0x78 #0b01111000 # 0b00000000 #11111111 #0b01110110

    i2c_device.configure(i2c_sensor_controller_URL, direction=output_pins) # direction=0x76 & direction=0x78
        
    gpio = i2c_device.get_gpio()

    pins = gpio.read()
    print("pins under IIC:",pins)

    # clearing out I2C bits (SCL, SDAo, SDAi)
    pins &= 0x07
    # set AD4
    pins |= 1 << 4
    # update GPIO output
    gpio.write(pins)

    exit()
 
if True: # Port and env tests


    from pyftdi.ftdi import Ftdi
    Ftdi().open_from_url('ftdi:///1')
    print("\n\n 2 Yes")

    import os
    print(os.environ["BLINKA_FT232H"])
    # print(os.environ[1]) Wrong!
    # if you get a KeyError it means you did not set the environment variable right
    print("\n\n 3 Yes")

if False: # Digital Output test
    import time
    import board
    import digitalio

    led = digitalio.DigitalInOut(board.C7)
    led.direction = digitalio.Direction.OUTPUT

    time_interval = 0.001
    count = 100
    while True:
        count -= 1
        print(count)
        if count < 0: break
        led.value = True
        time.sleep(time_interval*count)
        led.value = False
        time.sleep(time_interval)

if False: # Manual PWM test
    def PWM(led,freq,duration,duty_ratio):
        import time
        # time = 0 
        cycle_num = duration * freq
        print(cycle_num)
        cycle_count = 0
        print( 1/freq *duty_ratio)
        while True:
            cycle_count += 1
            if cycle_count > cycle_num: break
            else: 
                led.value = True
                time.sleep( 1/freq *duty_ratio)
                led.value = False
                time.sleep( 1/freq *(1-duty_ratio))
        pass

    import time
    import board
    import digitalio

    led = digitalio.DigitalInOut(board.C7)
    led.direction = digitalio.Direction.OUTPUT

    PWM_freq = 100 # Hz
    count = 0
    full_time = 1
    duty_ratio = 0.5
    PWM(led,PWM_freq,full_time,duty_ratio)
    time.sleep(0.1)
    PWM(led,PWM_freq*10,full_time,duty_ratio)
       
        
if False: # PWM Output test 
    import time
    import board
    import digitalio
    # from adafruit_blinka.microcontroller.generic_linux.libgpiod_pin import Pin
    from adafruit_blinka.microcontroller.nxp_imx6ull import pin

    led = digitalio.DigitalInOut( pin.GPIO115 ) 
    # PWM_C7 = PWM1 = pin.GPIO115 / GPIO115 = PWM_C7 = Pin((3, 19))  # GPIO4_IO19


    led.direction = digitalio.Direction.OUTPUT
    led.value = 0.5

    # led.drive_mode 
    time_interval = 0.001
    count = 100
    
    while False:
        count -= 1
        print(count)
        if count < 0: break
        led.value = True
        time.sleep(time_interval*count)
        led.value = False
        time.sleep(time_interval)

if False: # button input test
    import board
    import digitalio

    led = digitalio.DigitalInOut(board.C0)
    led.direction = digitalio.Direction.OUTPUT

    button = digitalio.DigitalInOut(board.C1)
    button.direction = digitalio.Direction.INPUT

    while True:
        led.value = button.value



if False:  # PCA 9685 Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

if False: # I2C test
    print('\n\n')
    # Based on: https://eblot.github.io/pyftdi/api/index.html
    import pyftdi.i2c as i2c

    # Instantiate an I2C controller
    i2c = i2c.I2cController()

    # Configure the first interface (IF/1) of the FTDI device as an I2C master
    i2c.configure('ftdi:///1') # ftdi:///1 OR ftdi://ftdi:2232h/1

    # Get a port to an I2C slave device
    slave = i2c.get_port( 0x40 ) # 0x21 
    print("Slave board obj: ",slave)
    
    slave.write_to( __MODE1, b'\x01') # Software reset

    # Turn into sleep mode
    print('Slave board mode 1 register: ',slave.read(0x00,1))
    slave.write(__MODE1, b'\0x04')
    print('Slave board mode 1 register: ',slave.read(0x00,1))

    # Send one byte, then receive one byte
        # FTDI pins in MPSSE mode cannot be (re)configured: the signal direction is hardcoded,
        # connect AD1 as SDA output, and AD2 as SDA input.
    # print(slave.exchange( [0x04] , 1))

    
    # Set iup freq
    slave.write_to(regaddr =__PRESCALE, out=b'\0x03')# PRE_SCALE registor / PWM freq : FF 24Hz, 03: 1526Hz
    print("PRE_SCALE Value:",slave.read_from(regaddr=__PRESCALE,readlen= 1))
    time.sleep(1)

    # Write a register to the I2C slave
    
    slave.write_to( __ALLLED_ON_L, bytearray(b'\x0F')) # ALL_LED_ON_L
    print("ALL_LED_ON_L :",slave.read_from(__ALLLED_ON_L,1))
    # slave.write_to( 0xFB, b'\x08') # ALL_LED_ON_H
    slave.write_to( __ALLLED_OFF_L, b'\xFFF') # ALL_LED_OFF_L b'\xFF'
    print("ALL_LED_OFF_L :",slave.read_from(__ALLLED_OFF_L,1))

    # slave.write_to( regaddr=0xFD, out=b'\x09',relax= False,start=False) # ALL_LED_OFF_H

    # print(slave.read_from(0x40, 1))

    time.sleep(2)

    # Read a register from the I2C slave
    # print(slave.read_from(0x00, 1))

    Pass

