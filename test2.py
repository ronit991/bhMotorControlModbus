import bholanath as bh
from time import sleep
from os import system

#bh.serialInit('COM5', 19200)
bh.serialInit('COM9', 19200)
pan = bh.motor("pan motor", 8, 19200, 3.0)
pan.stop_movement()

pan.disconnect()
bh.ser.close()