from datetime import date

from date_calculator.tenor_calculator import add_tenor

from date_calculator.day_count_calculator import DayCountCalculator
from utils.enum import DayCountConvention
from utils.utils import discount_to_spot_rate


class DepositCurveInstrument:

    def __init__(self, rate: float, base_date: date, rate_tenor_str: str,
                 day_count_convention=DayCountConvention.ACT_365):
        self._rate = rate

        self._base_date = base_date

        self._node_date = add_tenor(base_date, rate_tenor_str)

        self._day_count_convention = day_count_convention

    def calculate_zero_rate(self, partial_curve):

        t = DayCountCalculator(day_count_convention=self._day_count_convention).day_count(
            self._base_date, self._node_date)

        discount_factor = 1 / (1 + t * self._rate / 100)

        return discount_to_spot_rate(discount_factor)
