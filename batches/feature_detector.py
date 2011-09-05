import ms

import glob


def run_centwave(pattern):

    for path in glob.glob(pattern):

        if not path.endswith(".mzXML"):
            print "CAN NOT CONVERT ", path

        else:
            print "read ", path

            ds = ms.loadMzXmlFile(path)
            det = ms.CentWaveFeatureDetector()
            table = det.process(ds)
            print len(table), "features found"

            table.saveCSV(path.replace(".mzXML", ".csv"))

