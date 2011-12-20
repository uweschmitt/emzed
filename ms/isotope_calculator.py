
def singleIsotopeList(element, count):
    import abundance
    import mass
    import numpy as np
    #import scipy.signal
    abundances = getattr(abundance, element)
    vecsize = len(abundances)+5
    vector  = np.zeros((vecsize,))
    masses = sorted(abundances.keys())
    m0 = masses[0]
    for massnum in masses:
        vector[massnum-m0] = abundances[massnum]

    peaks = []
    probs = np.fft.ifft(np.fft.fft(vector)**count).real
    for i in range(vecsize):
        p = probs[i]
        if p >= 0.01:
            m = getattr(mass, element+str(i+m0))
            peaks.append((m,p))
    return peaks


def gaussiansFor(mf):
    import re
    import itertools
    atoms = re.findall("([A-Z][a-z]?)(\d*)", mf)

    singleAtomPeaks = []
    for symbol, count in atoms:
        if count=="":
            count = 1
        print symbol, count
        singleAtomPeaks.append(singleIsotopeList(symbol, int(count)))


    result = []
    for combination in itertools.product(*singleAtomPeaks):
        totalmass = 0
        totalp = 1.0
        for mass, p in combination:
            totalmass += mass
            totalp *= p
        if totalp >= 0.01:
            result.append((totalmass, totalp))
    return sorted(result)


def isotopeTable(mf, trunc=1e-3, probs=None):
    import numpy as np
    #import scipy.signal
    from   libms.DataStructures.Table import Table
    atoms = re.findall("([CHNOPS])(\d*)", mf)
    flattened = []
    for name, count in atoms:
        if count=="":
            count = 1
        flattened.extend([name]*int(count))

    # monoisotopic probabilities:
    if probs is None:
        probs = {
                       # probability of mass shift:
                       "C": { 0: 0.9, 1: 0.08, 2: 0.02 },
                       "H": { 0: 0.99, 1: 0.01 },
                       "N": { 0: 0.7, 1: 0.22, 2: 0.07 },
                       "O": { 0: 0.8, 1: 0.1, 2: 0.1 },
                       "P": { 0: 0.9, 1: 0.1},
                       "S": { 0: 0.6, 1: 0.3, 2: 0.1 },
                }

    def build_row(elem, n):
        # builds propability vector :
        rv = np.zeros((n,), dtype=np.float64)
        for shift, p in probs[elem].items():
            rv[shift]=p
        return rv

    # max num neutron shift in probs table:
    n = len(max(probs.items(), key=lambda (k,v): len(v))[1])

    # iterate convolution for getting the  prob distribution
    # of the shifts:
    r0 = build_row(flattened[0], n)
    for elem in flattened[1:]:
        rn = build_row(elem, n)
        r0 = np.convolve(r0, rn)
        # tried fft convolve, but this is not faster in this
        # case, maybe because the vectors are quite short
        # compared to other applications of fft
        #r0 = scipy.signal.fftconvolve(r0, rn)

    rows = []
    for i, p in enumerate(r0):
        rows.append([i,p])
        if p<trunc:
            break
    t = Table(["shift_mz", "p"], [int, float], ["%d", "%.3f"], rows,
              title=mf+"_shifts", meta=dict(mf=mf))
    return t




