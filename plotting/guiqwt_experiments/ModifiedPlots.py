from exceptions import Exception
from PyQt4.QtCore import Qt
from guiqwt.curve import CurvePlot, CurveItem

from SnappingRangeSelection import SnappingRangeSelection
from guiqwt.shapes import Marker, SegmentShape
import numpy as np

def memoize(function):
  memo = {}
  def wrapper(*args):
    if args in memo:
      return memo[args]
    else:
      rv = function(*args)
      memo[args] = rv
      return rv
  return wrapper


class ModifiedCurvePlot(CurvePlot):


    def do_zoom_view(self, dx, dy, lock_aspect_ratio=False):
        """ modified do_zoom_view such that y=0 stays at bottom of plot """

        dy = dy[0],dy[1], self.transform(0,0) ,dy[3]
        return super(ModifiedCurvePlot, self).do_zoom_view(dx, dy, lock_aspect_ratio)

    def do_pan_view(self, dx, dy):
        """ modified do_zoom_view such that only panning in x-direction happens """

        dy = dy[2],dy[2],dy[2],dy[3]
        return super(ModifiedCurvePlot, self).do_pan_view(dx, dy)


    def do_backspace_pressed(self, filter, evt):
        """ reset axes of plot """

        print "backspace"
        self.reset_x_limits()

    @memoize
    def get_items_of_class(self, clz):
        for item in self.items:
            if isinstance(item, clz):
                yield item

    @memoize
    def get_unique_item(self, clz):
        items = list(self.get_items_of_class(clz))
        if len(items) != 1:
            raise Exception("%d instance(s) of %s among CurvePlots items !" % (len(items), clz))
        return items[0]


    def reset_x_limits(self):

        xvals = []
        Delta = 0
        for item in self.items:
            if isinstance(item, CurveItem):
                x, _ = item.get_data()
                xvals.extend(list(x))

        xmin, xmax = min(xvals), max(xvals)
        self.update_plot_xlimits(xmin, xmax)

    def update_plot_xlimits(self, xmin, xmax):
        _, _, ymin, ymax= self.get_plot_limits()
        self.set_plot_limits(xmin, xmax, ymin, ymax)
        self.setAxisAutoScale(self.yLeft) # y-achse
        self.updateAxes()
        self.replot()


class RtPlot(ModifiedCurvePlot):

    def do_space_pressed(self, filter, evt):
        """ zoom to limits of snapping selection tool """

        item = self.get_unique_item(SnappingRangeSelection)
        if item._min != item._max:
            min_neu = min(item._min, item._max)
            max_neu = max(item._min, item._max)
            self.update_plot_xlimits(min_neu, max_neu)

    def do_enter_pressed(self, filter, evt):
        """ set snapping selection tool to center of actual x-range """

        xmin, xmax, _, _ = self.get_plot_limits()
        mid = (xmin+xmax)/2.0

        item = self.get_unique_item(SnappingRangeSelection)
        item.move_point_to(0, (mid, 0), None)
        item.move_point_to(1, (mid, 0), None)
        filter.plot.replot()

    def do_move_marker(self, evt):
        # do no not move marker !
        pass

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



class MzPlot(ModifiedCurvePlot):

    def label_info(self, curve, x, y):
        return None
        return "m/z=%.6f<br/>I=%.f" % (x,y)

    def on_plot(self, curve, x, y):
        """ callback for marker: dtermine marked point based on cursors coordinates """

        return self.next_peak_to(x, y)

    def next_peak_to(self, x, y):

        item = self.get_unique_item(CurveItem)
        xs, ys = item.get_data()
        # scale + avoid zero division
        xmin, xmax, ymin, ymax = self.get_plot_limits()
        xss = (xs-x) / (xmax-xmin)
        yss = (ys-y) / (ymax-ymin)
        imin = np.argmin(xss**2 + yss**2)
        return xs[imin], ys[imin]


    def do_move_marker(self, evt):

        marker = self.get_unique_item(Marker)
        marker.move_local_point_to(0, evt.pos())
        marker.setVisible(True)
        self.replot()


    def do_space_pressed(self, filter, evt):

        marker = self.get_unique_item(Marker)
        xs, _ = self.get_unique_item(CurveItem).get_data()
        xm = marker.xValue()

        isort = np.argsort(np.abs(xs-xm))
        xsel  = xs[isort[:10]]
        xmin, xmax = np.min(xsel), np.max(xsel)
        
        self.update_plot_xlimits(xmin, xmax)


    def start_drag(self,filter_,evt):

        x = self.invTransform(self.xBottom, evt.x())
        y = self.invTransform(self.yLeft, evt.y())
        self.start_coord = self.next_peak_to(x,y)
        print "started"

    def move_drag(self,filter_,evt):

        x = self.invTransform(self.xBottom, evt.x())
        y = self.invTransform(self.yLeft, evt.y())
        current_coord = self.next_peak_to(x, y)

        line = self.get_unique_item(SegmentShape)
        #print line
        line.set_rect(self.start_coord[0], self.start_coord[1], current_coord[0], current_coord[1])
        line.setVisible(1)

        self.replot()



    def stop_drag(self,filter_,evt):

        line = self.get_unique_item(SegmentShape)
        line.setVisible(0)
        print "stop", line
        self.replot()