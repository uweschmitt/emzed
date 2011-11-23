from load_utils import *
from save_utils import *
from custom_dialogs import *
from integration import *
from shell_helpers import *
from align import *
from isotope_calculator import *
from tools import *

from libms.Explorers       import inspectPeakMap, inspect
from libms.gui.TableDialog import showTable

__all__ = [ "inspectMap", "inspectFeatures", "showTable",
            "alignFeatureTables" ]

# remove namespace clutter, __all__ only works for "from ms import *"
# del fails in case of reload(ms) from shell, so we put them into try
# statements:
try:
    del load_utils
except: 
    pass
try:
    del save_utils
except: 
    pass
try:
    del custom_dialogs
except: 
    pass
try:
    del integration
except: 
    pass
try:
    del shell_helpers
except: 
    pass
try:
    del align
except: 
    pass
try:
    del isotope_calculator
except: 
    pass
try:
    del tools
except: 
    pass
