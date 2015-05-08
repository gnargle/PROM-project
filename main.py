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
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import csv
 
 
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
resp_counter = 0
global heart_counter
heart_counter = 0
global output
output = []

hr_array = []
reading = 0
'''
## Class definition for GUI
class Application(Frame):
    def say_hi(self):
        print "hi there, everyone!"
    def createWidgets(self):
        self.interview = Button(self)
        self.interview["text"] = "Interview Mode"
        self.interview["fg"]   = "red"
        self.interview["command"] = interview_mode()
        self.interview.pack({"side": "right"})
        self.calibrate = Button(self)
        self.calibrate["text"] = "Calibration mode"
        self.calibrate["command"] = calibration_mode()
        self.calibrate.pack({"side": "right"})
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
'''
##function definitions

def read_i2c(hex_address):
	bus.write_byte( I2C_ADDR, 0x20 )	
	tmp = bus.read_word_data( I2C_ADDR, hex_address )
	if len(hex(tmp)) == 6:
		try:
			tmpMID1 = hex(tmp)[2]
			tmpLOW = hex(tmp)[3]
			tmpcrap = hex(tmp)[4]
			tmpHIGH = hex(tmp)[5]
		except IndexError: 
			print hex(tmp)
			return read_i2c(hex_address)
		reorderedtmp = "0x" +tmpcrap +tmpHIGH +tmpMID1 +tmpLOW
		tmp = int(reorderedtmp, 16)
		tmp = tmp & 4095 
		return tmp
	elif len(hex(tmp)) == 5:
		try:
			tmpHIGH = hex(tmp)[4]
			tmpLOW = hex(tmp)[2]
			tmpcrap = hex(tmp)[3]
		except IndexError: 
			print hex(tmp)
			return read_i2c(hex_address)
		reorderedtmp = "0x" +tmpcrap +tmpHIGH +'0' +tmpLOW
		tmp = int(reorderedtmp, 16)
		tmp = tmp & 4095 
	
	return tmp
	elif len(hex(tmp)) == 4:
		try:
			tmpHIGH = hex(tmp)[3]
			tmpcrap = hex(tmp)[2]
		except IndexError: 
			print hex(tmp)
			return read_i2c(hex_address)
		reorderedtmp = "0x" +tmpcrap +tmpHIGH +'0' +'0'
		tmp = int(reorderedtmp, 16)
		tmp = tmp & 4095 
		return tmp
	elif len(hex(tmp)) == 3:
		try:
			tmpHIGH = hex(tmp)[2]
		except IndexError: 
			print hex(tmp)
			return read_i2c(hex_address)
		reorderedtmp = "0x" +'0' +tmpHIGH +'0' +'0'
		tmp = int(reorderedtmp, 16)
		tmp = tmp & 4095 
		return tmp


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

def cubic_spline_hr(xtime, yresults):
	x = np.arange(xtime)
	y = np.arange(yresults)
	tck = interpolate.splrep(x, y, s=0)
	xnew = np.arange(xtime)
	ynew = interpolate.splev(xnew, tck, der=0)

	plt.figure()
	plt.plot(x,y,'x',xnew,ynew,xnew,np.sin(xnew),x,y,'b')
	plt.legend(['Linear', 'Cubic Spline', 'True'])
	plt.axis([-0.05, 6.33, -1.05, 1.05])
	plt.title('Heart Rate Cubic Spline interpolation')
	plt.show()

def calibration_mode():  ##Should be finished!
	while True:
		resp = calibrate_respiratory()
		skin = calibrate_skin_conduct('f')
		temp = check_temp_hr_calib('f')
		temp_monitor_LED(temp)
		time.sleep(1)
		if resp == True and skin == True:
			break
	print "Both settings have been successfully calibrated"
	print "Please press i to enter interview mode"
	while True:
		key = check_key()
		if key == "i":
	    		return

def calibrate_respiratory():
	returned_value = read_i2c(0x10)
	print "resp calibrate", returned_value
	if returned_value > 1196 and returned_value < 1304:
		print "The respiratory voltage has been calibrated"
		time.sleep(1)
		return True
	elif returned_value < 1196:
		print "Increase the variable resistor"
		time.sleep(1)
	else:
		print "Decrease the variable resistor"
		time.sleep(1)

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
		if returned_value > 1700 and returned_value < 2300:
			print "The skin voltage has been calibrated"
			time.sleep(1)
			return True
		elif returned_value < 1700:
			print "Increase the variable resistor"
			time.sleep(1)
		else:
			print "Decrease the variable resistor"
			time.sleep(1)

