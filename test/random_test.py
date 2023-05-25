# For ramdon testing unkown parts
# a = range(2)

# for i in a:print(i)

# b0 = b'\xa0'
# b1 = b'\xa1'
# b2 = b'\xa2'
# b3 = b'\xa3'

# ba = bytearray([b0,b1,b2,b3])
num_ch = 2

ba = b'\xce\x8f\xfc\xff'
_reading = ba
print(ba,type(ba))
print(ba[0:2])

print("\n\n")
_res = []
for _i in range(num_ch):
    int_reading = int.from_bytes(_reading[_i*2:_i*2+2], byteorder='big', signed=True) 
    
    print(_reading[_i*2:_i*2+2])
    print(int_reading)

    _res.append( int_reading )