# %%
import pyftdi.ftdi as ftdi

import pyftdi.i2c as i2c
import pyftdi.spi as spi
import os,time

# i2c_device = i2c.I2cController()
# i2c_device.configure(url_1)
FCLKIN = 7.68E6
TCLKIN = 1/7.68E6

WAKEUP = 0x00
CMD_RDATA = 0x01
CMD_RREG = 0x10 
CMD_WREG = 0x50
CMD_RESET = 0xFE

url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/0') 
# url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/0')                
# url_2 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FD/1')
# url_3 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FC/1')



spi_device = spi.SpiController(cs_count=1)
spi_device.configure(url_0,frequency=7.8E6)

# %%
spi_ch_freq = FCLKIN/4
print("SPI Freq:",spi_ch_freq)
# Get a port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 12MHz
spi_slave_device = spi_device.get_port(cs=0,mode=1) # D: 12E6
spi_slave_device.set_frequency(spi_ch_freq)
# spi_slave_device.set_mode(1)
# Reset

spi_slave_device.exchange([CMD_RESET])
time.sleep(50*TCLKIN)

# Setting acquire  

addr = 0x00
nums_to_read = 16

# Send
to_exchange = [ CMD_RREG + addr ,nums_to_read-1]
spi_slave_device.exchange(to_exchange,stop=False)
time.sleep(50*TCLKIN)
data_addr = spi_slave_device.exchange([0x00],nums_to_read-1)


i = 0
for _byte in data_addr:
    print("Addr:",'%#x'%(0x00+i),'Value:','%#x'%_byte,bin(_byte))
    i += 1 

print("Finished!")

#%% READ DATA
for i in range(100):
    _res = []
    spi_slave_device.exchange([CMD_RDATA])
    # time.sleep(50*TCLKIN)
    raw_data = spi_slave_device.exchange([0x00],3)
    
    _res = (raw_data[0]<<16) + (raw_data[1]<<8) + raw_data[2]
    if not (_res&0x800000)==0: _res = -((_res^0xffffff) +1)

    print(i,': ',raw_data,_res)
    
 
# %%
st_time = time.time()
i = 0 
while True:
    spi_slave_device.exchange([CMD_RDATA])
    # time.sleep(50*TCLKIN)
    raw_data = spi_slave_device.exchange([0x00],3)
    
    _res = (raw_data[0]<<16) + (raw_data[1]<<8) + raw_data[2]
    if not (_res&0x800000)==0: _res = -((_res^0xffffff) +1)
    _res = _res/0xFFFFFF
    i += 1 

    # if time.time()-st_time > 1: break
    print('\r',_res,end='')
    time.sleep(0.2l.)
print(i)