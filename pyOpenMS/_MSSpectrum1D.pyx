
cdef class _MSSpectrum1D:

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

    def __str__(self):
        #toString(deref(self.inst))
        return "<dummy>"
        #pass
    def  __len__(self):
         return self.inst.size()

    def __getitem__(self, int index):
        
        cdef Peak1D p = deref(self.inst)[index]
        return p.getMZ()

    def getInstrumentSettings(self):
        cdef InstrumentSettings * inss = new InstrumentSettings(self.inst.getInstrumentSettings()) # copy
        rv = _InstrumentSettings(False)
        rv.inst = inss
        return rv

    

       
