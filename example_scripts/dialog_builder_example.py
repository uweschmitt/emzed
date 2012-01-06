import sys
sys.path.insert(0, "..")
import ms

# A simple one, only ask for one integer value:

value = ms.DialogBuilder().addInt("Integer Wert:").addInstruction("Hier Zahlenwert eingeben\nund sonst nix").show()
print "user entered", value

value1, value2 = ms.DialogBuilder().addInt("Integer Wert:")\
                                   .addFloat("Float Value:").show()
print "user entered", value1, value2


# And now a very complex one which shows all supported
# items:

def script(data):
    """ this script is triggered by a button, see below """
    print "script executed, got data"
    print data.float_value
    print data.integer
    print data.text_1
    print data.text_2
    print data.special_mode
    print data.choice_1
    print data.choice_2
    print data.open_file
    print data.open_files
    print data.save_files
    print data.directory

print ms.DialogBuilder("Test")\
        .addFloat("Float Value", min=0.0, help="float input, min=0")\
        .addInt("Integer", min=-3, help="int input, min=-3")\
        .addString("Text #1", default="input string")\
        .addText("Text #2", default="input text")\
        .addBool("Special Mode", default=True)\
        .addChoice("Choice #1", ["one", "two"], default=1)\
        .addMultipleChoice("Choice #2", ["a", "b"], default=[1])\
        .addFileOpen("Open File")\
        .addFilesOpen("Open Files")\
        .addFileSave("Save Files")\
        .addDirectory("Directory")\
        .addButton("Run Script", script)\
        .show()
