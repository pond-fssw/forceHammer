# Characterize spring by solving for spring constant k = dF/dx.
# Move TAT hammer through incremental z, taking measurements via NI-9215 DAQ.

from ni9215_interface import NI9215
import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Servo_off, Servo_on
import time
import matplotlib.pyplot as plt
import os
import csv

# Input parameters
centerX = 72600
centerY = 84735
centerZ = 31550
displaceZ = 500
address = 'ASRL3::INSTR'

vel = 5
acc = 20 #default20
dcl = 20 #default20
version = 31
delay1 = 5
delay2 = 5

folderName = "vel" + str(vel) + "acc" + str(acc) + "dcl" + str(dcl) + "v" + str(version)
folderPath = "./hammer_char_results/"
fileName = "/Test_Data.csv"

path = os.path.join(folderPath, folderName)
os.makedirs(path)
print("Directory '% s' created" % folderName)

plotPath = folderPath + folderName + "/plot.png"
dataPath = folderPath + folderName + fileName


# Machine setup
rm = visa.ResourceManager()
print(rm.list_resources())
TTA = rm.open_resource(address)
Servo_on(TTA)
Home(TTA)
time.sleep(5)

# Position hammer at surface
Move_XYZ(TTA, 20, 20, 100, centerX, centerY, centerZ, 1)
print("Positioning hammer...")
daq = NI9215(samplingRate = 2000, numSamples=2010000)
daq.startMeasure()
print("Hammer Positioned, setting up measurements.")
time.sleep(2)

# Start measurement
print("Starting experiment...")

# Start moving and start measurement
for i in range(100):
    Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, centerZ + displaceZ, delay1)
    Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, centerZ, delay2)

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
plt.xlabel("Time [s]")
plt.ylabel("Force Hammer Reading")
plt.title("vel" + str(vel) + "acc" + str(acc) + "dcl" + str(dcl) + "startz" + str(centerZ) + "displaceZ" + str(displaceZ))
plt.ylim([0, 0.05])

# Save plot and save data
with open(dataPath, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Velocity", vel])
    writer.writerow(["Acc", acc])
    writer.writerow(["Decel", dcl])
    writer.writerow(["Starting Z", centerZ])
    writer.writerow(["Travel Z", displaceZ])
    
    writer.writerow(["Time [s]", "Force Hammer Reading"])

    for i in range(len(time)):
        writer.writerow([time[i], data[i]])
        
plt.savefig(plotPath)

plt.show()