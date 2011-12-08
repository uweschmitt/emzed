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


class TableModel(QAbstractTableModel):

    LIGHT_BLUE = QColor(200, 200, 255)
    WHITE = QColor(255, 255, 255)

    def __init__(self, table, parent):
        super(TableModel, self).__init__(parent)
        self.table = table
        self.parent = parent
        nc = len(self.table.colNames)
        indizesOfVisibleCols = (j for j in range(nc)\
                                  if self.table.colFormats[j] is not None)
        self.widgetColToDataCol = dict(enumerate(indizesOfVisibleCols))
        self.savedRows = list()
        self.activeRow = None

    def getRow(self, idx):
        return self.table.get(self.table.rows[idx], None)

    def set(self, idx, name, value):
        self.table.set(self.table.rows[idx], name, value)

    def hasSavedRows(self):
        return len(self.savedRows) > 0

    def rowCount(self, index=QModelIndex()):
        return len(self.table)

    def columnCount(self, index=QModelIndex()):
        return len(self.widgetColToDataCol)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.table)):
            return QVariant()
        cidx = self.widgetColToDataCol[index.column()]
        value = self.table.rows[index.row()][cidx]
        shown =  self.table.colFormatters[cidx](value)
        if role == Qt.DisplayRole:
            return shown
        if role == Qt.EditRole:
            colType = self.table.colTypes[cidx]
            if colType in [int, float, str]:
                if shown.strip().endswith("m"):
                    return shown
                try:
                    colType(shown)
                    return shown
                except:
                    if colType == float:
                        return "%.4f" % value
                    return str(value)
            return str(value)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            dataIdx = self.widgetColToDataCol[section]
            return self.table.colNames[dataIdx]
        # vertical header:
        return QString("   ")

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        default = super(TableModel, self).flags(index)
        return Qt.ItemFlags(default | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.table):
            dataIdx = self.widgetColToDataCol[index.column()]
            expectedType = self.table.colTypes[dataIdx]
            if expectedType != object:
                # QVariant -> QString -> str + strip:
                value = str(value.toString()).strip()
                if value.endswith("m"): # minutes
                    value = 60.0 * float(value[:-1])
                try:
                    value = expectedType(value)
                except Exception, e:
                    guidata.qapplication().beep()
                    return False
            self.table.rows[index.row()][dataIdx] = value
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,\
                                                                     index)
            return True
        return False

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows -1)
        self.table.rows.insert(position+1, self.table.rows[position][:])
        self.endInsertRows()
        return True

    def undoLastDeletion(self, position):
        self.beginInsertRows(QModelIndex(), position, position)
        self.table.rows.insert(position+1, self.savedRows.pop())
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.savedRows.append(self.table.rows[position])
        del self.table.rows[position]
        self.endRemoveRows()
        if position == self.activeRow:
            self.activeRow = None
        return True

    def sort(self, colIdx, order=Qt.AscendingOrder):
        dataIdx = self.widgetColToDataCol[colIdx]
        self.table.sortBy(self.table.colNames[dataIdx],\
                          ascending= (order==Qt.AscendingOrder))
        self.reset()


