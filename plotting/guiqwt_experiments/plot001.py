import numpy as np
import guidata
app = guidata.qapplication()

from guiqwt.plot import CurveDialog
widget = CurveDialog(edit=False, toolbar = False)


from guiqwt.builder import make
from guiqwt.shapes import XRangeSelection

class R(XRangeSelection):

    def __init__(self, *a, **kw):
        self._xvals = kw.pop("xvals")
        XRangeSelection.__init__(self, *a, **kw)

    def hit_test(self, pos):
        x = XRangeSelection.hit_test(self, pos)
        print x
        return x

    def move_local_point_to(self, hnd, pos, ctrl=None):
        val = self.plot().invTransform(self.xAxis(), pos.x())
        self.move_point_to(hnd, (val, 0), ctrl)

    def move_point_to(self, hnd, pos, ctrl=None):
        print hnd, pos, ctrl
        val, y = pos
        imin = np.argmin(np.fabs(val-self._xvals))
        pos = self._xvals[imin], y
        if self._min == self._max and not ctrl: 
            XRangeSelection.move_point_to(self, 0, pos, ctrl)
            XRangeSelection.move_point_to(self, 1, pos, ctrl)
        else:    
            XRangeSelection.move_point_to(self, hnd, pos, ctrl)

       
        #self.plot().emit(SIG_RANGE_CHANGED, self, self._min, self._max)
        

    def _x_move_shape(self, old_pos, new_pos):
        if self._min == self._max: return
        return XRangeSelection.move_shape(self, old_pos, new_pos)




x = np.array([0, 1,3,4,6,8,10,12,13])
y = np.sin(x)
curve = make.curve(x,y,"r+")
range_ = R(1,2, xvals=x)

plot = widget.get_plot()

plot.add_item(curve)
plot.add_item(range_)
widget.show()
widget.exec_()

