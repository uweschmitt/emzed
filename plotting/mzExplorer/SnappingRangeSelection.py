from guiqwt.curve import CurveItem
from guiqwt.shapes import XRangeSelection
from guiqwt.signals import SIG_RANGE_CHANGED

import numpy as np


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


        # TODO: hit_test ?!?!??!


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
        # disabled, that is: do nothing !
        return