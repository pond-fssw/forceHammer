# Test code for getting measurements out of NI9215 DAQ
# Written for 2 channels (A0, A1) -- should work with connection to any USB port
import nidaqmx
from nidaqmx.constants import Edge
from nidaqmx.constants import AcquisitionType
import ControllerXYZ

import numpy as np
import time
import matplotlib.pyplot as plt

# Measurement Parameters
samplingTime = 10 # [s]
samplingRate = 200 # [Hz]

channelData = []
timeData = []
time0 = time.time()
currentTime = 0
numSamples = 10000

robot = ControllerXYZ.ControllerXYZ()

# DAQ Setup
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai0:1')
    task.timing.cfg_samp_clk_timing(samplingRate, source="", active_edge=Edge.RISING, sample_mode=AcquisitionType.FINITE, samps_per_chan=numSamples)
    print("Connected to NI 9215!")

    task.start()
    print("Beginning to take measurements...")
    
    robot.visit(50000, 50000, 50000)

    task.wait_until_done(timeout=20)
    data = task.read(number_of_samples_per_channel=numSamples)
    task.stop()
        
# Post-process data from 2 channels
print("Type: " + str(type(data)))
data = np.array(data)
print("Data shape: " + str(data.shape))

data1 = data[0]
data2 = data[1]
i = range(numSamples)

# Plot
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('Measured Voltage from A0 and A1')
ax1.plot(i, data1)
ax2.plot(i, data2)
plt.show()