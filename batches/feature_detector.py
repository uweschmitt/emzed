
def runCentwave(pattern, destination=None):

    # local import in order to keep namespaces clean
    import ms, utils
    import configs 
    import glob, os.path

    det = ms.CentWaveFeatureDetector(**configs.centwaveConfig)
    
    count = 0
    for path in glob.glob(pattern):

        try:
            print "read ", path
            ds = utils.loadMap(path)
        except:
            print "reading FAILED"
            continue
        
        table = det.process(ds)
        print len(table), "features found"

        if destination is None:
            destinationDir = os.path.dirname(path)
        else:
            destinationDir = destination
        fname, ext = os.path.splitext(os.path.basename(path))
        savePath = os.path.join(destinationDir, fname+".csv")
        print "save to ", savePath
        table.saveCSV(savePath)

        count += 1

    print
    print "converted %d datasets" % count
    print

