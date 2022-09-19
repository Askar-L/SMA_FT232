from ast import Try
from email.headerregistry import Address
import errno
from multiprocessing.dummy import active_children
from re import T
import time
from turtle import end_fill

# sys.path.append("..")
# from lib.pyftdi_mod import i2c as i2c

import lib.PCA9685Mod as PCA9685


if __name__=='__main__':
  print('\n\n')
  pwm_addr = 0x40
  device = PCA9685(address=pwm_addr, debug=False,easy_mdoe=True)
  device.reset()

  t=0
  if False: # Example 4*C1LED
    device.setPWMFreq(1000)

    # pwm_device.setChannelDutyRatio(0,1)

    while t < -10:
      t_start = time.time()
      t += 1
      device.setChannelDutyRatio(0,0,stop_sending=True)
      t_end = time.time()

      device.setChannelDutyRatio(0,1)

      print(t_end-t_start)
      # pwm_device.setChannelDutyRatio(0,0.1*t)
      # pwm_device.setChannelDutyRatio(0,0.1*t)
      # time.sleep(0.1)
    pass
    
    bust_interval = 0.12
    while True:
      if bust_interval - 0.02 < 0 : bust_interval = 0.12
      else: bust_interval -= 0.02
      try:
        device.setChannelDutyRatio(0,0.05,stop_sending=False)  
        device.setChannelDutyRatio(12,0,stop_sending=False) 
        device.setChannelDutyRatio(13,0,stop_sending=False) 
        device.setChannelDutyRatio(14,0,stop_sending=False) 
        device.setChannelDutyRatio(15,0) 
        time.sleep(bust_interval)

        device.setChannelDutyRatio(0,0,stop_sending=False)  
        device.setChannelDutyRatio(12,0.05)  
        time.sleep(bust_interval)
        
        device.setChannelDutyRatio(12,0,stop_sending=False)  
        device.setChannelDutyRatio(13,1)  
        time.sleep(bust_interval)

        device.setChannelDutyRatio(13,0,stop_sending=False)  
        device.setChannelDutyRatio(14,0.5)  
        time.sleep(bust_interval)

        device.setChannelDutyRatio(14,0,stop_sending=False)  
        device.setChannelDutyRatio(15,0.5)  
        time.sleep(bust_interval)

      except Exception as err: 
        print('Err: ',err,"\n Try Restart in:",4*bust_interval)
        time.sleep(4*bust_interval)
        try: device.reset()
        except Exception as err2: print('\tErr: ',err2,"\n when restarting in 1s:")
  
  while False: # Test reading sensor (Accelerometer meter)
    # TODO
    device.gpio.set_direction(0x10, 0)
    # device.gpio.set_direction(0x08 , 0)
    print(device.i2c_controller.gpio_pins)
    print('read_gpio: \t',device.i2c_controller.read_gpio())
    # print('read: \t','%08x'%device.gpio.read(),device.gpio.read() )
    # print('direction: \t','%02x'%(device.gpio.direction),device.gpio.direction)
    # print("pins: \t",'%08x'%(device.gpio.pins),device.gpio.pins)
    time.sleep(0.2)

    if False: # button input test
      import board
      import digitalio

      led = digitalio.DigitalInOut(board.C0)
      led.direction = digitalio.Direction.OUTPUT

      button = digitalio.DigitalInOut(board.C1)
      button.direction = digitalio.Direction.INPUT

      while True:
          led.value = button.value

  if True: # test one wire
    channels = [14, 0]
    dutys = [0.4,1,0.02] # [预热 响应 维持]
    intervals = [1,0.1,1]
    # device.testChannle(0)
    device.test_wires(channels,dutys,intervals,conf0 = True)




  if False: # Find 1 second test
    device.setPWMFreq(1000)
    channels = [14, 0]
    dutys = [0.4,1,0.25] # [预热 响应 维持]
    intervals = [1,0.1,1] 
    
    _d = 0.1

    while _d < 0.5 :
      _d += 0.05
      print("Duty: ", _d)
      # dutys = [0.4,_d,0.13,0] # [预热 响应 维持]
      # intervals = [0.14,0.5,1.5,2] 
      # print(channels[0:-2])
      device.test_wires(channels,dutys,intervals,conf0 = True)
      
    pass
    exit()

  if False: # Find minimum duty ratio & time
    print("Working")
    round_count = 0 

    bust_interval = 0.  
    sustain_interval = 0.000000000000000
    stop_interval = 0.0000000
    
    active_duty = 0.1
    sustain_duty = 0.0

    while round_count < 1000000000 : 
      round_count += 0
      device.setPWMFreq(25)
      try:
        # pwm_device.setDutyRatioCH(15,0,stop_sending=False)

        # pwm_device.setDutyRatioCH(0,active_duty,stop_sending=False) 
        # pwm_device.setDutyRatioCH(14,active_duty)  
        # pwm_device.setDutyRatioCH(14,sustain_duty)  
        
        device.setDutyRatioCH(14,0.2)  
        device.setDutyRatioCH(14,0.054)
        device.setDutyRatioCH(14,0.0)  
        # pwm_device.setDutyRatioCH(14,sustain_duty)    
        
        # time.sleep(bust_interval)

        # pwm_device.setDutyRatioCH(0,sustain_duty,stop_sending=False)
        # pwm_device.setDutyRatioCH(14,sustain_duty) 
        # time.sleep(sustain_interval)
        
        # pwm_device.setDutyRatioCH(0,active_duty,stop_sending=False)
        # pwm_device.setDutyRatioCH(14,0) 
        # time.sleep(stop_interval/2)



      except Exception as err: 
        print('Err: ',err,"\n Try Restart in:",0.4); time.sleep(0.4)
        try: device = PCA9685(address=pwm_addr, debug=False,easy_mdoe=True); device.reset()
        except Exception as err2: print('\tErr: ',err2,"\n when restarting in 1s:")
      
      # active_duty *= 1.1
      # sustain_duty *= 1.1

    device.setDutyRatioCH(0,0,stop_sending=False)  
    device.setDutyRatioCH(14,0,stop_sending=False)  
    device.setDutyRatioCH(15,0)  

  if False: # Example 2*C2LED
    device.setPWMFreq(1000)
    bust_interval = 0.12

    while True:
      if bust_interval - 0.02 < 0 : bust_interval = 0.12
      else: bust_interval -= 0.02
      try:
        device.setChannelDutyRatio(0,0.5,stop_sending=False)  
        device.setChannelDutyRatio(12,0,stop_sending=False) 
        device.setChannelDutyRatio(13,0,stop_sending=False) 
        device.setChannelDutyRatio(14,0,stop_sending=False) 
        device.setChannelDutyRatio(15,0) 
        time.sleep(bust_interval)

        device.setChannelDutyRatio(0,0,stop_sending=False)  
        device.setChannelDutyRatio(12,1)  
        time.sleep(bust_interval)
        
        device.setChannelDutyRatio(12,0,stop_sending=False)  
        device.setChannelDutyRatio(13,1)  
        time.sleep(bust_interval)

        device.setChannelDutyRatio(13,0,stop_sending=False)  
        device.setChannelDutyRatio(14,1)  
        time.sleep(bust_interval)

        device.setChannelDutyRatio(14,0,stop_sending=False)  
        device.setChannelDutyRatio(15,1)  
        time.sleep(bust_interval)

      except Exception as err: 
        print('Err: ',err,"\n Try Restart in:",4*bust_interval)
        time.sleep(4*bust_interval)
        try: device.reset()
        except Exception as err2: print('\tErr: ',err2,"\n when restarting in 1s:")
      # pwm_device.setChannelDutyRatio(14,1,stop_sending=False)  
      
    if False:
      t_start = time.time()
      for dt in range(5):
        for ch in range(16):
            device.setChannelDutyRatio(ch,dt/100,stop_sending=False)  
      t_end = time.time()
      device.setChannelDutyRatio(0,0.30,stop_sending=True)  
      print('Final',t_end-t_start)
  
  while False:
    # pwm_device.setChannelDutyRatio(0,0)
    # pwm_device.setChannelDutyRatio(15,0.2)
    # print("PWMFreq: ",int(pwm_device.getPWMFreq()),"Hz")
  
    # # pwm_device.quickShutdown()
    
    # pwm_device.setPWMFreq(60)
    # time.sleep(0.2)
    # print("PWMFreq: ",int(pwm_device.getPWMFreq()),"Hz")

    # pwm_device.restart()
    pass

  while False:
   # setServoPulse(2,2500)
    for i in range(500,2500,10):  
      device.setServoPulse(0,i)   
      time.sleep(0.02)     

    for i in range(2500,500,-10):
      device.setServoPulse(0,i) 
      time.sleep(0.02)