# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata

from PlottingWidgets import RtPlotter, MzPlotter

import sys
import numpy as np
import configs
import pprint
import os

from ..DataStructures.Table import Table

def widthOfTableWidget(tw):

    width = 0
    for i in range(tw.columnCount()):
        width += tw.columnWidth(i)

    width += tw.verticalHeader().sizeHint().width()
    width += tw.verticalScrollBar().sizeHint().width()
    width += tw.frameWidth()*2
    return width

class ValuedQTableWidgetItem(QTableWidgetItem):

    """ using this sublcass allows sorting columns in QTableWidget based on
        their numerical value
    """

    def __init__(self, rowIndex, value, *a, **kw):
        super(ValuedQTableWidgetItem, self).__init__(*a, **kw)
        self.rowIndex = rowIndex
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


def populateTableWidget(tWidget, table):
    assert isinstance(table, Table)

    tWidget.clear()
    tWidget.setRowCount(len(table))

    headers = table.getVisibleCols()
    tWidget.setColumnCount(len(headers))
    tWidget.setHorizontalHeaderLabels(headers)

    colidxmap = dict((name, i) for i, name in enumerate(headers))

    tableColToWidgetCol = dict()
    i = 0
    for j in range(len(table.colNames)):
        if table.colFormatters[j] is not None:
            tableColToWidgetCol[j] = i
            i+=1

    widgetColToTableCol = dict( (v,k) for k,v in tableColToWidgetCol.items() )

    tWidget.setSortingEnabled(False)  # needs to be done before filling the table

    for i, row in enumerate(table.rows):
        tWidget.setVerticalHeaderItem(i, QTableWidgetItem("  "))
        for value, formatter, type_, colName in zip(row, table.colFormatters,
                                               table.colTypes, table.colNames):
            tosee = formatter(value)
            if tosee is not None:
                item = ValuedQTableWidgetItem(i, value, tosee)
                if len(tosee)>50:
                    item.setSizeHint(QSize(50,-1))

                flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
                if table.isEditable(colName):
                    flags |= Qt.ItemIsEditable
                item.setFlags(flags)
                if type_ == float or type_ == int:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                font = item.font()
                font.setFamily("Courier")
                if type_ == str and tosee.startswith("http://"):
                    font.setUnderline(True)
                item.setFont(font)
                j = colidxmap[colName]
                tWidget.setItem(i, j, item)

    tWidget.setSortingEnabled(True)
    # adjust height of rows (normaly reduces size to a reasonable value)
    tWidget.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
    return colidxmap, tableColToWidgetCol, widgetColToTableCol

