#include <list>
#include <vector>
#include <iostream>
#include <sstream>
#include <string>
#include <OpenMS/DATASTRUCTURES/Param.h>

using namespace std;
using namespace OpenMS;


list<string> getKeys(Param &p)
{
    // workaround da cython probleme mit inneren klassen hat, falls die auessere klasse
    // keine template klasse ist.
    // -> http://groups.google.com/group/cython-users/msg/74f76f92b5305470
    list<string> rv;
    for (Param::ParamIterator pit = p.begin(); pit != p.end(); ++pit)
    {
        ostringstream trace;
        vector<Param::ParamIterator::TraceInfo> tr = pit.getTrace();
        for (vector<Param::ParamIterator::TraceInfo>::iterator tit = tr.begin(); tit != tr.end(); ++tit)
            trace << tit->name<< ":";
        trace << pit->name;
        rv.push_back(trace.str());
    }
    return rv;
}

// workaround: operator++ macht in cython probleme
list<string>::iterator next(list<string>::iterator it)
{
    return ++it;
}
