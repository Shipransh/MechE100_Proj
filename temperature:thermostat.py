from ina219 import INA219
from machine import SoftI2C, Pin, Timer

import time
from time import sleep

i2c = SoftI2C(scl=Pin(15), sda=Pin(33)) # Need to change scl & sda GPIO Pin number (enter only the number inside the parenthesis)

SHUNT_RESISTOR_OHMS = 0.1
ina = INA219(SHUNT_RESISTOR_OHMS, i2c)
ina.configure()

t = 65
def temp(x):
    global t
    t = 65 + (10*(x/10.8))
    return int(t)

def thermostat(timer):
    V = ina.voltage()
    I = ina.current()
    global t
    try:
        R = V/I
    except ZeroDivisionError:
        R = 0
    if R > 800:
        R = 800
    elif R > 0:
        print(R)
        print(I)
        print(temp(R))
        t = temp(R)
    

t_thermo = Timer(1)
t_thermo.init(period=1800, mode=t_thermo.PERIODIC, callback=thermostat)

t_thermo.deinit