import pytest

from product.fixed_rate_bond import FixedRateBond
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

    assert test_bond.present_value(curve) == 10652.994335330433
