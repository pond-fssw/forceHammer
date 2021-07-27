# Additional control class for proper movement execution
# Eventually PID for force control
# v1: z movement controls force

import pyvisa as visa
from xyz_functions_gui import Move_XY, Move_XYZ, Servo_on, Servo_off, Home
import time

class ControlXYZ:
    def __init__(self, x1, y1, z1):
        self.x = x1
        self.y = y1
        self.z = z1

        # Robot setup (open resource and turn servo on)
        rm = visa.ResourceManager()
        TTA = rm.open_resource('COM3')
        print("Successfully connected to: " + str(rm.list_resources()))
        Servo_on(TTA)

        self.hammerTime(TTA)

        # Robot cool down (close resource and turn servo off)
        Servo_off(TTA)
        TTA.close()

    def hammerTime(self, inst):
        # Configure this for best motion! -- delays needed for proper control.
        print("Start motion.")

        Home(inst)
        print("Initializing... returning home.")
        time.sleep(5)

        Move_XY(inst, 20, 20, 20, self.x, self.y, 1)
        print("Moving to position...")
        time.sleep(5)

        Move_XYZ(inst, 20, 20, 20, self.x, self.y, self.z, 1)
        print("Hammer time...")
        time.sleep(10)

        Home(inst)
        print("Return home...")
        time.sleep(5)

        print("Robot returned home.")
