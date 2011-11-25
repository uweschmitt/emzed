import urllib, urllib2
import sys, time, os
import xml.etree.ElementTree  as etree
import cPickle
from ..DataStructures.Table import Table
from ..Chemistry.Tools import monoisotopicMass


class PubChemDB(object):

    colNames = ["m0", "mw", "cid", "mf", "iupac", "synonyms", "url", "is_in_kegg",
                "is_in_hmdb"]
    colTypes = [float, float, str, str, str, str, str, int, int ]
    colFormats=["%.6f", "%.6f", "%s", "%s", "%s", None, "%s", "%d", "%d" ]

    @staticmethod
    def _get_count():
        url="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        data = dict(db="pccompound",
                    rettype="count",
                    term="metabolic[SRCC] AND 0[TFC]",
                    tool="msworkbench",
                    email="tools@ms-workbench.de",
                    )
        req = urllib2.Request(url, urllib.urlencode(data))
        resp = urllib2.urlopen(req)
        doc = etree.fromstring(resp.read())
        counts = doc.findall("Count")
        assert len(counts)==1
        count = int(counts[0].text)
        return count

    @staticmethod
    def _get_uilist(retmax=None, source=None):
        term="metabolic[SRCC] AND 0[TFC]"
        if source is not None:
            term +=' AND "%s"[SRC]' % source
        if retmax is None:
            retmax = 99999999
        data = dict(db="pccompound",
                    rettype="uilist",
                    term=term,
                    retmax=retmax,
                    tool="msworkbench",
                    email="tools@ms-workbench.de",
                    usehistory="Y"
                    )
        url="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        req = urllib2.Request(url, urllib.urlencode(data))
        resp = urllib2.urlopen(req)
        data = resp.read()
        doc = etree.fromstring(data)
        idlist = [id_.text for id_ in  doc.findall("IdList")[0].findall("Id")]
        return idlist

    @staticmethod
    def _get_summary_data(ids):
        data = dict(db="pccompound",
                    tool="msworkbench",
                    email="tools@ms-workbench.de",
                    id=",".join(str(id_) for id_ in ids),
                    version="2.0"
                    )
        url="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        req = urllib2.Request(url, urllib.urlencode(data))
        resp = urllib2.urlopen(req)
        data = resp.read()
        return data

    @staticmethod
    def _parse_data(data, keggIds=None, humanMBdbIds=None):
        doc = etree.fromstring(data)
        items = []
        for summary in doc[0]:
            cid = summary.findall("CID")[0].text
            mw = float(summary.findall("MolecularWeight")[0].text)
            mf = summary.findall("MolecularFormula")[0].text
            iupac = summary.findall("IUPACName")[0].text
            synonyms = ";".join(t.text for t in summary.findall("SynonymList")[0])
            d = dict(cid=cid, mw=mw, mf=mf, iupac=iupac, synonyms=synonyms)
            if keggIds is not None:
                d["is_in_kegg"]=cid in keggIds
            if humanMBdbIds is not None:
                d["is_in_hmdb"]=cid in humanMBdbIds
            items.append((mw, d))
        return items


    @staticmethod
    def _download(idlist, keggIds=None, humanMBdbIds=None):
        print
        print "START DOWNLOAD OF", len(idlist), "ITEMS"
        started = time.time()
        batchsize = 3000
        jobs = [idlist[i:i+batchsize] for i in range(0, len(idlist), batchsize)]
        items = []
        for i, j in enumerate(jobs):
            data = PubChemDB._get_summary_data(j)
            items.extend(PubChemDB._parse_data(data, keggIds, humanMBdbIds))
            print "   %3d %%" % (100.0 * (i+1)/len(jobs)), "done",
            needed = time.time()-started
            time_per_batch = needed / (i+1)
            remaining = time_per_batch * (len(jobs)-i-1)
            print "   end of download in %.fm %.fs" % divmod(remaining, 60)

        needed = time.time()-started
        print
        print "TOTAL TIME %.fm %.fs" % divmod(needed,60)
        return items

    def __init__(self, path=None):
        self.path = path
        if path is not None and os.path.exists(path):
            self.table = cPickle.load(open(path,"rb"))
            self.table.updateIndices()
        else:
            self.table = self._emptyTable()

    def _emptyTable(self):
        return Table(self.colNames, self.colTypes, self.colFormats,[],
                          "PubChem")

    def __len__(self):
        return len(self.table)

    def synchronize(self, maxIds = None):
        print len(self.table), "ITEMS IN LOCAL PUBCHEM DB"
        counts = PubChemDB._get_count()
        print counts, "ITEMS IN GLOBAL PUBCHEM DB"
        unknown = []
        missing = []
        if counts!=len(self.table):
            uis = set(PubChemDB._get_uilist(maxIds))
            known_uis = set(self.table.get(row, "cid") for row in self.table)
            unknown = list(uis - known_uis)
            missing = list(known_uis-uis)
        return unknown, missing

    def reset(self, fetchmax=99999999):
        ids = PubChemDB._get_uilist()
        self.table = self._emptyTable()
        self.update(ids[:fetchmax])
        self.store()

    def massCalculator(self, table, row, name):
        return monoisotopicMass(table.get(row, "mf"))

    def update(self, ids):

        keggids = set(PubChemDB._get_uilist(source="KEGG"))
        hmdbids = set(PubChemDB._get_uilist(source="Human Metabolome Database"))

        print "%d ENTRIES FROM KEGG" % len(keggids)
        print "%d ENTRIES FROM HUMAN METABOLOME DATABASE" % len(hmdbids)

        print "FETCH", len(ids), "ITEMS"
        if ids:
            for mw, dd in PubChemDB._download(ids, keggids, hmdbids):
                row = [ dd.get(n) for n in self.colNames ]
                self.table.rows.append(row)
        try:
            self.table.dropColumn("url")
        except: 
            pass
        try:
            self.table.dropColumn("m0")
        except: 
            pass
        url = "http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid="
        self.table.addColumn("url", url+self.table.cid, type_=str)
        self.table.addColumn("m0", self.massCalculator, type_=float, format="%.7f", insertBefore="mw")
        self.table.sortBy("m0")# build index

    def store(self, path=None):
        if path is None:
            path = self.path
        assert path is not None, "no path given in constructor nor as argument"
        cPickle.dump(self.table, open(path,"wb"))

    def __getattr__(self, colName):
        return getattr(self.table, colName)

