"""
ISDA Actual/Actual day count convention.
=====

Implemented according to 2006 ISDA definition:
http://www.hsbcnet.com/gbm/attachments/standalone/2006-isda-definitions.pdf

https://github.com/miradulo/isda_daycounters
"""

import calendar
import datetime as dt

from datetime import date

from date_calculator.day_count_calculators.abs_day_count_calculator import AbsDayCountCalculator
from utils.enum import DayCountConvention


class ActActDayCountCalculator(AbsDayCountCalculator):

    @staticmethod
    def day_count_convention() -> DayCountConvention:
        return DayCountConvention.ACT_ACT

    @staticmethod
    def day_count(start_date: date, end_date: date):
        """Returns number of days between start_date and end_date, using Actual/Actual convention"""
        return (end_date - start_date).days

    @staticmethod
    def year_fraction(start_date: date, end_date: date):
        """Returns fraction in years between start_date and end_date, using Actual/Actual convention"""
        if start_date == end_date:
            return 0.0

        start_date = dt.datetime.combine(start_date, dt.datetime.min.time())
        end_date = dt.datetime.combine(end_date, dt.datetime.min.time())

        start_year = start_date.year
        end_year = end_date.year
        year_1_diff = 366 if calendar.isleap(start_year) else 365
        year_2_diff = 366 if calendar.isleap(end_year) else 365

        total_sum = end_year - start_year - 1
        diff_first = dt.datetime(start_year + 1, 1, 1) - start_date
        total_sum += diff_first.days / year_1_diff
        diff_second = end_date - dt.datetime(end_year, 1, 1)
        total_sum += diff_second.days / year_2_diff

        return total_sum
