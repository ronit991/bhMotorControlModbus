import bholanath as bh
from os import system
from time import sleep

pan = bh.motor("pan motor", 20, 19200, 3.0)
tilt = bh.motor("tilt motor", 21, 19200, 3.0)

#bh.serialInit('COM10', 115200)

while(1):
    system('cls')
    print("Choose Option: \n  1. Pan\n  2. Tilt\n  3. Exit\n > ", end="")
    ch = input()

    if(ch == '1'):
        angle = float(input("Enter pan angle (in degrees): "))
        spd = int(input("Enter speed in rpm: "))
        dir = input("Enter direction (cw/ccw): ")
        if(dir == "cw"):
            pan.move(spd, "rpm", "Rotary_CW_Angle", angle)
        else:
            pan.move(spd, "rpm", "Rotary_CCW_Angle", angle)
    elif(ch == '2'):
        angle = float(input("Enter tilt angle (in degrees): "))
        spd = int(input("Enter speed in rpm: "))
        dir = input("Enter direction (cw/ccw): ")
        if(dir == "cw"):
            tilt.move(spd, "rpm", "Rotary_CW_Angle", angle)
        else:
            tilt.move(spd, "rpm", "Rotary_CCW_Angle", angle)
    elif(ch == '3'):
        quit()
    else:
        print("invalid input")

    input("Press enter to continue... ")