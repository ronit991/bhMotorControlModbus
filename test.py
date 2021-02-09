import bholanath as bh
from time import sleep

#bh.serialInit('COM5', 19200)
bh.serialInit('COM13', 19200)

pan = bh.motor("pan motor", 8, 19200, 3.0)

#pan.move(200, "rpm", "Rotary_CW_Angle", 30.55)
pan.show_details()
pan.run("cw", 100, "rpm")
sleep(60)
pan.stop_movement()
pan.set_slave_addr(1)
pan.show_details()
bh.ser.close()