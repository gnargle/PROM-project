import matplotlib.pyplot as plt
import time
import random
from collections import deque
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
#import matplotlib.animation as animation

############# for the que #######################
a1 = deque([0]*110)
a2 = deque([0]*110)
a3 = deque([0]*110)

############# making subplots ####################

plt.figure(0)

ax = plt.subplot2grid((3,2),(0,0), colspan = 3)
plt.xlabel('t')
plt.title('title')
plt.ylabel('j')
plt.ylim([0,200])
line3, = plt.plot(a2)
ax1 = plt.subplot2grid((3,2), (1,0), colspan = 3)
plt.xlabel('z')
plt.title('title')
plt.ylabel('p')
plt.ylim([0,200])
line2, = plt.plot(a3)
ax2 = plt.subplot2grid((3,2), (2,0), colspan = 3)


##################################################




############## gives us random values ############
def data():
    while True:
        if not paused:
            val = random.randint(1,180)
            yield val
            time.sleep(0.0001) ## needs the delays to stop the crashing
            plt.pause(0.0001)
        else:
            plt.pause(0.0001) ## needs the delays to stop crashing
            pass
data = data()
##################################################


#####Main plot,we need for subplots 2 function####


plt.ion()
plt.xlabel('x')
plt.title('title')
plt.ylabel('y')
          
plt.ylim([0,200])
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





for i in range(0,100000): ## it will get 10 values and stop
    a1.appendleft(next(data))
    a2.appendleft(next(data))
    a3.appendleft(next(data))
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




