import urllib, urllib2
import sys, time
import xml.etree.ElementTree  as etree
import cPickle


class PubChemDB(object):

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
    def _get_uilist(retmax):
        data = dict(db="pccompound",
                    rettype="uilist",
                    term="metabolic[SRCC] AND 0[TFC]",
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
    def _parse_data(data):
        doc = etree.fromstring(data)
        items = []
        for summary in doc[0]:
            cid = summary.findall("CID")[0].text
            mw = float(summary.findall("MolecularWeight")[0].text)
            mf = summary.findall("MolecularFormula")[0].text
            iupac = summary.findall("IUPACName")[0].text
            synonyms = ";".join(t.text for t in summary.findall("SynonymList")[0])
            d = dict(cid=cid, mw=mw, mf=mf, iupac=iupac, synonyms=synonyms)
            items.append((mw, d))
        return items


    @staticmethod
    def _download(idlist):
        print
        print "START DOWNLOAD OF", len(idlist), "ITEMS"
        started = time.time()
        batchsize = 3000
        jobs = [idlist[i:i+batchsize] for i in range(0, len(idlist), batchsize)]
        items = []
        for i, j in enumerate(jobs):
            data = PubChemDB._get_summary_data(j)
            items.extend(PubChemDB._parse_data(data))
            print "   %3d %%" % (100.0 * (i+1)/len(jobs)), "done",
            needed = time.time()-started
            time_per_batch = needed / (i+1)
            remaining = time_per_batch * (len(jobs)-i-1)
            print "   end of download in %.fm %.fs" % divmod(remaining, 60)

        needed = time.time()-started
        print
        print "TOTAL TIME %.fm %.fs" % divmod(needed,60)
        return items

    @staticmethod
    def load(path):
        try:
            data = cPickle.load(open(path,"rb"))
        except:
            data = []
        return data

    @staticmethod
    def getNewIds(data, maxIds = 9999999):
        print len(data), "ITEMS IN LOCAL PUBCHEM DB"
        counts = PubChemDB._get_count()
        print counts, "ITEMS IN GLOBAL PUBCHEM DB"
        unknown = []
        if counts>len(data):
            uis = set(PubChemDB._get_uilist(maxIds))
            known_uis = set(d.get("cid") for mw, d in data)
            unknown = list(uis - known_uis)
        return unknown

    @staticmethod
    def update(path, data, ids):
        print "FETCH", len(ids), "ITEMS"
        if ids:
            data.extend(PubChemDB._download(ids))
        cPickle.dump(data, open(path,"wb"))

