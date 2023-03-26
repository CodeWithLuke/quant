import pytest

from product.libor_swap import LiborSwap
from utils.constants import UNIT_TEST_ABS_TOLERANCE, UNIT_TEST_REL_TOLERANCE
from utils.enum import CashFlowFrequency
from yield_curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder


def test_swap_par_rate():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    par_swap = LiborSwap.par_swap(curve, 1, 2, CashFlowFrequency.QUARTERLY)

    assert par_swap.swap_rate * 100 == pytest.approx(3.5829073672588927, abs=UNIT_TEST_ABS_TOLERANCE,
                                                     rel=UNIT_TEST_REL_TOLERANCE)


def test_swap_valuation():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    swap = LiborSwap(1, 2, CashFlowFrequency.QUARTERLY, 0.03)

    assert swap.present_value(curve) == pytest.approx(0.011248615516038618, abs=UNIT_TEST_ABS_TOLERANCE,
                                                      rel=UNIT_TEST_REL_TOLERANCE)

def test_swap_delta_risk():
    deposits = {1 / 52: 2.0, 1 / 12: 2.2, 1 / 6: 2.27, 1 / 4: 2.36}
    futures = {6 / 12: 97.4, 9 / 12: 97.0}
    swap_rate = {1.0: 3.0, 2.0: 3.6, 3.0: 3.95, 4.0: 4.2}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    swap = LiborSwap(10000, 2, CashFlowFrequency.QUARTERLY, 0.03)

    report = swap.first_order_curve_risk(curve)

    assert report['IR_SWAP_2Y'] == pytest.approx(1.90489)
