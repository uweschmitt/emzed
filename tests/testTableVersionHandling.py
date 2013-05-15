import ms
import sys

def test_old():
    print >> sys.stderr, "TEST LOADING OF TABLE FROM EMZED BEFORE 1.3.2"
    t = ms.loadTable("feature_table_before_1.3.2.table")
    assert not hasattr(t, "version"),\
                                   "PLEASE READ cocepts/konzept_table_versions"


def test_1_3_2():
    print >> sys.stderr, "TEST LOADING OF TABLE FROM EMZED 1.3.2"
    t = ms.loadTable("feature_table_1.3.2.table")
    assert t.version == "1.3.2", "PLEASE READ cocepts/konzept_table_versions"

def test_1_3_4():
    print >> sys.stderr, "TEST LOADING OF TABLE FROM EMZED 1.3.4"
    t = ms.loadTable("feature_table_1.3.4.table")
    assert t.version == "1.3.4", "PLEASE READ cocepts/konzept_table_versions"

def test_1_3_5():
    print >> sys.stderr, "TEST LOADING OF TABLE FROM EMZED 1.3.5"
    t = ms.loadTable("feature_table_1.3.5.table")
    assert t.version == "1.3.5", "PLEASE READ cocepts/konzept_table_versions"

def test_1_3_6():
    print >> sys.stderr, "TEST LOADING OF TABLE FROM EMZED 1.3.6"
    t = ms.loadTable("feature_table_1.3.6.table")
    assert t.version == "1.3.6", "PLEASE READ cocepts/konzept_table_versions"
