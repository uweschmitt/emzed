from Feature import Feature

from  pyOpenMS.pxd.Feature cimport Feature as Feature_

cdef Feature_ OpenMsFeatureFromPy(feat):

        cdef Feature_ feat_
        feat_.setMZ(feat.MZ)
        feat_.setRT(feat.RT)
        return feat_


cdef OpenMsFeatureToPy(Feature_ feat_):
        return Feature(feat_.getRT(), feat_.getMZ())
        


    

    
    
