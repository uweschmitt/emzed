

long_cfg = dict( ppm=5, 
                 peakwidth=(15, 600),
                 prefilter=(3,1000), 
                 snthresh = 10, 
                 mzdiff=0.00 )

centwaveConfig += [ ( "orbitrap_long", "long peakwidths on orbitrap", long_cfg) ]

peakPickerHiResConfig += [ ( "low_noise", "low noise", dict(signal_to_noise = 0.5) ) ]

peakIntegrators += [ ( "sg22", SGIntegrator(window_size=23, order=2) ) ]
