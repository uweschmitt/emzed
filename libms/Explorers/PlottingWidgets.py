
from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.builder import make
from guiqwt.label import ObjectInfo

from ModifiedGuiQwtBehavior import *
from Config import setupStyleRangeMarker, setupCommonStyle

import numpy as np

class RtRangeSelectionInfo(ObjectInfo):
    
    def __init__(self, range_):
        self.range_ = range_

    def get_text(self):
        rtmin, rtmax = sorted(self.range_.get_range())
        if rtmin != rtmax:
            return u"RT: %.3f ... %.3f" % (rtmin, rtmax)
        else:
            return u"RT: %.3f" % rtmin

class PlotterBase(object):

    def __init__(self, xlabel, ylabel):
        self.widget = CurveWidget(xlabel=xlabel, ylabel=ylabel)

    def setXAxisLimits(self, xmin, xmax):
        self.widget.plot.update_plot_xlimits(xmin, xmax)

    def setMinimumSize(self, a, b):
        self.widget.setMinimumSize(a,b)

class RtPlotter(PlotterBase):

    def __init__(self, rtvalues, mzNotifier = None):
        super(RtPlotter, self).__init__("RT", "I")

        self.rtvalues = np.array(rtvalues)
        self.mzNotifier = mzNotifier

        self.minRT = np.min(self.rtvalues)
        self.maxRT = self.minRT

        widget = self.widget
        widget.plot.__class__ = RtPlot

        self.pm = PlotManager(widget)
        self.pm.add_plot(widget.plot)

        self.curve = make.curve([], [], color='b')
        self.curve.__class__ = ModifiedCurveItem

        widget.plot.add_item(self.curve)

        t = self.pm.add_tool(RtSelectionTool)
        self.pm.set_default_tool(t)
        t.activate()

        range_ = SnappingRangeSelection(self.minRT, self.maxRT, self.rtvalues)
        setupStyleRangeMarker(range_)
        self.range_ = range_

        # you have to register item to plot before you can register the rtSelectionHandler:
        widget.plot.add_item(range_)
        widget.connect(range_.plot(), SIG_RANGE_CHANGED, self.rangeSelectionHandler)

        cc = make.info_label("TR", [RtRangeSelectionInfo(range_)], title=None)
        widget.plot.add_item(cc)

    def notifyMZ(self):

        if self.mzNotifier is not None:
            self.mzNotifier(self.minRT, self.maxRT)


    def setRangeSelectionLimits(self, xleft, xright):
        self.range_.move_point_to(0, (xleft,0))  # left bar of range marker
        self.range_.move_point_to(1, (xright,0)) # right bar

    def setXAxisLimits(self, xmin, xmax):
        super(RtPlotter, self).setXAxisLimits(xmin, xmax)
        mid = 0.5*(xmin+xmax)
        self.setRangeSelectionLimits(mid, mid)
    
    def setRtHighlightInterval(self, min_, max_):
        self.minRT, self.maxRT = min_, max_
        self.notifyMZ()

    def rangeSelectionHandler(self, obj, min_, max_):
        self.setRtHighlightInterval(*sorted((min_, max_)))

    
    def plot(self, chromatogram):
        self.curve.set_data(self.rtvalues, chromatogram)
        self.curve.plot().replot()
       

class MzCursorInfo(ObjectInfo):
    def __init__(self, marker, line):
        self.marker = marker
        self.line   = line

    def get_text(self):
        mz, I = self.marker.xValue(), self.marker.yValue()
        txt = "mz=%.6f<br/>I=%.1e" % (mz, I)
        if self.line.isVisible():
            _, _ , mz2, I2 = self.line.get_rect()
            txt += "<br/><br/>dmz=%.6f<br/>rI=%.3e" % (mz2-mz, I2/I)
        return txt

class MzPlotter(PlotterBase):

    def __init__(self, peakmap):
        super(MzPlotter, self).__init__("m/z", "I")
        self.peakmap = peakmap 

        widget = self.widget

        # inject mofified behaviour of wigets plot attribute:
        widget.plot.__class__ = MzPlot


        self.pm = PlotManager(widget)
        self.pm.add_plot(widget.plot)
        self.curve = make.curve([], [], color='b', curvestyle="Sticks")
        # inject modified behaviour:
        self.curve.__class__ = ModifiedCurveItem

        self.widget.plot.add_item(self.curve)

        t = self.pm.add_tool(MzSelectionTool)
        self.pm.set_default_tool(t)
        t.activate()

        marker = Marker(label_cb=widget.plot.label_info, constraint_cb=widget.plot.on_plot)
        marker.attach(self.widget.plot)

        line   = make.segment(0, 0, 0, 0)
        line.__class__ = ModifiedSegment
        line.setVisible(0)

        setupCommonStyle(line, marker)

        label = make.info_label("TR", [MzCursorInfo(marker, line)], title=None)

        widget.plot.add_item(marker)
        widget.plot.add_item(label)
        widget.plot.add_item(line)


    def plot(self, peaks):
        self.curve.set_data(peaks[:, 0], peaks[:, 1])

        self.curve.plot().updateAxes()
        self.curve.plot().replot()
