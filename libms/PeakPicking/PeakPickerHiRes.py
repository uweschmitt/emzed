import pyOpenMS
from ..DataStructures import PeakMap

class PeakPickerHiRes(object):

    standardConfig = dict(ms1_only=False, signal_to_noise = 1.0)

    def __init__(self, **modified_config):
        self.pp = pyOpenMS.PeakPickerHiRes()
        params = self.pp.getParameters()
        config = self.standardConfig
        config.update(modified_config)
        for k, v in config.items():
            if type(v) not in [int, float]:
                v = str(v)
            value = pyOpenMS.DataValue(v)
            params.setValue(pyOpenMS.String(k), value, pyOpenMS.String(), 
                            pyOpenMS.StringList())

    def pickPeakMap(self, pm, show_progress=False):
        assert isinstance(pm, PeakMap)
        eout = pyOpenMS.MSExperiment()
        self.pp.pickExperiment(pm.toMSExperiment(), eout)
        return PeakMap.fromMSExperiment(eout)

