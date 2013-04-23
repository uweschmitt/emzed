#encoding:latin-1
import requests
import urllib2
import userConfig
from collections import OrderedDict

from ..DataStructures.Table import Table


class MetlinMatcher(object):

    col_names = [ "formula", "mass", "name", "molid"]
    col_types = [ str, float, str, int]
    col_formats = [ "%s", "%.5f", "%s", "%d" ]

    batch_size = 90 # should be 500 as metlin promises, but this is false

    # the REST webserive of METLIN returns a result set which does not explain
    # which combination of theoretical mass and adduct results in a match,
    # which is not what we want.  eg one gets the same result set for
    # masses=[195.0877, 194.07904], adducts=["M"] and for masses=[195.0877],
    # adducts = ["M", "M+H"]
    # so we start a separate query for mass and each adduct !

    @staticmethod
    def _query(masses, adduct, ppm):

        token = userConfig.getMetlinToken()

        url = "http://metlin.scripps.edu/REST/search/index.php"
        params = OrderedDict()
        params["token"] = token # "DqeN7qBNEAzVNm9n"
        params["mass[]"] = masses
        params["adduct[]"] = [adduct]
        params["tolunits"] = "ppm"
        params["tolerance"] = ppm

        #r = requests.post(url, data=params)
        r = requests.get(url, params=params)
        #print r
        #print urllib2.unquote(r.url)
        #print r.status_code
        if r.status_code != 200:
            raise Exception("matlin query %s failed: %s" %
                                              (urllib2.unquote(r.url), r.text))

        j = r.json()
        # TODO: token via config + fehlermeldung falls nicht vorhanden
        # TODO: requests module in setup !?

        # TODO: aksFor... udn DialogBUilder: pathes nach latin-1 encoden ?
        # oder: fuer unicode tabellenspaltentyp kein "type=None" ?

        col_names = MetlinMatcher.col_names
        col_types = MetlinMatcher.col_types
        col_formats = MetlinMatcher.col_formats
        tables = []
        for m_z, ji in zip(masses, j):
            rows = []
            for jii in ji:
                rows.append([t(jii[n]) for t, n in zip(col_types, col_names)])

            if rows:
                ti = Table(col_names, col_types, col_formats, rows[:])
                ti.addColumn("m_z", m_z, insertBefore=0)
                ti.addColumn("adduct", adduct, insertBefore=1)
                tables.append(ti)
        return tables

    @staticmethod
    def query(masses, adducts, ppm):
        all_tables = []
        for adduct in adducts:
            for i0 in range(0, len(masses), MetlinMatcher.batch_size):
                mass_slice = masses[i0:i0 + MetlinMatcher.batch_size]
                tables = MetlinMatcher._query(mass_slice, adduct, ppm)
                all_tables.extend(tables)
        result_table = all_tables[0]
        result_table.append(all_tables[1:])

        return result_table



if 0:
    t = MetlinMatcher.query(["282.222813", "292.229272"], 50, "-")
    t.info()

    t._print()



