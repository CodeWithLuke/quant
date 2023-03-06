from product.libor_swap import LiborSwap
from product.libor_swaption import LiborSwaption
from utils.enum import CashFlowFrequency, PayerReceiver, OptionType, LongShort
from vol_surface.swaption_vol_surface import AtmSwaptionVolSurface
from yield_curve.libor_curve import LiborCurve
from yield_curve.libor_curve_builder.libor_bumped_curve_builder import bump_libor_curve_by_node


class CancellableLiborSwap:

    def __init__(self, notional: float, swap_rate: float, termination_date: float, swap_tenor_years: float,
                 swap_cash_flow_frequency: CashFlowFrequency=CashFlowFrequency.SEMI_ANNUAL,
                 swap_payer_receiver: PayerReceiver=PayerReceiver.PAYER,
                 cancellation_payer_receiver: PayerReceiver = None):

        self._underlying_swap = LiborSwap(notional, swap_tenor_years, swap_cash_flow_frequency, swap_rate,
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

        self._offsetting_swaption = LiborSwaption(
            notional, swap_rate, termination_date, offsetting_swaption_tenor, swap_cash_flow_frequency,
            offsetting_swaption_payer_receiver, option_type=OptionType.CALL, long_short=offsetting_swaption_long_short
        )

        self._termination_date = termination_date

    def present_value(self, libor_curve: LiborCurve, swaption_vol_surface: AtmSwaptionVolSurface):
        return self._underlying_swap.present_value(libor_curve) + self._offsetting_swaption.present_value(libor_curve,
            swaption_vol_surface)

    def first_order_curve_risk(self, libor_curve: LiborCurve, swaption_vol_surface):
        risk_map = dict()

        bumped_curve_map = bump_libor_curve_by_node(libor_curve)

        npv = self.present_value(libor_curve, swaption_vol_surface)

        for node, bumped_curve in bumped_curve_map.items():
            risk_map[node] = self.present_value(bumped_curve, swaption_vol_surface) - npv

        return risk_map

    def gamma_curve_risk(self, libor_curve: LiborCurve, swaption_vol_surface):

        npv_1_map = dict()

        bumped_1_curve_map = bump_libor_curve_by_node(libor_curve)

        npv_0 = self.present_value(libor_curve, swaption_vol_surface)

        for node, bumped_curve in bumped_1_curve_map.items():
            npv_1_map[node] = self.present_value(bumped_curve, swaption_vol_surface)

        npv_2_map = dict()

        bumped_2_curve_map = bump_libor_curve_by_node(libor_curve, n_bps_bump=2)

        for node, bumped_curve in bumped_2_curve_map.items():
            npv_2_map[node] = self.present_value(bumped_curve, swaption_vol_surface)

        assert set(npv_1_map.keys()) == set(npv_2_map.keys())

        delta_1_map = {node: npv_2_map[node] - npv_1_map[node] for node in npv_1_map.keys()}

        delta_0_map = {node: npv_1 - npv_0 for node, npv_1 in npv_1_map.items()}

        gamma_map = {node: delta_1_map[node] - delta_0_map[node] for node in delta_0_map.keys()}

        return gamma_map
