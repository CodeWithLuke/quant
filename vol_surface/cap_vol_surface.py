import numpy as np
import pandas as pd

class CapVolSurface:

    def __init__(self, expiries, vols):
        self._t = np.array(expiries)
        self._vol = np.array(vols) / 100

    @classmethod
    def from_csv(cls, path):
        df = pd.read_csv(path)

        list_df = df.to_dict('list')

        expiries = list_df['Life']

        vol_data = list_df['Vol']

        return cls(expiries, vol_data)

    def interpolate_vol(self, t):
        s_interp = np.interp(t, self._t, self._vol)
        return s_interp
