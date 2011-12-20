# encoding: utf-8
import inspect, sys

from config_logger import do_config
do_config()

def replace( orig_func, target=None, verbose=False):

    def decorator(new_func, target=target):
        def wrapper(*a, **kw):
            return new_func(*a, **kw)

        wrapper.isPatched = True
        if inspect.ismethod(orig_func):
            if target is None:
                target =  orig_func.im_class
            setattr(target, orig_func.__name__, wrapper)
            setattr(target, "_orig_%s" % orig_func.__name__, orig_func)
        elif inspect.isfunction(orig_func):
            if target is None:
                target = sys.modules[orig_func.__module__]
            setattr(target, orig_func.func_name, wrapper)
            setattr(target, "_orig_%s" % orig_func.__name__, orig_func)
        else:
            raise Exception("can not wrap %s " % orig_func)
        return wrapper # not needed as new_func is not modified at all
    return decorator


def add(target, verbose=False):

    def decorator(new_func, target=target):
        #LLL.debug("add %s to %s" % (new_func, target))
        setattr(target, new_func.__name__, new_func)
    return decorator

def patch_oedit():
    # runs in external console, is triggered if someone clickst at items
    # in the variable explorer (aka namespace explorer)
    from  spyderlib.widgets import objecteditor

    @replace(objecteditor.dialog_for, verbose=True)
    def dialog_for(obj, obj_name):

        # for faster startup import appear not at top of file but here:
        import libms.Explorers
        from libms.DataStructures import PeakMap, Table

        if isinstance(obj, PeakMap):
            dlg = libms.Explorers.MzExplorer()
            dlg.setup(obj)
            return dlg, lambda x: x

        elif isinstance(obj, Table):
            dlg = libms.Explorers.TableExplorer([obj], False)
            return dlg, lambda x: [x]

        elif isinstance(obj, list) and all(isinstance(t, Table) for t in obj):
            dlg = libms.Explorers.TableExplorer(obj, False)
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
        for i, p in enumerate(pathlist):
            # replace path to ../externalshell/ with path to
            # patched_modules/
            if "externalshell" in p:
                # as we do not know "where we are", we take the
                # path to externalshell/ and walk three levels up:
                startupdir = os.sep.join(p.split(os.sep)[:-3])
                pathlist[i] = os.path.join(startupdir, "patched_modules")
        return baseshell._orig_add_pathlist_to_PYTHONPATH(env, pathlist)

def patch_userconfig():
    from spyderlib.userconfig import UserConfig, NoDefault
    @replace(UserConfig.get)
    def patch(self, section, option, default=NoDefault):
        override_defaults = {
            ("console" ,"pythonstartup/default") : True,
            ("console" ,"pythonstartup/custom") : False,
            ("console" ,"pythonstartup/custom") : False,
            ("console" ,"open_ipython_at_startup") : True,
            ("console" ,"open_python_at_startup") : False,
            # automatic imports are slow and insecure :
            ("inspector", "automatic_import") : False,
        }

        value = override_defaults.get((section,option))
        if value is not None:
            print "override default for", section, option, value
            return value
        return UserConfig._orig_get(self, section, option, default)

def patch_baseconfig():
    from spyderlib import baseconfig
    @replace(baseconfig.get_module_source_path, verbose=True)
    def patch(modname, basename=None):
        if modname == "spyderlib.widgets.externalshell"\
            and basename=="startup.py":
            import os
            return os.path.join(os.environ.get("MSWORKBENCH_HOME"),
                                "patched_modules",
                                "startup.py")
        return baseconfig._orig_get_module_source_path(modname, basename)


