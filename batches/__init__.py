from feature_detector import *
from peak_picker import *
from alignment import *

# remove clutter
try:
    del feature_detector
except: 
    pass
try:
    del peak_picker
except: 
    pass
try:
    del alignment
except: 
    pass
