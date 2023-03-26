import pytest

from product.bond.fixed_rate_bond import FixedRateBond
from product.bond.zero_coupon_bond import ZeroCouponBond
from utils.constants import UNIT_TEST_ABS_TOLERANCE, UNIT_TEST_REL_TOLERANCE
from utils.enum import CashFlowFrequency
from yield_curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder


def test_bond_priced_from_curve():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    test_bond = FixedRateBond(10000, 2, CashFlowFrequency.SEMI_ANNUAL, coupon_rate=0.07)

    assert test_bond.present_value(curve) == pytest.approx(
        10653, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)


def test_bond_price_to_yield_zero_coupon():
    price = 9910

    test_bond = ZeroCouponBond(10000, 0.5)

    yield_rate = test_bond.price_to_yield(price)

    assert yield_rate == pytest.approx(0.01808, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)

def test_bond_price_to_yield_fixed_rate():
    price = 98000

    test_bond = FixedRateBond(100000, 2.5, CashFlowFrequency.SEMI_ANNUAL, 0.07)

    yield_rate = test_bond.price_to_yield(price)

    assert yield_rate == pytest.approx(0.07813, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)
