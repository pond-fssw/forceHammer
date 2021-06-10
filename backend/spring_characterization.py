# Characterize spring by solving for spring constant k = dF/dx.
# Move TAT hammer through incremental z, taking measurements via NI-9215 DAQ.

from nidaqmx.constants import SampleInputDataWhen
from ni9215_interface import NI9215
import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Move_XY, Servo_off, Servo_on
import time
import matplotlib.pyplot as plt
import numpy as np

# Input parameters
centerX = 60000
centerY = 90000
centerZ = 59500
displaceZ = 5000
port = 'COM3'

# Machine setup
rm = visa.ResourceManager()
print(rm.list_resources())
TTA = rm.open_resource(port)
Servo_on(TTA)
Home(TTA)
time.sleep(5)

# Position hammer at surface
Move_XYZ(TTA, 20, 20, 20, centerX, centerY, centerZ, 1)
print("Positioning hammer...")
time.sleep(5)

# Start measurement
print("Hammer Positioned, setting up measurements.")
daq = NI9215(samplingRate = 100, numSamples=2000)
daq.startMeasure()
print("Starting experiment...")

# Start moving and start measurement
Move_XYZ(TTA, 1, 1, 1, centerX, centerY, centerZ + displaceZ, 5)
Move_XYZ(TTA, 1, 1, 1, centerX, centerY, centerZ, 5)

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
