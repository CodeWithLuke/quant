from product.interest_rate_swap import InterestRateSwap
from product.interest_rate_swaption import InterestRateSwaption
from utils.enum import CashFlowFrequency, PayerReceiver, LongShort
from vol_surface.swaption_vol_surface.abs_swaption_surface import AbsSwaptionSurface
from yield_curve.libor_curve import LiborCurve

class CancellableSwap:

    def __init__(self, notional: float, swap_rate: float, termination_date: float, swap_tenor_years: float,
                 swap_cash_flow_frequency: CashFlowFrequency = CashFlowFrequency.SEMI_ANNUAL,
                 swap_payer_receiver: PayerReceiver = PayerReceiver.PAYER,
                 cancellation_payer_receiver: PayerReceiver = None):

        self._underlying_swap = InterestRateSwap(notional, swap_tenor_years, swap_cash_flow_frequency, swap_rate,
                                                 swap_payer_receiver)

        offsetting_swaption_tenor = swap_tenor_years - termination_date

        if swap_payer_receiver == PayerReceiver.PAYER:
            offsetting_swaption_payer_receiver = PayerReceiver.RECEIVER
        else:
            offsetting_swaption_payer_receiver = PayerReceiver.PAYER

        if cancellation_payer_receiver is None:
            cancellation_payer_receiver = swap_payer_receiver

        # cancellation_payer_receiver is which party has the option to cancel the swap
        if swap_payer_receiver == cancellation_payer_receiver:
            offsetting_swaption_long_short = LongShort.LONG
        else:
            offsetting_swaption_long_short = LongShort.SHORT

        self._offsetting_swaption = InterestRateSwaption(
            notional, swap_rate, termination_date, offsetting_swaption_tenor, swap_cash_flow_frequency,
            offsetting_swaption_payer_receiver, long_short=offsetting_swaption_long_short
        )

        self._termination_date = termination_date

    def present_value(self, libor_curve: LiborCurve, swaption_vol_surface: AbsSwaptionSurface):
        return self._underlying_swap.present_value(libor_curve) + self._offsetting_swaption.present_value(libor_curve,
                                                                                                          swaption_vol_surface)

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
