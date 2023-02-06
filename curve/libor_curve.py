from typing import List, Dict

from curve.abs_curve import AbsCurve
from utils.enum import CurveInstrument, InterpolationType, InterestType
from utils.utils import *

import numpy as np

from scipy.interpolate import CubicSpline


class LiborCurve(AbsCurve):

    def __init__(self, curve_points: List[Dict[str, float]], interpolation_type=InterpolationType.CUBIC_SPLINE,
                 market_quotes: dict =None):
        assert any('time' in curve_point and 'spot_rate' in curve_point for curve_point in curve_points)

        self._market_quotes = market_quotes

        self._interpolation_type = interpolation_type

        self._interpolator = None

        get_time = lambda curve_point: curve_point['time']
        self._t = np.array(list(map(get_time, curve_points)))

        get_spot_rate = lambda curve_point: curve_point['spot_rate']
        self._s = np.array(list(map(get_spot_rate, curve_points)))

        if interpolation_type == InterpolationType.CUBIC_SPLINE:
            self._interpolator = CubicSpline(self._t, self._s, extrapolate=False)

        self._yield_curve_points = dict(zip(self._t, self._s))

    def interpolate_curve(self, t):
        if self._interpolation_type == InterpolationType.LINEAR:
            s_interp = np.interp(t, self._t, self._s, right=np.nan, left=1)
            return s_interp

        elif self._interpolation_type == InterpolationType.CUBIC_SPLINE:
            return self._interpolator(t)

        else:
            raise ValueError

    def interpolate_discount_factor(self, t, compounding=InterestType.COMPOUNDING):
        if compounding == InterestType.COMPOUNDING:
            return spot_rate_to_discount(self.interpolate_curve(t), t)

        elif compounding == InterestType.SIMPLE:
            r = self.interpolate_curve(t)
            return 1 / (1 + r * t)

        else:
            raise ValueError


    def is_extrapolated(self, t):
        return t > max(self._t) or t < min(self._t)

    def __getitem__(self, time):
        if time in self._yield_curve_points:
            return self._yield_curve_points[time]
        else:
            return self.interpolate_curve(time)

    @property
    def market_quotes(self) -> Dict[CurveInstrument, Dict[float, float]]:
        return self._market_quotes

