#encoding: utf-8

centwaveConfig =  dict(  ppm=5, 
                         peakwidth=(15, 600),
                         prefilter=(3,1000), 
                         snthresh = 10, 
                         integrate = 1,
                         mzdiff=0.00, 
                         noise=0,
                         mzCenterFun="wMean",
                         fitgauss=False,
                         verbose_columns = False )
