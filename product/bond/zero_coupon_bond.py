from math import exp

from scipy.optimize import newton

from yield_curve.libor_curve import LiborCurve


class ZeroCouponBond:
    def __init__(self, notional: float, maturity: float):
        self.notional = notional
        self.maturity = maturity

    def present_value(self, libor_curve, applied_z_spread=0):

        value = self.notional * exp(-1 * self.maturity * (libor_curve.interpolate_curve(self.maturity) + applied_z_spread))

        return value

    def yield_to_price(self, yield_rate: float):

        return self.notional * exp(-1 * self.maturity * yield_rate)

    def price_to_yield(self, price: float):
        def _f(y): return self.yield_to_price(y) - price

        return newton(_f, 0.0)

    def get_bond_duration_from_yield(self, yield_rate: float):

        return self.maturity * self.notional * exp(-1 * self.maturity * yield_rate)

    def z_spread(self, price: float, libor_curve: LiborCurve):

        def _f(z): return self.present_value(libor_curve, z) - price

        return newton(_f, 0)
