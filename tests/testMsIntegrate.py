try:
    import psyco
    psyco.full()
except:
    pass

import ms

def testIntegration():

    # test with and without unicode:
    ft = ms.loadTable(u"data/features.table")
    # an invalid row should not stop integration, but result
    # in None values for ms.integrate generated columns
    ftr = ms.integrate(ft, "trapez")
    assert len(ftr) == len(ft)
    assert "area" in ftr.getColNames()
    assert "rmse" in ftr.getColNames()
    assert ftr.area.values[0] > 0, ftr.area.values[0]
    assert ftr.rmse.values[0] >= 0, ftr.rmse.values[0]
    assert ftr.params.values[0] is not None
    assert ftr.method.values[0] is not None

    ft.setValue(ft.rows[0], "mzmin", None)

    ft._addColumnWithoutNameCheck("mzmin__0", ft.mzmin)
    ft._addColumnWithoutNameCheck("mzmax__0", ft.mzmax)
    ft._addColumnWithoutNameCheck("rtmin__0", ft.rtmin)
    ft._addColumnWithoutNameCheck("rtmax__0", ft.rtmax)
    ft._addColumnWithoutNameCheck("peakmap__0", ft.peakmap)

    ft.addColumn("mzminX", ft.mzmin)
    ft.addColumn("mzmaxX", ft.mzmax)
    ft.addColumn("rtminX", ft.rtmin)
    ft.addColumn("rtmaxX", ft.rtmax)
    ft.addColumn("peakmapX", ft.peakmap)

    ftr = ms.integrate(ft, "trapez")
    ftr.info()
    assert len(ftr) == len(ft)
    assert "area" in ftr.getColNames()
    assert "rmse" in ftr.getColNames()
    assert "area__0" in ftr.getColNames()
    assert "rmse__0" in ftr.getColNames()
    assert "areaX" in ftr.getColNames()
    assert "rmseX" in ftr.getColNames()

    assert ftr.area.values[0] is None
    assert ftr.rmse.values[0] is None
    assert ftr.params.values[0] is None
    assert ftr.method.values[0] is not None

    assert ftr.area.values[1] >= 0
    assert ftr.rmse.values[1] >= 0
    assert ftr.params.values[1] is not None
    assert ftr.method.values[1] is not  None

    assert ftr.area__0.values[0] is None
    assert ftr.rmse__0.values[0] is None
    assert ftr.params__0.values[0] is None
    assert ftr.method__0.values[0] is not None

    assert ftr.params__0.values[1] is not None
    assert ftr.method__0.values[1] is not None
    assert ftr.area__0.values[1] >= 0
    assert ftr.rmse__0.values[1] >= 0

    assert ftr.areaX.values[0] is None
    assert ftr.rmseX.values[0] is None
    assert ftr.paramsX.values[0] is None
    assert ftr.methodX.values[0] is not None

    assert ftr.paramsX.values[1] is not None
    assert ftr.methodX.values[1] is not None
    assert ftr.areaX.values[1] >= 0
    assert ftr.rmseX.values[1] >= 0

    #ftr.store("../doublefeat.table", True)
