# -*- coding: utf-8 -*-

from PyQt4.QtGui import QVBoxLayout, QDialog

from guiqwt.plot import CurveWidget, PlotManager
from guiqwt.builder import make
from guiqwt.tools import SelectTool

import numpy as np
    
class TestDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
    
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)

        self.widget = CurveWidget()
        self.curve_item = make.curve([], [], color='b')
        self.widget.plot.add_item(self.curve_item)


        self.pm = PlotManager(self.widget)
        self.pm.add_plot(self.widget.plot)

        t = self.pm.add_tool(SelectTool)
        self.pm.set_default_tool(t)
        t.activate()

        def dce(evt):
            print evt.pos()
            plot = self.curve_item.plot()
            print plot.invTransform(self.curve_item.xAxis(), evt.x())
            print plot.invTransform(self.curve_item.yAxis(), evt.y())
            print
            
        self.widget.plot.canvas().mouseReleaseEvent = dce
        
        self.layout().addWidget(self.widget)
        self.update_curve()
        
    def update_curve(self):

        x = np.arange(0,10,.1)
        y = np.sin(np.sin(x))+1
            
        self.curve_item.set_data(x, y)
        self.curve_item.plot().replot()
        
        

        
        
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication

    app = QApplication([])
    win = TestDialog()

    win.show()
    app.exec_()
    
