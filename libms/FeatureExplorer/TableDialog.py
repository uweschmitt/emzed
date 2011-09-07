from ..DataStructures import Table
from ..gui import helpers

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import guidata

class TableDialog(QDialog):

    def __init__(self, table, parent=None):
        super(TableDialog, self).__init__(parent)

        assert isinstance(table, Table)

        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Feature Explorer")

        self.table = table

        self.tw = QTableWidget()
        self.setupLayout()
        self.populate()

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)
        
        self.setMinimumWidth(helpers.widthOfTableWidget(self.tw))


       
    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)
        vlayout.addWidget(self.tw)

    def populate(self):
        self.tw.clear()
        self.tw.setSortingEnabled(False)

        self.tw.setRowCount(len(self.table.rows))
    
        self.tw.horizontalHeader().setStretchLastSection(True)
        #self.tw.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        headers = self.table.colNames
        self.tw.setColumnCount(len(headers))
        self.tw.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(self.table.rows):
            for j, (value, format_) in enumerate(zip(row, self.table.colFormats)):
                item = QTableWidgetItem(format_ % value)
                font = item.font()
                font.setFamily("Courier")
                item.setFont(font)
                self.tw.setItem(i, j, item)
 
        self.tw.setSortingEnabled(True)

   




def viewTable(table):
    assert isinstance(table, Table)

    #app = QApplication([])
    app = guidata.qapplication()

    tb = TableDialog(table)
    tb.activateWindow()
    tb.raise_()
    tb.exec_()
