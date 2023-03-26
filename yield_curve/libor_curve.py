from dataclasses import asdict
from typing import List, Dict, Union

import numpy as np
from scipy.interpolate import CubicSpline

from utils.enum import CurveInstrument, InterpolationType, InterestType
from utils.utils import *
from yield_curve.abs_curve import AbsCurve

from yield_curve.spot_rate_point import SpotRatePoint


class LiborCurve(AbsCurve):

    def __init__(self, curve_points: Union[List[SpotRatePoint], List[Dict[str, float]]],
                 interpolation_type=InterpolationType.LINEAR,
                 market_quotes: dict = None):

        is_curve_point_data_obj = any([isinstance(curve_point, SpotRatePoint) for curve_point in curve_points])

        if is_curve_point_data_obj:
            new_curve_points = []
            for curve_point in curve_points:
                if isinstance(curve_point, SpotRatePoint):
                    spot_rate_dict = asdict(curve_point)
                    if spot_rate_dict['spot_rate'] > 0.25:
                        spot_rate_dict['spot_rate'] /= 100
                    new_curve_points.append(spot_rate_dict)
                else:
                    new_curve_points.append(curve_point)

            curve_points = new_curve_points

        assert all(['time' in curve_point and 'spot_rate' in curve_point for curve_point in curve_points])

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

    def interpolate_curve(self, t) -> float:
        if self._interpolation_type == InterpolationType.LINEAR:
            s_interp = np.interp(t, self._t, self._s, right=np.nan, left=1)
            return s_interp

        elif self._interpolation_type == InterpolationType.CUBIC_SPLINE:
            return self._interpolator(t)

        else:
            raise ValueError

    def interpolate_discount_factor(self, t, compounding=InterestType.CONTINUOUS):
        if compounding == InterestType.CONTINUOUS:
            return spot_rate_to_discount(self.interpolate_curve(t), t)

        elif compounding == InterestType.SIMPLE:
            r = self.interpolate_curve(t)
            return 1 / (1 + r * t)

        else:
            raise ValueError

    def interpolate_forward_rate(self, t, term=1):
        t_a = t
        t_b = t + term

        d_a = self.interpolate_discount_factor(t_a, compounding=InterestType.CONTINUOUS)

        d_b = self.interpolate_discount_factor(t_b, compounding=InterestType.CONTINUOUS)

        return -1 * log(d_b / d_a) / term

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
