import sys
import os
# Reach back up to the root to find main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from main import *
import c9_bus_client  # C9 bus injection
