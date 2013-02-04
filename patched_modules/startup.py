# -*- coding: utf-8 -*-
#
# Copyright © 2009-2011 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""Startup file used by ExternalPythonShell exclusively for IPython sessions
(see spyderlib/widgets/externalshell/pythonshell.py)"""

import sys
import os
import os.path as osp

print "run patched startup"


# Remove this module's path from sys.path:
try:
    sys.path.remove(osp.dirname(__file__))
except ValueError:
    pass


locals().pop('__file__')
__doc__ = ''
__name__ = '__main__'


if os.environ.get('IPYTHON_KERNEL', False):

    # IPython >=v0.11 Kernel
    from IPython.zmq.ipkernel import IPKernelApp
    __ipythonkernel__ = IPKernelApp().instance()
    __ipythonkernel__.initialize(sys.argv[1:])
    __ipythonshell__ = __ipythonkernel__.shell
    __ipythonkernel__.start()

elif os.environ.get('IPYTHON', False):

    sys.path.insert(0, '')
    if os.name == 'nt':
        # Windows platforms: monkey-patching *pyreadline* module
        # to make IPython work in a remote process
        from pyreadline import unicode_helper
        unicode_helper.pyreadline_codepage = "ascii"
        # For pyreadline >= v1.7:
        from pyreadline import rlmain
        class Readline(rlmain.Readline):
            def __init__(self):
                super(Readline, self).__init__()
                self.console = None
        rlmain.Readline = Readline
        # For pyreadline v1.5-1.6 only:
        import pyreadline
        pyreadline.GetOutputFile = lambda: None

    # first modification eMZed # ##############################################
    ###########################################################################

    import traceback
    user_ns = dict()

    import startup # startup folder / package, not startup.py
    import glob
    pattern = os.path.join(os.path.abspath(startup.__path__[0]),"*.py")
    # execute all files in startup
    for python_file in sorted(glob.glob(pattern)):
        user_ns["__file__"] = os.path.abspath(python_file)
        print "STARTUP, EXE", python_file
        execfile(python_file, user_ns)

    try:
        from configs import repositoryPathes
        from string import Template

        for p in reversed(repositoryPathes):
            sys.path.insert(0, Template(p).substitute(os.environ))

    except ImportError, e:
        traceback.print_exc(file=sys.stdout)

    # ipython does not like __builtins__ in namespace:
    if "__builtins__" in user_ns:
        del user_ns["__builtins__"]

    # end of first modification ###############################################
    ###########################################################################

    try:
        # IPython >=v0.11
        # Support for these recent versions of IPython is limited:
        # command line options are not parsed yet since there are still
        # major issues to be fixed on Windows platforms regarding pylab
        # support.
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        banner2 = None
        if os.name == 'nt':
            # Patching IPython to avoid enabling readline:
            # we can't simply disable readline in IPython options because
            # it would also mean no text coloring support in terminal
            from IPython.core.interactiveshell import InteractiveShell, io
            def patched_init_io(self):
                io.stdout = io.IOStream(sys.stdout)
                io.stderr = io.IOStream(sys.stderr)
            InteractiveShell.init_io = patched_init_io
            banner2 = """Warning:
Spyder does not support GUI interactions with IPython >=v0.11
on Windows platforms (only IPython v0.10 is fully supported).

"""
        # second modification eMZed: user_ns arg ##########################
        __ipythonshell__ = InteractiveShellEmbed(banner2=banner2,
                                                 user_ns=user_ns)#,
#                                                 display_banner=False)
#        __ipythonshell__.shell.show_banner()
#        __ipythonshell__.enable_pylab(gui='qt')
        #TODO: parse command line options using the two lines commented
        #      above (banner has to be shown afterwards)
        #FIXME: Windows platforms: pylab/GUI loop support is not working
        __ipythonshell__.stdin_encoding = os.environ['SPYDER_ENCODING']
        del banner2
    except ImportError:
        # IPython v0.10
        import IPython.Shell
        # third modification eMZed: user_ns arg ###########################
        __ipythonshell__ = IPython.Shell.start(user_ns=user_ns)
        __ipythonshell__.IP.stdin_encoding = os.environ['SPYDER_ENCODING']
        __ipythonshell__.IP.autoindent = 0

    # Workaround #2 to make the HDF5 I/O variable explorer plugin work:
    # we import h5py only after initializing IPython in order to avoid
    # a premature import of IPython *and* to enable the h5py/IPython
    # completer (which wouldn't be enabled if we used the same approach
    # as workaround #1)
    # (see sitecustomize.py for the Workaround #1)
    try:
        import h5py  #analysis:ignore
    except ImportError:
        pass

    # fourth modification eMZed # #
    ############################################
    ###########################################################################
    ip = None
    try:
        ip = IPython.ipapi.get()
    except:
        try:
            ip = IPython.core.interactiveshell.InteractiveShell.instance()
        except:
            pass

    if ip:
        for name in ["e", "pi", "path"]:
            try:
                ip.ex("del %s" % name)
            except:
                pass
    __ipythonshell__.mainloop()

    # end of fourth modification ##############################################
    ###########################################################################
