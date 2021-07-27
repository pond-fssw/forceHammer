# Characterize spring by solving for spring constant k = dF/dx.
# Move TAT hammer through incremental z, taking measurements via NI-9215 DAQ.

from ni9215_interface import NI9215
from HammerDataProcessTools import HammerDataTools
import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Servo_off, Servo_on
import time
import matplotlib.pyplot as plt
import os
import csv

# Input parameters
# No electrode: pztID = 0, With electrrode: pztID = 1
pztID = 1

c = -1
c = 1

# if pztID == 1:
#     c = -1
# else:
#     c = -1

pztNumber = 0

# displaceZ = 400 #OLD SETUP
displaceZ = 800
#displaceZ = 8000
address = 'ASRL3::INSTR'

#vel = 10
vel = 2
vel2 = 2
acc = 5 #default20
#dcl = 20 #default20
dcl = 5
version = "2_0"
#delay1 = 3
delay1 = 2
delay2 = 6

cycles = 5
samplingRate = 3000 #min 1000Hz

centerY = 93000
centerX = 31000
#centerZ = 47000    # OLD SETUP
#centerZ = 60000 + 1200 # NEW SPRING
#centerZ = 60000 + 500 # NEW SPRING
centerZ = 60000 + 300 # NEW SPRING

totSamplingTime = cycles * (delay1 + delay2)
print("Total Sampling Time: " + str(totSamplingTime))
numSamples = samplingRate * totSamplingTime

folderName = "pzt" + str(pztID) + "n" + str(pztNumber) + "v" + str(version)
folderPath = "./hammer_char_results/depole/"
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
#Home(TTA)
time.sleep(1)

# Position hammer at surface
Move_XYZ(TTA, 20, 20, 100, centerX, centerY, centerZ, 1)
print("Hammer Positioned")

Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, centerZ + displaceZ, delay1)
Move_XYZ(TTA, acc, dcl, vel2, centerX, centerY, centerZ, delay2) 
time.sleep(2)
print("Warmed up.")

daq = NI9215(samplingRate=samplingRate, numSamples=numSamples)
daq.startMeasure()
print("Hammer Positioned, setting up measurements.")
time.sleep(2)

# Start measurement
print("Starting experiment...")

#Start moving and start measurement
for i in range(cycles):
    Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, centerZ + displaceZ, delay1)
    # Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, int(centerZ + displaceZ/2), delay2)
    # Move_XYZ(TTA, acc, dcl, vel, centerX, centerY, centerZ, delay2) 
    Move_XYZ(TTA, acc, dcl, vel2, centerX, centerY, centerZ, delay2) 

    print("Progress:    " + str((i/cycles) * 100) + "%")

# Close down
#Home(TTA)
time.sleep(5)
daq.endMeasure()
Servo_off(TTA)
print("Experiment complete, plotting.")

# Post-process (find k)
time = daq.data_index()
forceHammer = daq.data_a0()
pztVoltage = c * daq.data_a1()

# 60 Hz filter
forceHammer = HammerDataTools.notch60(forceHammer, samplingRate)
pztVoltage = HammerDataTools.notch60(pztVoltage, samplingRate)

# Plot
fig, axs = plt.subplots(2, sharex=True, sharey=False)
fig.suptitle('Force Hammer Analysis')
axs[0].plot(time, forceHammer)
axs[0].set_title("Force Hammer Output")
axs[1].plot(time, pztVoltage)
axs[1].set_title("Voltage across PZT")

# Save plot and save data
with open(dataPath, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Velocity", vel, vel2])
    writer.writerow(["Acc", acc, "Decel", dcl])
    writer.writerow(["Delay", delay1, delay2])
    writer.writerow(["Starting Z", centerZ, "Travel Z", displaceZ])
    writer.writerow(["Sampling Frequency", samplingRate])
    
    writer.writerow(["Index", "Force Hammer Reading", "Voltage Reading"])

    for i in range(len(time)):
        writer.writerow([time[i], forceHammer[i], pztVoltage[i]])
        
plt.savefig(plotPath)

plt.show()