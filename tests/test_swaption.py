from utils.enum import CashFlowFrequency, PayerReceiver
from yield_curve.libor_curve import LiborCurve
from yield_curve.spot_rate_point import SpotRatePoint
from vol_surface.swaption_vol_surface.swaption_flat_surface import SwaptionFlatVolSurface
from product.libor_swaption import LiborSwaption


def test_swaption_present_value():
    spot_rates = {
        0.0: 6.0, 5.5: 6.0, 6: 6.0, 6.5: 6.0, 7: 6.0, 7.5: 6.0, 8: 6.0, 10.0: 6.0
    }

    curve_points = []

    for t, spot_rate in spot_rates.items():
        curve_point = SpotRatePoint(t, spot_rate)

        curve_points.append(curve_point)

    curve = LiborCurve(curve_points)

    vol = SwaptionFlatVolSurface(0.2)

    swpn = LiborSwaption(100, 0.062, 5, 3, CashFlowFrequency.SEMI_ANNUAL, swap_payer_receiver=PayerReceiver.PAYER)

    print(swpn.present_value(curve,vol))

