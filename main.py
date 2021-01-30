import bholanath as bh

m2 = bh.motor(2, 56, 115200)

m2.go_home(2000, "rpm")
m2.start_movement()
m2.hold()
m2.release()
m2.stop_movement()

m2.run("CW", 2000, "RPH")
