# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata
import sys


from ..gui import helpers

from PlottingWidgets import RtPlotter, MzPlotter
import numpy as np

import configs


class StreamSplitter(object):

    """ output stream: prints output to given stream
        and to QTextEdit widget.

        The append() method of QTextEdit starts a new
        line for each call. That is why we have to
        collect outputs without "\n" at its end.
    """

    def __init__(self, qtextedit, stream):
        self.qtextedit = qtextedit
        self.stream = stream
        self.collected = []

    def write(self, what):
        # self.stream.write(what)
        if what.endswith("\n"):
            self.qtextedit.append("".join(self.collected)+what.rstrip("\n"))
            self.collected = []
        else:
            self.collected.append(what)


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

        self.setMinimumHeight(600)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

        
        sys.stdout = StreamSplitter(self.statusMessages, sys.stdout)
        sys.stderr = StreamSplitter(self.statusMessages, sys.stderr)

        self.lastRow = None


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


        self.tw.setMinimumHeight(150)

    def closeEvent(self, evt):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


    def setupLayout(self):
        vlayouto = QVBoxLayout()
        self.setLayout(vlayouto)

        #hlayout = QHBoxLayout()

        vlayout = QSplitter()
        vlayout.setOrientation(Qt.Vertical)
        vlayout.setOpaqueResize(False)

        hlayout = QSplitter()
        hlayout.setOpaqueResize(False)
        hlayout.addWidget(self.rtPlotter.widget)

        if self.integratedFeatures:

            #vlayout2 = QVBoxLayout()
            vlayout2 = QSplitter()
            vlayout2.setOpaqueResize(False)
            vlayout2.setOrientation(Qt.Vertical)

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

        #vlayout.addLayout(hlayout)
        vlayout.addWidget(hlayout)

        vlayout.addWidget(self.tw)
        vlayout.addWidget(self.statusMessages) # QTextEdit())

        vlayouto.addWidget(vlayout)

    def setupWidgets(self):

        plotconfigs = (None, dict(shade=0.35, linewidth=1, color="g") )
        self.rtPlotter = RtPlotter(rangeSelectionCallback=self.plotMz, numCurves=2, configs=plotconfigs)

        rts = [ spec.RT for spec in self.ftable.ds.specs ]
        self.rtPlotter.setRtValues(rts)

        self.mzPlotter = MzPlotter(self.ftable.ds)

        self.rtPlotter.setMinimumSize(300, 150)
        self.mzPlotter.setMinimumSize(300, 150)

        pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pol.setVerticalStretch(5)
        self.rtPlotter.widget.setSizePolicy(pol)
        self.mzPlotter.widget.setSizePolicy(pol)

        self.tw = QTableWidget()

        pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pol.setVerticalStretch(5)
        self.tw.setSizePolicy(pol)

        self.statusMessages = QTextEdit()
        self.statusMessages.setReadOnly(True)
        self.statusMessages.setMinimumHeight(20)
        pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pol.setVerticalStretch(1)
        self.statusMessages.setSizePolicy(pol)
        

        self.connect(self.tw.verticalHeader(), SIGNAL("sectionClicked(int)"), self.rowClicked)
        self.connect(self.tw, SIGNAL("cellClicked(int, int)"), self.cellClicked)

        if self.integratedFeatures:
            self.intLabel = QLabel("Integration")
            self.chooseIntMethod = QComboBox()
            for name, _ in configs.peakIntegrators:
                self.chooseIntMethod.addItem(name)
            self.connect(self.chooseIntMethod, SIGNAL("currentIndexChanged(int)"), self.intMethodChanged)
            self.reintegrateButton = QPushButton()
            self.reintegrateButton.setText("Integrate")
            self.connect(self.reintegrateButton, SIGNAL("clicked()"), self.doReIntegrate)

    def intMethodChanged(self, i):
        print configs.peakIntegrators[i][1], "chosen"

    def doReIntegrate(self):
        if not self.integratedFeatures:
            return

        widgetRowIdx = self.tw.currentRow()
        if widgetRowIdx < 0:
            return

        ft = self.ftable
        getIndex = ft.getIndex

        # setup integrator
        method = self.chooseIntMethod.currentText()
        integrator = dict(configs.peakIntegrators)[str(method)] # qstring -> python string
        integrator.setPeakMap(ft.ds)
        print str(integrator)

        # get eic limits
        row = ft.rows[self.tw.item(widgetRowIdx, 0).idx] # rowidx may be different to widgets row index due to sorting:
        mzmin = row[getIndex("mzmin")]
        mzmax = row[getIndex("mzmax")]
        intBegin, intEnd = sorted(self.rtPlotter.range_.get_range())

        # integrate
        res = integrator.integrate(mzmin, mzmax, intBegin, intEnd)
        area = res["area"]
        rmse = res["rmse"]
        intrts = res["intrts"]
        smoothed = res["smoothed"]

        # write values to ftable
        row[getIndex("method")] = method
        row[getIndex("intbegin")] = intBegin
        row[getIndex("intbegin")] = intEnd
        row[getIndex("area")] = area
        row[getIndex("rmse")] = rmse
        row[getIndex("intrts")] = intrts
        row[getIndex("smoothed")] = smoothed

        # format and write values to tableWidgetItems
        strIntBegin = ft.colFormatters[getIndex("intbegin")](intBegin)
        strIntEnd   = ft.colFormatters[getIndex("intend")](intEnd)
        strArea     = ft.colFormatters[getIndex("area")](area)
        strRmse     = ft.colFormatters[getIndex("rmse")](rmse)

        self.tw.item(widgetRowIdx, getIndex("intbegin")).setText(strIntBegin)
        self.tw.item(widgetRowIdx, getIndex("intend")).setText(strIntEnd)
        self.tw.item(widgetRowIdx, getIndex("method")).setText(method)
        self.tw.item(widgetRowIdx, getIndex("area")).setText(strArea)
        self.tw.item(widgetRowIdx, getIndex("rmse")).setText(strRmse)

        # plot result
        self.rtPlotter.plot(smoothed, x=intrts, index=1)
        self.rtPlotter.replot()
            

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


    def setRowBold(self, rowIdx, bold=True):

        for i in range(self.tw.columnCount()):
            item = self.tw.item(rowIdx,i)
            font = item.font()
            font.setBold(bold)
            item.setFont(font)

    def rowClicked(self, rowIdx):
        
        if self.lastRow is not None:
            self.setRowBold(self.lastRow, bold=False)

        self.setRowBold(rowIdx, bold=True)
        self.lastRow = rowIdx

        realIdx = self.tw.item(rowIdx, 0).idx # trotz umsortierung !
        ft = self.ftable 
        getIndex = ft.getIndex

        self.currentRow = self.ftable[realIdx]

        mzmin = self.ftable[realIdx][getIndex("mzmin")]
        mzmax = self.ftable[realIdx][getIndex("mzmax")]

        peaks = [ spec.peaks[ (spec.peaks[:,0] >= mzmin) * (spec.peaks[:,0] <= mzmax) ] for spec in ft.ds.specs ]

        chromatogram = [ np.sum(peak[:,1]) for peak in peaks ]
        self.rtPlotter.plot(chromatogram)

        if self.integratedFeatures:
            intrts = ft.rows[realIdx][getIndex("intrts")]
            smoothed = ft.rows[realIdx][getIndex("smoothed")]
            self.rtPlotter.plot(smoothed, x=intrts, index=1)
            self.intBeginItem = self.tw.item(rowIdx, getIndex("intbegin"))
            self.intEndItem = self.tw.item(rowIdx, getIndex("intend"))
            self.methodtem = self.tw.item(rowIdx, getIndex("method"))
            method = ft.rows[realIdx][getIndex("method")]
            ix = self.chooseIntMethod.findText(method)
            if ix<0: 
                print "INTEGRATOR NOT AVAILABLE"
            else:
                self.chooseIntMethod.setCurrentIndex(ix)
            intbegin = self.ftable[realIdx][getIndex("intbegin")]
            intend = self.ftable[realIdx][getIndex("intend")]
            self.rtPlotter.setRangeSelectionLimits(intbegin, intend)
        else:
            rtmin = self.ftable[realIdx][getIndex("rtmin")]
            rtmax = self.ftable[realIdx][getIndex("rtmax")]
            self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)
            

        self.rtPlotter.setXAxisLimits(0, self.maxRT)
        self.rtPlotter.replot()

        

def inspectFeatures(ftable):

    app = guidata.qapplication()
    fe = FeatureExplorer(ftable)
    fe.raise_()
    fe.exec_()
