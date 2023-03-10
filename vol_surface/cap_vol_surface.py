import numpy as np

class CapVolSurface:

    def __init__(self, expiries, vols):
        self._t = np.array(expiries)
        self._vol = np.array(vols)

    @classmethod
    def from_csv(cls, path):
        df = pd.read_csv(path, index_col=0)

        list_df = df.to_dict('list')

        expiries = list_df['Life']

        vol_data = list_df['Vol']

        return cls(expiries, vol_data)

    def interpolate_vol(self, t):
        s_interp = np.interp(t, self._t, self._vol, right=np.nan)
        return s_interp
