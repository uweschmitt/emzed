
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


class RtPlotter(object):

    def __init__(self, rtvalues, selectionNotifier = None):
        self.rtvalues = np.array(rtvalues)
        self.selectionNotifier = selectionNotifier

        self.minRT = np.min(self.rtvalues)
        self.maxRT = self.minRT

        widget = CurveWidget(xlabel="RT", ylabel="I")
        widget.plot.__class__ = RtPlot
        self.widget = widget

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

        # you have to register item to plot before you can register the rtSelectionHandler:
        widget.plot.add_item(range_)
        widget.connect(range_.plot(), SIG_RANGE_CHANGED, self.selectionHandler)

        cc = make.info_label("TR", [RtRangeSelectionInfo(range_)], title=None)
        widget.plot.add_item(cc)

    def refresh(self):

        if self.selectionNotifier is not None:
            self.selectionNotifier(self.minRT, self.maxRT)


    def selectionHandler(self, obj, min_, max_):
        self.minRT, self.maxRT = sorted((min_, max_))
        if self.selectionNotifier is not None:
            self.selectionNotifier(self.minRT, self.maxRT)

    def setMinimumSize(self, a, b):
        self.widget.setMinimumSize(a,b)
    
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

class MzPlotter(object):

    def __init__(self, peakmap):
        self.peakmap = peakmap 

        widget = CurveWidget(xlabel="m/z", ylabel="I")

        # inject mofified behaviour of wigets plot attribute:
        widget.plot.__class__ = MzPlot
        self.widget = widget


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

    def setMinimumSize(self, a, b):
        self.widget.setMinimumSize(a,b)

    def plot(self, peaks):
        self.curve.set_data(peaks[:, 0], peaks[:, 1])

        self.curve.plot().updateAxes()
        self.curve.plot().replot()
