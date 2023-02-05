from enum import IntEnum

from utils.constants import FLOAT_EQ_THRESHOLD

from curve.libor_curve import LiborCurve, InterestType
from utils.enum import CashFlowFrequency
from product.cash_flow import CashFlow


class PayerReceiver(IntEnum):
    PAYER = 1
    RECEIVER = -1


class LiborSwap:

    def __init__(self, notional: float, maturity: float, cash_flow_frequency: CashFlowFrequency, swap_rate: float,
                 payer_receiver=PayerReceiver.PAYER, start_time: float = 0.):
        self._notional = notional

        self._maturity = maturity

        self._start_time = start_time

        self._end_time = start_time + self._maturity

        assert cash_flow_frequency is not None and not cash_flow_frequency == CashFlowFrequency.NONE

        # want start time over zero
        assert start_time >= -FLOAT_EQ_THRESHOLD

        self._interest_type = InterestType.SIMPLE

        self._cash_flow_frequency = cash_flow_frequency

        self._number_of_cash_flows = round(self._maturity * int(self._cash_flow_frequency))

        self._cash_flow_period = 1 / int(cash_flow_frequency)

        # assume end_date has last cash_flow
        self._times_of_cash_flows = []
        t = self._end_time

        for i in range(self._number_of_cash_flows):
            self._times_of_cash_flows.insert(0, t)
            t -= self._cash_flow_period

        self._swap_rate = swap_rate

        self._payer_receiver = payer_receiver

    def present_value(self, libor_curve: LiborCurve):
        floating_leg_value = self._notional * (libor_curve.interpolate_discount_factor(self._start_time)
                                               - libor_curve.interpolate_discount_factor(self._end_time))

        fixed_cash_flow_notional = self._swap_rate * self._notional / self._number_of_cash_flows

        fixed_leg_value = sum(
            CashFlow(fixed_cash_flow_notional, t).present_value(libor_curve) for t in self._times_of_cash_flows
        )

        return int(self._payer_receiver) * (floating_leg_value - fixed_leg_value)

    def par_rate(self, libor_curve: LiborCurve):
        discount_factor_sum = sum(
            libor_curve.interpolate_discount_factor(t, compounding=self._interest_type)
            for t in self._times_of_cash_flows
        )

        d_range = libor_curve.interpolate_discount_factor(
            self._start_time, compounding=self._interest_type) - libor_curve.interpolate_discount_factor(
            self._end_time, compounding=self._interest_type)

        return self._number_of_cash_flows * d_range / discount_factor_sum
