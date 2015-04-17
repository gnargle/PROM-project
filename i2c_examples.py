import smbus					#I2C library 
import time					#Time library

def read_i2c(hex_address):
	bus.write_byte( I2C_ADDR, 0x20 )	
	tmp = bus.read_word_data( I2C_ADDR, hex_address )
	tmpLOW = hex(tmp)[2]
	tmpHIGH = hex(tmp)[3]
	reorderedtmp = tmpHIGH + tmpLOW
	tmp = int(reorderedtmp, 16)
	tmp = tmp & 4095 
	return tmp

I2C_ADDR = 0x21				#I2C base read address
'''
The I2C used has address format 0100xxx, then a r/w bit. 0 is write, 1 is read.
The 0100 is fixed, you can address specific things using the xxx portion of the address.
'''
LED_ON = 0x00					#value need to turn
LED_OFF = 0xFF					#LEDS on / off

bus = smbus.SMBus(1)				#enable I2C bus
						#set Port to 1s to 
						#allow inputs 

PORT_ON = 0xFF

while True:
	'''
	#I2C writing example
	bus.write_word_data( I2C_ADDR, 4, LED_ON )    	#set port to 0
	time.sleep(1)				#wait 1 sec
	bus.write_word_data( I2C_ADDR, 4, LED_OFF )   	#set port to 1
	time.sleep(1)                         	#wait 1 sec
	'''
	#I2C reading example
	i2cvalue = read_i2c(0x00)
	outputString = "INPUT = " + str( i2cvalue )#generate string 
	print( outputString )			   #print string 
	time.sleep(1)                 		   #wait 1 sec
