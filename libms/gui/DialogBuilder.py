#encoding: latin-1
import guidata

app = guidata.qapplication()

import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di

from guidata.qt.QtGui import QMessageBox

import string


# monkey patch following Items, else dt.DataSet.check() raises
# exceptions. They are assumed to be valid in any case:
di.BoolItem.check_value = lambda *a, **kw: True
di.ChoiceItem.check_value = lambda *a, **kw: True
di.MultipleChoiceItem.check_value = lambda *a, **kw: True
di.ButtonItem.check_value = lambda *a, **kw: True


def _translateLabelToFieldname(label):
    # translate label strings to python vairable names
    invalid = r"""^°!"\§$%&/()=?´``+*~#'-.:,;<>|@$"""
    trtable = string.maketrans(invalid, " "*len(invalid))
    return label.lower().translate(trtable)\
                .replace("  ", " ")\
                .replace("  ", " ")\
                .replace(" ", "_")\

def showWarning(message):
    guidata.qapplication().beep()
    QMessageBox.warning(None, "Warning", message)

def showInformation(message):
    guidata.qapplication().beep()
    QMessageBox.information(None, "Warning", message)

class DialogBuilder(object):

    def __init__(self, title="Dialog"):

        self.attrnum = 0
        self.title = title
        self.items = []
        self.instructions = []
        self.fieldNames = []
        self.buttonCounter = 0

    def __getattr__(self, name):
        """ dynamically provides methods which start with "add...", eg
            "addInt(....)".

            If one calls

                   b = Builder()
                   b.addInt(params)

            then

                   b.addInt

            is a stub function which is constructed and returned some
            lines below. Then

                   b.addInt(params)

            calls this stub function, which registers the corresponding
            IntItem with the given params.

        """
        if name.startswith("add"):

            def stub(label, *a, **kw):
                """ this function registers corresponding subclass of
                    DataItem
                """
                fieldName = _translateLabelToFieldname(label)
                # check if fieldName is valid in Python:
                try:
                    exec("%s=0" % fieldName) in dict()
                except:
                    raise Exception("converted label %r to field name %r "\
                                    "which is not allowed in python" \
                                    % (label, fieldName))
                # get DataItem subclass
                try:
                    item = getattr(di, name[3:]+"Item")
                except:
                    raise AttributeError("%r has no attribute '%s'"\
                                         % (self, name))
                # construct item
                item = item(label, *a, **kw)
                # regiter item and fieldname
                self.items.append(item)
                self.fieldNames.append(fieldName)
                return self

            return stub
        raise AttributeError("%r has no attribute '%s'" % (self, name))

    def addInstruction(self, what):
        self.instructions.append(what)
        return self

    def addButton(self, label, callback, help=None):
        """ addButton is not handled by __getattr__, as it need special
            handling.

            In contrast to the other DateItem subclasses, ButtonItem
            gets a callback which has to be constructed in a special
            way, see below.
        """

        # the signature of 'wrapped' is dictated by the guidata
        # framework:
        def wrapped(ds, it, value, parent):
            # check inputs before callback is executed
            invalidFields = ds.check()
            if len(invalidFields):
                msg = "The following fields are invalid: \n"
                msg += "\n".join(invalidFields)
                QMessageBox.warning(parent, "Error", msg)
                return
            callback(ds)
        # register ButtomItem in the same way other DataItem subclass
        # instances are registered in the "stub" function in
        # __getattr__:
        item = di.ButtonItem(label, wrapped, help=help)
        self.items.append(item)
        self.fieldNames.append("_button%d" % self.buttonCounter)
        self.buttonCounter += 1
        return self

    def show(self):
        """ opens the constructed dialog.

            In order to d so we construct sublcass of DataSet on the fly.

            the docstring of the class is the title of the dialog,
            class level attributes are instances of sublcasses of
            DataItem, eg IntItem.

            For more info see the docs of guidata how those classes
            are declared to get the wanted dialog.
        """

        # put the class level attributes in a dict
        attributes = dict(zip(self.fieldNames, self.items))
        # construct class "Dialog" which is a sublcass of "dt.DataSet"
        # with the  given attributes:
        clz = type("Dialog", (dt.DataSet,), attributes)
        # as said: the docstring is rendered as the dialogues title:
        clz.__doc__ = self.title+"\n"+"\n".join(self.instructions)
        # open dialog now !!!
        instance = clz()
        if instance.edit() == 0:
            raise Exception("dialog aborted by user")
        # return the values a tuple according to the order of the
        # declared input widgets:
        result = tuple(getattr(instance, name) for name in self.fieldNames)
        if len(result) == 1:
            result = result[0]
        return result



