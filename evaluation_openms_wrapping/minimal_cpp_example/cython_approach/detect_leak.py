
import wrap
import win32api
 
def show_mem():
    t = win32api.GlobalMemoryStatus()
    v, p = t['AvailVirtual'], t['AvailPhys']
    v /= 1024.0 * 1024
    p /= 1024.0 * 1024
    print "virtual: %8.2f MB   physical: %8.2f MB" %  (v,p)

show_mem()
wrap.runalot()
show_mem()
