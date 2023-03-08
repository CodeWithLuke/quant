from typing import List

import pandas as pd
from scipy.interpolate import griddata

import numpy as np

from utils.constants import BASIS_POINT_CONVERSION


class AtmSwaptionVolSurface:

    def __init__(self, points: np.array, data: np.array):

        self._points = points
        self._data = data

    @classmethod
    def from_market_data(cls, expiries: List[float], tenors: List[float], vol_data: List[List[float]]):

        points = list()

        data = list()

        for i, expiry in enumerate(expiries):
            for j, tenor in enumerate(tenors):
                points.append(np.array([float(expiry), float(tenor)]))
                data.append(float(vol_data[i][j]) / 100)

        return cls(np.array(points), np.array(data))

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

    def bump_surface(self, n_bps_bump=1):

        bumped_surfaces = {}

        bump = n_bps_bump * BASIS_POINT_CONVERSION ** 2

        for i, point in enumerate(self._points):

            data = self._data.copy()

            data[i] += bump

            bumped_surfaces[tuple(point)] = AtmSwaptionVolSurface(self._points.copy(), data)

        return bumped_surfaces
