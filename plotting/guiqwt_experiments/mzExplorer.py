# -*- coding: utf-8 -*-
#
# Copyright © 2009-2010 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see guiqwt/__init__.py for details)

"""Simple filter testing application based on PyQt and guiqwt"""

SHOW = True # Show test in GUI-based test launcher

from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PyQt4.QtCore import SIGNAL

#---Import plot widget base class
from guiqwt.plot import CurveWidget, BaseCurveWidget, PlotManager, SubplotWidget
from guiqwt.builder import make
from guiqwt.curve import CurvePlot, CurveItem
from guiqwt.signals import SIG_RANGE_CHANGED
from guiqwt.shapes import XRangeSelection
from guidata.configtools import get_icon
from guiqwt.tools import *
#---
import numpy as np
import sys, cPickle
import new

sys.path.insert(0, "../../pyOpenMS")


class SnappingRangeSelection(XRangeSelection):

    def __init__(self, min_, max_, xvals):
        super(SnappingRangeSelection, self).__init__(min_, max_)

    def move_local_point_to(self, hnd, pos, ctrl=None):
        val = self.plot().invTransform(self.xAxis(), pos.x())
        self.move_point_to(hnd, (val, 0), ctrl)


    def get_xvals(self):
        xvals = []
        for item in self.plot().get_items():
            if isinstance(item, CurveItem):
                xvals.append(np.array(item.get_data()[0]))
        
        return np.sort(np.hstack(xvals))
        

    def move_point_to(self, hnd, pos, ctrl=None):
        val, y = pos
        xvals = self.get_xvals()

        imin = np.argmin(np.fabs(val-xvals))
        pos = xvals[imin], y
        if self._min == self._max and not ctrl: 
            XRangeSelection.move_point_to(self, 0, pos, ctrl)
            XRangeSelection.move_point_to(self, 1, pos, ctrl)
        else:    
            XRangeSelection.move_point_to(self, hnd, pos, ctrl)

        self.plot().emit(SIG_RANGE_CHANGED, self, self._min, self._max)

    def get_neighbour_xvals(self, x):
        xvals = self.get_xvals()
        imin = np.argmin(np.fabs(x-xvals))
        if imin == 0: return xvals[0], xvals[1]
        if imin == len(xvals)-1 : return xvals[imin-1], xvals[imin] 
        return xvals[imin-1], xvals[imin+1]

        
    def move_shape(self, old_pos, new_pos):
        return

class MzSelectTool(InteractiveTool):
    """
        modified SelectTool from guiqwt.
    """
    TITLE = "mZ Selection"
    ICON = "selection.png"
    CURSOR = Qt.ArrowCursor


    def setup_filter(self, baseplot):
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        ObjectHandler(filter, Qt.LeftButton, start_state=start_state)
        ObjectHandler(filter, Qt.LeftButton, mods=Qt.ControlModifier,
                      start_state=start_state, multiselection=True)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Enter, Qt.Key_Return,)),

                         baseplot.do_enter_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Space,)),
                         baseplot.do_space_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Right,)),
                         baseplot.do_right_pressed, start_state)


        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Left,)),
                         baseplot.do_left_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Backspace,)),
                         baseplot.do_backspace_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch(((Qt.Key_A, Qt.ControlModifier),)),
                         self.select_all_items, start_state)

        return setup_standard_tool_filter(filter, start_state)

    def select_all_items(self, filter, event):
        pass


