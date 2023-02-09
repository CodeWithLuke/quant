from yield_curve.libor_curve_builder.libor_bumped_curve_builder import bump_libor_curve
from utils.constants import FLOAT_EQ_THRESHOLD

from yield_curve.libor_curve import LiborCurve
from utils.enum import CashFlowFrequency, InterestType, PayerReceiver
from product.cash_flow import CashFlow


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

        fixed_cash_flow_notional = self._swap_rate * self._notional / self._cash_flow_frequency

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

        return self._cash_flow_frequency * d_range / discount_factor_sum

    def first_order_risk(self, libor_curve: LiborCurve):
        risk_map = dict()

        bumped_curve_map = bump_libor_curve(libor_curve)

        npv = self.present_value(libor_curve)

        for node, bumped_curve in bumped_curve_map.items():
            risk_map[node] = self.present_value(bumped_curve) - npv

        return risk_map
