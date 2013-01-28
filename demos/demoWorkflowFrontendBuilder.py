import guidata
_app = guidata.qapplication() # not required if a QApplication has already been created

import libms.gui.DialogBuilder as gui

class Test(gui.WorkflowFrontendBuilder):

    parameter = gui.FloatItem("parameter")
    name = gui.StringItem("name")

    method_one = gui.RunJobButton("patricks method")
    method_two = gui.RunJobButton("uwes method", method_name="uwe")

    def run_method_one(self):
        self.name = "patrick"
        self.parameter = "42"
        print "you called method one"
        print "self.name=", self.name
        print "self.parameter=", self.parameter
        print
        

    def uwe(self):
        self.name = "uwe"
        self.parameter = "23"
        print "you called method two"
        print "self.name=", self.name
        print "self.parameter=", self.parameter
        print
        
    def run_method_two(self):
        self.name="what now?"
Test().show()