class TableExplorer(QDialog):

    def __init__(self, table):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.Window)

        self.hasFeatures = table.hasColumns("mz", "mzmin", "mzmax", "rt",
                                            "rtmin", "rtmax", "peakmap")

        self.isIntegrated = self.hasFeatures and \
                            table.hasColumns("area", "rmse", "intbegin",
                                             "intend")

        self.table = table
        if self.hasFeatures:
            peakmaps = set(table.getColumn("peakmap").values)
            assert len(peakmaps) == 1
            self.peakmap = peakmaps.pop()
            self.levelOneRts = list(self.peakmap.levelOneRts())
            self.maxRt = max(self.levelOneRts)
        else:
            self.peakmap = None

        self.setupWidgets()
        self.setupLayout()
        self.populateTable()
        self.setWindowSize() # depends on table size
        self.connectSignals()

        if table.title:
            title = table.title
        else:
            title = os.path.basename(table.meta.get("source",""))
        if self.hasFeatures:
            title += " aligned=%s" % table.meta.get("aligned", "False")
        self.setWindowTitle(title)

        if self.hasFeatures:
            self.plotMz()

        self.setMinimumHeight(600)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

    def populateTable(self):
        self.colIdxMap, self.tableColToWidgetCol, self.widgetColToTableCol\
                                      = populateTableWidget(self.tw, self.table)
        idcol = self.colIdxMap.get("id", 0)
        self.tw.sortByColumn(idcol, Qt.AscendingOrder)

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
        self.setMinimumWidth(widthOfTableWidget(self.tw))
        self.tw.setMinimumHeight(150)

    def setupLayout(self):
        vlayouto = QVBoxLayout()
        self.setLayout(vlayouto)

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.setOpaqueResize(False)

        if self.hasFeatures:

            hsplitter = QSplitter()
            hsplitter.setOpaqueResize(False)
            hsplitter.addWidget(self.rtPlotter.widget)

            if self.isIntegrated:
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

        vlayouto.addWidget(vsplitter)

    def setupWidgets(self):

        if self.hasFeatures:

            plotconfigs = (None, dict(shade=0.35, linewidth=1, color="g") )
            self.rtPlotter = RtPlotter(rangeSelectionCallback=self.plotMz,
                                       numCurves=2, configs=plotconfigs)

            rts = [ spec.rt for spec in self.peakmap ]
            self.rtPlotter.setRtValues(rts)

            self.mzPlotter = MzPlotter(self.peakmap)

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


        if self.isIntegrated:
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

    def connectSignals(self):
        # click at row head
        self.connect(self.tw.verticalHeader(), SIGNAL("sectionClicked(int)"),
                     self.rowClicked)
        # click at cell
        self.connect(self.tw, SIGNAL("cellClicked(int, int)"),
                     self.cellClicked)
        self.connect(self.tw, SIGNAL("cellChanged(int, int)"),
                     self.cellChanged)

    def intMethodChanged(self, i):
        pass

    def doIntegrate(self):

        widgetRowIdx = self.tw.currentRow()
        if widgetRowIdx < 0:
            return


        # setup integrator
        method = str(self.chooseIntMethod.currentText()) # conv from qstring
        integrator = dict(configs.peakIntegrators)[method]
        integrator.setPeakMap(self.peakmap)

        # get eic limits
        # rowidx may be different to widgets row index due to sorting:
        row = self.table.rows[self.tw.item(widgetRowIdx, 0).rowIndex]
        mzmin = self.table.get(row, "mzmin")
        mzmax = self.table.get(row, "mzmax")
        intBegin, intEnd = sorted(self.rtPlotter.range_.get_range())

        # integrate
        res = integrator.integrate(mzmin, mzmax, intBegin, intEnd)
        area = res["area"]
        rmse = res["rmse"]
        params = res["params"]
        intrts, smoothed = integrator.getSmoothed(self.levelOneRts, params)

        # write values to table
        t = self.table
        self.table.set(row, "method", method)
        self.table.set(row, "intbegin", intBegin)
        self.table.set(row, "intend", intEnd)
        self.table.set(row, "area", area)
        self.table.set(row, "rmse", rmse)
        self.table.set(row, "params", params)


        # format and write values to tableWidgetItems
        ft = self.table
        strIntBegin = ft.get(ft.colFormatters, "intbegin")(intBegin)
        strIntEnd   = ft.get(ft.colFormatters, "intend")(intEnd)
        strArea     = ft.get(ft.colFormatters, "area")(area)
        strRmse     = ft.get(ft.colFormatters, "rmse")(rmse)

        self.tw.item(widgetRowIdx, self.colIdxMap["intbegin"]).setText(strIntBegin)
        self.tw.item(widgetRowIdx, self.colIdxMap["intend"]).setText(strIntEnd)
        self.tw.item(widgetRowIdx, self.colIdxMap["method"]).setText(method)
        self.tw.item(widgetRowIdx, self.colIdxMap["area"]).setText(strArea)
        self.tw.item(widgetRowIdx, self.colIdxMap["rmse"]).setText(strRmse)

        # plot result
        self.rtPlotter.plot(smoothed, x=intrts, index=1)
        self.rtPlotter.replot()

    def plotMz(self):
        minRt=self.rtPlotter.minRTRangeSelected
        maxRt=self.rtPlotter.maxRTRangeSelected
        pm = self.peakmap
        peaks = [s.peaks for s in pm.levelOneSpecsInRange(minRt, maxRt)]
        if len(peaks):
            peaks = np.vstack(peaks)
            self.mzPlotter.plot(peaks)
            self.mzPlotter.replot()

    def cellChanged(self, rowIdx, colIdx):
        return
        print "changed"
        item = self.tw.currentItem()
        print item.text()
        newvalue = item.text()
        coltype = self.table.colTypes[colIdx]
        tableColIdx = self.widgetColToTableCol[colIdx]
        print colIdx, tableColIdx
        try:
            newvalue = coltype(newvalue)
        except:
            guidata.qapplication().beep()
            # reset content
            data = self.table.rows[item.rowIndex][tableColIdx]
            fmt  = self.table.colFormatters[tableColIdx]
            item.setText(fmt(data))
            return
        item.value = newvalue
        print item.rowIndex, self.colNames[tableColIdx], newvalue
        self.table.rows[item.rowIndex][tableColIdx] =newvalue

    def cellClicked(self, rowIdx, colIdx):
        name = self.table.colNames[colIdx]
        item = self.tw.currentItem()
        if 0 and self.table.isEditable(name):
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.oldtext = item.text()
            self.tw.editItem(item)
            return

        getIndex = self.table.getIndex
        # trotz umsortierung :
        row = self.table.rows[item.rowIndex]

        if type(item.value) == str and item.value.startswith("http://"):
            url = QUrl(item.value, QUrl.TolerantMode)
            QDesktopServices.openUrl(url)
            return

        if self.hasFeatures:
            if name.startswith("mz"):
                mzmin = row[getIndex("mzmin")]
                mzmax = row[getIndex("mzmax")]
                self.mzPlotter.setXAxisLimits(mzmin-0.002, mzmax+0.002)

                # update y-range
                minRt = self.rtPlotter.minRTRangeSelected
                maxRt = self.rtPlotter.maxRTRangeSelected
                spectra = self.peakmap.levelOneSpecsInRange(minRt, maxRt)
                peaks = [s.peaks[(s.peaks[:,0] >= mzmin) * (s.peaks[:,0] <= mzmax)]
                         for s in self.peakmap]
                peaks = np.vstack(peaks)
                if len(peaks)>0:
                    maxIntensity =  max(peaks[:,1])
                    self.mzPlotter.setYAxisLimits(0, maxIntensity*1.1)

            elif name.startswith("rtm"):  # rtmin or rtmax
                rtmin = row[getIndex("rtmin")]
                rtmax = row[getIndex("rtmax")]
                self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)
                self.rtPlotter.replot()

            elif name.startswith("rt"):  #  rt
                rt= row[getIndex("rt")]
                self.rtPlotter.setRangeSelectionLimits(rt, rt)
                self.rtPlotter.replot()

    def setRowBold(self, rowIdx, bold=True):
        for i in range(self.tw.columnCount()):
            item = self.tw.item(rowIdx,i)
            font = item.font()
            font.setBold(bold)
            item.setFont(font)

    def rowClicked(self, rowIdx):
        realIdx = self.tw.item(rowIdx, 0).rowIndex # trotz umsortierung !
        getIndex = self.table.getIndex

        row = self.table.rows[realIdx]

        if self.hasFeatures:
            mzmin = row[getIndex("mzmin")]
            mzmax = row[getIndex("mzmax")]

            spectra = [s for s in self.peakmap if s.msLevel == 1]
            chromatogram = [s.intensityInRange(mzmin, mzmax) for s in spectra]
            self.rtPlotter.plot(chromatogram, x=self.levelOneRts)
            rtmin = row[getIndex("rtmin")]
            rtmax = row[getIndex("rtmax")]
            self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)
            w = rtmax - rtmin
            self.rtPlotter.setXAxisLimits(rtmin -w, rtmax + w)

            if self.isIntegrated:

                method = str(row[getIndex("method")]) # qstring -> python string
                integrator = dict(configs.peakIntegrators)[method]

                params = row[getIndex("params")]
                intrts, smoothed = integrator.getSmoothed(self.levelOneRts,
                                                          params)

                self.rtPlotter.plot(smoothed, x=intrts, index=1)
                ix = self.chooseIntMethod.findText(method)
                if ix<0:
                    print "INTEGRATOR NOT AVAILABLE"
                else:
                    self.chooseIntMethod.setCurrentIndex(ix)
                intbegin = row[getIndex("intbegin")]
                intend = row[getIndex("intend")]
                self.rtPlotter.setRangeSelectionLimits(intbegin, intend)
                w = intend - intbegin 
                self.rtPlotter.setXAxisLimits(intbegin -w, intend + w)

            #self.rtPlotter.setXAxisLimits(0, self.maxRt)
            self.rtPlotter.replot()

def inspect(table):
    app = guidata.qapplication()
    fe = TableExplorer(table)
    fe.raise_()
    fe.exec_()