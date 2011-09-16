from ..DataStructures import Table
from PyQt4.QtGui      import QTableWidgetItem, QHeaderView
from PyQt4.QtCore     import Qt

def widthOfTableWidget(tw):

    width = 0
    for i in range(tw.columnCount()):
        width += tw.columnWidth(i)

    width += tw.verticalHeader().sizeHint().width()
    width += tw.verticalScrollBar().sizeHint().width()
    width += tw.frameWidth()*2
    return width

class NumericQTableWidgetItem(QTableWidgetItem):

    """ using this sublcass allows sorting columns in QTableWidget based on
        their numerical value 
    """


    def __init__(self, idx, *a, **kw):
        super(NumericQTableWidgetItem, self).__init__(*a, **kw)
        self.idx = idx


    def __lt__(self, other):
        try:
            return float(self.text()) <= float(other.text())
        except:
            return self.text() <= other.text()

def populateTableWidget(tWidget, table):
    assert isinstance(table, Table)

    tWidget.clear()
    tWidget.setRowCount(len(table))

    headers = table.getVisibleCols()
    tWidget.setColumnCount(len(headers))
    tWidget.setHorizontalHeaderLabels(headers)

    tWidget.setSortingEnabled(False)  # needs to be done before filling the table

    for i, row in enumerate(table.rows):
        for j, (value, formatter, type_) in enumerate(zip(row, table.colFormatters, table.colTypes)):
            tosee = formatter(value) 
            if tosee is not None:
                item = NumericQTableWidgetItem(i, tosee)
                item.setData(Qt.UserRole, value)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if type_ == float:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                font = item.font()
                font.setFamily("Courier")
                item.setFont(font)
                tWidget.setItem(i, j, item)
   
    tWidget.setSortingEnabled(True)
    # adjust height of rows (normaly reduces size to a reasonable value)
    tWidget.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)

