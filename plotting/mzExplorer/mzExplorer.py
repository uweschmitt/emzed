# -*- coding: utf-8 -*-

from PyQt4.QtGui import  QVBoxLayout, QDialog, QPainter

from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.builder import make
from guiqwt.label import ObjectInfo
from guiqwt.curve import  CurveItem
from guiqwt.signals import SIG_RANGE_CHANGED
from guiqwt.config import CONF
from guiqwt.shapes import Marker, SegmentShape

import numpy as np
import sys, cPickle

from SnappingRangeSelection import SnappingRangeSelection
from ModifiedPlots import RtPlot, MzPlot
from SelectTools import RtSelectionTool, MzSelectionTool

sys.path.insert(0, "../../pyOpenMS")

import pyOpenMS

class ModifiedCurveItem(CurveItem):
    def can_select(self):
        return False


class ModifiedSegment(SegmentShape):
     def set_rect(self, x1, y1, x2, y2):
        """
        Set the start point of this segment to (x1, y1)
        and the end point of this line to (x2, y2)
        """
        # the original shape has a extra point in the middle
        # of the line, which I moved to the beginning:

        self.set_points([(x1, y1), (x2, y2), (x1, y1) ])

     def draw(self, painter, xMap, yMap, canvasRect):

         # code copied and rearanged such that line has antialiasing,
         # but symbols have not.
         pen, brush, symbol = self.get_pen_brush(xMap, yMap)

         painter.setPen(pen)
         painter.setBrush(brush)

         points = self.transform_points(xMap, yMap)
         if self.ADDITIONNAL_POINTS:
             shape_points = points[:-self.ADDITIONNAL_POINTS]
             other_points = points[-self.ADDITIONNAL_POINTS:]
         else:
             shape_points = points
             other_points = []

         for i in xrange(points.size()):
             symbol.draw(painter, points[i].toPoint())

         painter.setRenderHint(QPainter.Antialiasing)
         if self.closed:
             painter.drawPolygon(shape_points)
         else:
             painter.drawPolyline(shape_points)

         if self.LINK_ADDITIONNAL_POINTS and other_points:
             pen2 = painter.pen()
             pen2.setStyle(Qt.DotLine)
             painter.setPen(pen2)
             painter.drawPolyline(other_points)



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
        
        markerSymbol = "Rect"
        edgeColor = "black"
        faceColor = "red"
        alpha = 0.6
        size = 3

        params = {
            "marker/cross/symbol/marker": markerSymbol,
            "marker/cross/symbol/edgecolor": edgeColor,
            "marker/cross/symbol/facecolor": faceColor,
            "marker/cross/symbol/alpha": alpha,
            "marker/cross/symbol/size": size,
            "marker/cross/pen/width": 0,
            "marker/cross/linestyle": 0,
        }
        CONF.update_defaults(dict(plot=params))
        marker.markerparam.read_config(CONF, "plot", "marker/cross")
        marker.markerparam.update_marker(marker)



        line   = make.segment(0, 0, 0, 0)
        line.__class__ = ModifiedSegment
        line.setVisible(0)
        params = {
                         "shape/drag/symbol/marker" : markerSymbol,
                         "shape/drag/symbol/size" : size,
                         "shape/drag/symbol/edgecolor" : edgeColor,
                         "shape/drag/symbol/facecolor" : faceColor,
                         "shape/drag/symbol/alpha" : alpha,

        }
        CONF.update_defaults(dict(plot=params))
        line.shapeparam.read_config(CONF, "plot", "shape/drag")
        line.shapeparam.update_shape(line)

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
    
