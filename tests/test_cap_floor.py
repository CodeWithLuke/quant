import pytest

from product.libor_cap_floor import Caplet
from utils.constants import UNIT_TEST_ABS_TOLERANCE, UNIT_TEST_REL_TOLERANCE
from yield_curve.flat_curve import FlatCurve


def test_caplet_present_value():
    curve = FlatCurve(0.07)

    caplet = Caplet(10000, 0.08, 1, 1.25)

    vol = 0.2

    assert caplet.present_value(curve, vol) == pytest.approx(5.162, abs=UNIT_TEST_ABS_TOLERANCE,
                                                             rel=UNIT_TEST_REL_TOLERANCE)
