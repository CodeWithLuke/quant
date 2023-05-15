"""
ISDA 30/360 day count convention.
=====

Implemented according to 2006 ISDA definition:
http://www.hsbcnet.com/gbm/attachments/standalone/2006-isda-definitions.pdf

https://github.com/miradulo/isda_daycounters
"""

from datetime import date

from abs_day_count_calculator import AbsDayCountCalculator
from utils.enum import DayCountConvention


class Thirty360DayCountCalculator(AbsDayCountCalculator):

    @staticmethod
    def day_count_convention() -> DayCountConvention:
        return DayCountConvention.THIRTY_360

    @staticmethod
    def day_count(start_date: date, end_date: date):
        """Returns number of days between start_date and end_date, using Thirty/360 convention"""
        d1 = min(30, start_date.day)
        d2 = min(d1, end_date.day) if d1 == 30 else end_date.day

        return 360*(end_date.year - start_date.year)\
               + 30*(end_date.month - start_date.month)\
               + d2 - d1

    @staticmethod
    def year_fraction(start_date: date, end_date: date):
        """Returns fraction in years between start_date and end_date, using Thirty/360 convention"""
        return Thirty360DayCountCalculator.day_count(start_date, end_date) / 360.0
