# Characterize spring by solving for spring constant k = dF/dx.
# Move TAT hammer through incremental z, taking measurements via NI-9215 DAQ.

from ni9215_interface import NI9215
import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Servo_off, Servo_on
import time
import matplotlib.pyplot as plt

# Input parameters (measured)
centerX = 101070
centerY = 69000
centerZ = 58500
displaceZ = 1000
port = 'COM3'

# Hammer cycles to go through
cycles = 2

# Machine and DAQ setup
daq = NI9215(samplingRate=1000, numSamples=30000)

rm = visa.ResourceManager()
print(rm.list_resources())
TTA = rm.open_resource(port)
Servo_on(TTA)
# Home(TTA)
time.sleep(5)
print("Machine and DAQ set up.")

# Position hammer at surface
Move_XYZ(TTA, 1, 1, 100, centerX, centerY, centerZ, 2)
print("Hammer positioned at surface.")

# Start measurement
daq.startMeasure()
time.sleep(2)
print("Measurement started. Starting experiment...")

# Pressing cycles
for i in range(cycles):
    Move_XYZ(TTA, 1, 1, 30, centerX, centerY, centerZ + displaceZ, 10)
    Move_XYZ(TTA, 1, 1, 30, centerX, centerY, centerZ, 10)

# Close down machine
# Home(TTA)
print("Returned home.")
time.sleep(5)
daq.endMeasure()
Servo_off(TTA)
print("Experiment complete! Plotting...")

# Post-process and plot
timeData = daq.data_index()
forceHammer = daq.data_a0()
voltagePZT = daq.data_a1()

fig, axs = plt.subplots(2, 1, constrained_layout=True)
axs[0].plot(timeData, forceHammer)
axs[0].set_title('Force Hammer Output Voltage')
axs[0].set_xlabel('time [non-dimensional index]')
axs[0].set_ylabel('Voltage [V]')
fig.suptitle('PZT and Force Hammer Setup Characterization', fontsize=13)

axs[1].plot(timeData, voltagePZT)
axs[1].set_xlabel('time (s)')
axs[1].set_title('PZT Output Voltage')
axs[1].set_ylabel('Voltage [V]')

plt.show()

print("Plotted results. Experiment complete.")