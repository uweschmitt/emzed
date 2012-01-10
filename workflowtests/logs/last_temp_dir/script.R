
                        if (require("xcms") == FALSE)
                        {
                            source("http://bioconductor.org/biocLite.R")
                            biocLite("xcms", dep=T)
                        }
                        library(xcms)
                        xs <- xcmsSet('c:\\dokume~1\\admini~1\\lokale~1\\temp\\tmpucc2f5\\input.mzData', method="centWave",
                                          ppm=3,
                                          peakwidth=c(8, 15),
                                          prefilter=c(8, 10000),
                                          snthresh = 40.000000,
                                          integrate= 1,
                                          mzdiff   = 1.500000,
                                          noise    = 0.000000,
                                          fitgauss = FALSE,
                                          verbose.columns = FALSE,
                                          mzCenterFun = 'wMean'
                                     )
                        write.table(xs@peaks, file='c:\\dokume~1\\admini~1\\lokale~1\\temp\\tmpucc2f5\\output.csv')
                        q(status=4711)
                     
