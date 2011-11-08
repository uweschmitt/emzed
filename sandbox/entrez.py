#encoding:latin-1
import urllib, urllib2
import re
import os.path


class PubChemParser(object):

    def __init__(self):
        self.webenv = None

    def _fetchWebEnv(self):
        # for testing: reduce amount of data by restrictring mz
        # range:
        mzmin=""# "100" # ""
        mzmax=""# "200" # ""
        from entrez_form import data
        data=data % (mzmin, mzmax)
        url = 'http://www.ncbi.nlm.nih.gov/sites/entrez'
        dd = dict()
        for line in data.split("\n"):
            if not line.strip(): continue
            k, v = line.split(":")
            dd[k]=v

        data = urllib.urlencode(dd)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()

        open("last.html","w").write(the_page)

        webenv = re.findall("WebEnv=([^;]+)", response.headers["set-cookie"])
        print webenv
        if len(webenv)!=1:
            raise Exception("wrong response got no webenv / too much webenvs")
        self.webenv=webenv[0]

    def fetchUIList(self):
        if self.webenv is None:
            self._fetchWebEnv()
        data = urllib.urlencode(dict(db="pccompound",
                                     query_key=1,
                                     WebEnv=self.webenv,
                                     usehistory="Y",
                                     report="uilist",
                                     mode="text"))
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        print "%s?%s" %(url,data)
        resp = urllib2.urlopen(urllib2.Request(url, data))
        # returns list of ids, one id per line:
        ids = map(int, resp.read().split())
        return ids


"""
# todo: errorhandling in case of wrong url:
        resp = urllib2.urlopen(urllib2.Request("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&query_key=1&WebEnv=%s&report=docsum&mode=text" % webenv))
        print >> open("sample.docsum","w"), resp.read()
exit()

idlist = ids[:20]

#st("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&query_key=1&WebEnv=%s&report=uilist&mode=text" % webenv))
url="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&id=%s&report=docsum&mode=text" % ",".join(str(i) for i in idlist)
resp = urllib2.urlopen(urllib2.Request(url))
print resp
print >> open("sample.docsum","w"), resp.read()
print
print url

"""

ids = PubChemParser().fetchUIList()
print len(ids)
