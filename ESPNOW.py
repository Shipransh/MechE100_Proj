import network
import espnow
from rcwl1601 import HCSR04
from machine import Pin,I2C

#sensor = HCSR04(trigger_pin=14, echo_pin=22,echo_timeout_us=1000000)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
#peer = b'\x44\x17\x93\x5C\x0B\x44'   # MAC address of peer's wifi interface
peer = b'\x4c\x75\x25\xf0\x06\xa0'
e.add_peer(peer)      # Must add_peer() before send()

e.send(peer, "Starting...")
e.send(peer, "1")
for i in range(100):
    e.send(peer, str(1).encode('UTF-8'), True)
    

    #Arguments for send are Mac address of receiver, message string, and whether or not to wait for a
    #confirmation from the receiver that the message has been received before moving on from this line (good for debugging). 
e.send(peer, b'end')




