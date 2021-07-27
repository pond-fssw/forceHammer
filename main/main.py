from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys, time
import pyvisa as visa
from xyz_functions_gui import Servo_on, Servo_off, Move_XYZ, Home
from ni9215_interface import NI9215
from HammerDataProcessTools import HammerDataTools

class HammerWorker(QObject):
    finished = pyqtSignal()
    # progress = pyqtSignal(int)

    def collectTestParameters(self, window):
        self.surfaceX = int(window.singleX.text())
        self.surfaceY = int(window.singleY.text())
        self.surfaceZ = int(window.singleZ.text())
        self.appliedDelta = int(window.singleDelta.text())

        self.addressXYZ = window.xyzPort.text()
        self.testCycles = int(window.singleCycles.text())
        self.v1 = int(window.singleV1.text())
        self.v2 = int(window.singleV2.text())
        self.acc = int(window.singleAcc.text())
        self.dcc = int(window.singleDcc.text())
        self.delay1 = int(window.singleDelay1.text())
        self.delay2 = int(window.singleDelay2.text())
        self.samplingRate = int(window.singleFreq.text())

    def runSingle(self, window):
        self.collectTestParameters(window)
        address = self.addressXYZ
        rm = visa.ResourceManager()
        print(rm.list_resources())
        TTA = rm.open_resource(address)
        Servo_on(TTA)
        time.sleep(1)

        Move_XYZ(TTA, 20, 20, 100, self.surfaceX, self.surfaceY, self.surfaceZ, 1)
        print("Hammer Positioned")

        Move_XYZ(TTA, self.acc, self.dcc, self.v1, self.surfaceX, self.surfaceY, self.surfaceZ + self.appliedDelta, self.delay1)
        Move_XYZ(TTA, self.acc, self.dcc, self.v2, self.surfaceX, self.surfaceY, self.surfaceZ, self.delay2) 
        time.sleep(2)
        print("Warmed up.")

        totSamplingTime = self.testCycles * (self.delay1 + self.delay2)
        print("Total Sampling Time: " + str(totSamplingTime))
        numSamples = self.samplingRate * totSamplingTime

        self.daq = NI9215(samplingRate=self.samplingRate, numSamples=numSamples)
        self.daq.startMeasure()
        print("Hammer Positioned. Experiment Started.")
        time.sleep(2)

        for i in range(self.testCycles):
            Move_XYZ(TTA, self.acc, self.dcc, self.v1, self.surfaceX, self.surfaceY, self.surfaceZ + self.appliedDelta, self.delay1)
            Move_XYZ(TTA, self.acc, self.dcc, self.v2, self.surfaceX, self.surfaceY, self.surfaceZ, self.delay2) 
            print("Progress:    " + str((i/self.testCycles) * 100) + "%")

        Servo_off(TTA)
        self.daq.endMeasure()
        self.finished.emit()

    def returnSamplingFreq(self):
        print(type(self.samplingRate))
        return self.samplingRate

    def returnDAQ(self):
        return self.daq


class ForceHammer(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ForceHammer, self).__init__(*args, **kwargs)
        uic.loadUi('ui/hammer_control.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Force Hammer Test")
        self.startSingle.clicked.connect(self.runSingleTest)
        self.forceGraph.setBackground('w')
        self.voltageGraph.setBackground('w')
        self.d33Box.setBackground('w')
        self.bringHome.clicked.connect(self.homeXYZ)

    def runSingleTest(self):
        self.thread = QThread()
        self.worker = HammerWorker()
        self.worker.moveToThread(self.thread)

        # self.thread.started.connect(self.worker.runSingle)
        self.thread.started.connect(lambda: self.worker.runSingle(self))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)

        self.thread.finished.connect(
            lambda: self.startSingle.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.showSingleResults(self.worker.returnDAQ())
        )

        self.thread.start()
        self.startSingle.setEnabled(False)

    def collectTestParameters(self):
        self.surfaceX = int(self.singleX.getText())
        self.surfaceY = int(self.singleY.getText())
        self.surfaceZ = int(self.singleZ.getText())
        self.appliedDelta = int(self.singleDelta.getText())

        self.addressXYZ = self.xyzPort.getText()
        self.testCycles = int(self.singleCycles.getText())
        self.v1 = int(self.singleV1.getText())
        self.v2 = int(self.singleV2.getText())
        self.acc = int(self.singleAcc.getText())
        self.dcc = int(self.singleDcc.getText())
        self.delay1 = int(self.singleDelay1.getText())
        self.delay2 = int(self.singleDelay2.getText())
        self.samplingRate = int(self.singleFreq.getText())

    def showSingleResults(self, daq):
        index = daq.data_index()
        forceHammer = daq.data_a0()
        pztVoltage = 1 * daq.data_a1()

        samplingRate = float(self.singleFreq.text())
        forceHammer = HammerDataTools.notch60(forceHammer, fs=samplingRate)
        pztVoltage = HammerDataTools.notch60(pztVoltage, fs=samplingRate)

        self.forceGraph.plot(index, forceHammer)
        self.voltageGraph.plot(index, pztVoltage)

    def homeXYZ(self):
        rm = visa.ResourceManager()
        TTA = rm.open_resource('ASRL3::INSTR')
        Servo_on(TTA)
        Home(TTA)
        time.sleep(2)
        Servo_off(TTA)

    def plotResults(self):
        x, y = [1, 2, 3], [1, 2, 3]
        self.forceGraph.plot(x, y)
        self.voltageGraph.plot(x, y)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = ForceHammer()
    main.show()
    sys.exit(app.exec_())
