import bholanath as bh

m2 = bh.motor(2, 56, 115200)

m2.disconnect()
m2.connect()
m2.set_microstep(5)

m2.show_details()