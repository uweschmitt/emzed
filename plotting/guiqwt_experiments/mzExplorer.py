# -*- coding: utf-8 -*-

from PyQt4.QtGui import  QVBoxLayout, QDialog

from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.builder import make
from guiqwt.label import ObjectInfo
from guiqwt.curve import  CurveItem
from guiqwt.signals import SIG_RANGE_CHANGED
from guiqwt.config import CONF
from guiqwt.shapes import Marker

import numpy as np
import sys, cPickle

from SnappingRangeSelection import SnappingRangeSelection
from ModifiedPlots import RtPlot, MzPlot
from SelectTools import RtSelectionTool, MzSelectionTool

sys.path.insert(0, "../../pyOpenMS")

class ModifiedCurveItem(CurveItem):
    def can_select(self):
        return False


class RtRangeSelectionInfo(ObjectInfo):
    def __init__(self, range_):
        self.range_ = range_

    def get_text(self):
        rtmin, rtmax = self.range_.get_range()
        if rtmin != rtmax:
            return u"RT: %.3f ... %.3f" % (rtmin, rtmax)
        else:
            return u"RT: %.3f" % rtmin


class MzCursorInfo(ObjectInfo):
    def __init__(self, marker):
        self.marker = marker

    def get_text(self):
        mz, I = self.marker.xValue(), self.marker.yValue()
        return "mz=%.6f<br/>I=%.0f" % (mz, I)


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

        # you have to register item to plot before you can register the rtSelectionHandler:
        self.widgetRt.plot.add_item(range_)
        self.connect(range_.plot(), SIG_RANGE_CHANGED, self.rtSelectionHandler)

        cc = make.info_label("TL", [RtRangeSelectionInfo(range_)])
        self.widgetRt.plot.add_item(cc)

    def rtSelectionHandler(self, obj, min_, max_):
        # right handle might be to the left of the left one !
        self.minRT, self.maxRT = sorted((min_, max_))
        self.plotMz()

    def addMzItems(self):
        marker = Marker(label_cb=self.widgetMz.plot.label_info, constraint_cb=self.widgetMz.plot.on_plot)
        marker.attach(self.widgetMz.plot)
        params = {
            "marker/cross/symbol/marker": 'Rect',
            "marker/cross/symbol/edgecolor": "black",
            "marker/cross/symbol/facecolor": "red",
            "marker/cross/symbol/alpha": 0.8,
            "marker/cross/symbol/size": 5,
            #"marker/cross/text/font/family": "default",
            #"marker/cross/text/font/size": 8,
            #"marker/cross/text/font/bold": False,
            #"marker/cross/text/font/italic": False,
            #"marker/cross/text/textcolor": "black",
            #"marker/cross/text/background_color": "#ffffff",
            #"marker/cross/text/background_alpha": 0.8,
            #"marker/cross/pen/style": "DashLine",
            #"marker/cross/pen/color": "red",
            "marker/cross/pen/width": 0,
            "marker/cross/linestyle": 0,
            #"marker/cross/spacing": 7
        }
        CONF.update_defaults(dict(plot=params))
        marker.markerparam.read_config(CONF, "plot", "marker/cross")
        marker.markerparam.update_marker(marker)

        label = make.info_label("TR", [MzCursorInfo(marker)])

        self.widgetMz.plot.add_item(marker)
        self.widgetMz.plot.add_item(label)

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

    peakmap = cPickle.load(file("peakmap.pickled", "rb"))

    app = QApplication([])
    win = MzExplorer(peakmap)

    win.show()
    app.exec_()


if __name__ == '__main__':
    test()
    
