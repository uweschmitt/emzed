#encoding: utf-8

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

from metabo import metaboFeatureFinder

from feature_detectors import *

from formula import *

from libms.Explorers       import inspectPeakMap, inspect
from libms.gui.DialogBuilder import (DialogBuilder,
                                     showWarning,
                                     showInformation)

def startfile(path):
    import sys, os
    if sys.platform=="win32":
        # needed for network pathes like "//gram/omics/...."
        path = path.replace("/","\\")
    return os.startfile(path)


__builtins__["MMU"] = 0.001
__builtins__["MASS_E"] = 5.4857990946e-4
__builtins__["MASS_P"] = 1.007276466812
__builtins__["MASS_N"] = 1.00866491600

# remove namespace clutter, __all__ only works for "from ms import *"
# del fails in case of reload(ms) from shell, so we put them into try
# statements:

for mod in ["load_utils", "store_utils", "custom_dialogs", "integration",
        "align", "mzalign", "formula_generator", "isotope_calculator",
        "tools", "statistics", "metlin", "metabo",
        ]:
    try:
        exec "del %s" % mod
    except:
        pass
