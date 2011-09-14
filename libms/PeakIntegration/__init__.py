
from SGIntegrator import SGIntegrator
from AssymetricGaussIntegrator import AssymetricGaussIntegrator


PeakIntegrators = dict( std_sg  = SGIntegrator(window_size=11, order=2),
                        sg_21_2 = SGIntegrator(window_size=21, order=2),
                        sg_11_1 = SGIntegrator(window_size=11, order=1),
                        sg_21_1 = SGIntegrator(window_size=21, order=1),
                        asym_gauss = AssymetricGaussIntegrator(),
                      )


