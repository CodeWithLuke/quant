import datetime
from datetime import date

from dataclasses import dataclass

from utils.enum import TenorUnit, DateRollingConvention

from business_day_calculator.utils import get_holiday_calendar, is_business_day

from dateutil.relativedelta import relativedelta

@dataclass
class Tenor:
    value: int
    unit: TenorUnit

    @classmethod
    def from_string(cls, tenor_string: str):

        value = tenor_string[:-1]

        unit = tenor_string[-1]

        if not value.isnumeric():
            raise ValueError ("Tenor value is not numeric.")

        tenor_value = int(value)

        try:
            tenor_unit = TenorUnit(unit.upper())

        except ValueError as ve:
            raise ValueError (f"Tenor unit must be one of D, M, Y.{ve}" )

        return cls(tenor_value, tenor_unit)

def roll_date(base_date: date, holiday_region: str = 'NYSE',
              rolling_convention: DateRollingConvention = DateRollingConvention.MODIFIED_FOLLOWING) -> date:
    holiday_calendar = get_holiday_calendar(holiday_region)

    if rolling_convention == DateRollingConvention.MODIFIED_FOLLOWING:
        original_date = base_date
        while not is_business_day(base_date, holiday_calendar):
            base_date += datetime.timedelta(days=1)
        if not base_date.month == original_date.month:
            base_date = original_date
            while not is_business_day(base_date, holiday_calendar):
                base_date -= datetime.timedelta(days=1)

        return base_date

    else:
        raise NotImplementedError


def add_tenor(base_date: date, tenor_string: str, holiday_region: str = 'NYSE',
              rolling_convention: DateRollingConvention=DateRollingConvention.MODIFIED_FOLLOWING):

    tenor_obj = Tenor.from_string(tenor_string)

    if tenor_obj.unit == TenorUnit.MONTH:
        time_delta = relativedelta(months=tenor_obj.value)

    elif tenor_obj.unit == TenorUnit.DAY:
        time_delta = datetime.timedelta(days=tenor_obj.value)

    elif tenor_obj.unit == TenorUnit.WEEK:
        time_delta = datetime.timedelta(weeks=tenor_obj.value)

    elif tenor_obj.unit == TenorUnit.YEAR:
        time_delta = relativedelta(years=tenor_obj.value)

    else:
        raise Exception

    result_date = base_date + time_delta

    return roll_date(result_date, holiday_region, rolling_convention)


