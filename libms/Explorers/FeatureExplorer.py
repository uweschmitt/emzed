# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

from ..gui import helpers
from PlottingWidgets import RtPlotter, MzPlotter

import sys
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
        self.stream.write(what)
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

        self.rows = self.ftable.rows

        self.integratedFeatures = "intbegin" in self.ftable.colNames

        self.ds = ftable.ds
        self.levelOneRts = list(ftable.ds.levelOneRts())
        self.maxRt = max(self.levelOneRts)

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

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.setOpaqueResize(False)

        hsplitter = QSplitter()
        hsplitter.setOpaqueResize(False)
        hsplitter.addWidget(self.rtPlotter.widget)

        if self.integratedFeatures:
            vlayout2 = QVBoxLayout()
            vlayout2.addWidget(self.intLabel)
            vlayout2.addWidget(self.chooseIntMethod)
            vlayout2.addWidget(self.reintegrateButton)
            vlayout2.addStretch()

            vlayout2.setSpacing(10)
            vlayout2.setMargin(5)
            vlayout2.setAlignment(self.intLabel, Qt.AlignTop)
            vlayout2.setAlignment(self.chooseIntMethod, Qt.AlignTop)
            vlayout2.setAlignment(self.reintegrateButton, Qt.AlignTop)

            frame = QFrame()
            frame.setLayout(vlayout2)
            hsplitter.addWidget(frame)
            
        hsplitter.addWidget(self.mzPlotter.widget)

        vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(self.tw)
        vsplitter.addWidget(self.statusMessages) 

        vlayouto.addWidget(vsplitter)

    def setupWidgets(self):
        plotconfigs = (None, dict(shade=0.35, linewidth=1, color="g") )
        self.rtPlotter = RtPlotter(rangeSelectionCallback=self.plotMz, 
                                   numCurves=2, configs=plotconfigs)

        rts = [ spec.rt for spec in self.ds.spectra ]
        self.rtPlotter.setRtValues(rts)

        self.mzPlotter = MzPlotter(self.ds)

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

        # click at row head
        self.connect(self.tw.verticalHeader(), SIGNAL("sectionClicked(int)"),
                     self.rowClicked)
        # click at cell
        self.connect(self.tw, SIGNAL("cellClicked(int, int)"), 
                     self.cellClicked)

        if self.integratedFeatures:
            self.intLabel = QLabel("Integration")
            self.chooseIntMethod = QComboBox()
            for name, _ in configs.peakIntegrators:
                self.chooseIntMethod.addItem(name)
            self.connect(self.chooseIntMethod, 
                         SIGNAL("currentIndexChanged(int)"), 
                         self.intMethodChanged)
            self.reintegrateButton = QPushButton()
            self.reintegrateButton.setText("Integrate")
            self.connect(self.reintegrateButton, SIGNAL("clicked()"), 
                         self.doIntegrate)

    def intMethodChanged(self, i):
        print configs.peakIntegrators[i][1], "chosen"

    def doIntegrate(self):
        if not self.integratedFeatures:
            return

        widgetRowIdx = self.tw.currentRow()
        if widgetRowIdx < 0:
            return

        getIndex = self.ftable.getIndex

        # setup integrator
        method = str(self.chooseIntMethod.currentText()) # conv from qstring
        integrator = dict(configs.peakIntegrators)[method] 
        integrator.setPeakMap(self.ds)

        # get eic limits
        # rowidx may be different to widgets row index due to sorting:
        row = self.rows[self.tw.item(widgetRowIdx, 0).idx] 
        mzmin = row[getIndex("mzmin")]
        mzmax = row[getIndex("mzmax")]
        intBegin, intEnd = sorted(self.rtPlotter.range_.get_range())

        # integrate
        res = integrator.integrate(mzmin, mzmax, intBegin, intEnd)
        area = res["area"]
        rmse = res["rmse"]
        params = res["params"]
        intrts, smoothed = integrator.getSmoothed(self.levelOneRts, params)

        # write values to ftable
        row[getIndex("method")] = method
        row[getIndex("intbegin")] = intBegin
        row[getIndex("intend")] = intEnd
        row[getIndex("area")] = area
        row[getIndex("rmse")] = rmse
        row[getIndex("params")] = params

        # format and write values to tableWidgetItems
        ft = self.ftable
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
        minRt=self.rtPlotter.minRTRangeSelected
        maxRt=self.rtPlotter.maxRTRangeSelected
        ds = self.ds
        peaks = [spec.peaks for spec in ds.levelOneSpecsInRange(minRt, maxRt)]
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
            mzmin = self.rows[realIdx][getIndex("mzmin")]
            mzmax = self.rows[realIdx][getIndex("mzmax")]
            self.mzPlotter.setXAxisLimits(mzmin-0.002, mzmax+0.002)

            # update y-range
            minRt = self.rtPlotter.minRTRangeSelected
            maxRt = self.rtPlotter.maxRTRangeSelected
            spectra = self.ds.levelOneSpecsInRange(minRt, maxRt)
            peaks = [s.peaks[(s.peaks[:,0] >= mzmin) * (s.peaks[:,0] <= mzmax)]
                     for s in self.ds.spectra ]
            peaks = np.vstack(peaks)
            if len(peaks)>0:            
                maxIntensity =  max(peaks[:,1])
                self.mzPlotter.setYAxisLimits(0, maxIntensity*1.1)

        elif name.startswith("rtm"):  # rtmin or rtmax
            rtmin = self.rows[realIdx][getIndex("rtmin")]
            rtmax = self.rows[realIdx][getIndex("rtmax")]
            self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)
            self.rtPlotter.replot()

        elif name.startswith("rt"):  #  rt
            rt= self.rows[realIdx][getIndex("rt")]
            self.rtPlotter.setRangeSelectionLimits(rt, rt)
            self.rtPlotter.replot()

    def setRowBold(self, rowIdx, bold=True):
        for i in range(self.tw.columnCount()):
            item = self.tw.item(rowIdx,i)
            font = item.font()
            font.setBold(bold)
            item.setFont(font)

    def rowClicked(self, rowIdx):
        realIdx = self.tw.item(rowIdx, 0).idx # trotz umsortierung !
        getIndex = self.ftable.getIndex

        row = self.rows[realIdx]

        mzmin = row[getIndex("mzmin")]
        mzmax = row[getIndex("mzmax")]

        spectra = [s for s in self.ds.spectra if s.msLevel == 1]
        chromatogram = [ s.intensityInRange(mzmin, mzmax) for s in spectra ]
        self.rtPlotter.plot(chromatogram, x=self.levelOneRts)

        if self.integratedFeatures:

            method = str(row[getIndex("method")]) # qstring -> python string
            integrator = dict(configs.peakIntegrators)[method] 

            params = row[getIndex("params")]
       
            intrts, smoothed = integrator.getSmoothed(self.levelOneRts, params)

            self.rtPlotter.plot(smoothed, x=intrts, index=1)
            ix = self.chooseIntMethod.findText(method)
            if ix<0: 
                print "INTEGRATOR NOT AVAILABLE"
            else:
                self.chooseIntMethod.setCurrentIndex(ix)
            intbegin = row[getIndex("intbegin")]
            intend = row[getIndex("intend")]
            self.rtPlotter.setRangeSelectionLimits(intbegin, intend)
        else:
            rtmin = row[getIndex("rtmin")]
            rtmax = row[getIndex("rtmax")]
            self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)

        self.rtPlotter.setXAxisLimits(0, self.maxRt)
        self.rtPlotter.replot()

def inspectFeatures(ftable):
    import guidata
    app = guidata.qapplication()
    try:
        fe = FeatureExplorer(ftable)
        fe.raise_()
        fe.exec_()
    except:
        # fix stdout and stderr if explorer
        # terminates not clearly
        import sys
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
