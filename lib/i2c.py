"""I2C H-s support for PyFdti.I2C"""
# from pca9685.PCA9685 import Pca9685_01 as PCA9685
import pyftdi.i2c as i2c

class I2cController(i2c.I2cController):
    def __init__(self):
        super(I2cController,self).__init__()

        pass

    def read_HS(self, address: int, readlen: int = 1,
             relax: bool = True) -> bytes:
        # with self._lock:
        #         while True:
        #             try:
        #                 self._do_prolog(i2caddress)
        #                 self._do_write(out)
        #                 self._do_prolog(i2caddress | self.BIT0)
        #                 if readlen:
        #                     data = self._do_read(readlen)
        #                 do_epilog = relax
        #                 return data
        #             except I2cNackError:
        #                 retries -= 1
        #                 if not retries:
        #                     raise
        #                 self.log.warning('Retry exchange')
        #             finally:
        #                 if do_epilog:
        #                     self._do_epilog()



        self.validate_address(address)
        if address is None:
            i2caddress = None
        else:
            i2caddress = (address << 1) & self.HIGH
            i2caddress |= self.BIT0

        with self._lock:
 

            # self._ftdi.write_data(cmd)
            # ack = self._ftdi.read_data_bytes(1, 4)
            self._do_prolog(i2caddress)
            self._do_write(0x00)
            self._do_prolog(i2caddress | self.BIT0)
            data = self._do_read(readlen)
            # do_epilog = relax
            return data

 

    def start_HS(self,usb_URL): # By Askar
        MS_code = 0b00001111
        self.MS_code = MS_code
 
        # 先在快速模式下发送主机地址，不需要从机回复。
        cmd = bytearray(self._idle * self._ck_delay)
        cmd.extend(self._start)
        # if True:
        #     print(self._start)
        #     print(self._nack)
        #     print(cmd)

        cmd.extend(bytearray(self.MS_code))
        cmd.extend(self._nack) # NACK
        # self._send_check_ack(cmd)



        # if self._fake_tristate:
        #     # SCL low, SDA high-Z (input)
        #     cmd.extend(self._clk_lo_data_input)
        #     # read SDA (ack from slave)
        #     cmd.extend(self._read_bit)
        #     # leave SCL low, restore SDA as output
        #     cmd.extend(self._clk_lo_data_hi)

        # else:
        #     # SCL low, SDA high-Z
        #     cmd.extend(self._clk_lo_data_hi)
        #     # read SDA (ack from slave)
        #     cmd.extend(self._read_bit)
        # cmd.extend(self._immediate)
        # self._ftdi.write_data(cmd)


        # 然后切换到高速模式，会发送一个 reSTART，
        # 是否在此切换高速模式？？？FREQ..Delay..
        self.force_clock_mode(enable=True)
        self.configure(usb_URL,frequency = 0.4E6,clockstretching=True)
        # self._ftdi.write_data(self._start)

        # 然后再发送自己想要操作，读或者写。
        print("\n---HS mode starts-----")
        # print("\nFREQ:",self._frequency)
