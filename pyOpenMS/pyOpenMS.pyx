
from cython.operator cimport address as addr, dereference as deref

# somehow the order if inclusion is important,
# else we get type clash due when openms includes
# headers
include "MzXMLFile.pyx"
include "Param.pyx"
include "Spectrum.pyx"
include "PeakMap.pyx"
include "tests.pyx"
