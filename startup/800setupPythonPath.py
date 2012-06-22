import userConfig as _userConfig
import sys
for _path in [ _userConfig.getExchangeFolder(),
               _userConfig.getDataHome(),
             ]:
    sys.path.insert(0, _path)
