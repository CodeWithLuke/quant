from typing import Dict

from utils.enum import CurveInstrument, InterpolationType
from yield_curve.libor_curve import LiborCurve
from .long_libor_curve_builder import LongLiborCurveBuilder
from .mid_libor_curve_builder import MidLiborCurveBuilder
from .short_libor_curve_builder import ShortLiborCurveBuilder


class LiborCurveBuilder:
    def __init__(self, cash_libor_rates: Dict[float, float], eurodollar_futures_prices: Dict[float, float],
                 market_swap_rates: Dict[float, float]):
        # short yield_curve
        scb = ShortLiborCurveBuilder(cash_libor_rates)

        short_curve_data = scb.curve

        mcb = MidLiborCurveBuilder(eurodollar_futures_prices, short_curve_data)

        mid_curve_data = mcb.curve

        self._curve_data = mid_curve_data

        lcb = LongLiborCurveBuilder(self._curve_data, market_swap_rates)

        self._curve_data += lcb.curve

        self._market_data = {
            CurveInstrument.CASH_DEPOSIT: cash_libor_rates, CurveInstrument.IR_FUTURES: eurodollar_futures_prices,
            CurveInstrument.IR_SWAP: market_swap_rates
        }

    @classmethod
    def from_market_data_dict(cls, market_data: dict):
        assert all([curve_instrument in market_data for curve_instrument in (
            CurveInstrument.CASH_DEPOSIT, CurveInstrument.IR_FUTURES, CurveInstrument.IR_SWAP)])

        return cls(
            market_data[CurveInstrument.CASH_DEPOSIT], market_data[CurveInstrument.IR_FUTURES],
            market_data[CurveInstrument.IR_SWAP]
        )

    def curve(self, interpolation_type=InterpolationType.LINEAR):
        return LiborCurve(self._curve_data, interpolation_type=interpolation_type, market_quotes=self._market_data)
