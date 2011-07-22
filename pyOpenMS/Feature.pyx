from Feature import Feature

cimport pxd.Feature as F

cdef F.Feature OpenMSFeatureFromPy(feat):
        cdef F.Feature feat_
        feat_.setMZ(feat.MZ)
        feat_.setRT(feat.RT)
        return feat_


cdef OpenMSFeatureToPy(F.Feature feat_):
        return Feature(feat_.getRT(), feat_.getMZ())
        


    

    
    
