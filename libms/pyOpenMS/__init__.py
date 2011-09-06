# load extension module which loads other python modules from this directory
import os
here = os.path.dirname(os.path.abspath(__file__))
os.environ["OPENMS_DATA_PATH"] = os.path.join(here, "shared", "openMS") # "shared/OpenMS/"
from _pyOpenMS import *  