class ModifiedCurvePlot(CurvePlot):

    
    def do_zoom_view(self, dx, dy, lock_aspect_ratio=False):
        """ modified do_zoom_view such that only zooming in x-direction happens """
   
        dy = dy[2],dy[2],dy[2],dy[3]
        return super(ModifiedCurvePlot, self).do_zoom_view(dx, dy, lock_aspect_ratio)

    def do_pan_view(self, dx, dy):
        """ modified do_zoom_view such that only panning in x-direction happens """

        dy = dy[2],dy[2],dy[2],dy[3]

        return super(ModifiedCurvePlot, self).do_pan_view(dx, dy)

    def do_move_marker(self, evt):
        pass

    def do_space_pressed(self, filter, evt):
        """ zoom to limits of snapping selection tool """

        item = get_unique_item(SnappingRangeSelection)
        if item._min != item._max:
            min_neu = min(item._min, item._max)
            max_neu = max(item._min, item._max)
            self.update_plot_xlimits(min_neu, max_neu)
        
    def do_enter_pressed(self, filter, evt):
        """ set snapping selection tool to center of actual x-range """

        xmin, xmax, _, _ = self.get_plot_limits() 
        mid = (xmin+xmax)/2.0
        
        item = get_unique_item(SnappingRangeSelection)
        item.move_point_to(0, (mid, 0), None)
        item.move_point_to(1, (mid, 0), None)
        filter.plot.replot()
                
    def do_backspace_pressed(self, filter, evt):
        """ reset axes of plot """

        self.reset_x_limits()

    
    def get_items_of_class(self, clz):
        for item in self.items:
            if isinstance(item, clz):
                yield item

    def get_unique_item(self, clz):
        items = list(self.get_items_of_class(clz))
        if len(items)>1:
            raise "more than one %s among CurvePlots items !" % clz
        return items[0]


    def move_selection_bounds(self, evt, filter_, selector):

        shift_pressed =  evt.modifiers() == Qt.ShiftModifier
        alt_pressed =  evt.modifiers() == Qt.AltModifier

        item = self.get_unique_item(SnappingRangeSelection) 
        neu1 = neu0 = None
        if not alt_pressed:
            neu1 = selector(item.get_neighbour_xvals(item._max))
        if not shift_pressed:
            neu0 = selector(item.get_neighbour_xvals(item._min))

        _min, _max = sorted((item._min, item._max))
        if neu0 is not None and (neu0 <= _max or neu0==neu1):

            item.move_point_to(0, (neu0, 0), True)
        if neu1 is not None and (neu1 >= _min or neu0==neu1):
            item.move_point_to(1, (neu1, 0), True)

        filter_.plot.replot()
                    
    def do_left_pressed(self, filter_, evt):
        self.move_selection_bounds(evt, filter_, lambda (a,b): a)

    def do_right_pressed(self, filter_, evt):
        self.move_selection_bounds(evt, filter_, lambda (a,b): b)

    

    def reset_x_limits(self):

        xvals = []
        Delta = 0
        for item in self.items:
            if isinstance(item, CurveItem):
                x, _ = item.get_data()
                xvals.extend(list(x))

        xmin, xmax = min(xvals), max(xvals)

        #xmin -= 0.01 * abs(xmin)
        #xmax += 0.01 * abs(xmax)
        self.update_plot_xlimits(xmin, xmax)

    def update_plot_xlimits(self, xmin, xmax):
        _, _, ymin, ymax= self.get_plot_limits() 
        self.set_plot_limits(xmin, xmax, ymin, ymax)
        self.setAxisAutoScale(0)
        self.updateAxes()
        self.replot()
            

                    
        


    
class TestWindow(QDialog):
    def __init__(self, peakmap):
        QDialog.__init__(self)
    
        self.peakmap = peakmap
        self.rts = np.array([ s.RT for s in self.peakmap ])
        self.chromatogram = np.array([ np.sum(spec.peaks[:,1]) for spec in peakmap])

        self.minRT = np.min(self.rts)
        self.maxRT = self.minRT

        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        self.widget1 = CurveWidget(xlabel="RT", ylabel="log I")
        self.widget2 = CurveWidget(xlabel="m/z", ylabel="log I")


        # inject mofified behaviour:
        self.widget1.plot.__class__ = ModifiedCurvePlot
        self.widget2.plot.__class__ = ModifiedCurvePlot


        self.curve_item1 = make.curve([], [], color='b')
        self.curve_item2 = make.curve([], [], color='b', curvestyle="Sticks")

        self.widget1.plot.add_item(self.curve_item1)
        self.widget2.plot.add_item(self.curve_item2)


        self.pm = PlotManager(self.widget1)
        self.pm.add_plot(self.widget1.plot)
        self.pm.add_plot(self.widget2.plot)
        self.pm.set_default_plot(self.widget1.plot)

        t = self.pm.add_tool(MzSelectTool)
        self.pm.set_default_tool(t)
        t.activate()

        range_ = SnappingRangeSelection(self.minRT, self.maxRT, self.rts)
        self.widget1.plot.add_item(range_)

        cc = make.computation(range_, "TL", "label %s", self.curve_item1, lambda x : x)
        #self.widget1.plot.add_item(cc)

        def release(evt):
            self.updateMZ()
            
        self.widget1.plot.mouseReleaseEvent = release
        
        self.layout().addWidget(self.widget1)
        self.layout().addWidget(self.widget2)

        self.curve_item1.set_data(self.rts, self.chromatogram)
        self.curve_item1.plot().replot()

        self.updateMZ()
    
        self.connect(range_.plot(), SIG_RANGE_CHANGED, self.sighandler)

    def sighandler(self, obj, min_, max_):
        # right handle might be to the left of the left one !
        self.minRT, self.maxRT = sorted((min_, max_))
        self.updateMZ()

    def updateMZ(self):

        si = [ s for s in self.peakmap if self.minRT <= s.RT <=self.maxRT ]

        all_ = np.vstack((s.peaks for s in si))
        all_sorted = all_[np.argsort(all_[:,0]),:]

        self.curve_item2.set_data(all_sorted[:,0], all_sorted[:,1])

        self.curve_item2.plot().updateAxes()
        self.curve_item2.plot().replot()
        
        

def test():
    """Testing this simple Qt/guiqwt example"""
    from PyQt4.QtGui import QApplication

    peakmap = cPickle.load(file("peakmap.pickled", "rb")) 
    
    app = QApplication([])
    win = TestWindow(peakmap)

    win.show()
    app.exec_()
        
        
if __name__ == '__main__':
    test()
    