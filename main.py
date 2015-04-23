#####################################################################
#					Raspberry Pi Polygraph controller				#
#																	#
#		All code and hardware by Nicholas Allen and Antony Dyer		#
#																	#
#####################################################################

'''
###############################################
CHANGELOG
###############################################
22/04/15, 18:39
*Cleaned up the pasted LED thermometer code - there'd been some weird corruption
leading to lines being repeated.
*Added the read_i2c() func. This takes a hex address as input and reads the data from I2C
using that address. It is currently used in all the check and calibrate functions, albeit
with arbitrary hex values.
Added some quick checking print statements to make sure the loop and key-based exits are working
'''

## Imports
import thread
import smbus
import time
import RPi.GPIO as GPIO
 
 
try:
    from msvcrt import getch  # try to import Windows version
except ImportError:
    def getch():   # define non-Windows version
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

## Set up GPIO

GPIO.setwarnings(False) 		#disable runtime warnings
GPIO.setmode(GPIO.BCM) 			#use Broadcom GPIO names

GPIO.setup(5, GPIO.OUT)			#set pins 5, 6, 12, 13, 16, 19, 20 and 26 as output
GPIO.setup(6, GPIO.OUT)			# these correspond to LEDs 0-7, respectively
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

## Set up I2C

bus = smbus.SMBus(1)
I2C_ADDR = 0x21

##function definitions

def read_i2c(hex_address):
	bus.write_byte( I2C_ADDR, 0x20 )	
	tmp = bus.read_word_data( I2C_ADDR, hex_address )
	tmpLOW = hex(tmp)[2]
	tmpHIGH = hex(tmp)[3]
	reorderedtmp = tmpHIGH + tmpLOW
	tmp = int(reorderedtmp, 16)
	tmp = tmp & 4095 
	return tmp

def calibration_mode():
	while True:
		key = check_key()
		if key == "i":
		    return
		calibrate_respiratory()
		calibrate_skin_conduct()
		time.sleep(0.5)

def interview_mode():
	while True:
		key = check_key()
		if key == "c":
		    return
		check_button_presses()
		temp = check_temp()
		temp_monitor_LED(temp)
		check_heart_rate()
		check_respiration()
		check_skin_conductance()
		time.sleep(1)

def calibrate_respiratory():
	print "resp calibration func working"
	read_i2c(0x01)

def calibrate_skin_conduct():
	print "skin calibration func working"
	read_i2c(0x02)

def check_key():  #theoretically complete
    char = getch()
    if char == 'c' or char == 'i':
        #print "Key pressed is " + char
        return char
    else:
        return None

def check_button_presses():
	#print "button check func working"
	#read_i2c(0x03)
	pass

def check_temp():
	#print "temp check func working"
	temp = read_i2c(0x20)
	#print temp
	return temp

def temp_monitor_LED(temperature): #almost complete, just need to add real values
	if temperature < 25:
		GPIO.output(5,True)	#led0
		GPIO.output(6, False)	#led1
		GPIO.output(12, False)	#led2
		GPIO.output(13, False)	#led3
		GPIO.output(16, False)	#led4
		GPIO.output(19, False)	#led5
		GPIO.output(20, False) 	#led6
		GPIO.output(26, False)	#led7

	elif temperature >25 and temperature < 50:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, False)
		GPIO.output(13, False)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >50 and temperature < 75:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, False)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >75 and temperature < 100:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >100 and temperature < 125:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)
	
	elif temperature >125 and temperature < 150:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, True)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >150 and temperature < 175:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, True)
		GPIO.output(20, True)
		GPIO.output(26, False)

	elif temperature >175:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, True)
		GPIO.output(20, True)
		GPIO.output(26, True)

	else:
		GPIO.output(5, False)
		GPIO.output(6, False)
		GPIO.output(12, False)
		GPIO.output(13, False)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)
	
	return

def check_heart_rate():
	print "heart check func working"
	#read_i2c(0x00)

def check_respiration():
	resp = read_i2c(0x10)
	print resp

def check_skin_conductance():
	print "skin check func working"
	#read_i2c(0x02)

## Main Loop

while True:
	#calibration_mode()
	interview_mode()
