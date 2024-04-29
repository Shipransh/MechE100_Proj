import time
import math
from ina219 import INA219
from time import sleep
from machine import Pin, Timer, I2C, SoftI2C
from binascii import hexlify

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
lukewarm = 65 #farhenheit temperature
thermo_t = 65 #thermostat temp dummy variable

def temp(timer): #get temperature from IMU and convert to F
    global lukewarm
    t = acc.get_temperature() # C
    lukewarm = int((t * (9/5)) + 32) # F
    return lukewarm
    #print(lukewarm)
    #print(int(f))

t = 65
def temp_thermo(x):
    global t
    t = 65 + (10*(x/10.8))
    return int(t)
    
#code to initialize INA219 for reading potentiometer
i2c = SoftI2C(scl=Pin(15), sda=Pin(33)) 
SHUNT_RESISTOR_OHMS = 0.1
ina = INA219(SHUNT_RESISTOR_OHMS, i2c)
ina.configure()


def thermostat(timer):
    V = ina.voltage()
    I = ina.current()
    global thermo_t
    global lukewarm
    try:
        R = V/I
    except ZeroDivisionError:
        R = 0
    if R > 800:
        R = 800
    elif R > 0:
        #print(R)
        #print(I)
        print(f'thermostat temperature is {temp_thermo(R)}')
        print(f'room temperature is {lukewarm}')
        #print(lukewarm)
        thermo_t = temp_thermo(R)
    if lukewarm > thermo_t:
        #fan(1)
        #x = 1
        print('fan on')
    elif lukewarm <= thermo_t:
        #fan(0)
        #y = 1
        print('fan off')

t_temp = Timer(2)
t_temp.init(period=1000, mode=t_temp.PERIODIC, callback=temp) #30 second timer to check the temperature and thermostat

t_thermo = Timer(3)
t_thermo.init(period=1000, mode=t_thermo.PERIODIC, callback=thermostat) #checks the thermostat state


t_temp.deinit
t_thermo.deinit


