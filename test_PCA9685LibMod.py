
from pickle import FALSE
from re import T
import time
# sys.path.append("..")
# from lib.pyftdi_mod import i2c as i2c
from pca9685.PCA9685 import Pca9685_01 as actuator_device

from pyftdimod import i2c as i2c


if __name__=='__main__':

  # Instantiate an I2C controller
  IIC_device = i2c.I2cController()

  i2c_actuator_controller_URL = 'ftdi://ftdi:232h:0:FF/0'
  # Configure the first interface (IF/1) of the FTDI device as an I2C master
  # IIC_device.configure('ftdi://ftdi:232h:0:FF/0',frequency=1E6) # ftdi:///1 OR ftdi://ftdi:2232h/1 ?? direction=0x78
  IIC_device.configure(i2c_actuator_controller_URL,frequency = 1E6,#3E6, 1E6
                            rdoptim=True,clockstretching=True) # On IIC   


  print('\n\n')
  pwm_addr = 0x40
  pca9685 = actuator_device(IIC_device,debug=False) # Link PCA9685
  # pca9685.reset()
  # exit()

  pca9685.setPWMFreq(1526)
  pca9685.setOCH()
  # pca9685.reset()
  # exit()


  # dr = 1
  # t0 = time.time()
  # for _i in range(100):
    
  #   pca9685.setDutyRatioCHS([0], duty_ratio=_i/100,relax=True) # 100 for 1.79 ->> 0.41794872283935547
  #   # pca9685.setDutyRatioCH(15, duty_ratio=_i/100,stop_sending=True) # 100 for 0.13S
  # print(time.time()-t0)
  # pca9685.setDutyRatioCHS([15,0], duty_ratio=0,relax=False) # 100 for 1.79
 
  channels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
  output_levels0 = [0,0,0,0, 0,1,0,0, 0,0,0,0, 0,0,0,0]
  output_levels1 = [1,0,0,0, 1,0,0,0, 0,0,0,0, 0,0,0,0]

  pulse_t = 0.1
  while True:
    time.sleep(pulse_t)

    for _ch,_DR, in zip( channels, output_levels0 ):
      # print(_ch,_DR)
      pca9685.setDutyRatioCH(channel=_ch,duty_ratio = _DR,relax=False)
      
    time.sleep(pulse_t)

    for _ch,_DR, in zip( channels, output_levels1 ):
      pca9685.setDutyRatioCH(channel=_ch,duty_ratio = _DR,relax=False)
  exit()


  t=0
  if False: # Example 4*C1LED
    pca9685.setPWMFreq(1000)

    # pwm_device.setChannelDutyRatio(0,1)

    while t < -10:
      t_start = time.time()
      t += 1
      pca9685.setChannelDutyRatio(0,0,stop_sending=True)
      t_end = time.time()

      pca9685.setChannelDutyRatio(0,1)

      print(t_end-t_start)
      # pwm_device.setChannelDutyRatio(0,0.1*t)
      # pwm_device.setChannelDutyRatio(0,0.1*t)
      # time.sleep(0.1)
    pass
    
    bust_interval = 0.12
    while False:
      if bust_interval - 0.02 < 0 : bust_interval = 0.12
      else: bust_interval -= 0.02
      try:
        pca9685.setChannelDutyRatio(0,0.05,stop_sending=False)  
        pca9685.setChannelDutyRatio(12,0,stop_sending=False) 
        pca9685.setChannelDutyRatio(13,0,stop_sending=False) 
        pca9685.setChannelDutyRatio(14,0,stop_sending=False) 
        pca9685.setChannelDutyRatio(15,0) 
        time.sleep(bust_interval)

        pca9685.setChannelDutyRatio(0,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(12,0.05)  
        time.sleep(bust_interval)
        
        pca9685.setChannelDutyRatio(12,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(13,1)  
        time.sleep(bust_interval)

        pca9685.setChannelDutyRatio(13,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(14,0.5)  
        time.sleep(bust_interval)

        pca9685.setChannelDutyRatio(14,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(15,0.5)  
        time.sleep(bust_interval)

      except Exception as err: 
        print('Err: ',err,"\n Try Restart in:",4*bust_interval)
        time.sleep(4*bust_interval)
        try: pca9685.reset()
        except Exception as err2: print('\tErr: ',err2,"\n when restarting in 1s:")
  
  while False: # Test reading sensor (Accelerometer meter)
    # TODO
    IIC_device.gpio.set_direction(0x10, 0)
    print(pca9685.i2c_controller.gpio_pins)
    print('read_gpio: \t',pca9685.i2c_controller.read_gpio())
 
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
  
  while True:
    pca9685.reset()
    pca9685.setPWMFreq(1000)
    
    channels = [12,13,14,0]
    dutys = [0] # [预热 响应 维持]
    intervals = [2]
    pca9685.test_wires(channels,dutys,intervals,conf0 = True)

    channels = [12,14,0]
    dutys = [1] # [预热 响应 维持]
    intervals = [20]
    pca9685.test_wires(channels,dutys,intervals,conf0 = True)
    
    exit()

  while True: # Instant up required least time
    print("Instant up sustain duty")
    pca9685.reset()
    pca9685.setPWMFreq(1000)
    channels = [12,14,0]

    tf = 0.28

    dutys = [1,0.2,0] # [预热 响应 维持]
    intervals = [tf,10,2.5]
    pca9685.test_wires(channels,dutys,intervals,conf0 = True)
    

  while False: # Instant up sustain duty
    print("Instant up sustain duty")
    pca9685.reset()
    pca9685.setPWMFreq(1000)
    channels = [14,0]
    dutys = [1,0.2,0] # [预热 响应 维持]
    intervals = [0.3,10,2.5]
    # device.testChannle(0)
    pca9685.test_wires(channels,dutys,intervals,conf0 = True)
 
  if False: # test Slow up min duty
    pca9685.setPWMFreq(1000)
    channels = [14, 0]
    dutys = [0.4,1,0.02] # [预热 响应 维持]
    intervals = [1,0.1,1]
    # device.testChannle(0)
    pca9685.test_wires(channels,dutys,intervals,conf0 = True)

  if False: # Find 1 second test
    pca9685.setPWMFreq(1000)
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
      pca9685.test_wires(channels,dutys,intervals,conf0 = True)
      
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
      pca9685.setPWMFreq(25)
      try:
        # pwm_device.setDutyRatioCH(15,0,stop_sending=False)

        # pwm_device.setDutyRatioCH(0,active_duty,stop_sending=False) 
        # pwm_device.setDutyRatioCH(14,active_duty)  
        # pwm_device.setDutyRatioCH(14,sustain_duty)  
        
        pca9685.setDutyRatioCH(14,0.2)  
        pca9685.setDutyRatioCH(14,0.054)
        pca9685.setDutyRatioCH(14,0.0)  
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
        try: pca9685 = PCA9685_lib(address=pwm_addr, debug=False,easy_mdoe=True); pca9685.reset()
        except Exception as err2: print('\tErr: ',err2,"\n when restarting in 1s:")
      
      # active_duty *= 1.1
      # sustain_duty *= 1.1

    pca9685.setDutyRatioCH(0,0,stop_sending=False)  
    pca9685.setDutyRatioCH(14,0,stop_sending=False)  
    pca9685.setDutyRatioCH(15,0)  

  if False: # Example 2*C2LED
    pca9685.setPWMFreq(1000)
    bust_interval = 0.12

    while True:
      if bust_interval - 0.02 < 0 : bust_interval = 0.12
      else: bust_interval -= 0.02
      try:
        pca9685.setChannelDutyRatio(0,0.5,stop_sending=False)  
        pca9685.setChannelDutyRatio(12,0,stop_sending=False) 
        pca9685.setChannelDutyRatio(13,0,stop_sending=False) 
        pca9685.setChannelDutyRatio(14,0,stop_sending=False) 
        pca9685.setChannelDutyRatio(15,0) 
        time.sleep(bust_interval)

        pca9685.setChannelDutyRatio(0,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(12,1)  
        time.sleep(bust_interval)
        
        pca9685.setChannelDutyRatio(12,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(13,1)  
        time.sleep(bust_interval)

        pca9685.setChannelDutyRatio(13,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(14,1)  
        time.sleep(bust_interval)

        pca9685.setChannelDutyRatio(14,0,stop_sending=False)  
        pca9685.setChannelDutyRatio(15,1)  
        time.sleep(bust_interval)

      except Exception as err: 
        print('Err: ',err,"\n Try Restart in:",4*bust_interval)
        time.sleep(4*bust_interval)
        try: pca9685.reset()
        except Exception as err2: print('\tErr: ',err2,"\n when restarting in 1s:")
      # pwm_device.setChannelDutyRatio(14,1,stop_sending=False)  
      
    if False:
      t_start = time.time()
      for dt in range(5):
        for ch in range(16):
            pca9685.setChannelDutyRatio(ch,dt/100,stop_sending=False)  
      t_end = time.time()
      pca9685.setChannelDutyRatio(0,0.30,stop_sending=True)  
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
      pca9685.setServoPulse(0,i)   
      time.sleep(0.02)     

    for i in range(2500,500,-10):
      pca9685.setServoPulse(0,i) 
      time.sleep(0.02)