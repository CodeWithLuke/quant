from typing import List

from yield_curve.libor_curve_builder.libor_bumped_curve_builder import bump_libor_curve

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

        self._interest_type = InterestType.COMPOUNDING

        self._cash_flow_frequency = cash_flow_frequency

        self._cash_flow_period = 1 / int(cash_flow_frequency)

        self._times_of_cash_flows = self._get_times_of_cash_flows(cash_flow_frequency, maturity, start_time)

        self._swap_rate = swap_rate

        self._payer_receiver = payer_receiver

    @classmethod
    def par_swap(cls, libor_curve: LiborCurve, notional: float, maturity: float, cash_flow_frequency: CashFlowFrequency,
                 payer_receiver=PayerReceiver.PAYER, interest_type :InterestType = InterestType.COMPOUNDING,
                 start_time: float = 0.):

        times_of_cash_flows = cls._get_times_of_cash_flows(cash_flow_frequency, maturity, start_time)

        swap_rate = cls._calc_par_rate(libor_curve, times_of_cash_flows, interest_type, maturity, start_time,
                                       cash_flow_frequency)

        return cls(notional, maturity, cash_flow_frequency, swap_rate, payer_receiver, start_time)



    def present_value(self, libor_curve: LiborCurve):
        floating_leg_value = self._notional * (libor_curve.interpolate_discount_factor(self._start_time)
                                               - libor_curve.interpolate_discount_factor(self._end_time))

        fixed_cash_flow_notional = self._swap_rate * self._notional / float(self._cash_flow_frequency)

        fixed_leg_value = sum(
            CashFlow(fixed_cash_flow_notional, t).present_value(libor_curve) for t in self._times_of_cash_flows
        )

        return int(self._payer_receiver) * (floating_leg_value - fixed_leg_value)

    def par_rate(self, libor_curve: LiborCurve):

        return self._calc_par_rate(libor_curve, self._times_of_cash_flows, self._interest_type, self._maturity,
                                   self._start_time, self._cash_flow_frequency)


    @staticmethod
    def _get_times_of_cash_flows(cash_flow_frequency: CashFlowFrequency, maturity: float, start_time: float):
        cash_flow_period = 1 / int(cash_flow_frequency)

        # assume end_date has last cash_flow
        times_of_cash_flows = []
        t = start_time + maturity

        number_of_cash_flows = round(maturity * int(cash_flow_frequency))

        for i in range(number_of_cash_flows):
            times_of_cash_flows.insert(0, t)
            t -= cash_flow_period

        return times_of_cash_flows


    @staticmethod
    def _calc_par_rate(libor_curve: LiborCurve, times_of_cash_flows: List[float], interest_type: InterestType,
                       maturity, start_time, cash_flow_frequency: CashFlowFrequency):

        end_time = start_time + maturity

        discount_factor_sum = sum(
            libor_curve.interpolate_discount_factor(t, compounding=interest_type)
            for t in times_of_cash_flows
        )

        d_range = libor_curve.interpolate_discount_factor(
            start_time, compounding=interest_type) - libor_curve.interpolate_discount_factor(
            end_time, compounding=interest_type)

        return cash_flow_frequency * d_range / discount_factor_sum

    def first_order_risk(self, libor_curve: LiborCurve):
        risk_map = dict()

        bumped_curve_map = bump_libor_curve(libor_curve)

        npv = self.present_value(libor_curve)

        for node, bumped_curve in bumped_curve_map.items():
            risk_map[node] = self.present_value(bumped_curve) - npv

        return risk_map

    @property
    def start_time(self):
        return self._start_time

    @property
    def swap_rate(self):
        return self._swap_rate

    @property
    def maturity(self):
        return self._maturity

    @property
    def cash_flow_frequency(self):
        return self._cash_flow_frequency

    @property
    def times_of_cash_flows(self):
        return self._times_of_cash_flows

    @property
    def notional(self):
        return self._notional
