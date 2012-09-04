import userConfig as _userConfig, os
import shutil
_dataHome = _userConfig.getDataHome()

if not os.path.exists(_dataHome):
    os.makedirs(_dataHome)

_flag_file = os.path.join(_dataHome, ".first_init_done")

_first_start = not os.path.exists(_flag_file)


if _first_start:
    # set flag
    open(_flag_file, "w").close()
    _this_path, _  = os.path.split(os.path.abspath(__file__))
    _this_emzed_files = os.path.join(_this_path, "..", "emzed_files")

    for f in os.listdir(_this_emzed_files):
        orig = os.path.join(_this_emzed_files, f)
        if os.path.isfile(orig):
            shutil.copy2(orig, _dataHome)
    os.chdir(_dataHome)
