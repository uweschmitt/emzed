from load_utils import *
from store_utils import *
from custom_dialogs import *
from integration import *
from align import *
from isotope_calculator import *
from formula_generator import formulaTable
from tools import *
from statistics import *
from mzalign import mzAlign
from metlin import matchMetlin

from formula import formula

from libms.Explorers       import inspectPeakMap, inspect
from libms.gui.DialogBuilder import (DialogBuilder,
                                     showWarning,
                                     showInformation)


__builtins__["MMU"] = 0.001
__builtins__["MASS_E"] = 5.4857990946e-4
__builtins__["MASS_P"] = 1.007276466812
__builtins__["MASS_N"] = 1.00866491600

# remove namespace clutter, __all__ only works for "from ms import *"
# del fails in case of reload(ms) from shell, so we put them into try
# statements:
try:
    del load_utils
except:
    pass
try:
    del store_utils
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
    del mzalign
except:
    pass
try:
    del formula_generator
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
try:
    del statistics
except:
    pass

try:
    del metlin
except:
    pass
