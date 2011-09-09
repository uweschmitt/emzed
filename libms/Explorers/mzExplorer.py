# -*- coding: utf-8 -*-

from PyQt4.QtGui import  QVBoxLayout, QDialog, QPainter, QMainWindow, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt4.QtCore import Qt, SIGNAL

import guidata
import sys


import guiqwt
assert guiqwt.__version__ == "2.1.4"


from PlottingWidgets import RtPlotter, MzPlotter
import numpy as np

class MzExplorer(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.Window)

    def setup(self, peakmap):

        self.processPeakmap(peakmap)
        self.setupPlotWidgets()
        self.setupInputWidgets()
        self.connectSignalsAndSlots()
        self.setupLayout()

        self.resetMzLimits()
        self.plotChromatogramm()
        self.rtPlotter.notifyMZ()

    def closeEvent(self, evt):
        pass

    def processPeakmap(self, peakmap):
        self.peakmap = peakmap
        self.rts = np.array([s.RT for s in self.peakmap])

        mzvals = np.hstack([ spec.peaks[:,0] for spec in peakmap ])
        self.absMinMZ = np.min(mzvals)
        self.absMaxMZ = np.max(mzvals)
        self.minMZ = self.absMinMZ
        self.maxMZ = self.absMaxMZ
        self.updateChromatogram()


    def updateChromatogram(self):
        min_, max_ = self.minMZ, self.maxMZ
        cc =[np.sum(spec.peaks[(spec.peaks[:,0] >= min_) * (spec.peaks[:,0] <= max_)][:, 1]) for spec in self.peakmap]
        self.chromatogram = np.array(cc)


    def connectSignalsAndSlots(self):

        self.connect(self.selectButton, SIGNAL("clicked()"), self.selectButtonPressed)
        self.connect(self.resetButton, SIGNAL("clicked()"), self.resetButtonPressed)

    def selectButtonPressed(self):
        try:
            self.minMZ=float(self.inputMin.text())
            self.maxMZ=float(self.inputMax.text())
            self.mzPlotter.setXAxisLimits(self.minMZ, self.maxMZ)
            self.updateChromatogram()
            self.plotChromatogramm()
        except Exception, e:
            print e

    def resetButtonPressed(self):
        self.resetMzLimits()

    def resetMzLimits(self):
        self.minMZ = self.absMinMZ
        self.maxMZ = self.absMaxMZ
        self.mzPlotter.setXAxisLimits(self.minMZ, self.maxMZ)
        self.inputMin.setText("%.6f" % self.absMinMZ)
        self.inputMax.setText("%.6f" % self.absMaxMZ)

        self.updateChromatogram()
        self.plotChromatogramm()
    
        

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.labelMin)
        hlayout.addWidget(self.inputMin)
        hlayout.addWidget(self.labelMax)
        hlayout.addWidget(self.inputMax)
        hlayout.addWidget(self.selectButton)
        hlayout.addWidget(self.resetButton)

        vlayout.addLayout(hlayout)

        vlayout.addWidget(self.rtPlotter.widget)
        vlayout.addWidget(self.mzPlotter.widget)

    def setupInputWidgets(self):
        self.labelMin = QLabel("minrz")
        self.labelMax = QLabel("maxrz")
        self.inputMin = QLineEdit()
        self.inputMax = QLineEdit()
        self.selectButton = QPushButton()
        self.selectButton.setText("Select")
        self.resetButton = QPushButton()
        self.resetButton.setText("Reset")

        self.inputMin.setText("%.6f" % self.absMinMZ)
        self.inputMax.setText("%.6f" % self.absMaxMZ)



        """
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))

        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.pushButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.lineEdit_2 = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.lineEdit = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.lineEdit)

        self.verticalLayout.addLayout(self.horizontalLayout)
        """



    def setupPlotWidgets(self):
        self.rtPlotter = RtPlotter(self.rts , self.plotMz)
        self.mzPlotter = MzPlotter(self.peakmap)


        self.rtPlotter.setMinimumSize(600, 300)
        self.mzPlotter.setMinimumSize(600, 300)

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

    
