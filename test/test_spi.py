# %%
import pyftdi.ftdi as ftdi

import pyftdi.i2c as i2c
import pyftdi.spi as spi
import os

i2c_device = i2c.I2cController()
# i2c_device.configure(url_1)

url_0 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FF/0') 
url_1 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FE/0')                
url_2 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FD/1')
url_3 = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h:0:FC/1')


spi_device = spi.SpiController(cs_count=1)
spi_device.configure(url_0)

# %%
# Get a port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 12MHz
spi_slave_device = spi_device.get_port(cs=0, freq=976563, mode=0) # D: 12E6

# # Request the JEDEC ID from the SPI slave
# jedec_id = spi_slave_device.exchange([0x9f], 3)
# print("jedec_id: ",jedec_id)

data_00 = spi_slave_device.exchange([0x00], 10)
print("data_00: ",data_00)

data_20 = spi_slave_device.exchange([0x20], 1)
print("data_20: ",data_20)
print("Finished!")

# %%
import Adafruit_FT232H as FT232H

# Temporarily disable FTDI serial drivers to use the FT232H device.
FT232H.use_FT232H()

# Create an FT232H device instance.
ft232h = FT232H.FT232H()