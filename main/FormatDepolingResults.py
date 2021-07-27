from os import name
import numpy as np
import matplotlib.pyplot as plt
from HammerDataProcessTools import HammerDataTools

class DepoleParser:
    def __init__(self, data, startingIndex=6000, compressionTime=2, relaxTime=6, samplingFreq=3000):
        self.indices, self.force, self.voltage = data[0], data[1], data[2]
        self.startingIndex = startingIndex
        self.compressionTime = compressionTime
        self.relaxTime = relaxTime
        self.samplingFreq = samplingFreq
        self.findSigRanges()

    def findSigDomains(self):
        self.sigLowerBounds = []
        self.sigUpperBounds = []
        sampledPoints = len(self.force)
        pointIndex = self.startingIndex
        sigRange = 0.5 * self.compressionTime * self.samplingFreq
        period = (self.compressionTime + self.relaxTime) * self.samplingFreq
        delay = int(self.samplingFreq)

        while pointIndex + sigRange < sampledPoints:
            lowerBound = pointIndex
            upperBound = int(pointIndex + sigRange)
            
            self.sigLowerBounds.append(lowerBound)
            self.sigUpperBounds.append(upperBound)

            pointIndex += (period + delay)

    def findSigRanges(self):
        self.findSigDomains()
        self.sigIndex = []
        self.sigForce = []
        self.sigVoltage = []

        for lower, upper in zip(self.sigLowerBounds, self.sigUpperBounds):
            self.sigIndex.append(self.indices[lower:upper])
            self.sigForce.append(self.force[lower:upper])
            self.sigVoltage.append(self.voltage[lower:upper])

    def returnSigRanges(self):
        return self.sigIndex, self.sigForce, self.sigVoltage

    def plotShowRange(self):
        fig, axs = plt.subplots(2, sharex=True, sharey=False)
        fig.suptitle('Show Analysis Range')
        axs[0].set_ylabel("Detected Force [N]")
        axs[0].plot(self.indices, self.force)
        axs[1].set_ylabel("PZT Voltage [V]")
        axs[1].plot(self.indices, self.voltage)
        
        for indexRange, forceRange, voltageRange in zip(self.sigIndex, self.sigForce, self.sigVoltage):
            axs[0].plot(indexRange, forceRange)
            axs[1].plot(indexRange, voltageRange)

        plt.show()

    def findDifferentials(self):
        self.diffForce = []
        self.diffVoltage = []
        
        for sigForces, sigVoltages in zip(self.sigForce, self.sigVoltage):
            self.diffForce.append(max(sigForces) - min(sigForces))
            self.diffVoltage.append(max(sigVoltages) - min(sigVoltages))
        
        return self.diffForce, self.diffVoltage

    def findD33Ratios(self):
        self.findDifferentials()
        return np.array(self.diffVoltage)/np.array(self.diffForce)

if __name__ == "__main__":
    file = "dataFiles/depole/e_2/v1.csv"
    parser = DepoleParser(file)
    diffForce, diffVoltage = parser.findDifferentials()
    parser.plotShowRange()

    # sample = 0 # 0-3
    # samples = ["dataFiles/depole/e_1/", "dataFiles/depole/e_2/", "dataFiles/depole/no_e_1/", "dataFiles/depole/no_e_2/"]
    # versions = ["v0.csv", "v1.csv"]    

    # fig, axs = plt.subplots(4, sharex=True, sharey=False)
    # fig.suptitle('Depoling Effect on PZT (20 min @170C)')
    
    # v01 = DepoleParser(samples[0]+versions[0])
    # v02 = DepoleParser(samples[0]+versions[1])
    # axs[0].boxplot([v01.findD33Ratios(), v02.findD33Ratios()])
    # axs[0].set_ylabel("No Electrode 1")

    # v11 = DepoleParser(samples[1]+versions[0])
    # v12 = DepoleParser(samples[1]+versions[1])
    # axs[1].boxplot([v11.findD33Ratios(), v12.findD33Ratios()])
    # axs[1].set_ylabel("No Electrode 2")

    # v21 = DepoleParser(samples[2]+versions[0])
    # v22 = DepoleParser(samples[2]+versions[1])
    # axs[2].boxplot([v21.findD33Ratios(), v22.findD33Ratios()])
    # axs[2].set_ylabel("Electrode 1")
    
    # v31 = DepoleParser(samples[3]+versions[0])
    # v32 = DepoleParser(samples[3]+versions[1])
    # axs[3].boxplot([v31.findD33Ratios(), v32.findD33Ratios()])
    # axs[3].set_ylabel("No Electrode 2")

    # plt.show()