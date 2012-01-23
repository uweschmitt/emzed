# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata

import configs
import os
import re

def isUrl(what):
    return what.startswith("http://")

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
        args = ", ".join("%s: %s" % it for it in self.toview.items())
        return "%s(%s)" % (self.actionName, args)

class DeleteRowAction(TableAction):

    actionName = "delete row"

    def __init__(self, model, rowIdx):
        super(DeleteRowAction, self).__init__(model, rowIdx=rowIdx)
        self.toview = dict(row = rowIdx)

    def do(self):
        self.beginDelete(self.rowIdx)
        table = self.model.table
        self.memory = table.rows[self.rowIdx][:]
        del table.rows[self.rowIdx]
        self.endDelete()
        return True

    def undo(self):
        super(DeleteRowAction, self).undo()
        table = self.model.table
        self.beginInsert(self.rowIdx)
        table.rows.insert(self.rowIdx, self.memory)
        self.endInsert()

class CloneRowAction(TableAction):

    actionName = "clone row"

    def __init__(self, model, rowIdx):
        super(CloneRowAction, self).__init__(model, rowIdx=rowIdx)
        self.toview = dict(row = rowIdx)

    def do(self):
        self.beginInsert(self.rowIdx+1)
        table = self.model.table
        table.rows.insert(self.rowIdx+1, table.rows[self.rowIdx][:])
        self.memory = True
        self.endInsert()
        return True

    def undo(self):
        super(CloneRowAction, self).undo()
        table = self.model.table
        self.beginDelete(self.rowIdx+1)
        del table.rows[self.rowIdx+1]
        self.endDelete()

class SortTableAction(TableAction):

    actionName = "sort table"

    def __init__(self, model, dataColIdx, colIdx, order):
        super(SortTableAction, self).__init__(model, dataColIdx=dataColIdx,
                                        colIdx=colIdx, order=order)
        self.toview = dict(sortByColumn = colIdx,
                           ascending = (order == Qt.AscendingOrder))

    def do(self):
        table = self.model.table
        ascending = self.order == Qt.AscendingOrder
        colName = table.colNames[self.dataColIdx]
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
        super(ChangeValueAction, self).__init__(model, idx=idx,
                                                dataColIdx=dataColIdx,
                                                value=value)
        self.toview = dict(row=idx.row(), column=idx.column(), value=value)

    def do(self):
        table = self.model.table
        row = table.rows[self.idx.row()]
        self.memory = row[self.dataColIdx]
        if self.memory == self.value: return False
        row[self.dataColIdx] = self.value
        self.model.emit(
                  SIGNAL("dataChanged(QModelIndex,QModelIndex,PyQt_PyObject)"),
                  self.idx,
                  self.idx,
                  self)
        return True

    def undo(self):
        super(ChangeValueAction, self).undo()
        table = self.model.table
        table.rows[self.idx.row()][self.dataColIdx] = self.memory
        self.model.emit(
                  SIGNAL("dataChanged(QModelIndex,QModelIndex,PyQt_PyObject)"),
                  self.idx,
                  self.idx,
                  self)

class IntegrateAction(TableAction):

    actionName = "integrate"

    def __init__(self, model, idx, postfix, method, rtmin, rtmax):
        super(IntegrateAction, self).__init__(model, idx=idx, postfix=postfix,
                                              method=method, rtmin=rtmin,
                                              rtmax=rtmax, )
        self.toview = dict(rtmin=rtmin, rtmax=rtmax, method=method,
                           postfix=postfix)

    def do(self):
        #pyqtRemoveInputHook()
        integrator = dict(configs.peakIntegrators)[self.method]
        table = self.model.table
        # returns Bunch which sublcasses dict
        args = table.get(table.rows[self.idx], None)
        postfix = self.postfix

        integrator.setPeakMap(args["peakmap"+postfix])

        # integrate
        mzmin = args["mzmin"+postfix]
        mzmax = args["mzmax"+postfix]
        res = integrator.integrate(mzmin, mzmax, self.rtmin, self.rtmax)

        area = res["area"]
        rmse = res["rmse"]
        params = res["params"]

        # var 'row' is a Bunch, so we have to get the row from direct access
        # to table.rows:
        self.memory = table.rows[self.idx][:]

        # write values to table
        row = table.rows[self.idx]
        table.set(row, "method"+postfix, self.method)
        table.set(row, "rtmin"+postfix, self.rtmin)
        table.set(row, "rtmax"+postfix, self.rtmax)
        table.set(row, "area"+postfix, area)
        table.set(row, "rmse"+postfix, rmse)
        table.set(row, "params"+postfix, params)
        args = table.get(table.rows[self.idx], None)
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
        # this one updates plots
        self.model.emit(
                  SIGNAL("dataChanged(QModelIndex,QModelIndex,PyQt_PyObject)"),
                  tl,
                  tr,
                  self)
        # this one updates cells in table
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), tl, tr)


