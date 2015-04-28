import time
from matplot


'''  random notes: 
    debug: if refresh rate is too slow catch the old data and just feed that in'''
''' skin conductive 1meg resistor, this is just  a quick mockup ill work on it tonight''' 

def timer(n):## i havent decided if i should just make a timer function yet, will see if it is needed.
	
	
	while n > 0:
		n -= 1
		sleep.time(0.994)
	return 
		




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
arr = [210,93]

def RRfilter(arr):
	percentage = 60
	#temp = read_i2c(0x10)
	percentage_change = float(arr[1] - arr[0]) / abs(arr[0]) * 100
	
	
	#lst = []
	#lst.append(arr)
	
	if abs(percentage_change) > percentage:
		return None
	else:
		return arr[0], arr[1]
	
	

while True:
	print RRfilter(arr)
	time.sleep(2)





'''RR,SST,SCR'''
