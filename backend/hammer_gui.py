# GUI for controlling xyz robot
# Will be used to implement force hammer for PZT classification.
# Input xyz values on top, plot measured output (force and charge) at the bottom.
# Velocity, acceleration, and decelleration of hammer are set to default.

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QFormLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys

import ControlXYZ

class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Experiment Results")
        layout.addWidget(self.label)
        self.setLayout(layout)

# Subclass for organizing window
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Formatting stuff
        self.setWindowTitle("Manual Force Hammer 1.0")
        title = QLabel("Welcome")

        # Widgets for communication -- desired x-y location and force input (int, >10000)
        self.x = QLineEdit()
        self.x.setValidator(QIntValidator())
        self.y = QLineEdit()
        self.y.setValidator(QIntValidator())
        self.z = QLineEdit()
        self.z.setValidator(QIntValidator())
        button = QPushButton("Start Experiment")
        # self.button.clicked.connect(self.run_experiment())
        button.clicked.connect(self.run_experiment)
        # LATER: ADD FUNCTION: ONLY ONE CLICK ALLOWED IN TIME INTERVAL? 

        # Layout design
        layout = QFormLayout()
        layout.addWidget(title)
        layout.addRow("Enter x displacement: ", self.x)
        layout.addRow("Enter y displacement: ", self.y)
        layout.addRow("Enter z displacement: ", self.z)
        layout.addWidget(button)

        # For final presentation
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def run_experiment(self):
        # Assign variables (x, y, z), instantiate controlXYZ
        x, y, z = int(float(self.x.text())), int(float(self.y.text())), int(float((self.z.text())))
        run = ControlXYZ.ControlXYZ(x, y, z)

        # Return results
        # results = run.showResults()

        print("Experiment complete.")

    def plot_results(self):
        self.w = AnotherWindow()
        self.w.show()
        return 0

# Run application
app = QApplication(sys.argv)
user_window = MainWindow()
user_window.show()

app.exec()