class TableExplorer(QDialog):

    def __init__(self, table, offerAbortOption):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.Window)

        self.hasFeatures = table.hasColumns("mz", "mzmin", "mzmax", "rt",
                                            "rtmin", "rtmax", "peakmap")

        self.isIntegrated = self.hasFeatures and \
                            table.hasColumns("area", "rmse")
        self.table = table
        self.offerAbortOption = offerAbortOption
        self.currentRow = -1

        if table.title:
            title = table.title
        else:
            title = os.path.basename(table.meta.get("source",""))
        if self.hasFeatures:
            title += " aligned=%s" % table.meta.get("aligned", "False")
        self.setWindowTitle(title)

        self.setupWidgets()
        self.connectSignals()
        self.setupLayout()

        #self.setMinimumHeight(600)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

    def paintEvent(self, *a):
        super(TableExplorer, self).paintEvent(*a)
        # now the table is filled ! (and painted)
        # enabling sort befor filling the table results in much slower
        # filling,
        if not self.tableView.isSortingEnabled():
            self.tableView.setSortingEnabled(True)
            self.tableView.resizeColumnsToContents()

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.setOpaqueResize(False)

        if self.hasFeatures:

            hsplitter = QSplitter()
            hsplitter.setOpaqueResize(False)
            hsplitter.addWidget(self.rtPlotter.widget)

            
            if self.isIntegrated:
                vlayout2 = QVBoxLayout()
                vlayout2.setSpacing(10)
                vlayout2.setMargin(5)
                vlayout2.addWidget(self.intLabel)
                vlayout2.addWidget(self.chooseIntMethod)
                vlayout2.addWidget(self.reintegrateButton)
                vlayout2.addStretch()
                vlayout2.setAlignment(self.intLabel, Qt.AlignTop)
                vlayout2.setAlignment(self.chooseIntMethod, Qt.AlignTop)
                vlayout2.setAlignment(self.reintegrateButton, Qt.AlignTop)

                frame = QFrame()
                frame.setLayout(vlayout2)
                #frame.setFrameStyle(QFrame.StyledPanel)
                hsplitter.addWidget(frame)

            hsplitter.addWidget(self.mzPlotter.widget)

            vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(self.tableView)
        vlayout.addWidget(vsplitter)

        if self.offerAbortOption:
            hbox = QHBoxLayout()
            hbox.addWidget(self.abortButton)
            hbox.setAlignment(self.abortButton, Qt.AlignVCenter)
            hbox.addWidget(self.okButton)
            hbox.setAlignment(self.okButton, Qt.AlignVCenter)
            vlayout.addLayout(hbox)

    def setupWidgets(self):
        if self.hasFeatures:
            self.plotconfigs = (None, dict(shade=0.35, linewidth=1, color="g") )
            self.rtPlotter = RtPlotter(rangeSelectionCallback=self.plotMz)
            self.rtPlotter.setMinimumSize(300, 150)
            self.mzPlotter = MzPlotter()
            self.mzPlotter.setMinimumSize(300, 150)
            pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            pol.setVerticalStretch(5)
            self.rtPlotter.widget.setSizePolicy(pol)
            self.mzPlotter.widget.setSizePolicy(pol)



        self.tableView = QTableView(self)
        self.model = TableModel(self.table, parent=self.tableView)
        # disabling sort before filling the table results in much faster
        # setup. we enable sorting in self.paintEvent()
        self.tableView.setSortingEnabled(False)
        self.tableView.horizontalHeader().setResizeMode(QHeaderView.Interactive)
        # following is much faster than # self.tableView.resizeColumnsToContents():
        self.tableView.setModel(self.model)

        pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pol.setVerticalStretch(5)
        self.tableView.setSizePolicy(pol)

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

        if self.offerAbortOption:
            self.okButton = QPushButton("Ok")
            self.abortButton = QPushButton("Abort")
            self.connect(self.okButton, SIGNAL("clicked()"), self.ok)
            self.connect(self.abortButton, SIGNAL("clicked()"), self.abort)
            self.result = 1 # default for closing

    def dataChanged(self, ix1, ix2):
        row = ix1.row()
        col = ix1.column()
        if row == ix2.row() and col == ix2.column():
            if row == self.currentRow:
                self.updatePlots()

    def abort(self):
        self.result = 1
        self.close()

    def ok(self):
        self.result = 0
        self.close()

    def ctxMenu(self, point, *a):
        idx = self.tableView.verticalHeader().logicalIndexAt(point)
        menu = QMenu()
        cloneAction = menu.addAction("Clone row")
        removeAction = menu.addAction("Delete row")
        if self.model.hasSavedRows():
            undoAction = menu.addAction("Append last deleted row")
        action = menu.exec_(self.tableView.verticalHeader().mapToGlobal(point))
        if action == removeAction:
            self.model.removeRows(idx)
        elif action == cloneAction:
            self.model.insertRows(idx)
        elif self.model.hasSavedRows() and action == undoAction:
            self.model.undoLastDeletion(idx)

    def connectSignals(self):
        # click at row head

        self.tableView.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.tableView.verticalHeader(),\
                     SIGNAL("customContextMenuRequested(QPoint)"), self.ctxMenu)

        self.connect(self.tableView.verticalHeader(), SIGNAL("sectionClicked(int)"),
                     self.rowClicked)

        self.connect(self.model, SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     self.dataChanged)


    def intMethodChanged(self, i):
        pass


    def doIntegrate(self):
        if self.currentRow < 0:
            return # no row selected

        # setup integrator
        method = str(self.chooseIntMethod.currentText()) # conv from qstring
        integrator = dict(configs.peakIntegrators)[method]
        integrator.setPeakMap(self.currentPeakMap)

        row = self.model.getRow(self.currentRow)

        rtmin, rtmax = self.rtPlotter.getRangeSelectionLimits()

        # integrate
        res = integrator.integrate(row.mzmin, row.mzmax, rtmin, rtmax)
        area = res["area"]
        rmse = res["rmse"]
        params = res["params"]

        # write values to table
        t = self.table
        self.model.set(self.currentRow, "method", method)
        self.model.set(self.currentRow, "rtmin", rtmin)
        self.model.set(self.currentRow, "rtmax", rtmax)
        self.model.set(self.currentRow, "area", area)
        self.model.set(self.currentRow, "rmse", rmse)
        self.model.set(self.currentRow, "params", params)

        tl = self.model.createIndex(self.currentRow, 0)
        tr = self.model.createIndex(self.currentRow, self.model.columnCount()-1)
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), tl, tr)

        self.updatePlots()
        self.rtPlotter.replot()

    def plotMz(self):
        minRt=self.rtPlotter.minRTRangeSelected
        maxRt=self.rtPlotter.maxRTRangeSelected
        pm = self.currentPeakMap
        peaks = [s.peaks for s in pm.levelOneSpecsInRange(minRt, maxRt)]
        if len(peaks):
            peaks = np.vstack(peaks)
            self.mzPlotter.plot(peaks)
            self.mzPlotter.replot()


    def rowClicked(self, rowIdx):
        self.currentRow = rowIdx
        row = self.model.getRow(rowIdx)
        if self.hasFeatures:
            self.currentPeakMap = row.peakmap
            self.currentL1Spectra=  [spec for spec in row.peakmap if spec.msLevel == 1]
            self.currentRts = [spec.rt for spec in self.currentL1Spectra]
            self.updatePlots()
            rtmin = row.rtmin
            rtmax = row.rtmax
            w = rtmax - rtmin
            if w == 0:
                w = 30.0 # seconds
            self.rtPlotter.setXAxisLimits(rtmin -w, rtmax + w)
            if self.isIntegrated:
                ix = self.chooseIntMethod.findText(row.method)
                self.chooseIntMethod.setCurrentIndex(ix)

    def updatePlots(self):
        row = self.model.getRow(self.currentRow)
        mzmin = row.mzmin
        mzmax = row.mzmax
        rtmin = row.rtmin
        rtmax = row.rtmax
        peakmap = row.peakmap

        chromatogram = [s.intensityInRange(mzmin, mzmax) for s in self.currentL1Spectra]

        # get ppm from  centwave if present, else ppm=10 as default
        ppm = row.get("centwave_config", dict(ppm=10))["ppm"]
        w2 = row.mz * ppm * 1e-6 / 2.0
        self.mzPlotter.setXAxisLimits(row.mz - w2, row.mz + w2)
        maxchromo = max(s.intensityInRange(mzmin, mzmax) for s in self.currentL1Spectra if rtmin <= s.rt <=rtmax)

        self.mzPlotter.setYAxisLimits(0, maxchromo)

        curves = [ (self.currentRts, chromatogram) ]

        if self.isIntegrated:

            method = str(row.method) # qstring -> python string
            integrator = dict(configs.peakIntegrators)[method]

            intrts, smoothed = integrator.getSmoothed(self.currentRts, row.params)
            curves.append((intrts, smoothed))

        self.rtPlotter.plot(curves, self.plotconfigs)
        self.rtPlotter.setRangeSelectionLimits(rtmin, rtmax)

def inspect(table, offerAbortOption=False):
    app = guidata.qapplication()
    explorer = TableExplorer(table, offerAbortOption)
    explorer.raise_()
    explorer.exec_()
    if offerAbortOption:
        if explorer.result == 1:
            raise Exception("Dialog aborted by user")
