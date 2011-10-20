# encoding: utf-8

from  spyderlib.widgets import objecteditor
from  spyderlib.widgets import dicteditorutils
from  spyderlib.widgets.dicteditor import RemoteDictEditorTableView
from  spyderlib.widgets.externalshell.namespacebrowser import NamespaceBrowser
from  spyderlib.widgets.externalshell.monitor import REMOTE_SETTINGS



from libms.intern_utils.patch_decorator import  replace, add


import libms.Explorers
from  libms.gui.TableDialog import TableDialog
import libms.DataStructures

import sys

def patch_startup_file():
    # modifies import in spyderlib\widgets\externalshell\pythonshell.py
    from patched_modules import patched_startup
    patched_mod = sys.modules["patched_modules.patched_startup"]
    sys.modules["spyderlib.widgets.externalshell"].startup = patched_mod
    
def patch_oedit():
    """
    """

    @replace(objecteditor.dialog_for, verbose=True)
    def dialog_for(obj, obj_name):

        if isinstance(obj, libms.DataStructures.PeakMap):
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

def patch_baseshell():
    # modifies assembly of PYTHONPATH before starting the external
    # shell in spyderlib\widgets\externalshell\pythonshell.py
    # so the sitecustomize will be loaded from patched_modules\
    # and not from spyderlib\widgets\externalshell\
 
    import spyderlib.widgets.externalshell.baseshell as baseshell
    import os.path
    @replace(baseshell.add_pathlist_to_PYTHONPATH, verbose=True)
    def patched(env, pathlist):
        print
        print "add_pathlist_to_PYTHONPATH"
        print
        for i, p in enumerate(pathlist):
            # replace path to ../externalshell/ with path to
            # patched_modules/
            if "externalshell" in p:
                # as we do not know "where we are", we take the
                # path to externalshell/ and walk three levels up:
                startupdir = os.sep.join(p.split(os.sep)[:-3])
                pathlist[i] = os.path.join(startupdir, "patched_modules")
        print "PATCHED ", pathlist
        return baseshell._orig_add_pathlist_to_PYTHONPATH(env, pathlist)

def patch_spyder():

    # the following path must appear before patching Externalshell, as the
    # corresponding import of ExternalConsole implies import of baseshell. So
    # patching baseshell will not work, as it is registered in sys.modules in
    # unpatched version !
    patch_baseshell() 
    patch_startup_file()
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
                   "isinstance(globals()['%s'], (libms.DataStructures.PeakMap))" % name)

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

    @replace(NamespaceBrowser.import_data, verbose=True)
    def import_data(self, filenames=None):
        NamespaceBrowser._orig_import_data(self, filenames)
        self.save_button.setEnabled(self.filename is not None)


    from  spyderlib.plugins.externalconsole import ExternalConsole
    @replace(ExternalConsole.get_default_ipython_options, verbose=True)
    def get_default_ipython_options(self):
        options = ExternalConsole._orig_get_default_ipython_options(self)
        return options.replace("-pylab", "")

def patch_external_shell():
    
    @replace(dicteditorutils.is_supported, verbose=True)
    def is_supported( value, *a, **kw):
        return dicteditorutils._orig_is_supported(value, *a, **kw) \
            or isinstance(value, libms.DataStructures.PeakMap) \
            or isinstance(value, libms.DataStructures.Table) \
            or isinstance(value, libms.DataStructures.FeatureTable)

    @replace(dicteditorutils.get_size, verbose=True)
    def get_size( item ):
        if isinstance(item, libms.DataStructures.PeakMap):
            return len(item)
        if isinstance(item, libms.DataStructures.Table):
            return len(item)
        if isinstance(item, libms.DataStructures.FeatureTable):
            return len(item)
        return dicteditorutils._orig_get_size(item)

    @replace(dicteditorutils.get_type_string, verbose=True)
    def get_type_string( item ):
        if isinstance(item, libms.DataStructures.PeakMap):
            return "PeakMap"
        if isinstance(item, libms.DataStructures.FeatureTable):
            return "FeatureTable"
        if isinstance(item, libms.DataStructures.Table):
            return "Table"
        return dicteditorutils._orig_get_type_string(item)


    @replace(dicteditorutils.value_to_display, verbose=True)
    def  value_to_display(value, *a, **kw):
        if isinstance(value, libms.DataStructures.PeakMap):
            return  "%s" % value.meta
        if isinstance(value, libms.DataStructures.FeatureTable):
            
            return "%r" %  dict( (k,v) for k, v in value.meta.items() if k in ["source", "reintegrated" ])
        if isinstance(value, libms.DataStructures.Table):
            return "%r" % value.meta.get("source")
        return dicteditorutils._orig_value_to_display(value, *a, **kw)

    patch_oedit()
    __builtins__["__msworkbench_patched_applied"] = True
