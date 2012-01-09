import userConfig as _userConfig
import sys
for path in [ _userConfig.getExchangeFolder(),
        _userConfig.getDataHome()]:
    sys.path.insert(0, path)
