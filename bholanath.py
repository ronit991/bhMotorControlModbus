from time import sleep
import binascii
import libscrc as crc

import serial
ser = None

#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
#                                           Motor (class) definition
# <description here>
class motor:
    # Private data members
    __id = None                 # Id number (for reference only)
    __status = "Not Connected"  # Connection Status
    __slave_addr = "04"         # The drivers have default slave address of 0x01
    __baudrate = 19200

    __device_type = ""
    __current = None            # Current in Ampere
    __microstep = None          # Full, Half, 1/4, 1/8, or 1/16
    __acceleration = None       # Acceleration & Deceleration in step/sec^2.
    __deceleration = None       # Range => 15 : 59590 RPM
    __pitch = None              # Pitch in mm/sec
    __speed = None              # Numerical value of speed (Max 4780 RPM)
    __unit_of_speed = None      # Unit - RPM, RPH, mm/sec

    # Public data members
    command = ""

    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    #                                           Member Function Definitions
    #
    # Constructor:  Initializes a motor driver with user-given or default values
    #
    # Public Functions:-
    #   connect()           - Connect the motor driver to the bus
    #   disconnect()        - Disconnect the motor driver from the bus
    #   
    #   set_slave_addr()    - Input = newSlaveAddr (1-247).
    #   set_baudrate()      - Input => {1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 72000, 115200, 128000}
    #   set_current()       - Input => {0.5, 1.0, 1.5, 2.0, 2.5, 2.8, 3.0, 3.2, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0}
    #   set_microstep()     - Input => {1, 2, 4, 8, 16}. These value correspond to {1, 1/2, 1/4, 1/8, 1/16} microstep
    #   set_acceleration()  - Input = newAcceleration (15 - 59590)
    #   set_deceleration()  - Input = newDeceleration (15 - 59590)
    #   set_pitch()         - Input = newPitch (0.5 - 100)
    #
    #   set_home()          - Set current position of motor as home_position
    #   start_movement()    -
    #   stop_movement()     -
    #   hold()              -
    #   release()           -
    #
    #   show_last_command() - Print (to console) the last command sent to the motor driver
    #   show_details()      - Print (to console) the values of different parameters currently set for the motor driver
    #
    # Private Functions:-
    #   getUnitOfSpeedCode()    - returns the hex code of the given unit of speed.
    #   getDirectionCode()      - returns the hex code of the given direction.
    #   send()                  - converts the command string into numeric form and sends it to the motor driver
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    # Class Constructor - Sets values of motor parameters when a motor object is created
    # ID & Slave Address are mandatory, while others parameters are optional.
    # If optional parameters are not given, they use the default values specified in the constructor.
    def __init__(self, ID, SlaveAddr, BaudRate = 19200, Current = 1, Microstep = 1, Accl = 1, Decel = 1, Pitch = 50, Speed = 200, UnitOfSpeed = "RPM"):
        self.__id = ID
        self.__slave_addr = format(SlaveAddr, '#04X')[2:]
        self.connect()
        self.set_baudrate(BaudRate)
        self.set_current(Current)
        self.set_microstep(Microstep)
        self.set_acceleration(Accl)
        self.set_deceleration(Decel)
        #self.set_pitch(Pitch)
        self.__speed = Speed
        self.__unit_of_speed = UnitOfSpeed
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def connect(self):
        if(self.__status == "Not Connected"):
            self.command = self.__slave_addr + "0600000001"  # connect command - <slave_address> 06 00 00 0001
            print("Connecting",self.__slave_addr, end="")
            self.__send()
            resp = readResponse(8)
            print("\t Response - ", resp)

            if(resp != ( self.__slave_addr + "0600000001") ):
                print("Invalid response for connect command... reconnecting")
                self.connect()
            else:
                print("Connect OK")

            self.readDeviceType()
            self.__status = "Connected"
        else:
            print("Device is already connected")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def readDeviceType(self):
        self.command = self.__slave_addr + "0300000001"
        self.__send()
        resp = readResponse(7)
        print("ReadDeviceType response - ", resp, end=" ")
        dtype = resp[8:10]
        print("=> Device type - ", dtype)
        if(dtype == "01"):
            print("Device found: Stepper Drive - 2 A")
            self.__device_type = "01"
        elif(dtype == "02"):
            print("Device found: Stepper Drive - 4.5 A")
            self.__device_type = "02"
        elif(dtype == "03"):
            print("Device found: Stepper Drive - 6 A")
            self.__device_type = "03"
        else:
            print("Read Current Limit - Failed. Retrying...")
            self.readDeviceType()
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    

    def disconnect(self):
        if(self.__status == "Connected"):
            self.command = self.__slave_addr + "0600000000"  # connect command - <slave_address> 06 00 00 0001
            print("Disconnecting ", self.__slave_addr, end="")
            self.__send()
            resp = readResponse(8)
            print("\t Response - ", resp)

            if(resp != ( self.__slave_addr + "0600000000") ):
                print("Invalid response for connect command... retrying")
                self.disconnect()
            else:
                print("Disconnect OK")

            self.__status = "Not Connected"
        else:
            print("Device is already disconnected")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_slave_addr(self, SlaveAddr):
        addr = format(SlaveAddr, '#06X')    # convert int value to hex string
        addr = addr[2:]                     # discard the 0x prefix from the hex string
        self.command = self.__slave_addr + "060004" + addr
        print("Change Slave addr - ", end="")
        self.__send()
        resp = readResponse(8)
        print("\t Response", resp)

        if(resp != ( self.__slave_addr + "060004" + addr) ):
                print("Invalid response for change slave address command... retrying")
                self.set_slave_addr(SlaveAddr)
            else:
                print("Change Slave Address OK")

        self.__slave_addr = addr[2:]
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_baudrate(self, BaudRate):
        br = "0000"
        
        if(BaudRate == 1200):
            br = "0000"
        elif(BaudRate == 1800):
            br = "0001"
        elif(BaudRate == 2400):
            br = "0002"
        elif(BaudRate == 4800):
            br = "0003"
        elif(BaudRate == 7200):
            br = "0004"
        elif(BaudRate == 9600):
            br = "0005"
        elif(BaudRate == 19200):
            br = "0006"
        elif(BaudRate == 38400):
            br = "0007"
        elif(BaudRate == 57600):
            br = "0008"
        elif(BaudRate == 72000):
            br = "0009"
        elif(BaudRate == 115200):
            br = "000A"
        elif(BaudRate == 128000):
            br = "000B"
        else:
            print("Invalid value (", BaudRate, ") for baudrate")
            return None

        self.command = self.__slave_addr + "060001" + br
        print("Set baudrate - ", end="")
        self.__send()
        # resp = readResponse(8)
        # print("\t Response", resp)
        self.__baudrate = BaudRate
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_current(self, Current):
        cur = "0000"
        if(self.__device_type == "01"): # 01 is the code for 2 A Stepper Drive
            if( Current == 0.25 ):
                cur = "0007"
            elif( Current == 0.4 ):
                cur = "000C"
            elif( Current == 0.5 ):
                cur = "000F"
            elif( Current == 0.6 ):
                cur = "0013"
            elif( Current == 0.75 ):
                cur = "0017"
            elif( Current == 0.85 ):
                cur = "001B"
            elif( Current == 1.0 ):
                cur = "001F"
            elif( Current == 1.2 ):
                cur = "0026"
            elif( Current == 1.33 ):
                cur = "002A"
            elif( Current == 1.5 ):
                cur = "002F"
            elif( Current == 1.7 ):
                cur = "0036"
            elif( Current == 1.8 ):
                cur = "0039"
            elif( Current == 2.0 ):
                cur = "003F"
            else:
                print("Invalid input (", Current, ") for current value of 2 A Stepper Drive")
                return None
        elif( (self.__device_type == "02") or (self.__device_type == "03") ): # 02 & 03 is the code for 4.5 A & 6 A Stepper Drive respectively
            if( Current == 0.5):
                cur = "0006"
            elif( Current == 1.0):
                cur = "000C"
            elif( Current == 1.5):
                cur = "0013"
            elif( Current == 2.0):
                cur = "0019"
            elif( Current == 2.5):
                cur = "0020"
            elif( Current == 2.8):
                cur = "0023"
            elif( Current == 3.0):
                cur = "0026"
            elif( Current == 3.2):
                cur = "0029"
            elif( Current == 3.5):
                cur = "002C"
            elif( Current == 4.0):
                cur = "0033"
            elif( Current == 4.5):
                cur = "0039"
            elif( Current == 5.0):
                cur = "0040"
            elif( Current == 5.5):
                cur = "0046"
            elif( Current == 6.0):
                cur = "004C"
            else:
                print("Invalid input (", Current, ") for current value of 4.5/6 A Stepper Drive")
                return None

        self.command = self.__slave_addr + "060012" + cur
        print("set current - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Current response", resp)

        if(resp != ( self.__slave_addr + "060012" + cur) ):
            print("Invalid response for set current command... retrying")
            self.set_current(Current)
        else:
            print("Set Current OK")

        self.__current = Current
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_microstep(self, Microstep):
        ms = "0000"
        if( Microstep == 1 ):
            ms = "0001"
        elif( Microstep == 2 ):
            ms = "0002"
        elif( Microstep == 4 ):
            ms = "0004"
        elif( Microstep == 8 ):
            ms = "0008"
        elif( Microstep == 16 ):
            ms = "0016"
        else:
            print("Invalid input (", Microstep, ") for microstep")
            return None

        self.command = self.__slave_addr + "06001A" + ms
        print("microstep - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Microstep response", resp)

        if(resp != ( self.__slave_addr + "06001A" + ms) ):
            print("Invalid response for microstep command... retrying")
            self.set_microstep(Microstep)
        else:
            print("Set Microstep OK")

        self.__microstep = Microstep
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
        

    def set_acceleration(self, Accl):
        acc = int(10*Accl)              # Acceleration value should be multiplied by 10 and rounded to an integer
        acc = format(acc, '#06X')       # Convert int value to hex string
        acc = acc[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "06000C" + acc
        print("acceleration - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Accl response", resp)

        if(resp != ( self.__slave_addr + "06000C" + acc) ):
            print("Invalid response for set acceleration command... retrying")
            self.set_acceleration(Accl)
        else:
            print("Set Acceleration OK")

        self.__acceleration = acc
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_deceleration(self, Decel):
        dec = int(10*Decel)             # Deceleration value should be multiplied by 10 and rounded to an integer
        dec = format(dec, '#06X')       # Convert int value to hex string
        dec = dec[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "06000D" + dec
        print("deceleration - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Decel response", resp)

        if(resp != ( self.__slave_addr + "06000D" + dec) ):
            print("Invalid response for set deceleration command... retrying")
            self.set_deceleration(Decel)
        else:
            print("Set Deceleration OK")

        self.__deceleration = dec
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_pitch(self, Pitch):
        pi = int(100*Pitch)         # Pitch value should be multiplied by 100 and rounded to an integer
        pi = format(pi, '#06X')     # Convert int value to hex string
        pi = pi[2:]                 # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "060022" + pi
        print("pitch - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Pitch response", resp)
        self.__pitch = Pitch
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_home(self):
        self.command = self.__slave_addr + "0600250004"
        print("set home position - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Set Home response", resp)
        if(resp != ( self.__slave_addr + "0600250004") ):
            print("Invalid response for set home command... retrying")
            self.set_home()
        else:
            print("Set Home OK")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    def start_movement(self):
        self.command = self.__slave_addr + "0600250005"
        print("start movement - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Start movement response", resp)
        if(resp != ( self.__slave_addr + "0600250005") ):
            print("Invalid response for start movement command... retrying")
            self.start_movement()
        else:
            print("Start Movement OK")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    def stop_movement(self):
        self.command = self.__slave_addr + "0600250006"
        print("stop movement - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Stop movement response", resp)
        if(resp != ( self.__slave_addr + "0600250006") ):
            print("Invalid response for stop movement command... retrying")
            self.stop_movement()
        else:
            print("Stop Movement OK")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def hold(self):
        self.command = self.__slave_addr + "0600250007"
        print("hold - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Hold response", resp)
        if(resp != ( self.__slave_addr + "0600250007") ):
            print("Invalid response for hold command... retrying")
            self.hold()
        else:
            print("Hold OK")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def release(self):
        self.command = self.__slave_addr + "0600250008"
        print("release - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Release response", resp)
        if(resp != ( self.__slave_addr + "0600250008") ):
            print("Invalid response for release command... retrying")
            self.release()
        else:
            print("Release OK")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def run(self, Direction, Speed, UnitOfSpeed):
        dir = self.__getDirCode(Direction)
        uSpd = self.__getUnitCode(UnitOfSpeed)

        spd = format(Speed, '#08X')     # Convert int value to hex string
        spd = spd[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "10002500030601" + dir + uSpd + spd
        print("run - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Run response", resp)
        if(resp != ( self.__slave_addr + "1000250003") ):
            print("Invalid response for run command... retrying")
            self.run(Direction, Speed, UnitOfSpeed)
        else:
            print("Run OK")

        self.__speed = Speed
        self.__unit_of_speed = UnitOfSpeed
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def move(self, Speed, UnitOfSpeed, Type, SAT):
        spd = format(Speed, '#08X')     # Convert int value to hex string
        spd = spd[2:]                   # Discard the 0x prefix from the hex string
        uSpd = self.__getUnitCode(UnitOfSpeed)

        mType = ""
        sat = ""                        # sat -> steps/angle/time

        if( ( Type == "Linear_CCW" ) or ( Type == "linear_ccw" ) ):
            mType = "00"
        elif( ( Type == "Linear_CW" ) or ( Type == "linear_cw" ) ):
            mType = "01"
        elif( ( Type == "Rotary_CCW_Angle" ) or ( Type == "rotary_ccw_angle" ) ):
            mType = "02"
        elif( ( Type == "Rotary_CW_Angle" ) or ( Type == "rotary_cw_angle" ) ):
            mType = "03"
        elif( ( Type == "Rotary_CCW_Time" ) or ( Type == "rotary_ccw_time" ) ):
            mType = "04"
        elif( ( Type == "Rotary_CW_Time" ) or ( Type == "rotary_cw_time" ) ):
            mType = "05"
        elif( ( Type == "Rotary_CCW_Steps" ) or ( Type == "rotary_ccw_steps" ) ):
            mType = "06"
        elif( ( Type == "Rotary_CW_Steps" ) or ( Type == "rotary_cw_steps" ) ):
            mType = "07"

        if( (mType == "02") or (mType == "03") ):   # If movement type is angle, multiply it by 100
            SAT *= 100                              # This is specified in the datasheet of the motor driver.

        sat = int(SAT)                  # Round off Step/Angle/Time value to an integer
        sat = format(sat, '#010X')      # Convert int value to hex string
        sat = sat[2:]                   # Discard 0x prefix from hex string

        self.command = self.__slave_addr + "10002500050A02" + mType + uSpd + spd + sat
        print("move - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Move response", resp)

        if(resp != ( self.__slave_addr + "1000250005") ):
            print("Invalid response for move command... retrying")
            self.move(Speed, UnitOfSpeed, Type, SAT)
        else:
            print("Move OK")

        self.__speed = Speed
        self.__unit_of_speed = UnitOfSpeed
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def go_home(self, Speed, UnitOfSpeed):
        uSpd = self.__getUnitCode(UnitOfSpeed)
        
        spd = format(Speed, '#08X')     # Convert int value to hex string
        spd = spd[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "10002500030603" + uSpd + spd
        print("go home - ", end="")
        self.__send()
        resp = readResponse(8)
        print("Go Home response", resp)
        
        if(resp != ( self.__slave_addr + "1000250003") ):
            print("Invalid response for go home command... retrying")
            self.go_home(Speed, UnitOfSpeed)
        else:
            print("Go Home OK")
        
        self.__speed = Speed
        self.__unit_of_speed = UnitOfSpeed
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def ForwardBackward(self, Speed, Angle):
        #cycle 1 - forward (CW) tilt 30 degrees  > next cycle = 2
        #cycle 2 - backward (CCW) tilt 60 degrees > next cycle = 3
        #cycle 3 - forward (Cw) tilt 60 degrees  > next cycle = 2
        # so the sequence of cycles is 1 -> 2 -> 3 -> 2-> 3 ->2 -> 3 ...

        # Auto Cycle Cmd Format - {Slave Addr 2x} + {Fn Code 10} + {Addr_Cn 4x} + {Qty 0008} + {Byte Count 10}
        # + {Next Cycle 2x} + {Dir, CycleType, MovementType - 2x} + {Acc 2x} + {Dcc 2x} + {UnitOfSpeed 2x} + {Speed 6x}
        # + {NoOfSteps 8x} + {StartAt? 2x} + {StopAt? 2x} + {O/P Status at Start 2x} + {O/P Status at Stop 2x}
        # Kx in the above format means 'K' no. of hex digits

        # Addr for Cycle 'n' is given by Addr_Cn = Addr_C1 + (n-1)*8 where Addr_C1 = 2A
        
        spd = format(Speed, '#08X')[2:]
        print("Speed =", spd)
        if( Angle <= 90 ):
            angC1 = int(100*Angle)
            angC2C3 = int(100*2*Angle)
            AngleC1Hex = format(angC1, '#010X')[2:]
            AngleC2C3Hex = format(angC2C3, '#010X')[2:]
            print("Angle hex =", AngleC1Hex)
            print("Angle hex =", AngleC2C3Hex)
        else:
            print("Invalid angle. Please enter a value bw 0 and 90 degrees")
            return None

        # Command for cycle 1: (Addr for C1 is 002A)
        self.command = self.__slave_addr + "10002A000810022C0A0A00" + spd + AngleC1Hex + "00000000"
        print("Auto Cycle (C1) command :", self.command)
        self.__send()
        respC1 = readResponse(8)
        print("C1 response - ", respC1)


        # Command for cycle 2: (Addr for C2 is 0032)
        self.command = self.__slave_addr + "10003200081003280A0A00" + spd + AngleC2C3Hex + "00000000"
        print("Auto Cycle (C2) command :", self.command)
        self.__send()
        respC2 = readResponse(8)
        print("C2 response - ", respC2)

        # Command for cycle 3: (Addr for C3 is 003A)
        self.command = self.__slave_addr + "10003A000810022C0A0A00" + spd + AngleC2C3Hex + "00000000"
        print("Auto Cycle (C3) command :", self.command)
        self.__send()
        respC3 = readResponse(8)
        print("C3 response - ", respC3)

        if( (respC1 != (self.__slave_addr + "10002A0008")) or (respC2 != (self.__slave_addr + "10002A0008")) or (respC3 != (self.__slave_addr + "10002A0008")) ):
            print("Invalid response for one of the auto cycle command in forward/backward tilt... retrying")
            self.ForwardBackward(Speed, Angle)
        else:
            print("Forward/Backward Tilt OK")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def show_details(self):
        print("\n Details for Motor #{mID}:".format(mID = self.__id))
        print("\t Device Type - ", self.__device_type)
        print("\t Status - ", self.__status)
        print("\t Slave Address - ", self.__slave_addr)
        print("\t Baud rate - ", self.__baudrate)
        print("\t Current - ", self.__current)
        print("\t Microstep - ", self.__microstep)
        print("\t Acceleration - ", self.__acceleration)
        print("\t Deceleration - ", self.__deceleration)
        print("\t Pitch - ", self.__pitch)
        print("\t Speed - ", self.__speed, self.__unit_of_speed)
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def show_last_command(self):
        print("Last sent command for motor #{mID} - {cmd}".format(mID = self.__id, cmd = self.command))
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    #——————————————————————————————————————————————— PRIVATE FUNCTIONS ————————————————————————————————————————————————

    # send()    - converts the command string into binary equivalents
    def __send(self):
        sleep(0.25)
        CmdHex = binascii.unhexlify(self.command)
        
        mCrc = crc.modbus(CmdHex)
        mCrcHex = format(mCrc, '#06X')[2:]
        
        mCrcLo = mCrcHex[2:]
        mCrcHi = mCrcHex[:2]
        
        invertedCrc = mCrcLo + mCrcHi
        actualCmd = self.command + invertedCrc

        #print("Sending Command: ", actualCmd, end="")
        ser.write(binascii.unhexlify(actualCmd))
        #print(" ... Sent.")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    
    
    def __getUnitCode(self, UnitOfSpeed):
        uSpd = ""
        if( (UnitOfSpeed == "RPM") or (UnitOfSpeed == "rpm") ):
            uSpd = "00"
        elif( (UnitOfSpeed == "RPH") or (UnitOfSpeed == "rph") ):
            uSpd = "01"
        elif( (UnitOfSpeed == "MMps") or (UnitOfSpeed == "mmps") ):
            uSpd = "02"
        else:
            print("Invalid unit of speed (", UnitOfSpeed, ")")
            quit()
        return uSpd
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def __getDirCode(self, Direction):
        dir = ""
        if( (Direction == "CW") or (Direction == "cw") ):
            dir = "00"
        elif( (Direction == "CCW") or (Direction == "ccw") ):
            dir = "01"
        else:
            print("Invalid direction (", Direction, ")")
            quit()
        
        return dir
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

#_end_of_motor_class_________________________________________________________________________________end_of_motor_class


def serialInit(Port, BaudRate = 115200):
    global ser
    ser = serial.Serial(Port, BaudRate)


def serialSend(mbCommand):
    for i in mbCommand:
        ser.write(i)


def readResponse(noOfBytes):
    resp = ser.read(noOfBytes)
    response = binascii.hexlify(resp)
    #return response.decode('ascii')    # Use this to get response with checksum
    return response.decode('ascii')[:-4]     # Use this to get response without checksum
