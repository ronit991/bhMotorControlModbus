import bholanath as bh
from time import sleep

bh.serialInit('COM9', 19200)

pan = bh.motor("pan motor", 8, 19200, 3.0)

#pan.move(200, "rpm", "Rotary_CW_Angle", 30.55)
#pan.show_details()
#pan.run("cw", 100, "rpm")
sleep(5)
pan.stop_movement()
pan.set_slave_addr(8)
pan.show_details()
pan.disconnect()
bh.ser.close()

#0803020002