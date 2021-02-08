from time import sleep
import binascii
import libscrc as crc
#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
#                                           Motor (class) definition
# <description here>
class motor:
    # Private data members
    __id = None                 # Id number (for reference only)
    __status = "Not Connected"  # Connection Status
    __slave_addr = "04"         # The drivers have default slave address of 0x01
    __baudrate = 19200

    __motor_current_limit = 0
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
    # Constructor:  Initializes a motor driver with user-given or default values
    #
    # Private Functions:-
    #   getUnitOfSpeedCode()    - returns the hex code of the given unit of speed.
    #   getDirectionCode()      - returns the hex code of the given direction.
    #   send()                  - converts the command string into numeric form and sends it to the motor driver
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    # Class Constructor - Sets values of motor parameters when a motor object is created
    # Slave Address is mandatory, while others are optional.
    # If optional parameters are not given, they use the default values specified in the next line.
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
            print("Connect - ", end="")
            self.__send()
            print("Waiting for response...")
            resp = ser.read(6)
            print("Connect response", resp)
            self.__status = "Connected"
        else:
            print("Device is already connected")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def disconnect(self):
        if(self.__status == "Connected"):
            self.command = self.__slave_addr + "0600000000"  # connect command - <slave_address> 06 00 00 0001
            print("Disconnect - ", end="")
            self.__send()
            resp = ser.read(6)
            print("Disconnect response", resp)
            self.__status = "Not Connected"
        else:
            print("Device is already disconnected")
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_slave_addr(self, SlaveAddr):
        addr = format(SlaveAddr, '#06X')    # convert int value to hex string
        addr = addr[2:]                     # discard the 0x prefix from the hex string
        self.command = self.__slave_addr + "060004" + addr
        print("Set Slave addr - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Slave addr response", resp)
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
        print("set baudrate - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Baudrate response", resp)

        self.__baudrate = BaudRate
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_current(self, Current):
        cur = "0000"
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
            print("Invalid input (", Current, ") for current value")
            return None

        self.command = self.__slave_addr + "060012" + cur
        print("set current - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Current response", resp)
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
        resp = ser.read(6)
        print("Microstep response", resp)
        self.__microstep = Microstep
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————
        

    def set_acceleration(self, Accl):
        acc = int(10*Accl)              # Acceleration value should be multiplied by 10 and rounded to an integer
        acc = format(acc, '#06X')       # Convert int value to hex string
        acc = acc[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "06000C" + acc
        print("acceleration - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Accl response", resp)
        self.__acceleration = Accl
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_deceleration(self, Decel):
        dec = int(10*Decel)             # Deceleration value should be multiplied by 10 and rounded to an integer
        dec = format(dec, '#06X')       # Convert int value to hex string
        dec = dec[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "06000D" + dec
        print("deceleration - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Decel response", resp)
        self.__deceleration = Decel
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_pitch(self, Pitch):
        pi = int(100*Pitch)         # Pitch value should be multiplied by 100 and rounded to an integer
        pi = format(pi, '#06X')     # Convert int value to hex string
        pi = pi[2:]                 # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "060022" + pi
        print("pitch - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Pitch response", resp)
        self.__pitch = Pitch
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def set_home(self):
        self.command = self.__slave_addr + "0600250004"
        print("set home position - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Set Home response", resp)
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    def start_movement(self):
        self.command = self.__slave_addr + "0600250005"
        print("start movement - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Start movement response", resp)
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    def stop_movement(self):
        self.command = self.__slave_addr + "0600250006"
        print("stop movement - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Stop movement response", resp)
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def hold(self):
        self.command = self.__slave_addr + "0600250007"
        print("hold - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Hold response", resp)
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def release(self):
        self.command = self.__slave_addr + "0600250008"
        print("release - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Release response", resp)
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def run(self, Direction, Speed, UnitOfSpeed):
        dir = self.__getDirCode(Direction)
        uSpd = self.__getUnitCode(UnitOfSpeed)

        spd = format(Speed, '#08X')     # Convert int value to hex string
        spd = spd[2:]                   # Discard the 0x prefix from the hex string

        self.command = self.__slave_addr + "10002500030601" + dir + uSpd + spd
        print("run - ", end="")
        self.__send()
        resp = ser.read(6)
        print("Run response", resp)
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
        resp = ser.read(6)
        print("Move response", resp)
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
        resp = ser.read(6)
        print("Go Home response", resp)
        self.__speed = Speed
        self.__unit_of_speed = UnitOfSpeed
    #——————————————————————————————————————————————————————————————————————————————————————————————————————————————————


    def show_details(self):
        print("\n Details for Motor #{mID}:".format(mID = self.__id))
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

        print("Sending Command: ", actualCmd, end="")
        #ser.write(binascii.unhexlify(self.command))
        ser.write(binascii.unhexlify(actualCmd))
        print("... Sent.")
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



import serial
ser = None

def serialInit(Port, BaudRate = 115200):
    global ser
    ser = serial.Serial(Port, BaudRate)



def serialSend(mbCommand):
    for i in mbCommand:
        ser.write(i)

