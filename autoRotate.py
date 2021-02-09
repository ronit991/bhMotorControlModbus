import bholanath as bh
from time import sleep

#bh.serialInit('COM5', 19200)
bh.serialInit('COM9', 19200)
tilt = bh.motor("tilt (1.5) motor", 2, 19200, 1.0)
pan = bh.motor("pan motor", 8, 19200, 3.0)
tilt.stop_movement()
tilt.set_home()

pan.run("cw", 60, "rpm")
tilt.ForwardBackward(100, 60)
tilt.start_movement()
sleep(10)
tilt.stop_movement()
tilt.go_home(60, "rpm")
sleep(1)
pan.stop_movement()
tilt.disconnect()
pan.disconnect()
bh.ser.close()