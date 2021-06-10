from PyQt5.QtWidgets import QApplication, QWidget

# For access to command
import sys

# One QApp instance per application
# sys.argv allows command line args (in Python list)
app = QApplication(sys.argv)

# Create Qt widget (our window)
window = QWidget()
window.show() # Hidden by default, required to quit program

# Start event loop
app.exec()

# Application reaches here when exit
# Event loop has stopped, code done