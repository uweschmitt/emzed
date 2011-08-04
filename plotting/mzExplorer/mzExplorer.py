# -*- coding: utf-8 -*-

from PyQt4.QtGui import  QVBoxLayout, QDialog, QPainter

from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.builder import make
from guiqwt.label import ObjectInfo
import sys

from ModifiedGuiQwtBehavior import *
from Config import *


sys.path.insert(0, "../../pyOpenMS")

import pyOpenMS


class RtRangeSelectionInfo(ObjectInfo):
    
    def __init__(self, range_):
        self.range_ = range_

    def get_text(self):
        rtmin, rtmax = sorted(self.range_.get_range())
        if rtmin != rtmax:
            return u"RT: %.3f ... %.3f" % (rtmin, rtmax)
        else:
            return u"RT: %.3f" % rtmin


class MzCursorInfo(ObjectInfo):
    def __init__(self, marker, line):
        self.marker = marker
        self.line   = line

    def get_text(self):
        mz, I = self.marker.xValue(), self.marker.yValue()
        txt = "mz=%.6f<br/>I=%.1f" % (mz, I)
        if self.line.isVisible():
            _, _ , mz2, I2 = self.line.get_rect()
            txt += "<br/><br/>dmz=%.6f<br/>rI=%.3f" % (mz2-mz, I2/I)
        return txt


class MzExplorer(QDialog):

    def __init__(self, peakmap):
        QDialog.__init__(self)

        self.processPeakmap(peakmap)
        self.setupPlotting()
        self.setupLayout()

        self.plotChromatogramm()
        self.plotMz()

    def processPeakmap(self, peakmap):
        self.peakmap = peakmap
        self.rts = np.array([s.RT for s in self.peakmap])
        self.chromatogram = np.array([np.sum(spec.peaks[:, 1]) for spec in peakmap])
        self.minRT = np.min(self.rts)
        self.maxRT = self.minRT

    def setupPlotting(self):
        self.setupPlotWidgets()
        self.addCurves()
        self.addTools()
        self.addRtItems()
        self.addMzItems()

    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)
        vlayout.addWidget(self.widgetRt)
        vlayout.addWidget(self.widgetMz)

    def setupPlotWidgets(self):
        self.widgetRt = CurveWidget(xlabel="RT", ylabel="I")
        self.widgetRt.setMinimumSize(600, 300)

        self.widgetMz = CurveWidget(xlabel="m/z", ylabel="I")
        self.widgetMz.setMinimumSize(600, 300)

        # inject mofified behaviour of wigets plot attribute:
        self.widgetRt.plot.__class__ = RtPlot
        self.widgetMz.plot.__class__ = MzPlot

        self.pmRt = PlotManager(self.widgetRt)
        self.pmRt.add_plot(self.widgetRt.plot)

        self.pmMz = PlotManager(self.widgetMz)
        self.pmMz.add_plot(self.widgetMz.plot)

    def addCurves(self):
        self.rTCurveItem = make.curve([], [], color='b')
        # inject modified behaviour:
        self.rTCurveItem.__class__ = ModifiedCurveItem

        self.mZCurveItem = make.curve([], [], color='b', curvestyle="Sticks")
        # inject modified behaviour:
        self.rTCurveItem.__class__ = ModifiedCurveItem

        self.widgetRt.plot.add_item(self.rTCurveItem)
        self.widgetMz.plot.add_item(self.mZCurveItem)

    def addTools(self):
        t = self.pmRt.add_tool(RtSelectionTool)
        self.pmRt.set_default_tool(t)
        t.activate()

        t = self.pmMz.add_tool(MzSelectionTool)
        self.pmMz.set_default_tool(t)
        t.activate()

    def addRtItems(self):
        range_ = SnappingRangeSelection(self.minRT, self.maxRT, self.rts)
        setupStyleRangeMarker(range_)

        # you have to register item to plot before you can register the rtSelectionHandler:
        self.widgetRt.plot.add_item(range_)
        self.connect(range_.plot(), SIG_RANGE_CHANGED, self.rtSelectionHandler)

        cc = make.info_label("TR", [RtRangeSelectionInfo(range_)])
        self.widgetRt.plot.add_item(cc)

    def rtSelectionHandler(self, obj, min_, max_):
        # right handle might be to the left of the left one !
        self.minRT, self.maxRT = sorted((min_, max_))
        self.plotMz()

    def addMzItems(self):

        marker = Marker(label_cb=self.widgetMz.plot.label_info, constraint_cb=self.widgetMz.plot.on_plot)
        marker.attach(self.widgetMz.plot)

        line   = make.segment(0, 0, 0, 0)
        line.__class__ = ModifiedSegment
        line.setVisible(0)

        setupCommonStyle(line, marker)

        label = make.info_label("TR", [MzCursorInfo(marker, line)])

        self.widgetMz.plot.add_item(marker)
        self.widgetMz.plot.add_item(label)
        self.widgetMz.plot.add_item(line)

    def plotChromatogramm(self):
        self.rTCurveItem.set_data(self.rts, self.chromatogram)
        self.rTCurveItem.plot().replot()

    def plotMz(self):
        
        peaks_in_range = np.vstack(( s.peaks for s in self.peakmap if self.minRT <= s.RT <= self.maxRT ))
        self.mZCurveItem.set_data(peaks_in_range[:, 0], peaks_in_range[:, 1])

        self.mZCurveItem.plot().updateAxes()
        self.mZCurveItem.plot().replot()


    

def test():
    """Testing this simple Qt/guiqwt example"""
    from PyQt4.QtGui import QApplication

    #peakmap = cPickle.load(file("peakmap.pickled", "rb"))
    print dir(pyOpenMS)
    peakmap = pyOpenMS.loadMzXMLFile("test.mzXML")

    app = QApplication([])
    win = MzExplorer(peakmap)

    win.show()
    app.exec_()


if __name__ == '__main__':
    test()
    
