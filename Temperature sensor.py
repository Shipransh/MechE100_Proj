from machine import Pin, Timer
from machine import I2C
from binascii import hexlify
import time
import math


class Accelerometer:

    def __init__(self):
        self.i2c = I2C(1,scl=Pin(14),sda=Pin(22),freq=400000)
        for i in range(len(self.i2c.scan())):
            print(hex(self.i2c.scan()[i]))
        self.i = i
        buff=[0xA0]
        self.i2c.writeto_mem(self.i2c.scan()[i],0x10,bytes(buff))
        self.i2c.writeto_mem(self.i2c.scan()[i],0x11,bytes(buff))
        time.sleep(0.1)
        
    def Temperature(self,i2caddr):
        temperature = self.i2c.readfrom_mem(i2caddr,0x20,2)
        if int.from_bytes(temperature,"little") > 32767:
            temperature = int.from_bytes(temperature,"little")-65536
        else:
            temperature = int.from_bytes(temperature,"little")
        return ((temperature)/(256) + 25)

    def get_temperature(self):
        return self.Temperature(self.i2c.scan()[self.i])
    

acc = Accelerometer()
f = 65


def temp(timer):
    global f
    t = acc.get_temperature() # C
    f = (t * (9/5)) + 32 # F
    print(int(f))
    
t1 = Timer(1)
t1.init(period=1000, mode=t1.PERIODIC, callback=temp)

