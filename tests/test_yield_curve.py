import pytest

from utils.constants import *
from yield_curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder


from yield_curve.spot_rate_point import SpotRatePoint


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

def test_forward_rate_calc():
    spot_rates = {
        0.5: 1.65, 1.0: 2.0, 2.0: 2.7, 3.0: 3.1, 5.0: 3.85, 7.0: 4.2, 10.0: 4.3
    }

    curve_points = []

    for t, spot_rate in spot_rates.items():
        curve_point = SpotRatePoint(t, spot_rate)

        curve_points.append(curve_point)

    curve = LiborCurve(curve_points)

    t1 = 2

    t2 = 5

    s1 = curve.interpolate_curve(t1)

    f_1_2 = curve.interpolate_forward_rate(t1, t2 - t1)

    s2 = curve.interpolate_curve(t2)

    payment_freq_to_test = (CashFlowFrequency.MONTHLY, CashFlowFrequency.ANNUAL, CashFlowFrequency.SEMI_ANNUAL)

    for m in payment_freq_to_test:

        lhs = ((1 + s1 / m) ** (m*t1)) * ((1 + f_1_2 / m) ** (m*(t2-t1)))

        rhs = ((1 + s2 / m) ** (m*t2))

        assert lhs == pytest.approx(rhs, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)
