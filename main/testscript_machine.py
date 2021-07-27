import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Servo_off, Servo_on
import time

x = 101070
y = 69000
z = 59168

rm = visa.ResourceManager()
print(rm.list_resources())
TTA = rm.open_resource('COM3')
Servo_on(TTA)

Home(TTA)
print("Going home...")
#time.sleep(3)
#print("Home... Moving to desired location.")
#Move_XYZ(TTA, 1, 1, 20, x, y, z, 1)
#print("Moved to desired location.")
#time.sleep(5)
#print("Moving back home...")
#Home(TTA)
time.sleep(3)
print("Home.")

Servo_off(TTA)
TTA.close()
print("Test complete!")
