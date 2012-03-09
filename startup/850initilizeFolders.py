import userConfig as _userConfig, os
import shutil, glob
_dataHome = _userConfig.getDataHome()

if not os.path.exists(_dataHome):
    os.makedirs(_dataHome)
    _examples = os.path.join(_dataHome, "example_scripts")
    if not os.path.exists(_examples):
        shutil.copytree("example_scripts", _examples)
    for _p in glob.glob("example_scripts/*.mzXML"):
        shutil.copy(_p, _dataHome)
    for _p in glob.glob("example_scripts/*.csv"):
        shutil.copy(_p, _dataHome)

    os.chdir(_dataHome) # first start




