# For interfacing with NI9215 or other NI DAQ.
# Get data after starting and ending measurements by calling self.datan 
# (where n is the wanted channel, ex. self.data0) and self.index for corresponding index.

import nidaqmx
from nidaqmx.constants import Edge
from nidaqmx.constants import AcquisitionType

import numpy as np

class NI9215:
    def __init__(self, samplingRate=2000, numSamples=10000):
        # DAQ Setup
        task = nidaqmx.Task()

        task.ai_channels.add_ai_voltage_chan("cDAQ1Mod1/ai0:3")

        task.timing.cfg_samp_clk_timing(samplingRate, source="", active_edge=Edge.RISING, sample_mode=AcquisitionType.FINITE,samps_per_chan=numSamples)
        print("Connected to NI 9215!")

        self.task = task
        self.samplingRate = samplingRate
        self.numSamples = numSamples
            
    # Start measurement.
    def startMeasure(self):
        task = self.task
        task.start()
    
    # End measurement, saves data and calls post-processing method.
    def endMeasure(self):
        task = self.task
        numSamples = self.numSamples

        task.wait_until_done(timeout=40)
        data = task.read(number_of_samples_per_channel=numSamples)
        task.stop()

        self.process(data)

    # Return the index corresponding to the channel data.
    def process(self, data):
        data = np.array(data)

        self.data0 = data[0]
        self.data1 = data[1]
        self.data2 = data[2]
        self.data3 = data[3]
        self.index = range(self.numSamples)

    def data_a0(self): 
        return self.data0

    def data_a1(self): 
        return self.data1

    def data_a2(self): 
        return self.data2

    def data_a3(self): 
        return self.data3

    def data_index(self): 
        return self.index
    
    # After completing experiment, run this to close DAQ communication channel.
    # DON'T USE THIS. Just stopping (self.endMeasure() works with less error).
    def closeDAQ(self):
        self.task.close()