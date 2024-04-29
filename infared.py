import network
import espnow
import time
import math
from rcwl1601 import HCSR04
from machine import Pin,I2C,deepsleep, Timer, SoftI2C
from time import sleep
from ina219 import INA219
from binascii import hexlify


first = 0
complete = 0
count = 0
sense_a = 0
sense_b = 0
state = 0
detected = 0

led1 = Pin(13, mode=Pin.OUT)
led2 = Pin(12, mode=Pin.OUT)

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
        print('a first')
    elif first == 1:
        print('reset')
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
        print('b first')
    elif first == 2:
        print('reset')
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
        if state == 1:
            #print(state)
            if sense_b == 1:
                count += 1
                print(f'count is {count}')
                print('someone entered')
                first = 0
                sense_a = 0
                sense_b = 0
            elif sense_b == 0:
                first = 0
                sense_a = 0
                #print('reset')
            detected = 0
            state = 0
        elif state == 2:
            #print(state)
            if sense_a == 1:
                
                if count > 0:
                    count -= 1
                #print(count)
                print('someone left')
                print(f'count is {count}')
                first = 0
                sense_a = 0
                sense_b = 0
            
            elif sense_a == 0:
                first = 0
                sense_b = 0
                print('reset')
            detected = 0
            state = 0
    
#triggered on 
def leave(timer):
    global first
    global sense_a
    global sense_b
    global t1
    global count
    
    if detected == 1:
        if sense_a == 1:
            if count > 0:
                count -= 1
            #print(count)
            first = 0
            sense_a = 0
            sense_b = 0
            
        elif sense_a == 0:
            first = 0
            sense_b = 0
            print('reset')
        detected = 0
        
def lights(timer): #triggered on infrared sensor trigger, waits five seconds then triggers lights if people in room 
    sleep(5)
    #if count > 0:
    #    light(1)
    #elif count = 0:
    #    light(0)








infared_a = Pin(36, mode = Pin.IN)
infared_a.irq( handler=state_a, trigger=Pin.IRQ_RISING) #calls state of infrared function

infared_b = Pin(4, mode = Pin.IN)
infared_b.irq( handler=state_b, trigger=Pin.IRQ_RISING)

t_inf = Timer(1)
t_inf.init(period=4000, mode=t_inf.PERIODIC, callback=enter) #will check the states of the sensors every 4 seconds


t_count = Timer(4)
t_count.init(period=100, mode=t_count.PERIODIC, callback=counter)


t_inf.deinit
t_count.deinit



