from math import log, sqrt

from scipy.stats import norm

from product.libor_swap import LiborSwap
from utils.enum import CashFlowFrequency, PayerReceiver, LongShort
from vol_surface.swaption_vol_surface.abs_swaption_surface import AbsSwaptionSurface
from yield_curve.abs_curve import AbsCurve
from yield_curve.libor_curve import LiborCurve


class LiborSwaption:

    def __init__(self, notional: float, strike: float, swaption_expiry: float, swap_tenor_years: float,
                 swap_cash_flow_frequency: CashFlowFrequency, swap_payer_receiver: PayerReceiver,
                 long_short: LongShort = LongShort.LONG):

        self._underlying_swap = LiborSwap(notional, swap_tenor_years, swap_cash_flow_frequency, strike,
                                          swap_payer_receiver, swaption_expiry)

        self._swaption_expiry = self._underlying_swap.start_time

        self._strike = self._underlying_swap.swap_rate

        self._swap_tenor_years = self._underlying_swap.maturity

        self._notional = self._underlying_swap.notional

        self._payer_receiver = self._underlying_swap.payer_receiver

        self._long_short = long_short

    @classmethod
    def from_forward_swap(cls, forward_swap: LiborSwap, long_short: LongShort = LongShort.LONG):

        return cls(forward_swap.notional, forward_swap.swap_rate, forward_swap.start_time, forward_swap.maturity,
                   forward_swap.cash_flow_frequency, forward_swap.payer_receiver, long_short)

    def present_value(self, libor_curve: AbsCurve, swaption_vol_surface: AbsSwaptionSurface):

        s_0 = self._underlying_swap.par_rate(libor_curve)

        s_k = self._strike

        vol = swaption_vol_surface.interpolate_vol(self._swaption_expiry, self._swap_tenor_years)

        d_1 = (log(s_0 / s_k) + 0.5 * self._swaption_expiry * vol ** 2) / (vol * sqrt(self._swaption_expiry))

        d_2 = d_1 - vol * sqrt(self._swaption_expiry)

        m = int(self._underlying_swap.cash_flow_frequency)

        a = (1 / m) * sum(
            [libor_curve.interpolate_discount_factor(t) for t in self._underlying_swap.times_of_cash_flows])

        l = self._notional * self._long_short * self._payer_receiver

        return l * a * (s_0 * norm.cdf(d_1 * self._payer_receiver) - s_k * norm.cdf(d_2 * self._payer_receiver))

    def cash_flow_report(self, libor_curve: LiborCurve, swaption_vol_surface: AbsSwaptionSurface):

        s_0 = self._underlying_swap.par_rate(libor_curve)

        s_k = self._strike

        vol = swaption_vol_surface.interpolate_vol(self._swaption_expiry, self._swap_tenor_years)

        d_1 = (log(s_0 / s_k) + 0.5 * self._swaption_expiry * vol ** 2) / (vol * sqrt(self._swaption_expiry))

        d_2 = d_1 - vol * sqrt(self._swaption_expiry)

        m = int(self._underlying_swap.cash_flow_frequency)

        l = self._notional * self._long_short * self._payer_receiver

        projected_cash_flows = []

        for t in self._underlying_swap.times_of_cash_flows:
            discount_factor = libor_curve.interpolate_discount_factor(t)

            projected_cash_flow = (l / m) * discount_factor * self._payer_receiver * (
                    s_0 * norm.cdf(d_1 * self._payer_receiver) - s_k * norm.cdf(d_2 * self._payer_receiver))

            projected_cash_flows.append({"time": t, "df": discount_factor, "projected": projected_cash_flow})

        return projected_cash_flows

    def first_order_curve_risk(self, libor_curve: LiborCurve, swaption_vol_surface):
        risk_map = dict()

        bumped_curve_map = libor_curve.bump_curve_by_instrument()

        npv = self.present_value(libor_curve, swaption_vol_surface)

        for node, bumped_curve in bumped_curve_map.items():
            risk_map[node] = self.present_value(bumped_curve, swaption_vol_surface) - npv

        return risk_map

    def gamma_curve_risk(self, libor_curve: LiborCurve, swaption_vol_surface):

        npv_1_map = dict()

        bumped_1_curve_map = libor_curve.bump_curve_by_instrument(n_bps_bump=1)

        npv_0 = self.present_value(libor_curve, swaption_vol_surface)

        for node, bumped_curve in bumped_1_curve_map.items():
            npv_1_map[node] = self.present_value(bumped_curve, swaption_vol_surface)

        npv_2_map = dict()

        bumped_2_curve_map = libor_curve.bump_curve_by_instrument(n_bps_bump=2)

        for node, bumped_curve in bumped_2_curve_map.items():
            npv_2_map[node] = self.present_value(bumped_curve, swaption_vol_surface)

        assert set(npv_1_map.keys()) == set(npv_2_map.keys())

        delta_1_map = {node: npv_2_map[node] - npv_1_map[node] for node in npv_1_map.keys()}

        delta_0_map = {node: npv_1 - npv_0 for node, npv_1 in npv_1_map.items()}

        gamma_map = {node: delta_1_map[node] - delta_0_map[node] for node in delta_0_map.keys()}

        return gamma_map

    def surface_vega_risk(self, libor_curve, swaption_vol_surface: AbsSwaptionSurface):

        npv_map = dict()

        npv = self.present_value(libor_curve, swaption_vol_surface)

        for expiry_tenor_tuple, bumped_surface in swaption_vol_surface.bump_surface().items():
            bump_npv = self.present_value(libor_curve, bumped_surface)

            npv_map[expiry_tenor_tuple] = bump_npv - npv

        return npv_map
