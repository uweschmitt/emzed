
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

    from BatchRunner import BatchRunner
    import configs
    import libms.RConnect
    import ms
    import os.path

    class P(BatchRunner):

        def setup(self, config):
            self.det = libms.RConnect.CentwaveFeatureDetector(**config)

        def process(self, path):
            

            try:
                print "read ", path
                ds = ms.loadMap(path)
            except Exception, e:
                print e
                print "reading FAILED"
                return None
            
            table = self.det.process(ds)
            table.title = path

            print len(table), "features found"
            return table

        def write(self, result, destinationDir, path):
            basename, ext = os.path.splitext(os.path.basename(path))
            savePath = os.path.join(destinationDir, basename+".csv")
            print "save to ", savePath
            result.saveCSV(savePath)


    return P(configs.centwaveConfig, True).run(pattern, destination, configid, **params)
            

