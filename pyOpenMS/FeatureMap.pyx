cimport pxd.Feature as F
cimport pxd.FeatureMap as FM

from FeatureMap import FeatureMap


cdef OpenMsFeatureMapToPy(FM.FeatureMap[F.Feature] map_):
        return FeatureMap( [ OpenMsFeatureToPy(map_[i]) for i in range(map_.size()) ])
       
cdef FM.FeatureMap[F.Feature] OpenMsFeatureMapFromPy(fm):
        assert isinstance(fm, FeatureMap)
        cdef FM.FeatureMap[F.Feature] fm_
        for f in fm.features:
            fm_.push_back(OpenMsFeatureFromPy(f)) 
        fm_.updateRanges()
        return fm_
        

