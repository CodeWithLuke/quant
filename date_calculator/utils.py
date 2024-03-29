import datetime
from datetime import date, timedelta
from holidays import financial_holidays, country_holidays
from utils.constants import WEEKEND_INDICES
from utils.enum import DayCountConvention
from functools import cache
from calendar import isleap


def get_num_business_days (end_date: date, base_date: date = date.today(), region: str = 'NYSE'):

    loaded_holidays = get_holiday_calendar(region)

    num_business_days = 0

    for i_date in _date_range(base_date, end_date):
        if is_business_day(i_date, loaded_holidays):
            num_business_days += 1

    return num_business_days

@cache
def get_holiday_calendar (region):
    try:
        loaded_holidays = financial_holidays(region)
    except NotImplementedError:
        loaded_holidays = country_holidays(region)

    return loaded_holidays

def is_leap_year (year: int):
    return isleap(year)


def _date_range(base_date: date, end_date:date):
    for n in range(int((end_date - base_date).days)):
        yield base_date + timedelta(n)

def is_business_day (base_date: date, loaded_holidays):
    return not (base_date.weekday() in WEEKEND_INDICES or base_date in loaded_holidays)
