from DataStructures import Table

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)


       
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

    app = QApplication([])

    tb = TableDialog(table)
    tb.activateWindow()
    tb.raise_()
    tb.exec_()
