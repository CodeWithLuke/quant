
from datetime import date

from date_calculator.tenor_calculator import add_tenor
from utils.enum import DayCountConvention

from date_calculator.day_count_calculator import DayCountCalculator

class FixedLeg:

    def __init__(self, notional: float, rate: float, cash_flow_frequency_tenor: str, start_date: date,
                 end_date: date, day_count_convention: DayCountConvention = DayCountConvention.ACT_365):

        self.cash_flows = []

        accrual_start_date = start_date

        accrual_end_date = add_tenor(start_date, cash_flow_frequency_tenor)

        while accrual_end_date < end_date:

            day_count_fraction = DayCountCalculator(day_count_convention).year_fraction(
                accrual_start_date, accrual_end_date)

            cash_flow_amount = notional * rate * day_count_fraction

            self.cash_flows.append(
                {'accrual_start_date': accrual_start_date, 'accrual_end_date': accrual_end_date,
                 'day_count_fraction': day_count_fraction, 'rate': rate, 'notional': notional,
                 'cash_flow_amount': cash_flow_amount}
            )

            accrual_start_date = add_tenor(accrual_start_date, cash_flow_frequency_tenor)

            accrual_end_date = add_tenor(accrual_end_date, cash_flow_frequency_tenor)
