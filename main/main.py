from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys

class forceHammer(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(forceHammer, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('ui/hammer_control.ui', self)

        self.runTest.clicked.connect(self.runExperiment)
        self.plotResults()

    def runExperiment(self):
        force, cycles = self.Force.text(), self.Cycles.text()
        print("!")
        return 0

    def plotResults(self):
        x, y = [1, 2, 3], [1, 2, 3]
        self.graph1.plot(x, y)
        self.graph2.plot(x, y)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = forceHammer()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()