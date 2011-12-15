# -*- coding: utf-8 -*-

from PyQt4.QtGui import  *
from PyQt4.QtCore import *

import guidata

from PlottingWidgets import RtPlotter, MzPlotter

import numpy as np
import configs
import os

from TableExplorerModel import *


class TableExplorer(QDialog):

    def __init__(self, tables, offerAbortOption):
        QDialog.__init__(self)

        self.offerAbortOption = offerAbortOption

        self.models = [TableModel(table, self) for table in tables]
        self.model = None
        self.tableView = None

        self.currentRow = -1
        self.hadFeatures = None
        self.wasIntegrated = None

        self.setupWidgets()
        self.setupLayout()
        self.connectSignals()

        self.setWindowFlags(Qt.Window)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

        self.setupViewForTable(0)

    def setupWidgets(self):
        self.setupMenuBar()
        self.setupTableViews()
        self.setupPlottingWidgets()
        self.setupIntegrationWidgets()
        if self.offerAbortOption:
            self.setupAcceptButtons()

    def setupMenuBar(self):
        self.menubar = QMenuBar(self)
        menu = self.buildEditMenu()
        self.menubar.addMenu(menu)
        self.chooseTableActions = []
        if len(self.models)>1:
            menu = self.buildChooseTableMenu()
            self.menubar.addMenu(menu)

    def buildEditMenu(self):
        self.undoAction = QAction("Undo", self)
        self.undoAction.setShortcut(QKeySequence("Ctrl+Z"))
        self.redoAction = QAction("Redo", self)
        self.redoAction.setShortcut(QKeySequence("Ctrl+Y"))
        menu = QMenu("Edit", self.menubar)
        menu.addAction(self.undoAction)
        menu.addAction(self.redoAction)
        return menu

    def setupTableViews(self):
        self.tableViews = []
        for i, model in enumerate(self.models):
            self.tableViews.append(self.setupTableViewFor(model))

    def setupTableViewFor(self, model):
        tableView = QTableView(self)

        def handler(evt, view=tableView, model=model):
            if not view.isSortingEnabled():
                view.setSortingEnabled(True)
                view.resizeColumnsToContents()
                model.emptyActionStack()
        tableView.showEvent = handler

        tableView.setModel(model)
        tableView.horizontalHeader().setResizeMode(QHeaderView.Interactive)
        pol = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tableView.setSizePolicy(pol)
        tableView.setVisible(False)
        # before filling the table, disabling sorting accelerates table
        # construction, sorting is enabled in TableView.showEvent, which is
        # called after construction
        tableView.setSortingEnabled(False)
        return tableView

    def buildChooseTableMenu(self):
        menu = QMenu("Choose Table", self.menubar)
        for i, model in enumerate(self.models):
            action = QAction(" [%d]: %s" % (i,model.getTitle()), self)
            menu.addAction(action)
            self.chooseTableActions.append(action)
        return menu

    def setupPlottingWidgets(self):
        self.plotconfigs = (None, dict(shade=0.35, linewidth=1, color="g") )
        self.rtPlotter = RtPlotter(rangeSelectionCallback=self.plotMz)
        self.rtPlotter.setMinimumSize(300, 100)
        self.mzPlotter = MzPlotter()
        self.mzPlotter.setMinimumSize(300, 100)
        pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pol.setVerticalStretch(5)
        self.rtPlotter.widget.setSizePolicy(pol)
        self.mzPlotter.widget.setSizePolicy(pol)

    def setupIntegrationWidgets(self):
        self.intLabel = QLabel("Integration")
        self.chooseIntMethod = QComboBox()
        for name, _ in configs.peakIntegrators:
            self.chooseIntMethod.addItem(name)
        self.reintegrateButton = QPushButton()
        self.reintegrateButton.setText("Integrate")

    def setupAcceptButtons(self):
        self.okButton = QPushButton("Ok")
        self.abortButton = QPushButton("Abort")
        self.result = 1 # default for closing

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.setOpaqueResize(False)

        vsplitter.addWidget(self.menubar)
        vsplitter.addWidget(self.layoutWidgetsAboveTable())

        for view in self.tableViews:
            vsplitter.addWidget(view)
        vlayout.addWidget(vsplitter)

        if self.offerAbortOption:
            vlayout.addLayout(self.layoutButtons())

    def layoutButtons(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.abortButton)
        hbox.setAlignment(self.abortButton, Qt.AlignVCenter)
        hbox.addWidget(self.okButton)
        hbox.setAlignment(self.okButton, Qt.AlignVCenter)
        return hbox

    def layoutWidgetsAboveTable(self):
        hsplitter = QSplitter()
        hsplitter.setOpaqueResize(False)
        hsplitter.addWidget(self.rtPlotter.widget)

        integrationLayout = QVBoxLayout()
        integrationLayout.setSpacing(10)
        integrationLayout.setMargin(5)
        integrationLayout.addWidget(self.intLabel)
        integrationLayout.addWidget(self.chooseIntMethod)
        integrationLayout.addWidget(self.reintegrateButton)
        integrationLayout.addStretch()
        integrationLayout.setAlignment(self.intLabel, Qt.AlignTop)
        integrationLayout.setAlignment(self.chooseIntMethod, Qt.AlignTop)
        integrationLayout.setAlignment(self.reintegrateButton, Qt.AlignTop)

        self.integrationFrame = QFrame()
        self.integrationFrame.setLayout(integrationLayout)

        hsplitter.addWidget(self.integrationFrame)
        hsplitter.addWidget(self.mzPlotter.widget)
        return hsplitter

    def setupModelDependendLook(self):
        hasFeatures = self.model.hasFeatures()
        isIntegrated = self.model.isIntegrated()
        self.hasFeatures = hasFeatures
        self.isIntegrated = isIntegrated

        self.setWindowTitle(self.model.getTitle())

        if hasFeatures != self.hadFeatures:
            self.setPlotVisibility(hasFeatures)
            self.hadFeatures = hasFeatures
        if isIntegrated != self.wasIntegrated:
            self.setIntegrationPanelVisiblity(isIntegrated)
            self.wasIntegrated = isIntegrated
        if hasFeatures:
            self.resetPlots()

    def setPlotVisibility(self, doShow):
        self.rtPlotter.widget.setVisible(doShow)
        self.mzPlotter.widget.setVisible(doShow)

    def resetPlots(self):
        self.rtPlotter.reset()
        self.mzPlotter.reset()

    def setIntegrationPanelVisiblity(self, doShow):
        self.integrationFrame.setVisible(doShow)

    def connectSignals(self):
        for i, action in enumerate(self.chooseTableActions):
            def handler(i=i):
                self.setupViewForTable(i)
            self.menubar.connect(action, SIGNAL("triggered()"), handler)

        for view in self.tableViews:
            vh = view.verticalHeader()
            vh.setContextMenuPolicy(Qt.CustomContextMenu)
            self.connect(vh, SIGNAL("customContextMenuRequested(QPoint)"),\
                         self.openContextMenu)

            self.connect(vh, SIGNAL("sectionClicked(int)"), self.rowClicked)

        self.connect(self.reintegrateButton, SIGNAL("clicked()"),
                     self.doIntegrate)

        if self.offerAbortOption:
            self.connect(self.okButton, SIGNAL("clicked()"), self.ok)
            self.connect(self.abortButton, SIGNAL("clicked()"), self.abort)

    def disconnectModelSignals(self):
        self.disconnect(self.model, SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     self.dataChanged)
        self.menubar.disconnect(self.undoAction, SIGNAL("triggered()"),\
                             self.model.undoLastAction)
        self.menubar.disconnect(self.redoAction, SIGNAL("triggered()"),\
                             self.model.redoLastAction)

    def connectModelSignals(self):
        self.connect(self.model, SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     self.dataChanged)
        self.menubar.connect(self.undoAction, SIGNAL("triggered()"),\
                             self.model.undoLastAction)
        self.menubar.connect(self.redoAction, SIGNAL("triggered()"),\
                             self.model.redoLastAction)

    def updateMenubar(self):
        undoInfo = self.model.infoLastAction()
        redoInfo = self.model.infoRedoAction()
        self.undoAction.setEnabled(undoInfo != None)
        self.redoAction.setEnabled(redoInfo != None)
        if undoInfo:
            self.undoAction.setText("Undo: %s" % undoInfo)
        if redoInfo:
            self.redoAction.setText("Redo: %s" % redoInfo)

    def setupViewForTable(self, i):
        for j, action in enumerate(self.chooseTableActions):
            txt = str(action.text()) # QString -> Python str
            if txt.startswith("*"):
                txt = " "+txt[1:]
                action.setText(txt)
            if i==j:
                action.setText("*"+txt[1:])

        for j in range(len(self.models)):
            self.tableViews[j].setVisible(i==j)

        if self.model is not None:
            self.disconnectModelSignals()
        self.model = self.models[i]
        self.tableView = self.tableViews[i]
        self.setupModelDependendLook()
        if self.isIntegrated:
            self.model.setNonEditable("method")
        self.updateMenubar()
        self.connectModelSignals()

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

    def openContextMenu(self, point):
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
        appearAt = self.tableView.verticalHeader().mapToGlobal(point)
        choosenAction = menu.exec_(appearAt)
        if choosenAction == removeAction:
            self.model.removeRow(idx)
        elif choosenAction == cloneAction:
            self.model.cloneRow(idx)
        elif undoInfo is not None and choosenAction == undoAction:
            self.model.undoLastAction()
        elif redoInfo is not None and choosenAction == redoAction:
            self.model.redoLastAction()

    def doIntegrate(self):
        if self.currentRow < 0:
            return # no row selected

        method = str(self.chooseIntMethod.currentText()) # conv from qstring
        rtmin, rtmax = self.rtPlotter.getRangeSelectionLimits()
        self.model.integrate(self.currentRow, method, rtmin, rtmax)

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
        if self.hasFeatures:
            eics = self.model.getEics(rowIdx)
            integrationCurves = self.model.getIntegrationCurves(rowIdx)
            self.rtPlotter.plot(eics, integrationCurves)
            spectra = self.model.getSpectra(rowIdx)
            self.mzPlotter.plot(spectra)

            #row = self.model.getRow(rowIdx)
            #self.currentPeakMap = row.peakmap
            #self.currentL1Spectra = [s for s in row.peakmap if s.msLevel == 1]
            #self.currentRts = [spec.rt for spec in self.currentL1Spectra]
            #self.updatePlots()
            #rtmin = row.rtmin
            #rtmax = row.rtmax
            #w = rtmax - rtmin
            #if w == 0:
                #w = 30.0 # seconds
            #self.rtPlotter.setXAxisLimits(rtmin -w, rtmax + w)
            if self.isIntegrated:
                print "TODO"
                #ix = self.chooseIntMethod.findText(row.method)
                #self.chooseIntMethod.setCurrentIndex(ix)

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

def inspect(tables, offerAbortOption=False):
    app = guidata.qapplication()
    explorer = TableExplorer(tables, offerAbortOption)
    explorer.raise_()
    explorer.exec_()
    if offerAbortOption:
        if explorer.result == 1:
            raise Exception("Dialog aborted by user")
