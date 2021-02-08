import bholanath as bh

bh.serialInit('COM13', 19200)

pan = bh.motor("pan motor", 1, 19200, 1.5)

#pan.move(200, "rpm", "Rotary_CW_Angle", 30.55)
pan.run("cw", 100, "rpm")
bh.ser.close()