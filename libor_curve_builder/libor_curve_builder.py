from typing import List, Dict

from libor_curve import LiborCurve
from .long_libor_curve_builder import LongLiborCurveBuilder
from .mid_libor_curve_builder import MidLiborCurveBuilder
from .short_libor_curve_builder import ShortLiborCurveBuilder


class LiborCurveBuilder:
    def __init__(self, cash_libor_rates: Dict[float, float], eurodollar_futures_prices: Dict[float, float],
                 market_swap_rates: Dict[float, float]):

        # short curve
        scb = ShortLiborCurveBuilder(cash_libor_rates)

        short_curve_data = scb.curve

        mcb = MidLiborCurveBuilder(eurodollar_futures_prices, short_curve_data)

        mid_curve_data = mcb.curve

        self._curve_data = mid_curve_data

        lcb = LongLiborCurveBuilder(self._curve_data, market_swap_rates)

        self._curve_data += lcb.curve

    def curve(self):

        return LiborCurve(self._curve_data)
