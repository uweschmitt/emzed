#encoding: utf-8


def alignPeakMaps(pattern=None, destination=None, **param):

    import glob, os.path
    import ms
    import libms.Alignment

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

    maps = [ ms.loadPeakMap(p) for p in files ]
    aligned_maps = libms.Alignment.alignPeakMapsWithPoseClustering(maps, 
                                                                   **param)
    for pm, path in zip(maps, files):
        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)
        new_name = name+"_aligned.mzML"
        if destination is None:
            destinationDir = os.path.dirname(path)
        else:
            destinationDir = destination
            try:
                os.makedirs(destinationDir)
            except:
                pass # verzeichnisse schon vorhanden
        target = os.path.join(destinationDir, new_name)
        print "write", target
        ms.storePeakMap(pm, target)
