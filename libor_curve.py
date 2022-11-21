from typing import List, Dict

import numpy as np


class LiborCurve:
    def __init__(self, curve_points: List[Dict[str, float]]):
        assert any('time' in curve_point and 'spot_rate' in curve_point for curve_point in curve_points)

        get_time = lambda curve_point: curve_point['time']
        self._t = np.array(list(map(get_time, curve_points)))

        get_spot_rate = lambda curve_point: curve_point['spot_rate']
        self._s = np.array(list(map(get_spot_rate, curve_points)))

        self._curve_points = dict(zip(self._t, self._s))

    def interpolate_curve(self, t, interpolation_type='linear'):
        if interpolation_type == 'linear':
            s_interp = np.interp(t, self._t, self._s, right=np.nan, left=1)
            return s_interp
        else:
            raise ValueError

    def is_extrapolated(self, t):

        return t > max(self._t) or t < min(self._t)

    def __getitem__(self, time):
        if time in self._curve_points:
            return self._curve_points[time]
        else:
            return self.interpolate_curve(time)
