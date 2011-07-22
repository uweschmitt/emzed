from pyOpenMS import *

import sys, pprint

if __name__ == "__main__":

    pprint.pprint(FeatureFinder(sys.argv[1]).getParameters())
