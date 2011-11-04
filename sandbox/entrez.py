#encoding:latin-1
import urllib, urllib2
import re
import time

# for testing restrict set:
mzmin=""# "100" # ""
mzmax=""# "200" # ""

data = """
EntrezSystem2.PEntrez.Pccompound.PubChem_SearchBar.SearchResourceList:pccompound
EntrezSystem2.PEntrez.Pccompound.PubChem_SearchBar.Term:
EntrezSystem2.PEntrez.Pccompound.PubChem_SearchBar.CurrDb:pccompound
EntrezSystem2.PEntrez.Pccompound.Entrez_PageController.PreviousPageName:limits
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.LimitsField:All+Fields
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_CreateDate_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_CreateDate_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_MW_Min:%s
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_MW_Max:%s
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Heavy_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Heavy_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_XLogP_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_XLogP_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Isotope_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Isotope_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_HBondDonor_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_HBondDonor_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Tautomer_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Tautomer_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_HBondAcceptor_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_HBondAcceptor_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_CovalentUnit_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_CovalentUnit_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_RotBond_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_RotBond_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Complexity_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Complexity_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_TPSA_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_TPSA_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Charge_Min:0
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Charge_Max:0
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Chirality_Rad:no-limit
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_EZ_Rad:no-limit
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Assay_Rad:no-limit
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_TestedConc_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_TestedConc_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_ActiveConc_Min:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_ActiveConc_Max:
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Sources_Mnu:Any
EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.lim_Categories_Mnu:Metabolic Pathways
EntrezSystem2.PEntrez.DbConnector.Db:pccompound
EntrezSystem2.PEntrez.DbConnector.LastDb:pccompound
EntrezSystem2.PEntrez.DbConnector.Term:
EntrezSystem2.PEntrez.DbConnector.LastTabCmd:Limits
EntrezSystem2.PEntrez.DbConnector.LastQueryKey:
EntrezSystem2.PEntrez.DbConnector.IdsFromResult:
EntrezSystem2.PEntrez.DbConnector.LastIdsFromResult:
EntrezSystem2.PEntrez.DbConnector.LinkName:
EntrezSystem2.PEntrez.DbConnector.LinkReadableName:
EntrezSystem2.PEntrez.DbConnector.LinkSrcDb:
EntrezSystem2.PEntrez.DbConnector.Cmd:search
EntrezSystem2.PEntrez.DbConnector.TabCmd:
EntrezSystem2.PEntrez.DbConnector.QueryKey:
p$a:EntrezSystem2.PEntrez.Pccompound.Pccompound_LimitsTab.ApplyLimits
p$l:EntrezSystem2
p$st:entrez
""" % (mzmin, mzmax)

url = 'http://www.ncbi.nlm.nih.gov/sites/entrez'
dd = dict()
for line in data.split("\n"):
    if not line.strip(): continue
    print repr(line)
    k, v = line.split(":")
    dd[k]=v

data = urllib.urlencode(dd)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()

webenv = re.findall("WebEnv=([^;]+)", response.headers["set-cookie"])
if len(webenv)==1:
    print webenv[0]
else:
    raise "wrong response got no webenv"

webenv=webenv[0]

# todo: errorhandling in case of wrong url:
resp = urllib2.urlopen(urllib2.Request("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&query_key=1&WebEnv=%s&report=uilist&mode=text" % webenv))
ids = (map(int, resp.read().split()))
print len(ids), "compounds"
# todo: errorhandling in case of wrong url:
#resp = urllib2.urlopen(urllib2.Request("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&query_key=1&WebEnv=%s&report=docsum&mode=text" % webenv))
#print >> open("docsum.txt","w"), resp.read()

idlist = ids[:20]

#st("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&query_key=1&WebEnv=%s&report=uilist&mode=text" % webenv))
url="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pccompound&id=%s&report=docsum&mode=text" % ",".join(str(i) for i in idlist)
resp = urllib2.urlopen(urllib2.Request(url))
print resp
print resp.read()

