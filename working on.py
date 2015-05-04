import time
from matplot

''' skin conductive 1meg resistor, this is just  a quick mockup ill work on it tonight''' 


'''We can just use the check_key function to turn it on/off, ill test that tomorrow''' 
import time
import matplotlib.pyplot as plt
import numpy as np
import random as ran

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

def check_key(): 
    char = getch()
    if char == 'c' or char == 'i' or char == 'u' or char == 'f' or char == 'm':
        #print "Key pressed is " + char
        return char
    else:
        return None



plt.axis([0, 100, -10, 210])## sets axis, if its bigger than y it wont show it on screen, it will go on untill it was reached the max value on the x axis.
plt.ion()
plt.show()
ydata = [0]## holds the rand data.
line, = plt.plot(ydata)

temp = time.time()


def graph(char)
    while char == 'm':
        y = ran.randint(1,10)


        X_axis = int(int(time.time())-int(temp))## time base
        Y_axis = y ### updates random values
        ydata.append(Y_axis)
        line.set_xdata(np.arange(len(ydata)))
        line.set_ydata(y)
        plt.draw()
        time.sleep(0.1)



def select_signal_type(): ## need to be able to change the signal at any time.
	char = getch()
	if char == 'f':
		return 'f'
	elif char == 'u':
		return 'u'
		
	else pass



def respitor_rate():### calibration: 
	resp = read_i2c(0x10)
	n = 60
	

	while n > 0 :   ### just a tests printing replace it entirely with time.sleep(60)
		print ( n, 'Seconds left') 
		n = n-1
		time.sleep(0.9994)
	return resp ## once timer is done it returns the resp value






			
def check_temp(filter):## need to link a signal type option
	#print "temp check func working"
	
	unsorted = read_i2c(0x20)
	temp = []
	if filter == 'u':
		return unsorted
	else:
		while len(temp) < 7:### test of returning mean value of an array of length 7
			temp.append((read_i2c(0x20))	
		return signal_filter(temp)
	
	#print temp
	


def signal_filter(input_array):
		
	sort = input_array
	sort.sort()
	length = len(input_array)
		
	if length == 0:
		pass
	
	elif (length % 2)  == 0:
		return ((sort[length/2] + sort[(length/2) -1]) / 2.0)
	else:
		return sort[length/2]





import random

import math
import time



### percentage change RR, basic model of RR filter, needs changing when i get my hands on the hardware to test.
##I think deeper breaths will cause a greater change, im not sure if we should record this or just the rate of breather per min.
##I don't think we need to actually plot these values, just too to count it as 1 breath, and run it through a,
## time program at calculate the expected breath's per minute(which will be displayed on GUI).
arr = [210,93]
counter = 0

arr = [210,93]

def RRfilter(arr):
	global counter
	percentage = 60
	#temp = read_i2c(0x10)
	percentage_change = float(arr[1] - arr[0]) / abs(arr[0]) * 100## change to lst[1],lst[0]
	#lst = []
	#while len(lst) < 1:
		#lst.append(temp)
	
	lst.append(arr)
	
	if abs(percentage_change) > percentage:
		return None
	else:
		counter += 1
		return counter
	
	

while True:
	print RRfilter(arr)
	time.sleep(2)
	
	

while True:
	print RRfilter(arr)
	time.sleep(2)





'''RR,SST,SCR'''
