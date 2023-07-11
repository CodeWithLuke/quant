from datetime import date

from date_calculator.tenor_calculator import add_tenor
from instrument_yield_curve.curve_instruments.abs_curve_instrument import AbsCurveInstrument

from date_calculator.day_count_calculator import DayCountCalculator
from instrument_yield_curve.instrument_yield_curve import InstrumentYieldCurve
from instrument_yield_curve.instrument_yield_curve_constructor import InstrumentYieldCurveConstructor
from utils.enum import DayCountConvention, CurveInstrument
from utils.utils import discount_to_spot_rate, future_price_to_forward_rate


class FuturesCurveInstrument(AbsCurveInstrument):

    @property
    def node_date(self):
        return self._node_date

    @property
    def quote(self):
        return self._price

    def __init__(self, price: float, expiry_date: date, convexity_adj=0,
                 tenor='3M', day_count_convention=DayCountConvention.ACT_365):
        self._price = price

        self._forward_rate = future_price_to_forward_rate(price) + convexity_adj

        self._expiry_date = expiry_date

        self._node_date = add_tenor(expiry_date, tenor)

        self._day_count_convention = day_count_convention


    def calculate_zero_rate(self, partial_yield_curve: InstrumentYieldCurve):

        dcc = DayCountCalculator(day_count_convention=self._day_count_convention)

        dcf_to_expiry = dcc.day_count(partial_yield_curve.base_date, self._expiry_date)

        zero_rate_at_expiry = partial_yield_curve.interpolate_curve(self._expiry_date)

        forward_rate_term_dcf = dcc.day_count(self._expiry_date, self._node_date)

        node_date_dcf = dcc.day_count(partial_yield_curve.base_date, self._node_date)

        zero_rate = ((self._forward_rate * forward_rate_term_dcf)
                     + (zero_rate_at_expiry * dcf_to_expiry)) / node_date_dcf

        return zero_rate

    @staticmethod
    def instrument_type():
        return CurveInstrument.IR_FUTURES
