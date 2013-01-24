import guidata
_app = guidata.qapplication() # not required if a QApplication has already been created


import libms.gui.DialogBuilder as gui


class Test(gui.WorkflowFrontendBuilder):

    parameter = gui.FloatItem("parameter")
    name = gui.StringItem("name")

    method_one = gui.RunJobButton("patricks method")
    method_two = gui.RunJobButton("uwes method")

    def run_method_one(self):
        print "in method one"
        print "name=", self.name
        print "parameter=", self.parameter
        self.name = "patrick"
        self.parameter = "42"

    def run_method_two(self):
        print "in method two"
        print "name=", self.name
        print "parameter=", self.parameter
        self.name = "uwe"
        self.parameter = "23"

Test().show()

