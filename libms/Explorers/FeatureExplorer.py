# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata
import sys


from ..gui import helpers

from PlottingWidgets import RtPlotter, MzPlotter
import numpy as np

class NumericQTableWidgetItem(QTableWidgetItem):

    """ using this sublcass allows sorting columns in QTableWidget based on
        their numerical value 
    """


    def __init__(self, idx, *a, **kw):
        super(NumericQTableWidgetItem, self).__init__(*a, **kw)
        self.idx = idx


    def __lt__(self, other):
        try:
            return float(self.text()) <= float(other.text())
        except:
            return self.text() <= other.text()



class FeatureExplorer(QDialog):

    def __init__(self, ftable):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.Window)

        self.ftable = ftable.requireColumn("mz") \
                            .requireColumn("mzmin") \
                            .requireColumn("mzmax") \
                            .requireColumn("rt") \
                            .requireColumn("rtmin") \
                            .requireColumn("rtmax") 

        self.integratedFeatures = "intbegin" in self.ftable.colNames

        self.rts = [ spec.RT for spec in ftable.ds.specs ]
        self.maxRT = max(self.rts)

        self.setupWidgets()
        self.setupLayout()
        self.populateTable()
        self.setWindowSize() # depends on table size

        self.plotMz()

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

    def populateTable(self):
        helpers.populateTableWidget(self.tw, self.ftable)

    def setWindowSize(self):

        # the following three steps 1)-3) set the dialog window to an optimal width
        # 
        # large table:
        #              - shrink columns witdts's as much as possible (step 1) 
        #              - table gives minimal width in step 2)
        #              - step 3: table columns are stretched to fit the windows width,
        #                this is a no op in this case, due to 1) and 2)
        #
        # small table:
        #              - shrink columns witdths's as much as possible (step 1) 
        #              - plots sizes shadow minimal width in step 2)
        #              - step 3: table columns are stretched to fit the windows width,
        #                this undoes step 1

        # 1) make columns as small as possible 
        #    might shrink too much, therefore step 3
        self.tw.resizeColumnsToContents()
 
        # 2) make windows size fit to tables size
        #    big table -> expand window
        #    small table: plots give mim
        self.setMinimumWidth(helpers.widthOfTableWidget(self.tw))


        self.tw.setMinimumHeight(300)

    def closeEvent(self, evt):
        pass


    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.rtPlotter.widget)

        if self.integratedFeatures:

            vlayout2 = QVBoxLayout()
            vlayout2.setSpacing(10)
            vlayout2.setMargin(5)
            vlayout2.addWidget(self.intLabel)
            vlayout2.setAlignment(self.intLabel, Qt.AlignTop)
            vlayout2.addWidget(self.chooseIntMethod)
            vlayout2.setAlignment(self.chooseIntMethod, Qt.AlignTop)
            vlayout2.addWidget(self.reintegrateButton)
            vlayout2.setAlignment(self.reintegrateButton, Qt.AlignTop)
            vlayout2.addStretch()
            hlayout.addLayout(vlayout2)
            

        hlayout.addWidget(self.mzPlotter.widget)

        vlayout.addLayout(hlayout)

        vlayout.addWidget(self.tw)

    def setupWidgets(self):

        self.rtPlotter = RtPlotter(rangeSelectionCallback=self.plotMz, numCurves=2)

        rts = [ spec.RT for spec in self.ftable.ds.specs ]
        self.rtPlotter.setRtValues(rts)

        self.mzPlotter = MzPlotter(self.ftable.ds)

        self.rtPlotter.setMinimumSize(300, 250)
        self.mzPlotter.setMinimumSize(300, 250)

        self.tw = QTableWidget()

        self.connect(self.tw.verticalHeader(), SIGNAL("sectionClicked(int)"), self.rowClicked)
        self.connect(self.tw, SIGNAL("cellClicked(int, int)"), self.cellClicked)

        if self.integratedFeatures:
            self.intLabel = QLabel("Integration")
            self.chooseIntMethod = QComboBox()
            self.chooseIntMethod.addItem("std")
            self.reintegrateButton = QPushButton()
            self.reintegrateButton.setText("Integrate")
            self.connect(self.reintegrateButton, SIGNAL("clicked()"), self.doReIntegrate)

    def doReIntegrate(self):
        intbegin, intend = self.rtPlotter.range_.get_range()

            
            

    def plotMz(self):

        minRT=self.rtPlotter.minRTRangeSelected
        maxRT=self.rtPlotter.maxRTRangeSelected

        peaks = [spec.peaks for spec in self.ftable.ds.specs if minRT <= spec.RT <= maxRT ]
        if len(peaks):
            peaks = np.vstack( peaks )
            self.mzPlotter.plot(peaks)
            self.mzPlotter.replot()

        
    def cellClicked(self, rowIdx, colIdx):
        name = self.ftable.colNames[colIdx]
        item = self.tw.currentItem()
        realIdx = item.idx # trotz umsortierung !
        
        getIndex = self.ftable.getIndex


        if name.startswith("mz"):
            mzmin = self.ftable[realIdx][getIndex("mzmin")]
            mzmax = self.ftable[realIdx][getIndex("mzmax")]
            self.mzPlotter.setXAxisLimits(mzmin-0.002, mzmax+0.002)

            # update y-range
            minRT = self.rtPlotter.minRTRangeSelected
            maxRT = self.rtPlotter.maxRTRangeSelected
            specs = [spec for spec in self.ftable.ds.specs if minRT <= spec.RT <= maxRT ]
            peaks = np.vstack([ spec.peaks[ (spec.peaks[:,0] >= mzmin) * (spec.peaks[:,0] <= mzmax) ] for spec in self.ftable.ds.specs ])
            maxIntensity =  max(peaks[:,1])
            self.mzPlotter.setYAxisLimits(0, maxIntensity*1.1)

        elif name.startswith("rtm"):  # rtmin or rtmax
            rtmin = self.ftable[realIdx][getIndex("rtmin")]
            rtmax = self.ftable[realIdx][getIndex("rtmax")]
            self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)
            self.rtPlotter.replot()

        elif name.startswith("rt"):  #  rt
            rt= self.ftable[realIdx][getIndex("rt")]
            self.rtPlotter.setRangeSelectionLimits(rt, rt)
            self.rtPlotter.replot()

    def rowClicked(self, rowIdx):


        realIdx = self.tw.item(rowIdx, 0).idx # trotz umsortierung !
        ft = self.ftable 
        getIndex = ft.getIndex

        if self.integratedFeatures:
            intrts = ft.rows[realIdx][getIndex("intrts")]
            smoothed = ft.rows[realIdx][getIndex("smoothed")]
            self.rtPlotter.plot(smoothed, x=intrts, index=1)

        mzmin = self.ftable[realIdx][getIndex("mzmin")]
        mzmax = self.ftable[realIdx][getIndex("mzmax")]
        rt    = self.ftable[realIdx][getIndex("rt")]

        peaks = [ spec.peaks[ (spec.peaks[:,0] >= mzmin) * (spec.peaks[:,0] <= mzmax) ] for spec in ft.ds.specs ]

        chromatogram = [ np.sum(peak[:,1]) for peak in peaks ]
        self.rtPlotter.plot(chromatogram)

        self.rtPlotter.setXAxisLimits(0, self.maxRT)
        self.rtPlotter.setRangeSelectionLimits(rt, rt)
        self.rtPlotter.replot()

        

def inspectFeatures(ftable):

    app = guidata.qapplication()
    fe = FeatureExplorer(ftable)
    fe.raise_()
    fe.exec_()
