import network
import espnow
import time
import math
from rcwl1601 import HCSR04
from machine import Pin,I2C,deepsleep, Timer, SoftI2C
from time import sleep
from ina219 import INA219
from binascii import hexlify


lukewarm = 65 #farhenheit temperature
thermo_t = 65 #thermostat temp dummy variable
t = 65

led1 = Pin(27, mode=Pin.OUT)
led2 = Pin(12, mode=Pin.OUT)

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
    
#code to initialize INA219 for reading potentiometer
i2c = SoftI2C(scl=Pin(15), sda=Pin(33)) 
SHUNT_RESISTOR_OHMS = 0.1
ina = INA219(SHUNT_RESISTOR_OHMS, i2c)
ina.configure()

acc = Accelerometer()

def temp(timer): #get temperature from IMU and convert from C to F
    global lukewarm
    x = acc.get_temperature() # C
    lukewarm = int((x * (9/5)) + 32) # F
    return lukewarm
    #print(lukewarm)
    #print(int(f))

def temp_thermo(x): #converts the potentiometer state to temperature
    global t
    t = 65 + (10*(x/10.8))
    return int(t)

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
        x = 0
        #print(R)
        #print(I)
        #print(f'thermostat temperature is {temp_thermo(R)}')
        #print(f'room temperature is {lukewarm}')
        #print(lukewarm)
        thermo_t = temp_thermo(R)
    if lukewarm > thermo_t: #fan turns on
        #if fan == 0:
        #    signal(1)
        #elif fan == 1: #do nothing, fan is on
        #    x =0
        #fan(1)
        x = 1
        #print('fan on')
    elif lukewarm <= thermo_t: # fan turns off
        #if fan == 1:
        #    signal(0)
        #elif fan == 0: #do nothing, fan is on
        #    x =0
        x = 0
        #fan(0)
        #y = 1
        #print('fan off')

first = 0        #variable to see which 
complete = 0     #
count = 0        #number of people in room
sense_a = 0      #
sense_b = 0      #
state = 0        #
detected = 0     #



def counter(timer): #counter for people 
    global count
    if count == 0:
        led1(0)
        led2(0)
    elif count == 1:
        led1(1)
        led2(0)
    elif count == 2:
        led1(1)
        led2(1)

def state_a(timer):
    global first
    global complete
    global sense_a
    global state
    global detected
    print('a')
    sense_a = 1
    detected = 1
    if first == 0: #sensor a triggered first // possible entrance
        first = 1
        state = 1
        #print('a first')
    elif first == 1:
        first = 0
        
def state_b(timer):
    global first
    global complete
    global sense_b
    global state
    global detected
    detected = 1
    print('b')
    sense_b = 1
    if first == 0: #sensor a triggered first // possible entrance
        first = 2
        state = 2
        #print('b first')
    elif first == 2:
        first = 0
        
def enter(timer):
    global first
    global sense_a
    global sense_b
    global count
    global t1
    global state
    global detected
    if detected == 1:
        if state == 1: #a first
            #print(state)
            #sleep(1)
            print('a first')
            if sense_b == 1:
                count += 1
                print(f'count is {count}')
                print('someone entered')
                
                #reset variables
                first = 0
                sense_a = 0
                sense_b = 0
            elif sense_b == 0: #only one triggered -> false signal
                first = 0
                sense_a = 0
                print('reset after a')
            detected = 0
            state = 0
        elif state == 2: #b first
            #print(state)
            #sleep(1)
            print('b first')
            if sense_a == 1:
                if count > 0:
                    count -= 1
                #print(count)
                print('someone left')
                print(f'count is {count}')
                
                #reset variables 
                first = 0
                sense_a = 0
                sense_b = 0
            
            elif sense_a == 0: #false signal
                first = 0
                sense_b = 0
                print('reset after b')
            #reset the variables 
            detected = 0
            state = 0
        
infared_a = Pin(36, mode = Pin.IN)
infared_a.irq( handler=state_a, trigger=Pin.IRQ_RISING) #calls state of infrared a function

infared_b = Pin(4, mode = Pin.IN)
infared_b.irq( handler=state_b, trigger=Pin.IRQ_RISING) #calls state of infrared b function

t_inf = Timer(1)
t_inf.init(period=5000, mode=t_inf.PERIODIC, callback=enter) #will check the states of the sensors every 4 seconds
        
t_temp = Timer(2)
t_temp.init(period=10500, mode=t_temp.PERIODIC, callback=temp) #30 second timer to check the temperature and thermostat

t_thermo = Timer(3)
t_thermo.init(period=10000, mode=t_thermo.PERIODIC, callback=thermostat) #checks the thermostat state

t_count = Timer(4)
t_count.init(period=1000, mode=t_count.PERIODIC, callback=counter) #continually calls counter to check the people

t_temp.deinit
t_thermo.deinit
t_inf.deinit
t_count.deinit