def check_temp_hr_calib(filter_char):
	unsorted = read_i2c(0x80)
	temp = []
	if filter_char == 'u':
		print unsorted
		return unsorted
	else:
		while len(temp) <11:
			temp.append(read_i2c(0x20))
		returned_value = signal_filter(temp)
		return returned_value

def temp_monitor_LED(temperature):
	if temperature < 500:
		GPIO.output(5,True)	#led0
		GPIO.output(6, False)	#led1
		GPIO.output(12, False)	#led2
		GPIO.output(13, False)	#led3
		GPIO.output(16, False)	#led4
		GPIO.output(19, False)	#led5
		GPIO.output(20, False) 	#led6
		GPIO.output(26, False)	#led7

	elif temperature >500 and temperature < 1000:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, False)
		GPIO.output(13, False)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >1000 and temperature < 1500:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, False)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >1500 and temperature < 2000:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, False)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >2000 and temperature < 2500:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, False)
		GPIO.output(20, False)
		GPIO.output(26, False)
	
	elif temperature >2500 and temperature < 3000:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, True)
		GPIO.output(20, False)
		GPIO.output(26, False)

	elif temperature >3000 and temperature < 3500:
		GPIO.output(5, True)
		GPIO.output(6, True)
		GPIO.output(12, True)
		GPIO.output(13, True)
		GPIO.output(16, True)
		GPIO.output(19, True)
		GPIO.output(20, True)
		GPIO.output(26, False)

	elif temperature >3500:
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

def interview_mode(): ## this should be pretty much finished. Added ways to calculate HR and RR. 
					  # All funcs that should now return a value do, also
	global output
	reading = 0
	start = time.time()
	while True:
		key = 'f'
		#temp = check_temp(key)
		#output.append(temp)
		#print "temp done"
		check_heart_rate()
		end_heart = time.time()
		elapsed = start-end_heart
		heart_rate = heart_counter/elapsed
		hr_array.append(heart_rate)
		output.append(heart_rate)
		print "hr done"
		#reading += 1
		#cubic_spline_hr(reading, hr_array)
		#check_respiration()
		#end_resp = time.time()
		#elapsed = start-end_resp
		#resp_rate = resp_counter/elapsed
		#output.append(resp_rate)
		#print "resp done"
		#output.append(check_skin_conductance())
		#print "skin done"
		#output.append(check_button_presses())
		#print "buttons done"
		#f = open('results.csv', 'w')
		#fileWriter = csv.writer(f)
		#fileWriter.writerow(output)
		#f.close()
		#print "file writing done"
		output = []
		time.sleep(1)

def check_key():  #theoretically complete
    char = getch()
    if char == 'c' or char == 'i' or char == 'u' or char == 'f':
        #print "Key pressed is " + char
        return char
    else:
        return None

def check_button_presses():
	#global output
	asked = switch_debounce(17)
	if asked != None:
		return asked
	answered = switch_debounce(4)
	if answered != None:
		return answered
	else:
		return

def switch_debounce(port):
	while True:
  		#take a reading
  		prev_input = GPIO.input(port)
  		time.sleep(0.05)
  		input = GPIO.input(port)
  		#if the last reading was low and this one high, print
  		if (prev_input and (not input)):
  			if port == 17:
  				return("question asked at ", datetime.datetime.now().time())
  			elif port == 4:
  				return("question answered at ", datetime.datetime.now().time())
  		else:
  			return None

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

def check_heart_rate(): # we need something similar to the RR filter here I think
	return HRFilter()

def HRFilter():
	global heart_counter
	percentage = 90 #need to adjust this value for hr
	## change to lst[1],lst[0]
	lst = []
	while len(lst) < 2:
		temp = read_i2c(0x80)
		print temp
		lst.append(temp)
	percentage_change = float(lst[1] - lst[0]) / abs(lst[0]) * 100
	
	if abs(percentage_change) > percentage:
		return None
	else:
		heart_counter += 1
		return heart_counter

def check_respiration(): #FUCKING DONE
	RRfilter()

def RRfilter():
	global resp_counter
	percentage = 20
	## change to lst[1],lst[0]
	lst = []
	while len(lst) < 2:
		temp = read_i2c(0x10)
		lst.append(temp)
		time.sleep(0.5)
	percentage_change = float(lst[1] - lst[0]) / abs(lst[0]) * 100
	
	if abs(percentage_change) < percentage:
		return None
	else:
		resp_counter += 1
		return resp_counter

def check_skin_conductance():
	return read_i2c(0x40)

## Main Loop
'''
root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
'''

while True:
	#calibration_mode()
	interview_mode()
