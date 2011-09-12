# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata
import sys


from ..gui import helpers

from PlottingWidgets import RtPlotter, MzPlotter
import numpy as np

class FeatureExplorer(QDialog):

    def __init__(self, ftable):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.Window)

        self.ftable = ftable.restrictToColumns("mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "into", "intb", "intf", "sn")

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

        self.tw.clear()

        self.tw.setRowCount(len(self.ftable.rows))
    
        headers = self.ftable.colNames
        self.tw.setColumnCount(len(headers))
        self.tw.setHorizontalHeaderLabels(headers)

        self.tw.setSortingEnabled(False)  # needs to be done before filling the table

        for i, row in enumerate(self.ftable.rows):
            for j, (value, format_) in enumerate(zip(row, self.ftable.colFormats)):
                item = QTableWidgetItem(format_ % value)
                font = item.font()
                font.setFamily("Courier")
                item.setFont(font)
                self.tw.setItem(i, j, item)
       
        self.tw.setSortingEnabled(True)
        
        # adjust height of rows (normaly reduces size to a reasonable value)
        self.tw.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)

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

        # 3) now stretch table if needed (plottings dictate a minmum size of the
        #    window, 2) only sets *mimumum* size)
        self.tw.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        self.tw.setMinimumHeight(300)

    def closeEvent(self, evt):
        pass


    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.rtPlotter.widget)
        hlayout.addWidget(self.mzPlotter.widget)

        vlayout.addLayout(hlayout)

        vlayout.addWidget(self.tw)

    def setupWidgets(self):

        self.rtPlotter = RtPlotter(self.plotMz)
        rts = [ spec.RT for spec in self.ftable.ds.specs ]
        self.rtPlotter.setRtValues(rts)

        self.mzPlotter = MzPlotter(self.ftable.ds)

        self.rtPlotter.setMinimumSize(300, 250)
        self.mzPlotter.setMinimumSize(300, 250)

        self.tw = QTableWidget()

        self.connect(self.tw.verticalHeader(), SIGNAL("sectionClicked(int)"), self.rowClicked)
        self.connect(self.tw, SIGNAL("cellClicked(int, int)"), self.cellClicked)

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


        if name.startswith("mz"):
            mzmin = float(self.tw.item(rowIdx, self.ftable.getIndex("mzmin")).text())
            mzmax = float(self.tw.item(rowIdx, self.ftable.getIndex("mzmax")).text())
            self.mzPlotter.setXAxisLimits(mzmin-0.002, mzmax+0.002)

            # update y-range
            minRT = self.rtPlotter.minRTRangeSelected
            maxRT = self.rtPlotter.maxRTRangeSelected
            specs = [spec for spec in self.ftable.ds.specs if minRT <= spec.RT <= maxRT ]
            peaks = np.vstack([ spec.peaks[ (spec.peaks[:,0] >= mzmin) * (spec.peaks[:,0] <= mzmax) ] for spec in self.ftable.ds.specs ])
            maxIntensity =  max(peaks[:,1])
            self.mzPlotter.setYAxisLimits(0, maxIntensity*1.1)

        elif name.startswith("rtm"):  # rtmin or rtmax
            rtmin = float(self.tw.item(rowIdx, self.ftable.getIndex("rtmin")).text())
            rtmax = float(self.tw.item(rowIdx, self.ftable.getIndex("rtmax")).text())
            self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)
            self.rtPlotter.replot()

        elif name.startswith("rt"):  #  rt
            rt= float(self.tw.item(rowIdx, self.ftable.getIndex("rt")).text())
            self.rtPlotter.setRangeSelectionLimits(rt, rt)
            self.rtPlotter.replot()

    def rowClicked(self, rowIdx):

        mzmin = float(self.tw.item(rowIdx, self.ftable.getIndex("mzmin")).text())
        mzmax = float(self.tw.item(rowIdx, self.ftable.getIndex("mzmax")).text())
        rt    = float(self.tw.item(rowIdx, self.ftable.getIndex("rt")).text())

        peaks = [ spec.peaks[ (spec.peaks[:,0] >= mzmin) * (spec.peaks[:,0] <= mzmax) ] for spec in self.ftable.ds.specs ]

        chromatogram = [ np.sum(peak[:,1]) for peak in peaks ]
        self.rtPlotter.plot(chromatogram)

        self.rtPlotter.setXAxisLimits(0, self.maxRT)
        self.rtPlotter.setRangeSelectionLimits(rt, rt)
        self.rtPlotter.replot()

        

def inspectFeatures(ftable):

    assert ftable.requireColumn("mz")
    assert ftable.requireColumn("mzmin")
    assert ftable.requireColumn("mzmax")
    assert ftable.requireColumn("rt")
    assert ftable.requireColumn("rtmin")
    assert ftable.requireColumn("rtmax")

    app = guidata.qapplication()
    fe = FeatureExplorer(ftable)
    fe.raise_()
    fe.exec_()
