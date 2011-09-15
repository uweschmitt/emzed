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

        if table.title is None:
            self.setWindowTitle("Table Explorer")

        else:
            self.setWindowTitle(table.title)

        self.table = table

        self.tw = QTableWidget()
        self.tw.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setupLayout()
        self.populate()

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setSizeGripEnabled(True)

    
        # set optimal window size in two steps:
        self.tw.resizeColumnsToContents()     
        self.setMinimumWidth(helpers.widthOfTableWidget(self.tw))
        #self.tw.horizontalHeader().setResizeMode(QHeaderView.Stretch)

       
    def setupLayout(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)
        vlayout.addWidget(self.tw)

    def populate(self):
        helpers.populateTableWidget(self.tw, self.ftable)


   
def showTable(table):
    assert isinstance(table, Table)

    #app = QApplication([])
    app = guidata.qapplication()

    tb = TableDialog(table)
    tb.activateWindow()
    tb.raise_()
    tb.exec_()
