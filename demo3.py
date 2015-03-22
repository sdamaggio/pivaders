#threaded GPIO interrupts demo

#!/usr/bin/env python
#import the GPIO library
import RPi.GPIO as GPIO

#import sleep function
from time import sleep

GPIO.setmode(GPIO.BCM)

#set the needed GPIO pins as input or output
GPIO.setup(23, GPIO.OUT) 
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

# now we'll define the threaded callback function  
# this will run in another thread when our event is detected  
def my_callback(channel):  
	print "Rising edge detected on port 24 - even though, in the main thread,"  
	print "we are still running the game - how cool?\n"  
	#toggle the pin
	GPIO.output(23,True)
	sleep(2)
	GPIO.output(23,False) 
	

GPIO.add_event_detect(24, GPIO.FALLING, callback=my_callback)  
# The GPIO.add_event_detect() sets things up so that  
# when a falling edge is detected on port 24, regardless of whatever   
# else is happening in the program, the function "my_callback" will be run  

while True:
	print "."
