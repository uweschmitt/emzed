
import wrap
import win32api
 
def show_mem():
    t = win32api.GlobalMemoryStatus()
    v, p = t['AvailVirtual'], t['AvailPhys']
    v /= 1024.0 * 1024
    p /= 1024.0 * 1024
    print "virtual: %8.2f MB   physical: %8.2f MB" %  (v,p)


def test2():
    s = "abcd0"*1000
    it = wrap.PyItem()
    for i in range(1000):
        it.setD(s)

        


def test3():
    for i in range(1000):
            cc = wrap.PyContainer()
            wrap.fill(1000, cc)
            items = cc.getItems()
            


print
show_mem()
test3()
show_mem()
    
print
show_mem()
test2()
show_mem()
    
        
print
show_mem()
wrap.runalot()
show_mem()



