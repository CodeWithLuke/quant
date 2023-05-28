from datetime import date

from date_calculator.utils import get_num_business_days

from date_calculator.tenor_calculator import Tenor, TenorUnit, add_tenor
from product.fixed_leg import FixedLeg


def test_count_business_days():
    base_date = date(2023, 12, 21)
    end_date = date(2023, 12, 28)
    # 21st, 22nd, 26th, 27th
    assert get_num_business_days(end_date, base_date) == 4


def test_tenor_string_parse():
    tenor = Tenor.from_string('1Y')

    assert tenor.value == 1 and tenor.unit == TenorUnit.YEAR

def test_add_tenor():
    d1 = add_tenor(date(2023, 3, 17), "1m")

    assert d1 == date(2023, 4, 17)

    d2 = add_tenor(date(2023, 7, 3), "1d")

    assert d2 == date(2023, 7, 5)

def test_leg_const():

    fl = FixedLeg(1000000, 0.05, "3M", start_date=date(2016, 1, 4), end_date=date(2026, 1, 30))

    print(fl.cash_flows)

    assert True
