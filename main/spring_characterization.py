# Characterize spring by solving for spring constant k = dF/dx.
# Move TAT hammer through incremental z, taking measurements via NI-9215 DAQ.

from pyvisa.constants import AddressModifiers
from ni9215_interface import NI9215
import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Servo_off, Servo_on
import time
import matplotlib.pyplot as plt

# Input parameters
centerX = 72600
centerY = 84735
centerZ = 32000
displaceZ = 1000
address = 'ASRL3::INSTR'

vel = 100
acc = 20
dcl = 20

# Machine setup
rm = visa.ResourceManager()
print(rm.list_resources())
TTA = rm.open_resource(address)
Servo_on(TTA)
Home(TTA)
time.sleep(5)

# Position hammer at surface
Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, centerZ, 1)
print("Positioning hammer...")
daq = NI9215(samplingRate = 100, numSamples=1000)
daq.startMeasure()
print("Hammer Positioned, setting up measurements.")
time.sleep(2)

# Start measurement
print("Starting experiment...")

# Start moving and start measurement
for i in range(3):
    Move_XYZ(TTA, 1, 1, 20, centerX, centerY, centerZ + displaceZ, .5)
    Move_XYZ(TTA, 1, 1, 20, centerX, centerY, centerZ, .5)

# Close down
Home(TTA)
time.sleep(5)
daq.endMeasure()
Servo_off(TTA)
print("Experiment complete, plotting.")

# Post-process (find k)
time = daq.data_index()
data = daq.data_a0()

# Plot
plt.plot(time, data)
plt.show()
