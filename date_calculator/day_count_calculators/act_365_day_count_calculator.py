"""
ISDA Actual/365 day count convention.
=====

Implemented according to 2006 ISDA definition:
http://www.hsbcnet.com/gbm/attachments/standalone/2006-isda-definitions.pdf

https://github.com/miradulo/isda_daycounters
"""

from abs_day_count_calculator import AbsDayCountCalculator

from datetime import date

from utils.enum import DayCountConvention


class Act365DayCountCalculator(AbsDayCountCalculator):

    @staticmethod
    def day_count_convention() -> DayCountConvention:
        return DayCountConvention.ACT_365

    @staticmethod
    def day_count(start_date: date, end_date: date):
        """Returns number of days between start_date and end_date, using Actual/365 convention"""
        return (end_date - start_date).days

    @staticmethod
    def year_fraction(start_date: date, end_date: date):
        """Returns fraction in years between start_date and end_date, using Actual/365 convention"""
        return Act365DayCountCalculator.day_count(start_date, end_date) / 365.0
