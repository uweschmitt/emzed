# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata

from PlottingWidgets import RtPlotter, MzPlotter

import numpy as np
import configs
import os

class TableAction(object):

    actionName = None

    def __init__(self, model, **kw):
        self.model = model
        self.args = kw
        self.__dict__.update(kw)
        self.memory = None

    def undo(self):
        assert self.memory != None

    def beginDelete(self, idx, idx2=None):
        if idx2 is None:
            idx2 = idx
        self.model.beginRemoveRows(QModelIndex(), idx, idx2)

    def endDelete(self):
        self.model.endRemoveRows()

    def beginInsert(self, idx, idx2=None):
        if idx2 is None:
            idx2 = idx
        self.model.beginInsertRows(QModelIndex(), idx, idx2)

    def endInsert(self):
        self.model.endInsertRows()

    def __str__(self):
        args = ", ".join("%s: %s" % it for it in self.args.items())
        return "%s(%s)" % (self.actionName, args)



class DeleteRowAction(TableAction):

    actionName = "delete row"

    def __init__(self, model, idx):
        super(DeleteRowAction, self).__init__(model, idx=idx)

    def do(self):
        self.beginDelete(self.idx)
        table = self.model.table
        self.memory = table.rows[self.idx][:]
        del table.rows[self.idx]
        self.endDelete()
        return True

    def undo(self):
        super(DeleteRowAction, self).undo()
        table = self.model.table
        self.beginInsert(self.idx)
        table.rows.insert(self.idx, self.memory)
        self.endInsert()


class CloneRowAction(TableAction):

    actionName = "clone row"

    def __init__(self, model, idx):
        super(CloneRowAction, self).__init__(model, idx=idx)

    def do(self):
        self.beginInsert(self.idx+1)
        table = self.model.table
        table.rows.insert(self.idx+1, table.rows[self.idx][:])
        self.memory = True
        self.endInsert()
        return True

    def undo(self):
        super(CloneRowAction, self).undo()
        table = self.model.table
        self.beginDelete(self.idx+1)
        del table.rows[self.idx+1]
        self.endDelete()

class SortTableAction(TableAction):

    actionName = "sort table"

    def __init__(self, model, colIdx, order):
        super(SortTableAction, self).__init__(model, colIdx=colIdx,\
                                        order=order)

    def do(self):
        table = self.model.table
        ascending = self.order == Qt.AscendingOrder
        colName = table.colNames[self.colIdx]
        # memory is the permutation which sorted the table rows
        # sortBy returns this permutation:
        self.memory = table.sortBy(colName, ascending)
        self.model.reset()
        return True

    def undo(self):
        super(SortTableAction, self).undo()
        table = self.model.table
        # calc inverse permuation:
        decorated = [ (self.memory[i], i) for i in range(len(self.memory))]
        decorated.sort()
        invperm = [i for (_, i) in decorated]
        table.applyRowPermutation(invperm)
        self.model.reset()


class ChangeValueAction(TableAction):

    actionName = "change value"

    def __init__(self, model, idx, dataColIdx, value):
        super(ChangeValueAction, self).__init__(model, idx=idx,\
                                                dataColIdx=dataColIdx,\
                                                value=value)

    def do(self):
        table = self.model.table
        row = table.rows[self.idx.row()]
        self.memory = row[self.dataColIdx]
        if self.memory == self.value: return False
        row[self.dataColIdx] = self.value
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),\
                        self.idx, self.idx)
        return True

    def undo(self):
        super(ChangeValueAction, self).undo()
        table = self.model.table
        table.rows[self.idx.row()][self.dataColIdx] = self.memory
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),\
                        self.idx, self.idx)

class IntegrateAction(TableAction):

    actionName = "integrate"

    def __init__(self, model, idx, method, rtmin, rtmax):
        super(IntegrateAction, self).__init__(model, idx=idx, method=method,
                                        rtmin=rtmin, rtmax=rtmax, )

    def do(self):
        integrator = dict(configs.peakIntegrators)[self.method]
        table = self.model.table
        # returns Bunch
        args = table.get(table.rows[self.idx], None)
        integrator.setPeakMap(args.peakmap)

        # integrate
        res = integrator.integrate(args.mzmin, args.mzmax, self.rtmin, self.rtmax)
        area = res["area"]
        rmse = res["rmse"]
        params = res["params"]

        # var 'row' is a Bunch, so we have to get the row from direct access
        # to table.rows:
        self.memory = table.rows[self.idx][:]

        # write values to table

        row = table.rows[self.idx]
        table.set(row, "method", self.method)
        table.set(row, "rtmin", self.rtmin)
        table.set(row, "rtmax", self.rtmax)
        table.set(row, "area", area)
        table.set(row, "rmse", rmse)
        table.set(row, "params", params)
        self.notifyGUI()
        return True

    def undo(self):
        super(IntegrateAction, self).undo()
        table = self.model.table
        table.rows[self.idx] = self.memory
        self.notifyGUI()

    def notifyGUI(self):
        tl = self.model.createIndex(self.idx, 0)
        tr = self.model.createIndex(self.idx, self.model.columnCount()-1)
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), tl, tr)


