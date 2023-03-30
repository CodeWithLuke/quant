from typing import List

from utils.enum import CashFlowFrequency, CompoundingType, PayerReceiver, SwapLegType
from yield_curve.abs_curve import AbsCurve
from dataclasses import dataclass

class InterestRateSwap:

    def __init__(self, notional: float, maturity: float, cash_flow_frequency: CashFlowFrequency, swap_rate: float,
                 payer_receiver=PayerReceiver.PAYER, start_time: float = 0.):
        self._notional = notional

        self._maturity = maturity

        self._start_time = start_time

        self._end_time = start_time + self._maturity

        self._interest_type = CompoundingType.CONTINUOUS

        self._cash_flow_frequency = cash_flow_frequency

        self._cash_flow_period = 1 / int(cash_flow_frequency)

        self._times_of_cash_flows = self._get_times_of_cash_flows(cash_flow_frequency, maturity, start_time)

        self._swap_rate = swap_rate

        self._payer_receiver = payer_receiver

    @classmethod
    def par_swap(cls, libor_curve: AbsCurve, notional: float, maturity: float, cash_flow_frequency: CashFlowFrequency,
                 payer_receiver=PayerReceiver.PAYER, start_time: float = 0.):

        times_of_cash_flows = cls._get_times_of_cash_flows(cash_flow_frequency, maturity, start_time)

        swap_rate = cls._calc_par_rate(libor_curve, times_of_cash_flows, maturity, start_time,
                                       cash_flow_frequency)

        return cls(notional, maturity, cash_flow_frequency, swap_rate, payer_receiver, start_time)

    def present_value(self, libor_curve: AbsCurve):
        floating_leg_value = self._notional * (libor_curve.interpolate_discount_factor(self._start_time)
                                               - libor_curve.interpolate_discount_factor(self._end_time))

        fixed_cash_flow_notional = self._swap_rate * self._notional / float(self._cash_flow_frequency)

        fixed_leg_value = sum(
            [fixed_cash_flow_notional * libor_curve.interpolate_discount_factor(t) for t in self._times_of_cash_flows]
        )

        return int(self._payer_receiver) * (floating_leg_value - fixed_leg_value)

    def par_rate(self, libor_curve: AbsCurve):

        return self._calc_par_rate(libor_curve, self._times_of_cash_flows, self._maturity, self._start_time,
                                   self._cash_flow_frequency)

    def cash_flow_report(self, libor_curve: AbsCurve):
        times_of_cash_flows = self._times_of_cash_flows.copy()

        cash_flow_report = []

        notional_w_sign = self.notional * int(self._payer_receiver)

        # fixed leg
        for t in times_of_cash_flows:
            d_t = libor_curve.interpolate_discount_factor(t)

            cash_flow = SwapLegCashFlow(
                t, self._swap_rate, SwapLegType.FIXED, -1 * notional_w_sign, d_t, self._cash_flow_frequency
            )

            cash_flow_report.append(cash_flow.as_dict())

        # insert 0 at beginning for loop to be complete
        times_of_cash_flows.insert(0, self._start_time)

        # floating leg
        for i in range(1, len(times_of_cash_flows)):
            t_i = times_of_cash_flows[i]

            t_im1 = times_of_cash_flows[i - 1]

            d_i = libor_curve.interpolate_discount_factor(t_i)

            d_im1 = libor_curve.interpolate_discount_factor(t_im1)

            floating_factor = d_im1 - d_i

            projected_rate = floating_factor * self._cash_flow_frequency / d_i

            cash_flow = SwapLegCashFlow(
                t_i, projected_rate, SwapLegType.FLOATING, notional_w_sign, d_i, self._cash_flow_frequency
            )

            cash_flow_report.append(cash_flow.as_dict())

        cash_flow_report.sort(key=lambda cf: cf['time'])

        return cash_flow_report

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
    def _calc_par_rate(libor_curve: AbsCurve, times_of_cash_flows: List[float], maturity, start_time,
                       cash_flow_frequency: CashFlowFrequency):

        end_time = start_time + maturity

        discount_factor_sum = sum(
            [libor_curve.interpolate_discount_factor(t) for t in times_of_cash_flows]
        )

        d_range = libor_curve.interpolate_discount_factor(start_time) - libor_curve.interpolate_discount_factor(
            end_time)

        return cash_flow_frequency * d_range / discount_factor_sum

    def pv01(self, libor_curve: AbsCurve):
        parallel_bumped_curve = libor_curve.parallel_bump_curve()

        npv = self.present_value(libor_curve)

        bumped_npv = self.present_value(parallel_bumped_curve)

        return bumped_npv - npv

    def first_order_curve_risk(self, libor_curve: AbsCurve):
        risk_map = dict()

        bumped_curve_map = libor_curve.bump_curve_by_instrument()

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

    @property
    def payer_receiver(self):
        return self._payer_receiver

@dataclass
class SwapLegCashFlow:
    time: float
    projected_rate: float
    leg_type: SwapLegType
    notional: float
    discount_factor: float
    cash_flow_frequency: CashFlowFrequency

    def get_cash_flow_present_value(self):
        return self.projected_rate * self.notional * self.discount_factor / float(self.cash_flow_frequency)

    def get_cash_flow_future_value(self):
        return self.projected_rate * self.notional / float(self.cash_flow_frequency)

    def as_dict(self):
        d = self.__dict__

        d.update({
            "present_value": self.get_cash_flow_present_value(), "future_value": self.get_cash_flow_future_value()
        })
        return d
