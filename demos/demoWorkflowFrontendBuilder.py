import guidata
_app = guidata.qapplication() # not required if a QApplication has already been created

import libms.gui.DialogBuilder as gui

class Test(gui.WorkflowFrontendBuilder):

    parameter = gui.FloatItem("parameter")
    name = gui.StringItem("name")

    method_one = gui.RunJobButton("patricks method")
    method_two = gui.RunJobButton("uwes method", method_name="uwe")

    def run_method_one(self):
        print "you called method one"
        print "self.name=", self.name
        print "self.parameter=", self.parameter
        print
        self.name = "patrick"
        self.parameter = "42"

    def uwe(self):
        print "you called method two"
        print "self.name=", self.name
        print "self.parameter=", self.parameter
        print
        self.name = "uwe"
        self.parameter = "23"

Test().show()

