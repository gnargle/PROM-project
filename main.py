###########################################################################################
#				Raspberry Pi Polygraph controller			  #
#											  #							#
#			All code and hardware by Nicholas Allen and Antony Dyer		  #
#											  #							#
###########################################################################################

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
*Added some quick checking print statements to make sure the loop and key-based exits are working
27/04/15, 14:30
*Merged Antony's filter changes for temperature and respiratory rate.
28/04/15
*Small update to change the hex values for the inputs we haven't worked on yet to be their correct values
'''

## Imports
import thread
import smbus
import time
import RPi.GPIO as GPIO
import datetime
 
 
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

## The below pins are for the push buttons. 7 corresponds to CE1, 8 is CE0.
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

## Set up I2C

bus = smbus.SMBus(1)
I2C_ADDR = 0x21

## global vars

global resp_counter
counter = 0
global heart_counter
heart_counter = 0
global output
output = []

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

def timer(n):## i havent decided if i should just make a timer function yet, will see if it is needed.
	
	
	while n > 0:
		n -= 1
		sleep.time(0.994)
	return 

def signal_filter(input_array):
		
	sort = input_array
	sort.sort()
	length = len(input_array)
		
	if length == 0:
		return None
	elif (length % 2)  == 0:
		return ((sort[length/2] + sort[(length/2) -1]) / 2.0)
	else:
		return sort[length/2]

def calibration_mode():
	while True:
		resp = calibrate_respiratory()
		resp = True
		skin = calibrate_skin_conduct('f')
		time.sleep(1)
		if resp == True and skin == True:
			break
	print "Both settings have been successfully calibrated"
	print "Please press i to enter interview mode"
	while True:
		key = check_key()
		if key == "i":
	    		return

def interview_mode(): ## this should be pretty much finished. Added ways to calculate HR and RR. 
					  # All funcs that should now return a value do, also
	start = time.time()
	while True:
		key = check_key()
		if key == "c":
		    return
		temp = check_temp(key)
		output.append(temp)
		temp_monitor_LED(temp)
		check_heart_rate()
		end_heart = time.time()
		elapsed = start-end_heart
		heart_rate = heart_counter/elapsed
		check_respiration()
		end_resp = time.time()
		elapsed = start-end_resp
		resp_rate = resp_counter/elapsed
		output.append(resp_rate)
		#output.append(check_skin_conductance())
		output.append(check_button_presses())
		f = open('results.csv', 'w')
		for val in output:
			f.write(str(val) + ',')
		f.write('\n')
		f.close()
		time.sleep(1)

def calibrate_respiratory():
	returned_value = read_i2c(0x10)
	if returned_value > 60 and returned_value < 80:
			print "The respiratory voltage has been calibrated"
			time.sleep(1)
			return True
		elif returned_value < 60:
			print "Increase the variable resistor"
			time.sleep(1)
		else:
			print "Decrease the variable resistor"
			time.sleep(1)

def RRfilter():
	global resp_counter
	percentage = 90
	## change to lst[1],lst[0]
	lst = []
	while len(lst) < 2:
		temp = read_i2c(0x10)
		lst.append(temp)
	percentage_change = float(lst[1] - lst[0]) / abs(lst[0]) * 100
	
	if abs(percentage_change) > percentage:
		return None
	else:
		resp_counter += 1
		return resp_counter

def calibrate_skin_conduct(filter_char):
	unsorted = read_i2c(0x40)
	temp = []
	if filter_char == 'u':
		print unsorted
		return unsorted
	else:
		while len(temp) <11:
			temp.append(read_i2c(0x40))
		returned_value = signal_filter(temp)
		print "skin calibrate", returned_value
		if returned_value > 60 and returned_value < 80:
			print "The skin voltage has been calibrated"
			time.sleep(1)
			return True
		elif returned_value < 60:
			print "Increase the variable resistor"
			time.sleep(1)
		else:
			print "Decrease the variable resistor"
			time.sleep(1)

def check_key():  #theoretically complete
    char = getch()
    if char == 'c' or char == 'i' or char == 'u' or char == 'f':
        #print "Key pressed is " + char
        return char
    else:
        return None

def check_button_presses():
	global output
	if (GPIO.input(17)==0):
		return("question asked at ", datetime.datetime.now().time())
	if (GPIO.input(4)==0):
		return("question answered at ", datetime.datetime.now().time())
	return

def check_temp(filter_char):
	unsorted = read_i2c(0x20)
	temp = []
	if filter_char == 'u':
		print unsorted
		return unsorted
	else:
		while len(temp) <11:
			temp.append(read_i2c(0x20))
		returned_value = signal_filter(temp)
		print returned_value
		return returned_value


def temp_monitor_LED(temperature):
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

def check_heart_rate(): # we need something similar to the RR filter here I think
	return HRFilter()

def HRFilter():
	global heart_counter
	percentage = 90 #need to adjust this value for hr
	## change to lst[1],lst[0]
	lst = []
	while len(lst) < 2:
		temp = read_i2c(0x80)
		lst.append(temp)
	percentage_change = float(lst[1] - lst[0]) / abs(lst[0]) * 100
	
	if abs(percentage_change) > percentage:
		return None
	else:
		heart_counter += 1
		return heart_counter

def check_respiration():
	print "respiratory output", RRfilter()

def check_skin_conductance():
	print "skin check func working"
	print read_i2c(0x40)

## Main Loop

while True:
	#calibration_mode()
	interview_mode()
