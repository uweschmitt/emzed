from ..DataStructures.Table import Table
from PyQt4.QtGui      import QTableWidgetItem, QHeaderView
from PyQt4.QtCore     import Qt, QSize

def widthOfTableWidget(tw):

    width = 0
    for i in range(tw.columnCount()):
        width += tw.columnWidth(i)

    width += tw.verticalHeader().sizeHint().width()
    width += tw.verticalScrollBar().sizeHint().width()
    width += tw.frameWidth()*2
    return width

class ValuedQTableWidgetItem(QTableWidgetItem):

    """ using this sublcass allows sorting columns in QTableWidget based on
        their numerical value
    """

    def __init__(self, rowIndex, value, *a, **kw):
        super(ValuedQTableWidgetItem, self).__init__(*a, **kw)
        self.rowIndex = rowIndex
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


def populateTableWidget(tWidget, table):
    assert isinstance(table, Table)

    tWidget.clear()
    tWidget.setRowCount(len(table))

    headers = table.getVisibleCols()
    tWidget.setColumnCount(len(headers))
    tWidget.setHorizontalHeaderLabels(headers)

    colidxmap = dict((name, i) for i, name in enumerate(headers))

    tWidget.setSortingEnabled(False)  # needs to be done before filling the table

    for i, row in enumerate(table.rows):
        for value, formatter, type_, colName in zip(row, table.colFormatters,
                                               table.colTypes, table.colNames):
            tosee = formatter(value)
            if tosee is not None:
                item = ValuedQTableWidgetItem(i, value, tosee)
                if len(tosee)>50:
                    item.setSizeHint(QSize(50,-1))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if type_ == float:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                font = item.font()
                font.setFamily("Courier")
                if type_ == str and tosee.startswith("http://"):
                    font.setUnderline(True)
                item.setFont(font)
                j = colidxmap[colName]
                tWidget.setItem(i, j, item)

    tWidget.setSortingEnabled(True)
    # adjust height of rows (normaly reduces size to a reasonable value)
    tWidget.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
    return colidxmap

