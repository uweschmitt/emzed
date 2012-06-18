import userConfig as _userConfig, os
import shutil, glob
_dataHome = _userConfig.getDataHome()

if not os.path.exists(_dataHome):
    os.makedirs(_dataHome)
    
_flag_file = os.path.join(_dataHome, ".first_init_done")

_first_start = not os.path.exists(_flag_file)

if _first_start:
    open(_flag_file, "w").close()
    
    examples = os.path.join(_dataHome, "example_scripts")
    if not os.path.exists(_examples):
	shutil.copytree("example_scripts", _examples)
	for _p in glob.glob("example_scripts/*.mzXML"):
	    shutil.copy(_p, _dataHome)
	for _p in glob.glob("example_scripts/*.csv"):
	    shutil.copy(_p, _dataHome)
    os.chdir(_dataHome)
