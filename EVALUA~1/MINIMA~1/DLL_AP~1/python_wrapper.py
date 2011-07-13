#encoding: utf-8

import ctypes as ct
import copy

_lll = ct.CDLL("cdll.dll")

_lll.buildString.argtypes = [ ct.c_char_p ]

import win32api
 
def show_mem():
    t = win32api.GlobalMemoryStatus()
    v, p = t['AvailVirtual'], t['AvailPhys']
    v /= 1024.0 * 1024
    p /= 1024.0 * 1024
    print "virtual: %8.2f MB   physical: %8.2f MB" %  (v,p)


class Container(object):

    def __init__(self):
        self.handle = _lll.buildContainer()
        #print "constructed container", hex(self.handle)

    def __del__(self):
        #print "del container", hex(self.handle)
        _lll.freeContainer(self.handle)

    def addItem(self, item):
        _lll.containerAddItem(self.handle, item.handle)

    def getFront(self):
        return Item(_lll.containerGetFront(self.handle))

    def getBack(self):
        return Item(_lll.containerGetBack(self.handle))

    def __len__(self):
        return _lll.containerSize(self.handle)


class Item(object):

    def __init__(self, handle):
        #print "construct Item ", hex(handle)
        self.handle = handle
        self._freeItem = _lll.freeItem

    @staticmethod
    def build(name):

        bs = _lll.buildString(name)
        handle = _lll.buildItem(bs)
        _lll.freeString(bs)
        return Item(handle)
        
    def getD(self):

        p = _lll.getD(self.handle)
        # laut ctypes/python quellcode wird eine kopie angelegt:
        rv = ct.string_at(p)
        _lll.freeCharArray(p)
        return rv

    def __del__(self):
        #print "del Item ", hex(self.handle)
        # TODO: vor ende a? atexit() `???
        self._freeItem(self.handle)


def filler(n, cont):
    _lll.FillerFiller(n, cont.handle)

        



if __name__ == "__main__":

    def one_run():

        c = Container()

        i = Item.build("name")
        #print "D=", i.getD()
        c.addItem(i)

        fi = c.getFront()
        #print "front =", fi, hex(fi.handle)
        #print "front.D = ", repr(fi.getD())

        # TODO: i löschen
        # was macht der container ???
        #print "size =", len(c)

        #print "fill 100"
        filler(1000, c)
        #print "size =", len(c)
        fi = c.getFront()
        #print "front =", fi, hex(fi.handle)
        #print "front.D = ", repr(fi.getD())

        fi = c.getBack()
        #print "back =", fi, hex(fi.handle)
        #print "back.D = ", repr(fi.getD())

        del c

        #print "back =", fi, hex(fi.handle)
        #print "back.D = ", repr(fi.getD())
    
    def test_mem_leak():

        show_mem()
        for k in range(1000):
            one_run()
        show_mem()


    test_mem_leak()
