
cdef class _PeakSpectrum:

    cdef MSSpectrum[Peak1D] * inst

    def __cinit__(self):
        self.inst = new MSSpectrum[Peak1D] ()

    def getRT(self):
        return self.inst.getRT()


    def getMSLevel(self):
        return self.inst.getMSLevel()


    def setName(self, char *name):
        cdef string* sname = new string(name)
        self.inst.setName(deref(sname))
        del sname
        
    def getName(self):
        return self.inst.getName().c_str()

    def  __len__(self):
         return self.inst.size()

    def __getitem__(self, int index):
        
        if index<0:
            index = self.inst.size()+index
        cdef Peak1D p = deref(self.inst)[index]
        return (p.getMZ(), p.getIntensity())

    def getInstrumentSettings(self):
        cdef InstrumentSettings * inss = new InstrumentSettings(self.inst.getInstrumentSettings()) # copy
        rv = _InstrumentSettings(False)
        rv.inst = inss
        return rv

    def getPrecursors(self):

        cdef vector[Precursor] precursors = self.inst.getPrecursors()
        cdef Precursor * newPc
        rv =[]
        for i in range(precursors.size()):
            newPc = new Precursor(precursors.at(i))
            prec = _Precursor(False)
            prec.inst = newPc
            rv.append(prec)

        return rv
    
            
    def findNearest(self, double mz):
        return self.inst.findNearest(mz)

    
    def __iter__(self):
        return IterWrapper(self)

       
