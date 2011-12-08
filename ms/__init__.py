from load_utils import *
from store_utils import *
from custom_dialogs import *
from integration import *
from shell_helpers import *
from align import *
from isotope_calculator import *
from tools import *
from mzalign import mzalign

from libms.Explorers       import inspectPeakMap, inspect
from libms.gui.TableDialog import showTable

__all__ = [ "inspectMap", "inspectFeatures", "showTable",
            "alignFeatureTables" ]

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
    del isotope_calculator
except:
    pass
try:
    del tools
except:
    pass

