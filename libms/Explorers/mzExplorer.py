# -*- coding: utf-8 -*-

from PyQt4.QtGui import  QVBoxLayout, QDialog, QPainter, QMainWindow
from PyQt4.QtCore import Qt

#from guiqwt.plot import CurveWidget, PlotManager
#from guiqwt.builder import make
#from guiqwt.label import ObjectInfo
import guidata
import sys

#+from ModifiedGuiQwtBehavior import *
#from Config import *

import guiqwt
assert guiqwt.__version__ == "2.1.4"

#sys.path.insert(0, "..")



from PlottingWidgets import RtPlotter, MzPlotter

import numpy as np




class MzExplorer(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        
        #self.manager = PlotManager(self)
        self.setWindowFlags(Qt.Window)


    def setup(self, peakmap):

        self.processPeakmap(peakmap)
        self.setupPlotWidgets()
        self.setupLayout()

        self.plotChromatogramm()
        
    def closeEvent(self, evt):
        pass

    def processPeakmap(self, peakmap):
        self.peakmap = peakmap
        self.rts = np.array([s.RT for s in self.peakmap])
        self.chromatogram = np.array([np.sum(spec.peaks[:, 1]) for spec in peakmap])

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)
        vlayout.addWidget(self.rtPlotter.widget)
        vlayout.addWidget(self.mzPlotter.widget)


    def setupPlotWidgets(self):
        self.rtPlotter = RtPlotter(self.rts , self.plotMz)
        self.mzPlotter = MzPlotter(self.peakmap)

        self.rtPlotter.setMinimumSize(600, 300)
        self.mzPlotter.setMinimumSize(600, 300)

        self.rtPlotter.refresh()


    def plotChromatogramm(self):
        self.rtPlotter.plot(self.chromatogram)

    def plotMz(self, minRT = None, maxRT = None):
        
        if minRT is not None:
            peaks = np.vstack(( s.peaks for s in self.peakmap if minRT <= s.RT <= maxRT ))
        else:
            peaks = np.vstack(( s.peaks for s in self.peakmap ))

        # not sure if sortin speeds up ?
        #perm = np.argsort(peaks[:,0])
        #peaks = peaks[perm,:]
        self.mzPlotter.plot(peaks)




    

def inspectMap(peakmap):
    """Testing this simple Qt/guiqwt example"""

    if len(peakmap) == 0:
        raise Exception("empty peakmap")

    app = guidata.qapplication()
    
    win = MzExplorer()
    win.setup(peakmap)
    win.activateWindow()
    win.raise_()
    win.exec_()
    

if __name__ == '__main__':
    import pyOpenMS
    peakmap = pyOpenMS.loadMzXmlFile("../test.mzXML")
    print "got data"
    inspect(peakmap)

    
