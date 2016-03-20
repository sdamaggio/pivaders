#!/usr/bin/env python2.7

import time

# http://raspi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

credits = 0

pinCoinCounter = 31

### coin counter signal interrupt sensing
def coin_counted_event(channel):
    global credits
    credits += 1 
    print "credits++"

GPIO.setup(pinCoinCounter, GPIO.IN)  
GPIO.add_event_detect(pinCoinCounter, GPIO.FALLING, callback=coin_counted_event, bouncetime=300)

raw_input("Press Enter when ready\n>")

for i in range(0, 60):
	time.sleep(3.0)


#try:
#    print "Waiting for falling edge on port 23"
#    GPIO.wait_for_edge(6, GPIO.FALLING)
#    print "Falling edge detected. Here endeth the second lesson."

#except KeyboardInterrupt:
#    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit

