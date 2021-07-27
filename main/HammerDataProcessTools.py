from scipy.signal import butter, lfilter, bessel, iirnotch
import pandas as pd
import matplotlib.pyplot as plt

# Read force hammer data file
class HammerDataTools:
    def getData(fileName):
        df = pd.read_csv(fileName, skiprows=5)
        arr = df.to_numpy()
        index = arr[:, 0]
        forceReading = arr[:, 1]
        return index, forceReading

    def getDataPZT(fileName):
        df = pd.read_csv(fileName, skiprows=5)
        arr = df.to_numpy()
        index = arr[:, 0]
        forceReading = arr[:, 1]
        voltageReading = arr[:, 2]
        return index, forceReading, voltageReading

    def butterLowPass(cutoff, fs, order=5):
        nyq = .5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butterLowPassFilter(data, cutoff, fs, order=5):
        b, a = HammerDataTools.butterLowPass(cutoff, fs, order)
        y = lfilter(b, a, data)
        return y

    def besselLowPass(cutoff, fs, order=5):
        nyq = .5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def besselLowPassFilter(data, cutoff, fs, order=5):
        b, a = HammerDataTools.besselLowPass(cutoff, fs, order)
        y = lfilter(b, a, data)
        return y

    def notch(data, f0, fs, Q):
        b, a = iirnotch(f0, Q, fs)
        y = lfilter(b, a, data)
        return y

    def notch60(data, fs, Q=30):
        return HammerDataTools.notch(data, 60, fs, Q)

    def limitRange(x, y, min, max):
        newX = x[(y >= min) & (y <= max)]
        newY = y[(y >= min) & (y <= max)]
        return newX, newY

if __name__ == "__main__":
    # Parameters
    dataFile = '26.csv'

    order = 6
    fs = 1000
    cutoff = 7

    minVal = -0.02
    maxVal = 0.02
    index, forceReading = HammerDataTools.getData(dataFile)

    # Process Data
    index, forceReading = HammerDataTools.limitRange(index, forceReading, minVal, maxVal)
    
    # Uncomment to choose filter
    filteredData = HammerDataTools.butterLowPassFilter(forceReading, cutoff, fs, order)
    #filteredData = besselLowPassFilter(forceReading, cutoff, fs, order)

    # Plot
    plt.plot(index, forceReading)
    plt.plot(index, filteredData, linewidth=2)
    plt.legend(["Unfiltered", "Filtered"])
    plt.title("Processed Force Reading Measurements")

    plt.ylim([-.02, .03])

    plt.show()
