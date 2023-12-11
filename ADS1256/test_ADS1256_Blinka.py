# %%
print("Start")

FCLKIN = 7.68E6
TCLKIN = 1/7.68E6
CMD_RREG =  0x10 

import time
import board
import digitalio
import busio

FT232H_DIR = dir(board)
print(type(FT232H_DIR)) 
 
# OR create library object using our Bus SPI port
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
bme_cs = digitalio.DigitalInOut(board.C0)
 