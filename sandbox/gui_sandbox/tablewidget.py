from PyQt4.QtCore import *
from PyQt4.QtGui import *

app = QApplication([])

class Table(QDialog):

    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
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
        self.tw.setRowCount(10)
    
        self.tw.horizontalHeader().setStretchLastSection(True)
        #self.tw.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        headers = "a b c d e".split()
        self.tw.setColumnCount(len(headers))
        self.tw.setHorizontalHeaderLabels(headers)
        
        maxsize = 0
        for i in range(10):
            size = 0
            for j, c in enumerate("abcde"):
                item = QTableWidgetItem((j+1)*c)
                self.tw.setItem(i, j, item)
                size += item.sizeHint().width()
                print size,
            if size>maxsize:
                maxsize = size

        print maxsize
 
        self.tw.setSortingEnabled(True)
        self.setMinimumWidth(maxsize)

   



tb = Table()
tb.show()
tb.exec_()
