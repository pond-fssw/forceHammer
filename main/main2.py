from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys, time
import pyvisa as visa
import numpy as np
from xyz_functions_gui import Servo_on, Servo_off, Move_XYZ, Home
from ni9215_interface import NI9215
from FormatDepolingResults import DepoleParser

class HammerWorker(QObject):
    finished = pyqtSignal()
    # progress = pyqtSignal(int)

    def runSingle(self, surfaceX, surfaceY, surfaceZ, d, port, cycles, v1, v2, acc, dcc, d1, d2, freq):
        address = port
        rm = visa.ResourceManager()
        print(rm.list_resources())
        TTA = rm.open_resource(address)
        Servo_on(TTA)
        time.sleep(1)

        Move_XYZ(TTA, 20, 20, 100, surfaceX, surfaceY, surfaceZ, 1)
        print("Hammer Positioned")

        Move_XYZ(TTA, acc, dcc, v1, surfaceX, surfaceY, surfaceZ + d, d1)
        Move_XYZ(TTA, acc, dcc, v2, surfaceX, surfaceY, surfaceZ, d2) 
        time.sleep(2)
        print("Warmed up.")

        totSamplingTime = cycles * (d1 + d2)
        print("Total Sampling Time: " + str(totSamplingTime))
        numSamples = freq * totSamplingTime

        self.daq = NI9215(samplingRate=freq, numSamples=numSamples)
        self.daq.startMeasure()
        print("Hammer Positioned. Experiment Started.")
        time.sleep(2)

        for i in range(cycles):
            Move_XYZ(TTA, acc, dcc, v1, surfaceX, surfaceY, surfaceZ + d, d1)
            Move_XYZ(TTA, acc, dcc, v2, surfaceX, surfaceY, surfaceZ, d2) 
            print("Progress:    " + str((i/cycles) * 100) + "%")

        Servo_off(TTA)
        self.daq.endMeasure()
        self.finished.emit()

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
        self.rangeRegen.clicked.connect(self.regenerateSigRange)
        self.calibrateMove.clicked.connect(self.calibrate)
        self.bringHome_2.clicked.connect(self.homeXYZ)

    def calibrate(self):
        x = int(self.calibrateX.text())
        y = int(self.calibrateY.text())
        z = int(self.calibrateZ.text())
        v = int(self.calibrateV.text())
        a = int(self.calibrateA.text())
        d = int(self.calibrateD.text())
        delay = int(self.calibrateDelay.text())
        address = str(self.calibratePort.text())

        rm = visa.ResourceManager()
        print(rm.list_resources())
        TTA = rm.open_resource(address)
        
        Servo_on(TTA)
        time.sleep(1)
        Move_XYZ(TTA, a, d, v, x, y, z, delay)
        Servo_off(TTA)
        print("Moved (Calibration).")

    def runSingleTest(self):
        self.thread = QThread()
        self.worker = HammerWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.collectTestParameters)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.finished.connect(
            lambda: self.startSingle.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.showSingleResults(self.worker.returnDAQ())
        )

        self.thread.start()
        self.startSingle.setEnabled(False)

    def collectTestParameters(self):
        x = int(self.singleX.text())
        y = int(self.singleY.text())
        z = int(self.singleZ.text())
        d = int(self.singleDelta.text())

        port = self.xyzPort.text()
        cycles = int(self.singleCycles.text())
        v1 = int(self.singleV1.text())
        v2 = int(self.singleV2.text())
        acc = int(self.singleAcc.text())
        dcc = int(self.singleDcc.text())
        d1 = int(self.singleDelay1.text())
        d2 = int(self.singleDelay2.text())
        freq = int(self.singleFreq.text())

        self.worker.runSingle(x, y, z, d, port, cycles, v1, v2, acc, dcc, d1, d2, freq)

    def showSingleResults(self, daq):

        index = daq.data_index()
        forceHammer = daq.data_a0()
        pztVoltage = -1 * daq.data_a1()

        self.forceGraph.clear()
        self.voltageGraph.clear()

        self.forceGraph.plot(index, forceHammer)
        self.voltageGraph.plot(index, pztVoltage)

        self.findSignificantRange([index, forceHammer, pztVoltage])

    #####################TO DO: ADD REGENERATE RANGE FUNCTION############################
    def regenerateSigRange(self):
        parser = DepoleParser()
    #####################TO DO: ADD REGENERATE RANGE FUNCTION############################

    def findSignificantRange(self, data):
        parser = DepoleParser(data)
        sigIndex, sigForce, sigVoltage = parser.returnSigRanges()
        for index, force, voltage in zip(sigIndex, sigForce, sigVoltage):
            self.forceGraph.plot(index, force, pen='g')
            self.voltageGraph.plot(index, voltage, pen='g')
        self.plotD33(parser)
    
    def plotD33(self, parser):
        self.d33Box.clear()
        ratios = parser.findD33Ratios()
        print(len(ratios))
        self.d33Box.plot(np.arange(len(ratios)), ratios, symbol='o', symbolPen='b', symbolBrush=0.2)

        self.avgRatio.setText(str(np.round(np.mean(ratios), 3)))
        self.stdRatio.setText(str(np.round(np.std(ratios), 6)))
        self.projD33.setText(str(np.round(np.mean(ratios) * float(self.calibrationFactor.text()), 3)))

    def homeXYZ(self):
        rm = visa.ResourceManager()
        TTA = rm.open_resource('ASRL3::INSTR')
        Servo_on(TTA)
        Home(TTA)
        time.sleep(2)
        Servo_off(TTA)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = ForceHammer()
    main.show()
    sys.exit(app.exec_())
