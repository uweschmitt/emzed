#encoding: utf-8


class _MapAligner(object):

    def __init__(self):
        pass

    def align(self, pattern=None, destination=None, nPeaks=None, 
                    configId="std"):
        import ms
        from configs import mapAlignmentAlgorithmPoseClusteringConfig as cfg
        config = dict(cfg).get(configId)
        if nPeaks is not None:
            config["nPeaks"] = nPeaks

        files, destination = self.getFiles(pattern, destination)
        if files is None:
            return
        print "load maps"
        maps = [ ms.loadPeakMap(p) for p in files ]
        refmap = self.determineRefMap(maps)

        job = _AlignJob(refmap, maps, destination, config)
        try:
            __IPYTHON__.user_ns["_j"] = job
        except:
            pass
        job.rerun()

    def determineRefMap(self, maps):
        import os.path
        # count peaks
        peaks = [ (map_,sum(len(spec) for spec in map_)) for map_ in maps ]
        # find map with max num peaks:
        refmap = max(peaks, key=lambda (m,l): l)[0]
        print
        print "Reference map is", os.path.basename(refmap.meta["source"])
        return refmap

    def getFiles(self, pattern, destination):
        import ms
        import glob
        if pattern is None:
            extensions=["mzXML", "mzData", "mzML"]
            files = ms.askForMultipleFiles(extensions=extensions)
            if not files:
                print "aborted"
                return None, None
            destination = ms.askForDirectory()
            if not destination:
                print "aborted"
                return None, None
        else:
            files = glob.glob(pattern)
        return files, destination

class _AlignJob(object):

    """
       job scheduler class

       methods are:

            rerun(**params)  -- run from begining  over all maps with given 
                                parameters

            cont(**params)   -- continue with new parameter setting

            next(**params)   -- process next map with new parameter setting

            skip()           -- skip alignging of current map

    
       attributes:

            refmap          -- reference map

            maps            -- all selected maps

            mapsToProcess   -- remaining unprocessed maps
                               in case of trouble mapsToProcess[0] is
                               the last map which failed

            param           -- current parameter setting for alignment

    """

    def __init__(self, refmap, maps, destination, param):
        self.refmap = refmap
        self.mapsToProcess = maps
        self.param = param
        self.maps = maps
        self._destination = destination

    def rerun(self, **param_update):
        self.mapsToProcess = self.maps[:] # use copy 
        return self.cont(**param_update)

    def cont(self, **param_update):
        import os
        while len(self.mapsToProcess):
            result = self.next(**param_update)
            if not self._ok:
                return self
        return self

    def skip(self):
        if len(self.mapsToProcess):
           self.mapsToProcess.pop(0)
        print len(self.mapsToProcess), "maps left to process"

    def next(self, **param_update):
        if len(self.mapsToProcess) == 0:
            print 
            print "all maps processed."
            print
            return
        self._ok = False
        # fetch job
        map_ = self.mapsToProcess[0]
        # process job
        self.param.update(param_update)
        alignedMap, fig = self._align(map_)
        if alignedMap is None:
            return self
        self._saveResult(alignedMap, fig)
        # succeeded: remove job
        self.mapsToProcess.pop(0) 
        self._ok = True
        return self

    def _align(self, map_):
        import os.path, pylab
        from  libms.Alignment import alignPeakMapsWithPoseClustering
        path = map_.meta["source"]
        basename = os.path.basename(path)
        try:
            pp=dict(plotAlignment=True, doShow=False, showProgress=True)
            pp.update(self.param)
            if "nPeaks" in pp:
                # typing open-ms parameter max_num_peaks_considered is
                # error prone, so we use nPeaks instead:
                pp["max_num_peaks_considered"] = pp.get("nPeaks")
                del pp["nPeaks"]
            print
            print "align ", basename
            print
            toAlign = [self.refmap, map_]
            # align
            print pp
            alignedMaps = alignPeakMapsWithPoseClustering(toAlign, refIdx=0, 
                                                          **pp)
            fig = None
            if pp.get("plotAlignment"):
                fig = pylab.gcf() # last figure
            return alignedMaps[1], fig
        except Exception, e:
            # if open-ms complains about max_num_peaks_considered, rewrite
            # the trace back as follows:
            import traceback
            out = traceback.format_exc()
            print
            print out.replace("max_num_peaks_considered", "nPeaks")
            if "_j" in globals():
                print
                print "you can use _j.cont(nPeaks=...) or _j.next(...) "\
                      "to go on with new setting"
                print
            return None, None

    def _saveResult(self, map_, fig):
        import ms
        import os
        path = map_.meta["source"]
        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)
        if self._destination is None:
            destinationDir = os.path.dirname(path)
        else:
            destinationDir = self._destination
            try:
                os.makedirs(destinationDir)
            except:
                pass # verzeichnisse schon vorhanden
        target = os.path.join(destinationDir, name+"_aligned.mzML")
        print "write aligned map to", target
        ms.storePeakMap(map_, target)
        if fig is not None:
            target = os.path.join(destinationDir, name+"_aligned.png")
            print "write plot of model fit to", target
            fig.savefig(target)

        
def alignPeakMaps(*a, **kw):
    _MapAligner().align(*a, **kw)
