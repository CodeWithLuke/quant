import pytest

from product.cancellable_swap import CancellableSwap
from product.interest_rate_swap import InterestRateSwap
from utils.enum import CashFlowFrequency
from vol_surface.swaption_vol_surface.atm_swaption_vol_surface import AtmSwaptionVolSurface
from yield_curve.libor_curve import LiborCurve


def test_cancellable_swap_valuation():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rates = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2, 5.0: 4.4}
    curve = LiborCurve.from_market_quotes(deposits, futures, swap_rates)

    vol = AtmSwaptionVolSurface.from_csv(r"tests/data/vol_surfaces/sample_swaption_vols.csv")

    par_swap = InterestRateSwap.par_swap(curve, 1000000, 3, CashFlowFrequency.SEMI_ANNUAL)


    cs_obj = CancellableSwap(1000000, par_swap.swap_rate, 2, 3)

    assert cs_obj.present_value(curve, vol) == pytest.approx(2165.44)

def test_cancellable_swap_delta_risk():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rates = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2, 5.0: 4.4}
    curve = LiborCurve.from_market_quotes(deposits, futures, swap_rates)

    vol = AtmSwaptionVolSurface.from_csv(r"tests/data/vol_surfaces/sample_swaption_vols.csv")

    par_swap = InterestRateSwap.par_swap(curve, 1000000, 3, CashFlowFrequency.SEMI_ANNUAL)


    cs_obj = CancellableSwap(1000000, par_swap.swap_rate, 2, 3)

    assert cs_obj.first_order_curve_risk(curve, vol)

def test_cancellable_swap_vega_risk():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rates = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2, 5.0: 4.4}
    curve = LiborCurve.from_market_quotes(deposits, futures, swap_rates)

    vol = AtmSwaptionVolSurface.from_csv(r"tests/data/vol_surfaces/sample_swaption_vols.csv")

    par_swap = InterestRateSwap.par_swap(curve, 1000000, 3, CashFlowFrequency.SEMI_ANNUAL)


    cs_obj = CancellableSwap(1000000, par_swap.swap_rate, 2, 3)

    assert cs_obj.surface_vega_risk(curve, vol)

def test_cancellable_swap_gamma_risk():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rates = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2, 5.0: 4.4}
    curve = LiborCurve.from_market_quotes(deposits, futures, swap_rates)

    vol = AtmSwaptionVolSurface.from_csv(r"tests/data/vol_surfaces/sample_swaption_vols.csv")

    par_swap = InterestRateSwap.par_swap(curve, 1000000, 3, CashFlowFrequency.SEMI_ANNUAL)


    cs_obj = CancellableSwap(1000000, par_swap.swap_rate, 2, 3)

    assert cs_obj.gamma_curve_risk(curve, vol)
