import userConfig as _userConfig, os
import shutil, glob
target = _userConfig.getDataHome()

indicatorFile = os.path.join(target, ".initialized")

if not os.path.exists(indicatorFile):
    for p in glob.glob("example_scripts/*.mzXML"):
        shutil.copy(p, target)

open(indicatorFile, "w").close()

