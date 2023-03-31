from datetime import date

from business_day_calculator.utils import get_num_business_days


def test_count_business_days():
    base_date = date(2023, 12, 21)
    end_date = date(2023, 12, 28)
    # 21st, 22nd, 26th, 27th
    assert get_num_business_days(end_date, base_date) == 4