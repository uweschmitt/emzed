import guiqwt
assert guiqwt.__version__ == "2.1.5", guiqwt.__version__

from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.builder import make
from guiqwt.label import ObjectInfo

from ModifiedGuiQwtBehavior import *
from Config import setupStyleRangeMarker, setupCommonStyle

from PyQt4.Qwt5 import QwtScaleDraw, QwtText

import numpy as np
import new


def formatSeconds(seconds):
    
        hours = int(seconds / 3600)
        remainder = seconds %  3600   # % works for floating point !

        minutes = int(remainder / 60)
        seconds = remainder % 60  

        if hours:
            formatted = "%dh %dm %.1f" % (hours, minutes, seconds)
        elif minutes:
            formatted = "%dm %.1f" % (minutes, seconds)
        else:
            formatted = "%.1f" % seconds
                
        return  formatted.rstrip(".0")+"s"
        

class RtRangeSelectionInfo(ObjectInfo):
    
    def __init__(self, range_):
        self.range_ = range_

    def get_text(self):
        rtmin, rtmax = sorted(self.range_.get_range())
        if rtmin != rtmax:
            return u"RT: %s ... %s" % (formatSeconds(rtmin), formatSeconds(rtmax))
        else:
            return u"RT: %s" % formatSeconds(rtmin)

class PlotterBase(object):

    def __init__(self, xlabel, ylabel):
        self.widget = CurveWidget(xlabel=xlabel, ylabel=ylabel)

    def setXAxisLimits(self, xmin, xmax):
        self.widget.plot.update_plot_xlimits(xmin, xmax)

    def setYAxisLimits(self, ymin, ymax):
        self.widget.plot.update_plot_ylimits(ymin, ymax)

    def setMinimumSize(self, a, b):
        self.widget.setMinimumSize(a,b)

    def reset_x_limits(self, xmin=None, xmax=None, fac=1.0):
        self.widget.plot.reset_x_limits(xmin, xmax, fac)

    def reset_y_limits(self, ymin=None, ymax=None, fac=1.0):
        self.widget.plot.reset_y_limits(ymin, ymax, fac)

    def set_limit(self, ix, value):
        self.widget.plot.set_limit(ix, value)

    def replot(self):
        self.widget.plot.replot()

class RtPlotter(PlotterBase):



    def __init__(self, rangeSelectionCallback = None, numCurves=1, configs=None):
        super(RtPlotter, self).__init__("RT", "I")

        
        self.rangeSelectionCallback = rangeSelectionCallback


        widget = self.widget
        widget.plot.__class__ = RtPlot

        # todo: refactor as helper
        a = QwtScaleDraw()
        a.label = new.instancemethod(lambda self, v: QwtText(formatSeconds(v)), widget.plot, QwtScaleDraw)
        widget.plot.setAxisScaleDraw(widget.plot.xBottom, a)

        self.pm = PlotManager(widget)
        self.pm.add_plot(widget.plot)

        
        self.curves  =[]

        colors = "bgrkcmG"
        for i in range(numCurves):
            c = colors[i % len(colors)] # cycle through colors
            if configs is None or configs[i] is None:
                config = dict()
            else:
                config = configs[i]
            if not "color" in config:
                 config["color"] = c
            curve = make.curve([], [], **config)
            curve.__class__ = ModifiedCurveItem
            widget.plot.add_item(curve)
            self.curves.append(curve)

        t = self.pm.add_tool(RtSelectionTool)
        self.addTool(RtSelectionTool)
        self.pm.set_default_tool(t)

        self.minRTRangeSelected = None
        self.maxRTRangeSelected = None

    def addTool(self, tool):
        t = self.pm.add_tool(tool)
        t.activate()


    def setRtValues(self, rtvalues):

        self.rtvalues = rtvalues
        self.minRTRangeSelected = 0 
        self.maxRTRangeSelected = 0 

        range_ = SnappingRangeSelection(self.minRTRangeSelected, self.maxRTRangeSelected, self.rtvalues)
        setupStyleRangeMarker(range_)
        self.range_ = range_

        # you have to register item to plot before you can register the rtSelectionHandler:
        self.widget.plot.add_item(range_)
        self.widget.connect(range_.plot(), SIG_RANGE_CHANGED, self.rangeSelectionHandler)

        cc = make.info_label("TR", [RtRangeSelectionInfo(range_)], title=None)
        cc.labelparam.label = None
        self.widget.plot.add_item(cc)

    def setRangeSelectionLimits(self, xleft, xright):
        self.minRTRangeSelected = xleft
        self.maxRTRangeSelected = xright
        self.range_.move_point_to(0, (xleft,0), emitsignal=False)  # left and right bar of range marker
        self.range_.move_point_to(1, (xright,0))  # left and right bar of range marker
        # calls self.rangeSelectionHandler !

    def setXAxisLimits(self, xmin, xmax):
        super(RtPlotter, self).setXAxisLimits(xmin, xmax)
        mid = 0.5*(xmin+xmax)
        #self.setRangeSelectionLimits(mid, mid)
    
    def rangeSelectionHandler(self, obj, left, right):
        min_, max_ = sorted((left, right))
        self.minRTRangeSelected = min_
        self.maxRTRangeSelected = max_
        if self.rangeSelectionCallback is not None:
            self.rangeSelectionCallback()
    
    def plot(self, chromatogram, x=None, index=0):
        if x is None:
            x = self.rtvalues
        self.curves[index].set_data(x, chromatogram)

    def replot(self, index=None): 
        if index is None:
            indices = range(len(self.curves))
        else:
            indices = [index]
        for i in indices:
            self.curves[i].plot().replot()
       

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

    def __init__(self, peakmap, c_callback=None):
        super(MzPlotter, self).__init__("m/z", "I")
        self.peakmap = peakmap 

        self.c_callback = c_callback

        widget = self.widget

        # inject mofified behaviour of wigets plot attribute:
        widget.plot.__class__ = MzPlot
        widget.plot.register_c_callback(self.handle_c_pressed)

        # todo: refactor as helper
        a = QwtScaleDraw()
        label = lambda self, x : QwtText("%s" % x)
        a.label = new.instancemethod(label, widget.plot, QwtScaleDraw)
        widget.plot.setAxisScaleDraw(widget.plot.xBottom, a)


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
        label.labelparam.label = None

        widget.plot.add_item(marker)
        widget.plot.add_item(label)
        widget.plot.add_item(line)

    def handle_c_pressed(self, p):
        if self.c_callback:
            self.c_callback(p)
        
    def plot(self, peaks):
        self.curve.set_data(peaks[:, 0], peaks[:, 1])

        self.curve.plot().updateAxes()
        self.curve.plot().replot()

