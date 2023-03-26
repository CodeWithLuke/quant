import pytest

from utils.constants import UNIT_TEST_ABS_TOLERANCE, UNIT_TEST_REL_TOLERANCE
from utils.enum import CashFlowFrequency, PayerReceiver
from yield_curve.flat_curve import FlatCurve
from yield_curve.libor_curve import LiborCurve
from yield_curve.spot_rate_point import SpotRatePoint
from vol_surface.swaption_vol_surface.swaption_flat_surface import SwaptionFlatVolSurface
from product.libor_swaption import LiborSwaption


def test_swaption_present_value():

    curve = FlatCurve(0.06)

    vol = SwaptionFlatVolSurface(0.2)

    swpn = LiborSwaption(100, 0.062, 5, 3, CashFlowFrequency.SEMI_ANNUAL, swap_payer_receiver=PayerReceiver.PAYER)

    assert swpn.present_value(curve,vol) == pytest.approx(
        2.07, abs=UNIT_TEST_ABS_TOLERANCE, rel=UNIT_TEST_REL_TOLERANCE)

