
cdef double intensityInRange_(np.ndarray[np.float32_t, ndim=2] peaks, float mzmin, float mzmax):
       
        cdef int n
        cdef int N 
        N = peaks.shape[0]
        cdef double I

        I = 0
        for i in range(N):
                if peaks[i,0] >= mzmin:
                    break

        for j in range(i, N):
                if peaks[j,0] > mzmax:
                    break
                I += peaks[j,1]

        return I

        #cdef np.ndarray[np.float32_t, ndim=2] result
        #result = np.zeros( [n,2], dtype = np.float32)
        #n = 0
        #for i in range(N):
            #if peaks[i,0] >= mzmin and peaks[i,0] <= mzmax:
                #result[n,0] = peaks[i,0]
                #result[n,1] = peaks[i,1]
                #n = n + 1
        #return result

#class Extended

def intensityInRange(peaks, float mzmin, float mzmax):
    return intensityInRange_(peaks, mzmin, mzmax)

#Spectrum.intensityInRange = intensityInRange
