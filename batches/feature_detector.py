
def runCentwave(pattern=None, destination=None):

    """
         runs centwave algorithm from xcms in batch mode.
         input files are map files (mzXML, mxML, mzData),
         ouput files are csv files

         examples:
                
              runCentwave():
                     asks for source files and target directory

              runCentwave(pattern):
                     looks for map files matching pattern
                     resulting csv files are stored next to input map file

              runCentwave(pattern, destination):
                     looks for map files matching pattern
                     resulting csv files are stored at destination directory
                    

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

    det = libms.CentWaveFeatureDetector(**configs.centwaveConfig)
    
    count = 0
    for path in files:

        try:
            print "read ", path
            ds = ms.loadMap(path)
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
    print "analyzed %d datasets" % count
    print