class TableModel(QAbstractTableModel):

    LIGHT_BLUE = QColor(200, 200, 255)
    WHITE = QColor(255, 255, 255)

    def __init__(self, table, parent):
        super(TableModel, self).__init__(parent)
        self.table = table
        self.parent = parent
        nc = len(self.table.colNames)
        indizesOfVisibleCols = (j for j in range(nc)
                                  if self.table.colFormats[j] is not None)
        self.widgetColToDataCol = dict(enumerate(indizesOfVisibleCols))
        self.emptyActionStack()

        self.nonEditables=set()
        self.postfixes = table.findPostfixes()

    def addNonEditable(self, name):
        dataColIdx = self.table.getIndex(name)
        self.nonEditables.add(dataColIdx)

    def emptyActionStack(self):
        self.actions = []
        self.redoActions = []

    def getRow(self, idx):
        return self.table.get(self.table.rows[idx], None)

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
                        return "-" if value is None else "%.4f" % value
                    return str(value)
            return str(value)
        if role == Qt.FontRole:
            content = self.data(index)
            if isUrl(content):
                font = QFont(super(TableModel, self).data(index, Qt.DisplayRole))
                font.setUnderline(True)
                return font

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
        #urls are not editable
        if isUrl(str(self.data(index))):
            return default
        if self.widgetColToDataCol[index.column()] in self.nonEditables:
            return default
        return Qt.ItemFlags(default | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        assert isinstance(value, QVariant)
        if index.isValid() and 0 <= index.row() < len(self.table):
            dataIdx = self.widgetColToDataCol[index.column()]
            expectedType = self.table.colTypes[dataIdx]
            if value.toString().trimmed()=="-":
                value = None
            elif expectedType != object:
                # QVariant -> QString -> str + strip:
                value = str(value.toString()).strip()
                # minutes ?
                if re.match("^((\d+m)|(\d*.\d+m))$", value):
                    value = 60.0 * float(value[:-1])
                try:
                    value = expectedType(value)
                except Exception:
                    guidata.qapplication().beep()
                    return False
            return self.runAction(ChangeValueAction, index, dataIdx, value)
        return False

    def runAction(self, clz, *a):
        action = clz(self, *a)
        done = action.do()
        if not done:
            return done
        self.actions.append(action)
        self.redoActions = []
        self.parent.updateMenubar()
        return done

    def infoLastAction(self):
        if len(self.actions):
            return str(self.actions[-1])
        return None

    def infoRedoAction(self):
        if len(self.redoActions):
            return str(self.redoActions[-1])
        return None

    def undoLastAction(self):
        if len(self.actions):
            action = self.actions.pop()
            action.undo()
            self.redoActions.append(action)
            self.parent.updateMenubar()
            return
        raise Exception("no action to be undone")

    def redoLastAction(self):
        if len(self.redoActions):
            action = self.redoActions.pop()
            action.do()
            self.actions.append(action)
            self.parent.updateMenubar()
            return
        raise Exception("no action to be redone")

    def cloneRow(self, position):
        self.runAction(CloneRowAction, position)
        return True

    def removeRow(self, position):
        self.runAction(DeleteRowAction, position)
        return True

    def sort(self, colIdx, order=Qt.AscendingOrder):
        dataColIdx = self.widgetColToDataCol[colIdx]
        self.runAction(SortTableAction, dataColIdx, colIdx, order)

    def integrate(self, idx, postfix, method, rtmin, rtmax):
        self.runAction(IntegrateAction, postfix, idx, method, rtmin, rtmax)

    def eicColNames(self):
        return ["peakmap", "mzmin", "mzmax", "rtmin", "rtmax"]

    def getEicValues(self, rowIdx, p):
        get = lambda nn: self.table.get(self.table.rows[rowIdx], nn+p)
        return dict((nn, get(nn)) for nn in self.eicColNames())

    def hasFeatures(self):
        return self.checkForAny(*self.eicColNames())

    def integrationColNames(self):
        return ["area", "rmse", "method", "params"]

    def getIntegrationValues(self, rowIdx, p):
        get = lambda nn: self.table.get(self.table.rows[rowIdx], nn+p)
        return dict((nn, get(nn)) for nn in self.integrationColNames())

    def isIntegrated(self):
        return self.hasFeatures()\
               and self.checkForAny(*self.integrationColNames())

    def checkForAny(self, *names):
        """ checks if names or derived names are present in table at once
            derived names are colum names postfixed with _1, _2, ....
            which happens during join if column names appear twice.
        """
        for postfix in self.postfixes:
            colNames = [ n + postfix for n in names]
            if self.table.hasColumns(*colNames):
                return True
        return False

    def setNonEditable(self, colBaseName):
        for postfix in self.postfixes:
            name = colBaseName+postfix
            if self.table.hasColumns(name):
                self.addNonEditable(name)

    def getTitle(self):
        table = self.table
        if table.title:
            title = table.title
        else:
            title = os.path.basename(table.meta.get("source",""))
        if self.hasFeatures():
            title += " rt_aligned=%s" % table.meta.get("rt_aligned", "False")
            title += " mz_aligned=%s" % table.meta.get("mz_aligned", "False")
        return title

    def postfixesSupportedBy(self, colNames):
        postfixes = []
        for p in self.postfixes:
            names = [ n+p for n in colNames ]
            if not self.table.hasColumns(*names):
                continue
            postfixes.append(p)
        return postfixes

    def getSmoothedEics(self, rowIdx, rts):
        allsmoothed = []
        for p in self.postfixesSupportedBy(self.integrationColNames()):
            values = self.getIntegrationValues(rowIdx, p)
            method = values["method"]
            params = values["params"]
            integrator = dict(configs.peakIntegrators)[method]
            intrts, smoothed = integrator.getSmoothed(rts, params)
            allsmoothed.append((intrts, smoothed))
        return allsmoothed

    def getPeakmaps(self, rowIdx):
        peakMaps = []
        for p in self.postfixesSupportedBy(["peakmap"]):
            pm = self.table.get(self.table.rows[rowIdx], "peakmap"+p)
            peakMaps.append(pm)
        return peakMaps

    def getLevelNSpectra(self, rowIdx, minLevel=2, maxLevel=999):
        spectra=[]
        postfixes = []
        for p in self.postfixesSupportedBy(self.eicColNames()):
            values = self.getEicValues(rowIdx, p)
            pm = values["peakmap"]
            rtmin = values["rtmin"]
            rtmax = values["rtmax"]
            for spec in pm.levelNSpecs(minLevel, maxLevel):
                if rtmin <= spec.rt <= rtmax:
                    spectra.append(spec)
                    postfixes.append(p)
        return postfixes, spectra

    def getEics(self, rowIdx):
        eics = []
        mzmins = []
        mzmaxs = []
        rtmins = []
        rtmaxs = []
        allrts = []
        for p in self.postfixesSupportedBy(self.eicColNames()):
            values = self.getEicValues(rowIdx, p)
            pm = values["peakmap"]
            mzmin = values["mzmin"]
            mzmax = values["mzmax"]
            rtmin = values["rtmin"]
            rtmax = values["rtmax"]
            rtmins.append(rtmin)
            rtmaxs.append(rtmax)
            chromo = pm.chromatogram(mzmin, mzmax)
            eics.append(chromo)
            allrts.extend(chromo[0])
            mzmins.append(mzmin)
            mzmaxs.append(mzmax)
        return eics, min(mzmins), max(mzmaxs), min(rtmins), max(rtmaxs),\
               sorted(allrts)
