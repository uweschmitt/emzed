#encoding: latin-1
import logging
logging.basicConfig(level=logging.DEBUG,\
                    format='%(asctime)s - %(levelname)s - %(message)s')


from libms.RConnect import RExecutor
from userConfig import getExchangeFolder, getRLibsFolder
exchangeFolderAvailable = getExchangeFolder() is not None

if not exchangeFolderAvailable:
    print "no xcms upgrade as exchange folder is not available"

else:

    r_libs = getRLibsFolder().replace("\\", "\\\\")

    script = """
     todo <- install.packages("Rcpp_0.9.10.zip", repos=NULL, lib="%s")
     q(status=length(todo))
    """ % (r_libs, )

    print RExecutor().run_command(script)


# vim: ts=4 et sw=4 sts=4

