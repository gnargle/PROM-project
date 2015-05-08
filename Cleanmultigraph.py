import matplotlib.pyplot as plt
import time
import random
from collections import deque
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.animation as animation
import csv
#import RPi.GPIO as GPIO
############# for the que #######################
a1 = deque([0]*110)
a2 = deque([0]*110)
a3 = deque([0]*110)
############# making subplots ####################

plt.figure(0)

ax = plt.subplot2grid((3,3),(0,0), colspan = 3)
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.ylim([0,4100])
line3, = plt.plot(a2)
ax1 = plt.subplot2grid((3,3), (1,0), colspan = 3)
plt.xlabel('Time')
plt.ylabel('HR')
plt.ylim([0,4100])
line2, = plt.plot(a3)
ax2 = plt.subplot2grid((3,3), (2,0), colspan = 3)
plt.xlabel('Time')
plt.ylabel('Resp')
plt.ylim([0,4100])

##################################################


#####Main plot,we need for subplots 2 function####


plt.ion()
plt.xlabel('x')
plt.title('title')
plt.ylabel('y')
          
plt.ylim([0,4100])
line, = plt.plot(a1)
plt.show()



plt.figure(0)




paused = False

###################################################


######## pause button #############################

axcolor = 'red'
pauseax = plt.axes([0.83, 0.025, 0.15, 0.036])
button = Button(pauseax, 'Pause/Start', color=axcolor, hovercolor='0.975')
def Kill(event):
    global paused
    paused ^= True
    
    
button.on_clicked(Kill)

###################################################


###############main loop###########################
while True:
    f = open('results1.csv', 'r')
    fileReader = csv.reader(f)
    linelist = fileReader.next()
    a1.appendleft(linelist[0])
    a2.appendleft(linelist[1])
    a3.appendleft(linelist[2])
    f.close()
    for i in range(0,10): ## it will get 10 values and stop
    
    
    
        datatoplot = a1.pop()
        datatoplot2 = a2.pop()
        datatoplot3 = a3.pop()
        line.set_ydata(a1)
        line2.set_ydata(a2)
        line3.set_ydata(a3)
        plt.draw()
    
        time.sleep(0.001)
        plt.pause(0.001) 
        print paused

