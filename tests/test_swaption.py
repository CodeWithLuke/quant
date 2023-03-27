import pytest

from utils.constants import UNIT_TEST_ABS_TOLERANCE, UNIT_TEST_REL_TOLERANCE
from utils.enum import CashFlowFrequency, PayerReceiver
from yield_curve.flat_curve import FlatCurve
from yield_curve.libor_curve import LiborCurve
from vol_surface.swaption_vol_surface.swaption_flat_surface import SwaptionFlatVolSurface
from product.interest_rate_swaption import InterestRateSwaption


def test_swaption_present_value():

    curve = FlatCurve(0.06)

    vol = SwaptionFlatVolSurface(0.2)

    swaption_obj = InterestRateSwaption(100, 0.062, 5, 3, CashFlowFrequency.SEMI_ANNUAL, swap_payer_receiver=PayerReceiver.PAYER)

    assert swaption_obj.present_value(curve,vol) == pytest.approx(
        2.07, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)

def test_swaption_delta_risk():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2, 5.0: 4.4}
    curve = LiborCurve.from_market_quotes(deposits, futures, swap_rate)

    vol = SwaptionFlatVolSurface(0.2)

    swaption_obj = InterestRateSwaption(10000, 0.062, 1, 3, CashFlowFrequency.SEMI_ANNUAL, swap_payer_receiver=PayerReceiver.PAYER)

    report = swaption_obj.first_order_curve_risk(curve, vol)

    assert report["IR_SWAP_1Y"] == pytest.approx(-0.08625383967139122) and report["IR_SWAP_4Y"] == pytest.approx(0.32758424778292294)


# TODO: check test results not just exception
def test_swaption_gamma_risk():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2, 5.0: 4.4}
    curve = LiborCurve.from_market_quotes(deposits, futures, swap_rate)

    vol = SwaptionFlatVolSurface(0.2)

    swaption_obj = InterestRateSwaption(10000, 0.062, 1, 3, CashFlowFrequency.SEMI_ANNUAL, swap_payer_receiver=PayerReceiver.PAYER)

    report = swaption_obj.gamma_curve_risk(curve, vol)

    assert report