def patch_spyder():
    patch_userconfig()
    patch_baseconfig()

    # the following path must appear before patching Externalshell, as the
    # corresponding import of ExternalConsole implies import of baseshell. So
    # patching baseshell will not work, as it is registered in sys.modules in
    # unpatched version !
    patch_baseshell()

    from  spyderlib.widgets.dicteditor import RemoteDictEditorTableView
    @replace(RemoteDictEditorTableView.oedit_possible, verbose=True)
    def oedit_possible(self, key):
        return self.is_peakmap(key) \
            or self.is_table(key) \
            or self.is_tablelist(key) \
            or RemoteDictEditorTableView._orig_oedit_possible(self, key)

    from spyderlib.widgets.externalshell.monitor import communicate
    from spyderlib.widgets.externalshell.namespacebrowser\
                                                 import NamespaceBrowser

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
    def is_tablelist(self, name):
        """Return True if variable is a PeakMap"""
        return communicate(self._get_sock(),
            "isinstance(globals()['%s'], list) "\
            "and all(isinstance(li, libms.DataStructures.Table "\
            "        for li in globals()['%s'])")

    @replace(NamespaceBrowser.setup, verbose=True)
    def setup(self, *a, **kw):
        NamespaceBrowser._orig_setup(self, *a, **kw)
        self.editor.is_peakmap = self.is_peakmap
        self.editor.is_table = self.is_table
        self.editor.is_tablelist = self.is_tablelist

    @replace(NamespaceBrowser.import_data, verbose=True)
    def import_data(self, filenames=None):
        NamespaceBrowser._orig_import_data(self, filenames)
        self.save_button.setEnabled(self.filename is not None)

    from spyderlib.widgets.externalshell.monitor import REMOTE_SETTINGS
    @add(NamespaceBrowser, verbose=True)
    def get_view_settings(self):
        """Return dict editor view settings"""
        settings = {}
        for name in REMOTE_SETTINGS:
            settings[name] = getattr(self, name)
        return settings

    @add(NamespaceBrowser, verbose=True)
    def get_remote_view_settings(self):
        """Return dict editor view settings for the remote process,
        but return None if this namespace browser is not visible (no need
        to refresh an invisible widget...)"""
        if self.is_visible and self.isVisible():
            return self.get_view_settings()

def patch_external_shell():

    from  spyderlib.widgets import dicteditorutils
    @replace(dicteditorutils.is_supported, verbose=True)
    def is_supported( value, *a, **kw):
        import libms.DataStructures
        return dicteditorutils._orig_is_supported(value, *a, **kw) \
            or isinstance(value, libms.DataStructures.PeakMap) \
            or isinstance(value, libms.DataStructures.Table)

    @replace(dicteditorutils.get_size, verbose=True)
    def get_size( item ):
        import libms.DataStructures
        if isinstance(item, libms.DataStructures.PeakMap):
            return len(item)
        if isinstance(item, libms.DataStructures.Table):
            return len(item)
        return dicteditorutils._orig_get_size(item)

    @replace(dicteditorutils.get_type_string, verbose=True)
    def get_type_string( item ):
        from libms.DataStructures import Table, PeakMap
        if isinstance(item, list) and any(isinstance(ii, Table) for ii in item):
            return "[Table, ...]"
        if isinstance(item, PeakMap):
            return "PeakMap"
        if isinstance(item, Table):
            return "Table"
        return dicteditorutils._orig_get_type_string(item)

    @replace(dicteditorutils.value_to_display, verbose=True)
    def  value_to_display(value, *a, **kw):
        from libms.DataStructures import Table, PeakMap
        import os

        trunc_len = kw.get("trunc_len", 80)
        truncate = kw.get("truncate", False)
        def trunc(what, trunc_len=trunc_len, truncate=truncate):
            if truncate and len(what)>trunc_len:
               return "..."+ res[(len(what) + 3 - trunc_len):]
            return what

        if isinstance(value, PeakMap):
            try:
                return trunc(value.meta.get("source", ""))
            except Exception, e:
                return "exception: "+e.message

        if isinstance(value, list) and\
           any(isinstance(ii, Table) for ii in value):
           names = [os.path.basename(d.title) for d in value
                                              if isinstance(d, Table)]
           prefix = os.path.commonprefix(names)
           if len(prefix) == 0:
               res = ", ".join(names)
           else:
               res = prefix+"*"
           return "[%s]" % trunc(res, trunc_len=trunc_len-2)

        if isinstance(value, Table):
            if value.title:
                res = value.title
            else:
                try:
                    res = os.path.basename(value.meta.get("source", ""))
                except Exception, e:
                    return "exception: "+e.message
            return trunc(res)
        return dicteditorutils._orig_value_to_display(value, *a, **kw)

    patch_oedit()
    __builtins__["__msworkbench_patched_applied"] = True
