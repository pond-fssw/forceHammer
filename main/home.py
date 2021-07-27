# Characterize spring by solving for spring constant k = dF/dx.
# Move TAT hammer through incremental z, taking measurements via NI-9215 DAQ.
import pyvisa as visa
from xyz_functions_gui import Home, Move_XYZ, Servo_off, Servo_on
import time

# Input parameters
address = 'ASRL3::INSTR'

# Machine setup
rm = visa.ResourceManager()
TTA = rm.open_resource('ASRL3::INSTR')
Servo_on(TTA)
Home(TTA)
time.sleep(2)
Servo_off(TTA)