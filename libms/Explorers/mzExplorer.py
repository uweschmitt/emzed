# -*- coding: utf-8 -*-

from PyQt4.QtGui import  (QVBoxLayout, QDialog, QLabel, QLineEdit,\
                          QPushButton, QHBoxLayout, QComboBox)

from PyQt4.QtCore import Qt, SIGNAL

import guidata
import os


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
        self.plotMz()

    def processPeakmap(self, peakmap):
        self.level1Peakmap = peakmap.filter(lambda s: s.msLevel == 1)
        self.levelNSpecs = [ s for s in peakmap.spectra if s.msLevel > 1 ]

        self.rts = np.array([s.rt for s in self.level1Peakmap.spectra])

        mzvals = np.hstack([ spec.peaks[:,0] for spec in peakmap.spectra ])
        self.absMinMZ = np.min(mzvals)
        self.absMaxMZ = np.max(mzvals)
        self.minMZ = self.absMinMZ
        self.maxMZ = self.absMaxMZ
        self.updateChromatogram()

        title = os.path.basename(peakmap.meta.get("source", ""))
        self.setWindowTitle(title)

    def updateChromatogram(self):
        min_, max_ = self.minMZ, self.maxMZ
        cc =[np.sum(spec.peaks[(spec.peaks[:,0] >= min_)\
                              *(spec.peaks[:,0] <= max_)][:, 1])\
             for spec in self.level1Peakmap.spectra]
        self.chromatogram = np.array(cc)

    def connectSignalsAndSlots(self):
        self.connect(self.selectButton, SIGNAL("clicked()"), self.selectButtonPressed)
        self.connect(self.resetButton, SIGNAL("clicked()"), self.resetButtonPressed)
        self.connect(self.inputW2, SIGNAL("textEdited(QString)"), self.w2Updated)
        self.connect(self.inputMZ, SIGNAL("textEdited(QString)"), self.mzUpdated)
        if self.chooseLevelNSpec:
            self.connect(self.chooseLevelNSpec, SIGNAL("activated(int)"), self.levelNSpecChosen)

    def selectButtonPressed(self):
        try:
            mz  = float(self.inputMZ.text())
            w2  = float(self.inputW2.text())
            self.minMZ= mz-w2
            self.maxMZ= mz+w2
            self.updateChromatogram()
            self.plotChromatogramm()
        except Exception, e:
            print e

    def levelNSpecChosen(self, idx):
        if idx == 0:
            self.plotMz()
        else:
            spec = self.levelNSpecs[idx-1]
            self.mzPlotter.plot([spec.peaks])
            self.mzPlotter.resetAxes()
            self.mzPlotter.replot()
        self.rtPlotter.setEnabled(idx==0)

    def resetButtonPressed(self):
        self.resetMzLimits()

    def resetMzLimits(self):
        self.minMZ = self.absMinMZ
        self.maxMZ = self.absMaxMZ

        self.updateChromatogram()
        self.plotChromatogramm()

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.labelMin)
        hlayout.addWidget(self.inputMZ)
        hlayout.addWidget(self.labelMax)
        hlayout.addWidget(self.inputW2)
        hlayout.addWidget(self.selectButton)
        hlayout.addWidget(self.resetButton)

        vlayout.addLayout(hlayout)

        vlayout.addWidget(self.rtPlotter.widget)
        if self.chooseLevelNSpec:
            vlayout.addWidget(self.chooseLevelNSpec)
        vlayout.addWidget(self.mzPlotter.widget)

    def setupInputWidgets(self):
        self.labelMin = QLabel("mz")
        self.labelMax = QLabel("w/2")
        self.inputMZ = QLineEdit()
        self.inputW2 = QLineEdit()
        self.selectButton = QPushButton()
        self.selectButton.setText("Select")
        self.resetButton = QPushButton()
        self.resetButton.setText("Reset")
        self.inputW2.setText("0.05")

        if len(self.levelNSpecs):
            self.chooseLevelNSpec = QComboBox()
            self.chooseLevelNSpec.addItem("Only Level 1 Spectra")
            for s in self.levelNSpecs:
                txt = "rt=%.2fm, level=%d" % (s.rt, s.msLevel)
                mzs = [ mz for (mz, I) in s.precursors ]
                precursors = ", ".join("%.6f" % mz for mz in mzs)
                if precursors:
                    txt += ", precursor mzs=[%s]" % precursors
                self.chooseLevelNSpec.addItem(txt)
        else:
            self.chooseLevelNSpec = None

    def w2Updated(self, txt):
        try:
            self.mzPlotter.setHalfWindowWidth(float(txt))
        except:
            pass
    def mzUpdated(self, txt):
        txt = str(txt)
        if txt.strip()=="":
            self.mzPlotter.setCentralMz(None)
            return
        try:
            self.mzPlotter.setCentralMz(float(txt))
        except:
            pass

    def handleCPressed(self, (mz, I)):
        self.inputMZ.setText("%.6f" % mz)

    def setupPlotWidgets(self):
        self.rtPlotter = RtPlotter(self.plotMz)
        self.mzPlotter = MzPlotter(self.handleCPressed)

        self.rtPlotter.setMinimumSize(600, 300)
        self.mzPlotter.setMinimumSize(600, 300)

        self.mzPlotter.setHalfWindowWidth(0.05)

    def plotChromatogramm(self):
        self.rtPlotter.plot([(self.rts, self.chromatogram)])
        self.rtPlotter.setXAxisLimits(self.rts[0], self.rts[-1])
        self.rtPlotter.setYAxisLimits(0, max(self.chromatogram)*1.1)
        self.rtPlotter.setRangeSelectionLimits(self.rts[0], self.rts[0])
        self.rtPlotter.replot()

    def plotMz(self):
        minRT = self.rtPlotter.minRTRangeSelected
        maxRT = self.rtPlotter.maxRTRangeSelected
        peaks = self.level1Peakmap.ms1Spectrum(minRT, maxRT)
        self.mzPlotter.resetAxes()
        self.mzPlotter.plot([peaks])
        self.mzPlotter.replot()


__avoidcleanup = []
def inspectPeakMap(peakmap):
    """Testing this simple Qt/guiqwt example"""

    if len(peakmap) == 0:
        raise Exception("empty peakmap")

    app = guidata.qapplication()

    win = MzExplorer()
    __avoidcleanup.append(win)
    win.setup(peakmap)
    win.activateWindow()
    win.raise_()
    win.exec_()
    del win.level1Peakmap
    del win.levelNSpecs
    del win.rts


    
