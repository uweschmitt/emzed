from libms.Explorers.TableExplorerModel import *
from libms.DataStructures.Table import *
import ms

from PyQt4.QtCore import QAbstractTableModel, Qt, QVariant


class RecordingObject(QAbstractTableModel):

    def __init__(self, *a, **kw):
        super(RecordingObject, self).__init__(*a, **kw)
        self.emptyAccesses()

    def __getattr__(self, what):
        self.accesses.append(what)

    def updateMenubar(self):
        self.accesses.append("updateMenubar")

    def emptyAccesses(self):
        self.accesses = []

def buildTable():
    t = ms.toTable("mz",[1.0, 2.0, None])
    t.addColumn("mzmin", t.mz-0.025)
    t.addColumn("mzmax", t.mz+0.025)

    t.addColumn("rt", [ 10.0, 20.0, None])
    t.addColumn("rtmin", t.rt-1.0)
    t.addColumn("rtmax", t.rt+5.0)

    t.addColumn("peakmap", [ None, (1,2), None])
    return t

def buildTable2():
    t = ms.toTable("mz",[1.0, 2.0, None])
    t.addColumn("mzmin", t.mz-0.025)
    t.addColumn("mzmax", t.mz+0.025)

    t.addColumn("rt", [ 10.0, 20.0, None])
    t.addColumn("rtmin", t.rt-1.0)
    t.addColumn("rtmax", t.rt+5.0)

    t.addColumn("peakmap", [ None, (1,2), None])
    t._renameColumnsUnchecked(mz="mz__1",mzmin="mzmin__1", mzmax="mzmax__1",
                              rt="rt__1", rtmin="rtmin__1", rtmax="rtmax__1",
                              peakmap="peakmap__1")

    return t

def testTable2():
    t = buildTable2()
    recorder = RecordingObject()
    model = TableModel(t, recorder)
    model.table.info()
    assert model.checkForAny("mz", "rt", "rtmin", "rtmax", "mzmin", "mzmax", "peakmap")
    assert model.checkForAny("mz__1")
    assert not model.checkForAny("mz__1", "rt__x")



def testSimpleTable():
    t =buildTable()
    t.info()
    t._print()
    recorder = RecordingObject()
    model = TableModel(t, recorder)
    model.addNonEditable("rtmax")


    assert model.checkForAny("mzmin")
    assert not model.checkForAny("xxx")

    def idx(r,c):
        return model.createIndex(r,c)

    row = model.getRow(0)
    assert row.mz == 1.0
    assert row.mzmin == 0.975
    assert row.mzmax == 1.025

    assert row.rt == 10.0
    assert row.rtmin == 9.0
    assert row.rtmax == 15.0

    assert model.rowCount() == 3
    assert model.columnCount() == 6 # one invisibible column

    for i in range(3):
        for j in range(6):
            val = t.rows[i][j]
            is_ = model.data(idx(i,j))
            tobe = t.colFormatters[j](val)
            assert is_ == tobe, (is_, tobe)

    for i in range(3):
        for j in range(6):
            val = t.rows[i][j]
            is_ = model.data(idx(i,j), Qt.EditRole)
            tobe = t.colFormatters[j](val)
            assert is_ == tobe, (is_, tobe)

    for j in range(6):
        is_ = model.headerData(j, Qt.Horizontal)
        tobe = t.getColNames()[j]
        assert is_ == tobe, (is_, tobe)

    for j in range(6):
        flag = model.flags(idx(0,j))
        if j==5:
            assert flag & Qt.ItemIsEditable == Qt.NoItemFlags
        else:
            assert flag & Qt.ItemIsEditable == Qt.ItemIsEditable

    for i in range(3):
        for j in range(3):
            val = i+j+1.5
            assert model.setData(idx(i,j), QVariant(str(val)))
            is_ = model.data(idx(i,j))
            tobe = t.colFormatters[j](val)
            assert is_ == tobe, (is_, tobe)
        for j in range(3,6):
            val = j*1.0+i
            sv = "%.1fm" % val
            assert model.setData(idx(i,j), QVariant(sv))
            is_ = model.data(idx(i,j))
            tobe = t.colFormatters[j](val*60.0)
            assert is_ == tobe, (is_, tobe)

    assert len(model.actions) == 3*6
    assert recorder.accesses == 3*6 * ["updateMenubar"]
    model.emptyActionStack()

    before = model.data(idx(0,0))
    model.setData(idx(0,0), QVariant("-"))
    assert model.data(idx(0,0)) == "-"
    assert model.table.rows[0][0] == None

    model.undoLastAction()
    assert before == model.data(idx(0,0))
    assert len(model.actions) == 0

    model.redoLastAction()
    assert model.data(idx(0,0)) == "-"
    assert model.table.rows[0][0] == None

    # here no undo !

    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3
    model.cloneRow(0)
    assert model.table.rows[0] == model.table.rows[1]
    assert model.rowCount() == 4
    model.undoLastAction()
    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3

    model.cloneRow(0)
    model.removeRow(0)
    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3

    model.undoLastAction()
    model.undoLastAction()
    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3

    assert len(model.actions) == 1 # 1 undo missing

    model.sort(0, Qt.DescendingOrder)

    assert model.table.mz.values == [ 3.5, 2.5, None]
    model.undoLastAction()
    assert model.table.mz.values == [ None, 2.5, 3.5]

    #assert model.postfixes == [""]

    assert model.hasFeatures()
    assert not model.isIntegrated()



def testMixedRows():
    names = """rt rtmin rtmax rt__1 rtmin__1 rtmax__1
               mz mzmin mzmax mz__1 mzmin__1 mzmax__1
               rt__0 rtmin__0 rtmax__0
               mz__0 mzmin__0 mzmax__0
               rt__2 rtmin__2""".split()

    names = [n.strip() for n in names]

    tab = Table._create(names, [float]*len(names), "%f" * len(names))

    recorder = RecordingObject()
    model = TableModel(tab, recorder)

    #assert model.postfixes == [ "", "__0", "__1", "__2"], model.postfixes

    assert model.table.supportedPostfixes(["rtmin","rt"]) == ["","__0", "__1", "__2"]
    assert model.table.supportedPostfixes(["mz","rt", "mzmin"]) == ["","__0", "__1"]
    assert model.table.supportedPostfixes(["mz","rt", "x"]) == []



