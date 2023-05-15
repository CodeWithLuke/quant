from date_calculator.day_count_calculators.abs_day_count_calculator import AbsDayCountCalculator
from utils.enum import DayCountConvention

from datetime import date


class DayCountCalculator:
    '''
    day_count algorithms referenced from https://github.com/miradulo/isda_daycounters
    '''

    ENUM_TO_CALC_MAP = {day_count_calc.day_count_convention(): day_count_calc.__class__
                        for day_count_calc in AbsDayCountCalculator.__subclasses__()}

    def __init__(self, day_count_convention: DayCountConvention):
        self._day_count_calculator: AbsDayCountCalculator = DayCountCalculator.ENUM_TO_CALC_MAP[day_count_convention]

    def set_day_count_convention(self, day_count_convention: DayCountConvention):
        self._day_count_calculator: AbsDayCountCalculator = DayCountCalculator.ENUM_TO_CALC_MAP[day_count_convention]

    def day_count(self, start_date: date, end_date: date):
        self._day_count_calculator.day_count(start_date, end_date)

    def year_fraction(self, start_date: date, end_date: date):
        self._day_count_calculator.year_fraction(start_date, end_date)
