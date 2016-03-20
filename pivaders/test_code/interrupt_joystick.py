#!/usr/bin/env python2.7

# http://raspi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Joystick:
# UP            gpio22  pin 15
# DOWN          gpio17  pin 11
# RIGHT         gpio27  pin 13
# LEFT          gpio18  pin 12
# BUTTON1       gpio23  pin 16
# GND           pin 11, 14

GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# now we'll define the threaded callback function
# this will run in another thread when our event is detected
def callbackUP(channel):
    print "UP\n"

def callbackDOWN(channel):
    print "DOWN\n"	
	
def callbackRIGHT(channel):
    print "RIGHT\n"

def callbackLEFT(channel):
    print "LEFT\n"

#def callbackBUTTON1(channel):
    #print "RIGHT\n"

raw_input("Press Enter when ready\n>")

# The GPIO.add_event_detect() line below set things up so that
# when a rising edge is detected on the pin, regardless of whatever
# else is happening in the program, the function "callbackXXXX" will be run
# It will happen even while the program is waiting for
# a falling edge on the other button.
GPIO.add_event_detect(22, GPIO.FALLING, callback=callbackUP, bouncetime=300)
GPIO.add_event_detect(17, GPIO.FALLING, callback=callbackDOWN, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=callbackRIGHT, bouncetime=300)
GPIO.add_event_detect(18, GPIO.FALLING, callback=callbackLEFT, bouncetime=300)
#GPIO.add_event_detect(23, GPIO.FALLING, callback=callbackBUTTON1, bouncetime=400)

try:
    print "Waiting for falling edge on port 23"
    GPIO.wait_for_edge(23, GPIO.FALLING)
    print "Falling edge detected. Here endeth the second lesson."

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit

