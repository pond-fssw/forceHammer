# Test code for getting measurements out of NI9215 DAQ
# Written for 2 channels (A0, A1) -- should work with connection to any USB port
import nidaqmx
from nidaqmx.constants import Edge
from nidaqmx.constants import AcquisitionType

import numpy as np
import time
import matplotlib.pyplot as plt

# Measurement Parameters
samplingTime = 10 # [s]
samplingRate = 2000 # [Hz]

channelData = []
timeData = []
time0 = time.time()
currentTime = 0

# DAQ Setup
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("cDAQ1Mod1/ai0")
    task.ai_channels.add_ai_voltage_chan("cDAQ1Mod1/ai1")
    task.timing.cfg_samp_clk_timing(samplingRate, source="", active_edge=Edge.RISING, sample_mode=AcquisitionType.CONTINUOUS)
    print("Connected to NI 9215!")
    print("Beginning to take measurements...")

# Measurement Loop
    while currentTime < samplingTime:
        currentTime = time.time() - time0
        data = task.read(number_of_samples_per_channel=1)
        
        timeData.append(currentTime)
        channelData.append(data)
        
# Post-process Data
channelData = np.array(channelData)
timeData = np.array(timeData)
channelData1 = channelData[:, 0]
channelData2 = channelData[:, 1]

print("Measurements taken. Plotting...")

# Plot
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('Measured Voltage from A0 and A1')
ax1.plot(timeData, channelData1)
ax2.plot(timeData, channelData2)
plt.show()