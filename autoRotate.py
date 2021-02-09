import bholanath as bh
from time import sleep
from os import system

#bh.serialInit('COM5', 19200)
bh.serialInit('COM9', 19200)
tilt = bh.motor("tilt (1.5) motor", 2, 19200, 1.0)
pan = bh.motor("pan motor", 8, 19200, 3.0)
tilt.stop_movement()
pan.stop_movement()
tilt.set_home()

# pan.run("cw", 20, "rpm")
# sleep(1)
# system('cls')
# tilt.ForwardBackward(60, 45)
# tilt.start_movement()
# sleep(5)
# tilt.stop_movement()
# tilt.go_home(60, "rpm")
# sleep(1)
# pan.stop_movement()

tilt.disconnect()
pan.disconnect()
bh.ser.close()