class TableModel(QAbstractTableModel):

    LIGHT_BLUE = QColor(200, 200, 255)
    WHITE = QColor(255, 255, 255)

    def __init__(self, table, parent, dialog):
        super(TableModel, self).__init__(parent)
        self.table = table
        self.parent = parent
        self.dialog = dialog
        nc = len(self.table.colNames)
        indizesOfVisibleCols = (j for j in range(nc)\
                                  if self.table.colFormats[j] is not None)
        self.widgetColToDataCol = dict(enumerate(indizesOfVisibleCols))
        self.emptyActionStack()

        self.nonEditables=set()

    def setNonEditables(self, dataColIndices):
        self.nonEditables = dataColIndices

    def emptyActionStack(self):
        self.actions = []
        self.redoActions = []

    def getRow(self, idx):
        return self.table.get(self.table.rows[idx], None)

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
        if self.widgetColToDataCol[index.column()] in self.nonEditables:
            return default
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
                except Exception:
                    guidata.qapplication().beep()
                    return False
            self.runAction(ChangeValueAction, index, dataIdx, value)
            return True
        return False

    def runAction(self, clz, *a):
        action = clz(self, *a)
        done = action.do()
        if not done:
            return
        self.actions.append(action)
        self.redoActions = []
        self.dialog.updateMenubar()

    def infoLastAction(self):
        if len(self.actions):
            return self.actions[-1].actionName
        return None

    def infoRedoAction(self):
        if len(self.redoActions):
            return self.redoActions[-1].actionName
        return None

    def undoLastAction(self):
        if len(self.actions):
            action = self.actions.pop()
            action.undo()
            self.redoActions.append(action)
            self.dialog.updateMenubar()
            return
        raise Exception("no action to be undone")

    def redoLastAction(self):
        if len(self.redoActions):
            action = self.redoActions.pop()
            action.do()
            self.actions.append(action)
            self.dialog.updateMenubar()
            return
        raise Exception("no action to be redone")


    def cloneRow(self, position):
        self.runAction(CloneRowAction, position)
        return True

    def removeRow(self, position):
        self.runAction(DeleteRowAction, position)
        return True

    def sort(self, colIdx, order=Qt.AscendingOrder):
        self.runAction(SortTableAction, colIdx, order)

    def integrate(self, idx, method, rtmin, rtmax):
        self.runAction(IntegrateAction, idx, method, rtmin, rtmax)


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
            self.model.emptyActionStack()
            self.updateMenubar()

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.setOpaqueResize(False)

        vsplitter.addWidget(self.menubar)
        #qf = QFrame(self)
        #qf.setFrameShape(QFrame.HLine)
        #vsplitter.addWidget(qf)

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


    def updateMenubar(self):
        undoInfo = self.model.infoLastAction()
        redoInfo = self.model.infoRedoAction()
        self.undoAction.setEnabled(undoInfo != None)
        self.redoAction.setEnabled(redoInfo != None)
        if undoInfo:
            self.undoAction.setText("Undo: %s" % undoInfo)
        if redoInfo:
            self.redoAction.setText("Redo: %s" % redoInfo)

    def setupWidgets(self):
        self.tableView = QTableView(self)
        self.model = TableModel(self.table, parent=self.tableView, dialog=self)

        self.menubar = QMenuBar(self)
        self.undoAction = QAction("Undo", self)
        self.undoAction.setShortcut(QKeySequence("Ctrl+Z"))
        self.menubar.connect(self.undoAction, SIGNAL("triggered()"), self.model.undoLastAction)
        menu = QMenu("Edit", self.menubar)
        menu.addAction(self.undoAction)

        self.redoAction = QAction("Redo", self)
        self.redoAction.setShortcut(QKeySequence("Ctrl+Y"))
        self.menubar.connect(self.redoAction, SIGNAL("triggered()"), self.model.redoLastAction)
        menu.addAction(self.redoAction)
        self.menubar.addMenu(menu)
        self.menu = menu

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
            noneditables=["method"]
            self.model.setNonEditables([self.model.table.getIndex(nonedit)
                                        for nonedit in noneditables])

        if self.offerAbortOption:
            self.okButton = QPushButton("Ok")
            self.abortButton = QPushButton("Abort")
            self.connect(self.okButton, SIGNAL("clicked()"), self.ok)
            self.connect(self.abortButton, SIGNAL("clicked()"), self.abort)
            self.result = 1 # default for closing

    def dataChanged(self, ix1, ix2):
        if self.hasFeatures:
            minr, maxr = sorted((ix1.row(), ix2.row()))
            if minr <= self.currentRow <= maxr:
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
        undoInfo = self.model.infoLastAction()
        redoInfo = self.model.infoRedoAction()

        if undoInfo is not None:
            undoAction = menu.addAction("Undo %s" % undoInfo)
        if redoInfo is not None:
            redoAction = menu.addAction("Redo %s" % redoInfo)
        action = menu.exec_(self.tableView.verticalHeader().mapToGlobal(point))
        if action == removeAction:
            self.model.removeRow(idx)
        elif action == cloneAction:
            self.model.cloneRow(idx)
        elif undoInfo is not None and action == undoAction:
            self.model.undoLastAction()
        elif redoInfo is not None and action == redoAction:
            self.model.redoLastAction()

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

        rtmin, rtmax = self.rtPlotter.getRangeSelectionLimits()
        self.model.integrate(self.currentRow, method, rtmin, rtmax)
        self.updateMenubar()


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

        chromatogram = [s.intensityInRange(mzmin, mzmax)\
                        for s in self.currentL1Spectra]

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
        self.rtPlotter.replot()

def inspect(table, offerAbortOption=False):
    app = guidata.qapplication()
    explorer = TableExplorer(table, offerAbortOption)
    explorer.raise_()
    explorer.exec_()
    if offerAbortOption:
        if explorer.result == 1:
            raise Exception("Dialog aborted by user")
