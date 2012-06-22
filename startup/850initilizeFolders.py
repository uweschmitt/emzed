import userConfig as _userConfig, os
import shutil, glob
_dataHome = _userConfig.getDataHome()

if not os.path.exists(_dataHome):
    os.makedirs(_dataHome)
    
_flag_file = os.path.join(_dataHome, ".first_init_done")

_first_start = not os.path.exists(_flag_file)

if _first_start:
    # set flag
    open(_flag_file, "w").close()
    os.chdir(_dataHome)
    shutil.copytree("emzed_files", _dataHome)
