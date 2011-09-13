# encoding: utf-8

from  spyderlib.widgets import objecteditor
from  spyderlib.widgets import dicteditorutils
from  spyderlib.widgets.dicteditor import RemoteDictEditorTableView
from  spyderlib.widgets.externalshell.namespacebrowser import NamespaceBrowser
from  spyderlib.widgets.externalshell.monitor import REMOTE_SETTINGS


from libms.intern_utils.patch_decorator import  replace, add


import libms.pyOpenMS
import libms.Explorers
from  libms.gui.TableDialog import TableDialog
import libms.DataStructures

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
            dlg = libms.Explorers.MzExplorer()
            dlg.setup(obj)
            return dlg, lambda x: x

        elif isinstance(obj, libms.DataStructures.FeatureTable):
            dlg = libms.Explorers.FeatureExplorer(obj)
            return dlg, lambda x: x

        elif isinstance(obj, libms.DataStructures.Table):
            dlg = TableDialog(obj)
            return dlg, lambda x: x

        return objecteditor._orig_dialog_for(obj, obj_name)

def patch_spyder():

    patch_oedit()

    @replace(RemoteDictEditorTableView.oedit_possible, verbose=True)
    def oedit_possible(self, key):
        return self.is_peakmap(key) \
            or self.is_table(key) \
            or self.is_featureTable(key) \
            or RemoteDictEditorTableView._orig_oedit_possible(self, key)

    from spyderlib.widgets.externalshell.monitor import communicate

    @add(NamespaceBrowser, verbose=True)
    def is_peakmap(self, name):
        """Return True if variable is a PeakMap"""
        return communicate(self._get_sock(),
                   "isinstance(globals()['%s'], (libms.pyOpenMS.PeakMap))" % name)

    @add(NamespaceBrowser, verbose=True)
    def is_table(self, name):
        """Return True if variable is a PeakMap"""
        return communicate(self._get_sock(),
                   "isinstance(globals()['%s'], (libms.DataStructures.Table))" % name)

    @add(NamespaceBrowser, verbose=True)
    def is_featureTable(self, name):
        """Return True if variable is a PeakMap"""
        return communicate(self._get_sock(),
                   "isinstance(globals()['%s'], (libms.DataStructures.FeatureTable))" % name)

    @replace(NamespaceBrowser.setup, verbose=True)
    def setup(self, *a, **kw):
        NamespaceBrowser._orig_setup(self, *a, **kw)
        self.editor.is_peakmap = self.is_peakmap
        self.editor.is_table = self.is_table
        self.editor.is_featureTable = self.is_featureTable

    @add(NamespaceBrowser, verbose=True)
    def get_remote_view_settings(self):
        """Return dict editor view settings for the remote process,
        but return None if this namespace browser is not visible (no need 
        to refresh an invisible widget...)"""
        if self.is_visible and self.isVisible():
            return self.get_view_settings()
        
    @add(NamespaceBrowser, verbose=True)
    def get_view_settings(self):
        """Return dict editor view settings"""
        settings = {}
        for name in REMOTE_SETTINGS:
            settings[name] = getattr(self, name)
        return settings

    patch_startup_file()


def patch_external_shell():
    
    @replace(dicteditorutils.is_supported, verbose=True)
    def is_supported( value, *a, **kw):
        return dicteditorutils._orig_is_supported(value, *a, **kw) \
            or isinstance(value, libms.pyOpenMS.PeakMap) \
            or isinstance(value, libms.DataStructures.Table) \
            or isinstance(value, libms.DataStructures.FeatureTable)

    @replace(dicteditorutils.get_size, verbose=True)
    def get_size( item ):
        if isinstance(item, libms.pyOpenMS.PeakMap):
            return len(item)
        if isinstance(item, libms.DataStructures.Table):
            return len(item)
        if isinstance(item, libms.DataStructures.FeatureTable):
            return len(item)
        return dicteditorutils._orig_get_size(item)

    @replace(dicteditorutils.get_type_string, verbose=True)
    def get_type_string( item ):
        if isinstance(item, libms.pyOpenMS.PeakMap):
            return "libms.pyOpenMS.PeakMap"
        if isinstance(item, libms.DataStructures.FeatureTable):
            return "libms.DataStructures.FeatureTable"
        if isinstance(item, libms.DataStructures.Table):
            return "libms.DataStructures.Table"
        return dicteditorutils._orig_get_type_string(item)


    @replace(dicteditorutils.value_to_display, verbose=True)
    def  value_to_display(value, *a, **kw):
        if isinstance(value, libms.pyOpenMS.PeakMap):
            return  "%s" % value.meta
        if isinstance(value, libms.DataStructures.FeatureTable):
            return "%r" % value.title
        if isinstance(value, libms.DataStructures.Table):
            return "%r" % value.title
        return dicteditorutils._orig_value_to_display(value, *a, **kw)

    patch_oedit()



