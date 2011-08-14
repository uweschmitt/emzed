# encoding: utf-8

from  spyderlib.widgets import objecteditor
from  spyderlib.widgets import dicteditorutils

from local_utils.patch_decorator import  patch

import pyOpenMS


def patch_spyder():
    """

    """
    import mzExplorer

    @patch(objecteditor.dialog_for, verbose=True)
    def dialog_for(obj, obj_name):

        if isinstance(obj, pyOpenMS.PeakMap):
            dlg = mzExplorer.MzExplorer()
            dlg.setup(obj)
            return dlg, lambda x: x
        return objecteditor._orig_dialog_for(obj, obj_name)

def patch_external_shell():
    
    @patch(dicteditorutils.is_supported, verbose=True)
    def is_supported( value, *a, **kw):
        return dicteditorutils._orig_is_supported(value, *a, **kw) or isinstance(value, pyOpenMS.PeakMap)

    @patch(dicteditorutils.get_size, verbose=True)
    def get_size( item ):
        if isinstance(item, pyOpenMS.PeakMap):
            return len(item)
        return dicteditorutils._orig_get_size(item)

    @patch(dicteditorutils.get_type_string, verbose=True)
    def get_type_string( item ):
        if isinstance(item, pyOpenMS.PeakMap):
            return "pyOpenMS.PeakMap"
        return dicteditorutils._orig_get_type_string(item)


    @patch(dicteditorutils.value_to_display, verbose=True)
    def  value_to_display(value, *a, **kw):
        if isinstance(value, pyOpenMS.PeakMap):
            return  "%s" % value.meta
        return dicteditorutils._orig_value_to_display(value, *a, **kw)




