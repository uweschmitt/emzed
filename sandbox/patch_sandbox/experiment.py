import new


def ispeakmap(self):
    print "ispeakamp", self
    #self.connect()


class Editor(object):

    pass

class NSBOrig(object):

    def __init__(self):
        self.editor = Editor()
    


class NSBPatchOK(object):

    def __init__(self):
        self.editor = Editor()
        #modification !
        self.editor.ispeakmap = self.ispeakmap



class NSBbesser(NSBPatchOK):

    def __init__(self):
        super(NSBbesser, self).__init__()
        self.editor.ispeakmap = self.ispeakmap

NSBPatchOK.ispeakmap = ispeakmap
NSBOrig.ispeakmap = ispeakmap


nsb1 = NSBPatchOK()
print "modifikation ok"
nsb1.editor.ispeakmap()


Editor.ispeakmap = ispeakmap
nsb2 = NSBOrig()
print "not ok"
nsb2.editor.ispeakmap()

NSBOrig= NSBbesser

nsb2 = NSBOrig()
nsb2.editor.ispeakmap()




#EDITOR.ispeakmap = ispeakmap


