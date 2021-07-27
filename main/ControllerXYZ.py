# Don't forget to close robot for it to keep working properly.

import pyvisa as visa
from xyz_functions_gui import Move_XY, Move_XYZ, Servo_on, Servo_off, Home
import time

class ControllerXYZ:
    # Robot setup (open resource and turn servo on), port (str): port name.
    # PID controller constants Kp, Ki, and Kd.
    def __init__(self, port="COM3", Kp = 1, Ki = 0, Kd = 0):
        rm = visa.ResourceManager()
        TTA = rm.open_resource(port)
        print("Successfully connected to: " + str(rm.list_resources()))
        Servo_on(TTA)

        self.inst = TTA

        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.error_tot = 0

        Home(TTA)
        self.x, self.y, self.z = 0, 0, 0

    # Use this to test if robot is moves to desired location (x, y, z)
    def visit(self, x, y, z):
        TTA = self.inst

        print("Start motion.")
        Home(TTA)
        print("Initializing... returning home.")
        time.sleep(5)
        print("Home.")

        Move_XY(TTA, 20, 20, 20, x, y, 1)
        print("Moving to position...")
        time.sleep(5)

        Move_XYZ(TTA, 20, 20, 20, x, y, z, 1)
        print("Hammer time...")
        time.sleep(10)

        Home(TTA)
        print("Return home...")
        time.sleep(5)

        print("Robot returned home.")

    # Moves hammer to desired location
    def moveTo(self, x, y, z):
        inst = self.inst
        Move_XYZ(inst, 20, 20, 20, x, y, z, .1)

    # Robot shut off (close resource and turn servo off)   
    def close(self):
        TTA = self.TTA
        Servo_off(TTA)
        TTA.close()    

    # Apply a certain amount of force (voltage reading), maintained with a PID controller (voltage as ref).
    # Use controllerXYZ_object.moveTo() to get as close to surface as possible first.
    # Additional feature: displays live force being applied for check.
    # param error should be the voltage error (force hammer reading w.r.t. ref force applied)
    def drive(self, desiredForce, error):
        desiredVoltage = self.forceToVoltage(desiredForce)
        TTA = self.inst

        # Error calculations
        self.error_tot += error

        correction_p = self.Kp * error
        correction_i = self.Ki * self.error_tot
        correction_d = self.Kd * error # NEED TO REIMPLEMENT

        correction = correction_p + correction_i + correction_d

        # Actuation
        # Make actuation fast/slow enough (acc, dcl, vel, delay params) so that the controller can move smoothly
        Move_XYZ(TTA, 2, 2, 5, self.x, self.y, self.z + correction, .1)
    
    # Converts desired force applied to voltage (rough linear conversion: N to mV).
    def forceToVoltage(self, force):
        return 16.59 * force

    def voltageToForce(self, voltage):
        return voltage/16.59

    # Returns inst object for user to manually control.
    def controlTTA(self):
        return self.inst