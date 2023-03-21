import pytest

from utils.constants import *
from yield_curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder


def test_yield_curve_construction():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    expected_rates = [1.9996154832063695,
                      2.197985794764072,
                      2.265716716659804,
                      2.3530652632622195,
                      2.4723258511729345,
                      2.644485879275427,
                      2.9815170310766788,
                      3.5823684733174996,
                      3.936610028120395,
                      4.193130458902937]

    for i, expected_rate in enumerate(expected_rates):
        expected_rate_scaled = expected_rate / 100
        assert curve._s[i] == pytest.approx(expected_rate_scaled, abs=UNIT_TEST_ABS_TOLERANCE,
                                            rel=UNIT_TEST_REL_TOLERANCE)


def test_discount_factor_calc():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    df_1 = curve.interpolate_discount_factor(3.0)
    df_2 = curve.interpolate_discount_factor(3.5)
    v = 100000 * (df_2 * 0.5 * 0.02 + df_2 - df_1)

    assert v == pytest.approx(-1254.8198358152129, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)
