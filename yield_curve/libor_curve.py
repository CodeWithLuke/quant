from copy import deepcopy
from dataclasses import asdict
from typing import List, Dict, Union

import numpy as np
from scipy.interpolate import CubicSpline

from utils.constants import BASIS_POINT_CONVERSION
from utils.enum import CurveInstrument, InterpolationType, CompoundingType
from utils.utils import *
from yield_curve.abs_curve import AbsCurve
from yield_curve.libor_curve_builder.long_libor_curve_builder import LongLiborCurveBuilder
from yield_curve.libor_curve_builder.mid_libor_curve_builder import MidLiborCurveBuilder
from yield_curve.libor_curve_builder.short_libor_curve_builder import ShortLiborCurveBuilder

from yield_curve.spot_rate_point import SpotRatePoint


class LiborCurve(AbsCurve):

    def __init__(self, curve_points: Union[List[SpotRatePoint], List[Dict[str, float]]],
                 interpolation_type=InterpolationType.LINEAR, market_quotes: dict = None):

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

    @classmethod
    def from_market_data_dict(cls, market_data: dict):
        assert all([curve_instrument in market_data for curve_instrument in (
            CurveInstrument.CASH_DEPOSIT, CurveInstrument.IR_FUTURES, CurveInstrument.IR_SWAP)])

        return cls.from_market_quotes(
            market_data[CurveInstrument.CASH_DEPOSIT], market_data[CurveInstrument.IR_FUTURES],
            market_data[CurveInstrument.IR_SWAP]
        )

    @classmethod
    def from_market_quotes(cls, cash_libor_rates: Dict[float, float], eurodollar_futures_prices: Dict[float, float],
                 market_swap_rates: Dict[float, float], interpolation_type=InterpolationType.LINEAR):
        # short yield_curve
        scb = ShortLiborCurveBuilder(cash_libor_rates)

        short_curve_data = scb.curve

        mcb = MidLiborCurveBuilder(eurodollar_futures_prices, short_curve_data)

        mid_curve_data = mcb.curve

        curve_data = mid_curve_data

        lcb = LongLiborCurveBuilder(curve_data, market_swap_rates)

        curve_data += lcb.curve

        market_data = {
            CurveInstrument.CASH_DEPOSIT: cash_libor_rates, CurveInstrument.IR_FUTURES: eurodollar_futures_prices,
            CurveInstrument.IR_SWAP: market_swap_rates
        }

        return cls(curve_data, interpolation_type=interpolation_type, market_quotes=market_data)

    def interpolate_curve(self, t) -> float:
        if self._interpolation_type == InterpolationType.LINEAR:
            s_interp = np.interp(t, self._t, self._s, left=0)
            return s_interp

        elif self._interpolation_type == InterpolationType.CUBIC_SPLINE:
            return self._interpolator(t)

        else:
            raise ValueError

    def interpolate_discount_factor(self, t, compounding=CompoundingType.CONTINUOUS):
        if compounding == CompoundingType.CONTINUOUS:
            return spot_rate_to_discount(self.interpolate_curve(t), t)

        else:
            raise ValueError

    def interpolate_forward_rate(self, t, term=1):
        t_a = t
        t_b = t + term

        d_a = self.interpolate_discount_factor(t_a, compounding=CompoundingType.CONTINUOUS)

        d_b = self.interpolate_discount_factor(t_b, compounding=CompoundingType.CONTINUOUS)

        return -1 * log(d_b / d_a) / term

    def bump_curve_by_instrument(self, n_bps_bump=1):
        bumped_curves = dict()

        market_data = self.market_quotes

        for curve_instrument, quotes in market_data.items():

            market_data_copy = deepcopy(market_data)

            for time, quote in quotes.items():
                curve_instrument_quotes_copy = deepcopy(market_data[curve_instrument])

                curve_instrument_quotes_copy[time] += n_bps_bump * BASIS_POINT_CONVERSION

                market_data_copy[curve_instrument] = curve_instrument_quotes_copy

                time_str = f"{round(time)}Y" if time.is_integer() else f"{round(time * 12)}M"

                bumped_curves["_".join((curve_instrument.name, time_str))] = LiborCurve.from_market_data_dict(
                    market_data_copy)

        return bumped_curves

    def parallel_bump_curve(self, n_bps_bump=1):
        market_data = self.market_quotes

        market_data_copy = deepcopy(market_data)

        for curve_instrument, instrument_quotes in market_data.items():

            for time, quote in instrument_quotes.items():
                new_quote = quote + n_bps_bump * BASIS_POINT_CONVERSION

                market_data_copy[curve_instrument][time] = new_quote

        return LiborCurve.from_market_data_dict(market_data_copy)

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
