from pyOpenMS.pxd.Feature cimport Feature as Feature_
from pyOpenMS.pxd.FeatureMap cimport FeatureMap as FeatureMap_

from FeatureMap import FeatureMap


cdef OpenMsFeatureMapToPy(FeatureMap_[Feature_] map_):
        return FeatureMap( [ OpenMsFeatureToPy(map_[i]) 
                             for i in range(map_.size()) ])
       
cdef FeatureMap_[Feature_] OpenMsFeatureMapFromPy(fm):
        assert isinstance(fm, FeatureMap)
        cdef FeatureMap_[Feature_] fm_
        for f in fm.features:
            fm_.push_back(OpenMsFeatureFromPy(f)) 
        fm_.updateRanges()
        return fm_
        

