import userConfig as _userConfig, os
import shutil
_dataHome = _userConfig.getDataHome()

if not os.path.exists(_dataHome):
    os.makedirs(_dataHome)

_flag_file = os.path.join(_dataHome, ".first_init_done")
print "FLAGFILE=", _flag_file

_first_start = not os.path.exists(_flag_file)
print "IS FIRST START=", _first_start

if _first_start:
    # set flag
    _home = os.environ.get("EMZED_HOME")
    _this_emzed_files = os.path.join(_home, "emzed_files")

    for f in os.listdir(_this_emzed_files):
        orig = os.path.join(_this_emzed_files, f)
        if os.path.isfile(orig):
            shutil.copy2(orig, _dataHome)
    open(_flag_file, "w").close()
    os.chdir(_dataHome)
