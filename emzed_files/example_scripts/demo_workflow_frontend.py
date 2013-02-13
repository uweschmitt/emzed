
import libms.gui.DialogBuilder as gui

class TestFrontend(gui.WorkflowFrontend):
    """TestFrontEnd
    The first line of this docstring appeas as windows title,
    the following text (the text you read right now) appears
    as instrutions at the top of the dialog.
    """

    parameter = gui.FloatItem("parameter")
    name = gui.StringItem("name", notempty=True)
    optional = gui.StringItem("optional")

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
        self.name = "uwe"
        self.parameter = "23"

TestFrontend().show()
