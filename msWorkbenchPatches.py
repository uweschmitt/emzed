# encoding: utf-8

from  spyderlib.widgets import objecteditor
from  spyderlib.widgets import dicteditorutils
from  spyderlib.widgets.dicteditor import RemoteDictEditorTableView
from  spyderlib.widgets.externalshell.namespacebrowser import NamespaceBrowser

from libms.intern_utils.patch_decorator import  replace, add

import libms.pyOpenMS
import libms.mzExplorer
import sys

def patch_startup_file():
    from patched_modules import startup
    patched_mod = sys.modules["patched_modules.startup"]
    sys.modules["spyderlib.widgets.externalshell"].startup = patched_mod
    

def patch_oedit():
    """

    """

    @replace(objecteditor.dialog_for, verbose=True)
    def dialog_for(obj, obj_name):

        if isinstance(obj, libms.pyOpenMS.PeakMap):
            dlg = libms.mzExplorer.MzExplorer()
            dlg.setup(obj)
            return dlg, lambda x: x
        return objecteditor._orig_dialog_for(obj, obj_name)

def patch_spyder():

    patch_oedit()

    @replace(RemoteDictEditorTableView.oedit_possible, verbose=True)
    def oedit_possible(self, key):
        return self.is_peakmap(key) or RemoteDictEditorTableView._orig_oedit_possible(self, key)

    from spyderlib.widgets.externalshell.monitor import communicate

    @add(NamespaceBrowser, verbose=True)
    def is_peakmap(self, name):
        """Return True if variable is a PeakMap"""
        return communicate(self._get_sock(),
                   "isinstance(globals()['%s'], (libms.pyOpenMS.PeakMap))" % name)


    @replace(NamespaceBrowser.setup, verbose=True)
    def setup(self, *a, **kw):
        NamespaceBrowser._orig_setup(self, *a, **kw)
        self.editor.is_peakmap = self.is_peakmap

    patch_startup_file()



def patch_external_shell():
    
    @replace(dicteditorutils.is_supported, verbose=True)
    def is_supported( value, *a, **kw):
        return dicteditorutils._orig_is_supported(value, *a, **kw) or isinstance(value, libms.pyOpenMS.PeakMap)

    @replace(dicteditorutils.get_size, verbose=True)
    def get_size( item ):
        if isinstance(item, libms.pyOpenMS.PeakMap):
            return len(item)
        return dicteditorutils._orig_get_size(item)

    @replace(dicteditorutils.get_type_string, verbose=True)
    def get_type_string( item ):
        if isinstance(item, libms.pyOpenMS.PeakMap):
            return "libms.pyOpenMS.PeakMap"
        return dicteditorutils._orig_get_type_string(item)


    @replace(dicteditorutils.value_to_display, verbose=True)
    def  value_to_display(value, *a, **kw):
        if isinstance(value, libms.pyOpenMS.PeakMap):
            return  "%s" % value.meta
        return dicteditorutils._orig_value_to_display(value, *a, **kw)

    patch_oedit()



