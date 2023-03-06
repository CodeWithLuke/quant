from typing import List, Tuple

import pandas as pd
from scipy.interpolate import griddata

import numpy as np

from utils.constants import BASIS_POINT_CONVERSION


class AtmSwaptionVolSurface:

    def __init__(self, points: List[np.array], data: List[float]):

        self._points = np.array(points)
        self._data = np.array(data)

    @classmethod
    def from_market_data(cls, expiries: List[float], tenors: List[float], vol_data: List[List[float]]):

        points = list()

        data = list()

        for i, expiry in enumerate(expiries):
            for j, tenor in enumerate(tenors):
                points.append(np.array([float(expiry), float(tenor)]))
                data.append(float(vol_data[i][j]) / 100)

        return cls(points, data)

    @classmethod
    def from_csv (cls, path):
        df = pd.read_csv(path, index_col=0)

        split_df = df.to_dict('split')

        expiries = split_df['index']

        tenors = split_df['columns']

        vol_data = split_df['data']

        return cls.from_market_data(expiries, tenors, vol_data)

    def interpolate_vol(self, expiry, tenor):
        return griddata(self._points, self._data, (np.array([expiry]), np.array([tenor])))[0]
