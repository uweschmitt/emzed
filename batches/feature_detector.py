
def runCentwave(pattern=None, destination=None, configid=None, **params):

    """
         runs centwave algorithm from xcms in batch mode.
         input files are map files (mzXML, mxML, mzData),
         ouput files are csv files

         you can add modifications to the standard pamaeters, eg ppm,
         as named arguments.

         if you have multiple configs for centwave, you can give an
         configid as defined in configs.py, or you are asked to choose
         a config.

         if you have a single config this one is used automatically

         examples:
                
              runCentwave():
                     asks for source files and target directory
                     asks for config if multiple configs are defined

              runCentwave(configid="std", ppm=17)
                     uses config with id "std", overwrites ppm parameter
                     with ppm=17.

              runCentwave(ppm=13):
                     asks for source files and target directory
                     runs centwave with modified ppm=13 parameter.
                     
              runCentwave(pattern):
                     looks for map files matching pattern
                     resulting csv files are stored next to input map file

              runCentwave(pattern, msDiff=0.003):
                     looks for map files matching pattern
                     resulting csv files are stored next to input map file
                     runs centwave with modified msDiff parameter

              runCentwave(pattern, destination):
                     looks for map files matching pattern
                     resulting csv files are stored at destination directory
                    
              runCentwave(pattern, destination, ppm=17, peakwidth=(5,100) ):
                     looks for map files matching pattern
                     resulting csv files are stored at destination directory
                     runs centwave with modified ppm and peakwidth parameters.

    """

    # local import in order to keep namespaces clean
    import libms, ms
    import configs 
    import glob, os.path

    if pattern is None:
        files = ms.askForMultipleFiles(extensions=["mzXML", "mzData", "mzML"])
        if not files:
            print "aborted"
            return
        destination = ms.askForDirectory()
        if not destination:
            print "aborted"
            return
    else:
        files = glob.glob(pattern)

    if configid is not None:
        for id_, _, config in configs.centwaveConfig:
            if id_ == configid:
                break
        else:
            print "invalid configid %r" % configid
            return
                
    elif len(configs.centwaveConfig) > 1:
        config = ms.chooseConfig(configs.centwaveConfig, params)
    else:
        config = configs.centwaveConfig[0]

    config.update(params)
    det = libms.RConnect.CentWaveFeatureDetector(**config)
    
    count = 0
    tables = []
    for path in files:

        try:
            print "read ", path
            ds = ms.loadMap(path)
        except:
            print "reading FAILED"
            continue
        
        table = det.process(ds)
        table.title = path

        print len(table), "features found"

        if destination is None:
            destinationDir = os.path.dirname(path)
        else:
            destinationDir = destination
        fname, ext = os.path.splitext(os.path.basename(path))
        savePath = os.path.join(destinationDir, fname+".csv")
        print "save to ", savePath
        table.saveCSV(savePath)
        tables.append(table)

        count += 1

    print
    print "analyzed %d datasets" % count
    print
    return tables

