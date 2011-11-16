#encoding: utf-8
import sys
sys.path.insert(0, "..")

import cProfile

import ms

table = ms.loadTable("features.table")


def integrate(table=table):
    return ms.reintegrate(table, "emg_exakt")

reinttab = integrate()

reinttab.store("integrated_features.table")
